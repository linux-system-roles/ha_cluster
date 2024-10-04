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

from typing import Any, Dict, List, Optional, Tuple

from ansible.module_utils.basic import AnsibleModule

# pylint: disable=no-name-in-module
from ansible.module_utils.ha_cluster_lsr.info import exporter, loader


def get_cmd_runner(module: AnsibleModule) -> loader.CommandRunner:
    """
    Provide a function responsible for running external processes
    """

    def runner(
        args: List[str], environ_update: Optional[Dict[str, str]] = None
    ) -> Tuple[int, str, str]:
        return module.run_command(
            args, check_rc=False, environ_update=environ_update
        )

    return runner


def export_cluster_configuration(module: AnsibleModule) -> Dict[str, Any]:
    """
    Export existing HA cluster configuration
    """
    # Until pcs is able to export the whole configuration in one go, we need to
    # put it together from separate parts provided by pcs. Some parts are only
    # available in recent pcs versions. Check pcs capabilities.
    result: dict[str, Any] = dict()
    cmd_runner = get_cmd_runner(module)

    result["ha_cluster_start_on_boot"] = loader.get_start_on_boot(cmd_runner)

    # Corosync config is availabe via CLI since pcs-0.10.8, via API v2 since
    # pcs-0.12.0 and pcs-0.11.9. For old pcs versions, CLI must be used, and
    # there is no benefit in implementing access via API on top of that.
    # No need to check pcs capabilities. If this is not supported by pcs,
    # exporting anything else is pointless (and not supported by pcs anyway).
    corosync_conf_pcs = loader.get_corosync_conf(cmd_runner)
    # known-hosts file is available since pcs-0.10, but is not exported by pcs
    # in any version.
    # No need to check pcs capabilities.
    known_hosts_pcs = loader.get_pcsd_known_hosts()

    # Convert corosync config to role format
    corosync_conf_role = exporter.export_corosync_options(corosync_conf_pcs)
    for key in (
        "ha_cluster_cluster_name",
        "ha_cluster_transport",
        "ha_cluster_totem",
        "ha_cluster_quorum",
    ):
        if key in corosync_conf_role:
            result[key] = corosync_conf_role[key]

    # Convert cluster definition to role format
    try:
        result["ha_cluster_node_options"] = exporter.export_cluster_nodes(
            corosync_conf_pcs["nodes"], known_hosts_pcs
        )
    except KeyError as e:
        raise exporter.JsonMissingKey(
            e.args[0], corosync_conf_pcs, "corosync configuration"
        ) from e

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
        if loader.has_corosync_conf():
            ha_cluster_result.update(**export_cluster_configuration(module))
            ha_cluster_result["ha_cluster_cluster_present"] = True
        else:
            ha_cluster_result["ha_cluster_cluster_present"] = False
        module.exit_json(**module_result)
    except exporter.JsonMissingKey as e:
        module.fail_json(
            msg=f"Missing key {e.key} in pcs {e.data_desc} JSON output",
            error_details=e.kwargs,
        )
    except loader.JsonParseError as e:
        module.fail_json(
            msg="Error while parsing pcs JSON output", error_details=e.kwargs
        )
    except loader.CliCommandError as e:
        module.fail_json(msg="Error while running pcs", error_details=e.kwargs)


if __name__ == "__main__":
    main()
