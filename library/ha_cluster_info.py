#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# make ansible-test happy, even though the module requires Python 3
from __future__ import absolute_import, division, print_function

# make ansible-test happy, even though the module requires Python 3
# pylint: disable=invalid-name
__metaclass__ = type
# pylint: enable=invalid-name

DOCUMENTATION = r"""
---
module: ha_cluster_info
short_description: Export HA cluster configuration
description:
    This module exports live cluster configuration in form of variables which
    recreate the same configuration when passed to ha_cluster role. Note that
    the set of variables may not be complete and manual modification of the
    result is expected (at least setting ha_cluster_hacluster_password is
    required).
author:
    - Tomas Jelinek (@tomjelinek)
requirements:
    - pcs-0.10.8 or newer installed on managed nodes
    - pcs-0.10.8 or newer for exporting corosync configuration
    - python 3.6 or newer
"""

EXAMPLES = r"""
- name: Get HA cluster configuration
  ha_cluster_info:
  register: my_ha_cluster_info
"""

RETURN = r"""
ha_cluster:
    returned: success
    type: dict
    description:
        - Information about existing cluster on the node. If passed to
          ha_cluster role, the role recreates the same cluster. Note that the
          set of variables may not be complete and manual modification of the
          result is expected. The variables are documented in the role.
        - Note that depending on pcs version present on the managed node,
          certain variables may not be exported.
        - HORIZONTALLINE
        - Following variables are present in the output
        - ha_cluster_cluster_present
        - ha_cluster_start_on_boot
        - ha_cluster_cluster_name
        - ha_cluster_transport
        - ha_cluster_totem
        - ha_cluster_quorum
        - ha_cluster_node_options - currently only node_name,
          corosync_addresses and pcs_address are present
        - HORIZONTALLINE
        - Following variables are required for running ha_cluster role but are
          never present in this module output
        - ha_cluster_hacluster_password
        - HORIZONTALLINE
        - Following variables are never present in this module output (consult
          the role documentation for impact of the variables missing)
        - ha_cluster_corosync_key_src
        - ha_cluster_pacemaker_key_src
        - ha_cluster_fence_virt_key_src
        - ha_cluster_regenerate_keys
        - HORIZONTALLINE
"""

import json
import os.path
from typing import Any, Dict, List

from ansible.module_utils.basic import AnsibleModule

COROSYNC_CONF_PATH = "/etc/corosync/corosync.conf"
KNOWN_HOSTS_PATH = "/var/lib/pcsd/known-hosts"


class PcsCliError(Exception):
    """
    Parent exception for errors from running pcs CLI
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


class PcsCliRunError(PcsCliError):
    """
    Running pcs has failed
    """


class PcsCliJsonError(PcsCliError):
    """
    Pcs output cannot be decoded as a JSON
    """

    def __init__(
        self,
        pcs_command: List[str],
        rc: int,
        stdout: str,
        stderr: str,
        json_error: str,
    ):
        # pylint: disable=too-many-arguments
        # pylint 3.3 produces too-many-positional-arguments, but pylint 3.2
        # complies that it doesn't know such an option. So we need
        # unknown-option-value to silence pylint 3.2.
        # pylint: disable=unknown-option-value
        # pylint: disable=too-many-positional-arguments
        super().__init__(pcs_command, rc, stdout, stderr)
        self.json_error = json_error

    @property
    def kwargs(self) -> Dict[str, Any]:
        result = super().kwargs
        result.update(dict(json_error=self.json_error))
        return result


class PcsJsonParseError(Exception):
    """
    Unable to parse JSON data
    """

    def __init__(self, error: str, data: str, data_desc: str):
        self.error = error
        self.data = data
        self.data_desc = data_desc

    @property
    def kwargs(self) -> Dict[str, Any]:
        """
        Arguments given to the constructor
        """
        return dict(error=self.error, data=self.data, data_desc=self.data_desc)


class PcsJsonMissingKey(Exception):
    """
    A key is not present in pcs JSON output
    """

    def __init__(self, key: str, data: Dict[str, Any], data_desc: str):
        self.key = key
        self.data = data
        self.data_desc = data_desc

    @property
    def kwargs(self) -> Dict[str, Any]:
        """
        Arguments given to the constructor
        """
        return dict(key=self.key, data=self.data, data_desc=self.data_desc)


def dict_to_nv_list(input_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Convert a dict to a list of dicts with keys 'name' and 'value'
    """
    return [dict(name=name, value=value) for name, value in input_dict.items()]


def is_service_enabled(module: AnsibleModule, service: str) -> bool:
    """
    Check whether a specified service is enabled in the OS

    service -- name of the service to check without the ".service" suffix
    """
    env = {
        # make sure to get output of external processes in English and ASCII
        "LC_ALL": "C",
    }
    # wokeignore:rule=dummy
    rc, dummy_stdout, dummy_stderr = module.run_command(
        ["systemctl", "is-enabled", f"{service}.service"],
        check_rc=False,
        environ_update=env,
    )
    return rc == 0


def call_pcs_cli(module: AnsibleModule, command: List[str]) -> Dict[str, Any]:
    """
    Run pcs CLI with the specified command, transform resulting JSON into a dict

    command -- pcs command to run without the "pcs" prefix
    """
    env = {
        # make sure to get output of external processes in English and ASCII
        "LC_ALL": "C",
    }
    full_command = ["pcs"] + command
    rc, stdout, stderr = module.run_command(
        full_command,
        check_rc=False,
        environ_update=env,
    )
    if rc != 0:
        raise PcsCliRunError(full_command, rc, stdout, stderr)
    try:
        return json.loads(stdout)
    except json.JSONDecodeError as e:
        raise PcsCliJsonError(full_command, rc, stdout, stderr, str(e)) from e


