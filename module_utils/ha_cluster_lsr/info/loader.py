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
