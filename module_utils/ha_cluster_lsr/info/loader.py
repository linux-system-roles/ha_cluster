# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# make ansible-test happy, even though the module requires Python 3
from __future__ import absolute_import, division, print_function

# make ansible-test happy, even though the module requires Python 3
# pylint: disable=invalid-name
__metaclass__ = type

import json
import os.path
from typing import Any, Callable, Dict, List, Optional, Tuple

COROSYNC_CONF_PATH = "/etc/corosync/corosync.conf"
KNOWN_HOSTS_PATH = "/var/lib/pcsd/known-hosts"
PCSD_SETTINGS_PATH = "/var/lib/pcsd/pcs_settings.conf"

CommandRunner = Callable[
    # parameters: args, environ_update
    # environ_update should be a keyword argument, but they are not possible in
    # Callable. typing.Protocol would have to be used to type that, but that is
    # not available in Python 3.6
    [List[str], Optional[Dict[str, str]]],
    # return value: rc, stdout, stderr
    Tuple[int, str, str],
]


class CliCommandError(Exception):
    """
    Running pcs has failed
    """

    def __init__(
        self, pcs_command: List[str], rc: int, stdout: str, stderr: str
    ):
        self.pcs_command = pcs_command
        self.rc = rc
        self.stdout = stdout
        self.stderr = stderr

    @property
    def kwargs(self) -> Dict[str, Any]:
        """
        Arguments given to the constructor
        """
        return dict(
            pcs_command=self.pcs_command,
            rc=self.rc,
            stdout=self.stdout,
            stderr=self.stderr,
        )


class JsonParseError(Exception):
    """
    Unable to parse JSON data
    """

    def __init__(
        self,
        error: str,
        data: str,
        data_desc: str,
        additional_info: Optional[str] = None,
    ):
        self.error = error
        self.data = data
        self.data_desc = data_desc
        self.additional_info = additional_info

    @property
    def kwargs(self) -> Dict[str, Any]:
        """
        Arguments given to the constructor
        """
        return dict(
            error=self.error,
            data=self.data,
            data_desc=self.data_desc,
            additional_info=self.additional_info,
        )


def is_rhel_or_clone() -> bool:
    """
    Check whether current OS is RHEL or its clone
    """
    # Check https://github.com/chef/os_release/ to see os-release content for
    # various distros.
    searched_lines = [
        f'PLATFORM_ID="platform:{platform}"'
        for platform in ("el8", "el9", "el10")
    ]
    try:
        with open(
            "/etc/os-release", "r", encoding="utf-8", errors="replace"
        ) as os_release_file:
            for file_line in os_release_file:
                if file_line.strip() in searched_lines:
                    return True
    except OSError:
        return False
    return False


def get_dnf_repolist(run_command: CommandRunner) -> Optional[str]:
    """
    Get list of enabled repositories or None on error
    """
    # wokeignore:rule=dummy
    rc, stdout, dummy_stderr = run_command(["dnf", "repolist"], {})
    return stdout if rc == 0 else None


def get_rpm_installed_packages(
    run_command: CommandRunner,
) -> Optional[List[str]]:
    """
    Return names of installed packages or None on error
    """
    # wokeignore:rule=dummy
    rc, stdout, dummy_stderr = run_command(
        ["rpm", "--query", "--all", "--queryformat", "%{NAME}\\n"], {}
    )
    return stdout.splitlines() if rc == 0 else None


def is_service_enabled(run_command: CommandRunner, service: str) -> bool:
    """
    Check whether a specified service is enabled in the OS

    service -- name of the service to check without the ".service" suffix
    """
    env = {
        # make sure to get output of external processes in English and ASCII
        "LC_ALL": "C",
    }
    # wokeignore:rule=dummy
    rc, dummy_stdout, dummy_stderr = run_command(
        ["systemctl", "is-enabled", f"{service}.service"], env
    )
    return rc == 0


def get_firewall_config(
    fw: Any,  # firewall module doesn't provide type hints
) -> Optional[Dict[str, Any]]:
    """
    Get simplified firewall config of a given zone or None on error

    fw -- firewall client instance
    """
    try:
        settings = fw.config().getZoneByName(fw.getDefaultZone()).getSettings()
        return {
            "services": settings.getServices(),
            "ports": settings.getPorts(),
        }
    # catch any exception, firewall is not installed or not running, etc.
    except Exception:  # pylint: disable=broad-except
        return None


def get_firewall_ha_cluster_ports(
    fw: Any,  # firewall module doesn't provide type hints
) -> Optional[List[Tuple[str, str]]]:
    """
    Get ports used by HA cluster or None on error

    fw -- firewall client instance
    """
    try:
        return (
            fw.config()
            .getServiceByName("high-availability")
            .getSettings()
            .getPorts()
        )
    # catch any exception, firewall is not installed or not running, etc.
    except Exception:  # pylint: disable=broad-except
        return None