def export_start_on_boot(module: AnsibleModule) -> bool:
    """
    Detect wheter a cluster is configured to start on boot
    """
    return is_service_enabled(module, "corosync") or is_service_enabled(
        module, "pacemaker"
    )


def export_corosync_conf(module: AnsibleModule) -> Dict[str, Any]:
    """
    Export corosync configuration
    """
    conf_dict = call_pcs_cli(
        module, ["cluster", "config", "--output-format=json"]
    )
    result: Dict[str, Any] = dict()
    try:
        result["ha_cluster_cluster_name"] = conf_dict["cluster_name"]

        transport = dict(type=conf_dict["transport"].lower())
        if conf_dict["transport_options"]:
            transport["options"] = dict_to_nv_list(
                conf_dict["transport_options"]
            )
        if conf_dict["links_options"]:
            link_list = []
            for link_dict in conf_dict["links_options"].values():
                # linknumber is an index in links_options, but it is present in
                # link_dict as well
                link_list.append(dict_to_nv_list(link_dict))
            transport["links"] = link_list
        if conf_dict["compression_options"]:
            transport["compression"] = dict_to_nv_list(
                conf_dict["compression_options"]
            )
        if conf_dict["crypto_options"]:
            transport["crypto"] = dict_to_nv_list(conf_dict["crypto_options"])
        result["ha_cluster_transport"] = transport

        if conf_dict["totem_options"]:
            result["ha_cluster_totem"] = dict(
                options=dict_to_nv_list(conf_dict["totem_options"])
            )
        if conf_dict["quorum_options"]:
            result["ha_cluster_quorum"] = dict(
                options=dict_to_nv_list(conf_dict["quorum_options"])
            )

        if conf_dict["nodes"]:
            node_list = []
            for index, node_dict in enumerate(conf_dict["nodes"]):
                try:
                    node_list.append(
                        dict(
                            node_name=node_dict["name"],
                            corosync_addresses=[
                                addr_dict["addr"]
                                for addr_dict in sorted(
                                    node_dict["addrs"],
                                    key=lambda item: item["link"],
                                )
                            ],
                        )
                    )
                except KeyError as e:
                    raise PcsJsonMissingKey(
                        e.args[0],
                        conf_dict,
                        f"corosync configuration for node on index {index}",
                    ) from e
            result["ha_cluster_node_options"] = node_list

    except KeyError as e:
        raise PcsJsonMissingKey(
            e.args[0], conf_dict, "corosync configuration"
        ) from e
    return result


def load_pcsd_known_hosts() -> Dict[str, str]:
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
        raise PcsJsonParseError(
            str(e), "not logging data", "known hosts"
        ) from e


def merge_known_hosts(
    result: Dict[str, Any], node_addr: Dict[str, str]
) -> None:
    """
    Merge pcs node addresses into ha_cluster_node_options key

    result -- structure with exported corosync configuration
    node_addr -- node_name: node_addr map loaded from known hosts
    """
    # node_addr may contain records for nodes which are not part of the cluster
    # being exported. These are ignored. We are only interested in pcs
    # addresses of nodes forming the exported cluster.
    if not node_addr:
        return
    if "ha_cluster_node_options" not in result:
        return
    for node_options in result["ha_cluster_node_options"]:
        if node_options["node_name"] in node_addr:
            node_options["pcs_address"] = node_addr[node_options["node_name"]]


def export_cluster_configuration(module: AnsibleModule) -> Dict[str, Any]:
    """
    Export existing HA cluster configuration
    """
    # Until pcs is able to export the whole configuration in one go, we need to
    # put it together from separate parts provided by pcs. Some parts are only
    # available in recent pcs versions. Check pcs capabilities.
    result: dict[str, Any] = dict()

    result["ha_cluster_start_on_boot"] = export_start_on_boot(module)

    # Corosync config is availabe via CLI since pcs-0.10.8, via API v2 since
    # pcs-0.12.0 and pcs-0.11.9. For old pcs versions, CLI must be used, and
    # there is no benefit in implementing access via API on top of that.
    # No need to check pcs capabilities. If this is not supported by pcs,
    # exporting anything else is pointless (and not supported by pcs anyway).
    result.update(**export_corosync_conf(module))

    # known-hosts file is available since pcs-0.10, but is not exported by pcs
    # in any version.
    # No need to check pcs capabilities.
    merge_known_hosts(result, load_pcsd_known_hosts())

    return result


def main() -> None:
    """
    Top level module function
    """
    module_args: Dict[str, Any] = dict()
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    module_result: Dict[str, Any] = dict()
    ha_cluster_result: Dict[str, Any] = dict()
    module_result["ha_cluster"] = ha_cluster_result

    try:
        if os.path.exists(COROSYNC_CONF_PATH):
            ha_cluster_result.update(**export_cluster_configuration(module))
            ha_cluster_result["ha_cluster_cluster_present"] = True
        else:
            ha_cluster_result["ha_cluster_cluster_present"] = False
        module.exit_json(**module_result)
    except PcsJsonMissingKey as e:
        module.fail_json(
            msg=f"Missing key in pcs {e.data_desc} JSON output: {e.key}",
            pcs_error=e.kwargs,
        )
    except PcsCliJsonError as e:
        module.fail_json(
            msg="Error while parsing pcs JSON output", pcs_error=e.kwargs
        )
    except PcsCliError as e:
        module.fail_json(msg="Error while running pcs", pcs_error=e.kwargs)


if __name__ == "__main__":
    main()