def get_selinux_ha_cluster_ports(
    selinux_ports: Any,  # selinux module doesn't provide type hints
) -> Optional[Tuple[List[str], List[str]]]:
    """
    Get TCP and UDP ports labelled for HA cluster in selinux or None on error

    selinux_ports -- selinux port records instance
    """
    try:
        all_ports = selinux_ports.get_all_by_type()
        return (
            all_ports.get(("cluster_port_t", "tcp"), []),
            all_ports.get(("cluster_port_t", "udp"), []),
        )
    # catch any exception, selinux not available, etc.
    except Exception:  # pylint: disable=broad-except
        return None


def _call_pcs_cli(
    run_command: CommandRunner, command: List[str]
) -> Dict[str, Any]:
    """
    Run pcs CLI with the specified command, transform resulting JSON into a dict

    command -- pcs command to run without the "pcs" prefix
    """
    env = {
        # make sure to get output of external processes in English and ASCII
        "LC_ALL": "C",
    }
    full_command = ["pcs"] + command
    rc, stdout, stderr = run_command(full_command, env)
    if rc != 0:
        raise CliCommandError(full_command, rc, stdout, stderr)
    try:
        return json.loads(stdout)
    except json.JSONDecodeError as e:
        raise JsonParseError(
            str(e), stdout, " ".join(full_command), stderr
        ) from e


def has_corosync_conf() -> bool:
    """
    Check whether corosync.conf file is present
    """
    return os.path.exists(COROSYNC_CONF_PATH)


def get_corosync_conf(run_command: CommandRunner) -> Dict[str, Any]:
    """
    Get corosync configuration from pcs
    """
    return _call_pcs_cli(
        run_command, ["cluster", "config", "--output-format=json"]
    )


def get_pcsd_known_hosts() -> Dict[str, str]:
    """
    Load pcsd known hosts and return dict node_name: node_address
    """
    result: Dict[str, str] = dict()
    if not os.path.exists(KNOWN_HOSTS_PATH):
        return result
    try:
        with open(KNOWN_HOSTS_PATH, "r", encoding="utf-8") as known_hosts_file:
            known_hosts = json.load(known_hosts_file)
        for host_name, host_data in known_hosts.get("known_hosts", {}).items():
            if not host_data.get("dest_list"):
                continue
            # currently no more than one address is supported by both the role
            # and pcs
            addr = host_data.get("dest_list")[0].get("addr")
            port = host_data.get("dest_list")[0].get("port")
            if not addr:
                continue
            host_addr = addr
            if port:
                host_addr = (
                    f"[{addr}]:{port}" if ":" in addr else f"{addr}:{port}"
                )
            result[host_name] = host_addr
        return result
    except json.JSONDecodeError as e:
        # cannot show actual data as they contain sensitive information - tokens
        raise JsonParseError(str(e), "not logging data", "known hosts") from e


def get_pcsd_settings_conf() -> Optional[Dict[str, Any]]:
    """
    Load pcsd config file pcs_settings.conf
    """
    # There is no pcs interface for the file yet, so we parse the file directly.
    if not os.path.exists(PCSD_SETTINGS_PATH):
        return None

    try:
        with open(
            PCSD_SETTINGS_PATH, "r", encoding="utf-8"
        ) as pcsd_settings_file:
            file_data = pcsd_settings_file.read()
            return json.loads(file_data)
    except json.JSONDecodeError as e:
        raise JsonParseError(str(e), file_data, "pcsd settings") from e


def get_resources_configuration(run_command: CommandRunner) -> Dict[str, Any]:
    """
    Get resources, groups, clones, bundles configuration from pcs
    """
    return _call_pcs_cli(
        run_command, ["resource", "config", "--output-format=json"]
    )


def get_stonith_configuration(run_command: CommandRunner) -> Dict[str, Any]:
    """
    Get resources, groups, clones, bundles configuration from pcs
    """
    return _call_pcs_cli(
        run_command, ["stonith", "config", "--output-format=json"]
    )


def get_pcs_version_info(run_command: CommandRunner) -> Tuple[str, List[str]]:
    """
    Get pcs version and list of capabilities
    """
    env = {
        # make sure to get output of external processes in English and ASCII
        "LC_ALL": "C",
    }
    command = ["pcs", "--version", "--full"]
    rc, stdout, stderr = run_command(command, env)
    if rc != 0:
        raise CliCommandError(command, rc, stdout, stderr)
    lines = stdout.splitlines() + [""]  # empty line for case without 2. line
    return (lines[0], lines[1].split())
