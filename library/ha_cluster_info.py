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
        - ha_cluster_enable_repos
        - ha_cluster_enable_repos_resilient_storage
        - ha_cluster_cluster_present
        - ha_cluster_start_on_boot
        - ha_cluster_install_cloud_agents
        - ha_cluster_pcs_permission_list
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
        - ha_cluster_fence_agent_packages
        - ha_cluster_extra_packages
        - ha_cluster_use_latest_packages
        - ha_cluster_hacluster_qdevice_password
        - ha_cluster_corosync_key_src
        - ha_cluster_pacemaker_key_src
        - ha_cluster_fence_virt_key_src
        - ha_cluster_pcsd_public_key_src
        - ha_cluster_pcsd_private_key_src
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


def export_os_configuration(module: AnsibleModule) -> Dict[str, Any]:
    """
    Export OS configuration managed by the role
    """
    result: dict[str, Any] = dict()
    cmd_runner = get_cmd_runner(module)

    if loader.is_rhel_or_clone():
        # The role only enables repos on RHEL and SLES.
        dnf_repolist = loader.get_dnf_repolist(cmd_runner)
        if dnf_repolist is not None:
            result["ha_cluster_enable_repos"] = exporter.export_enable_repos_ha(
                dnf_repolist
            )
            result["ha_cluster_enable_repos_resilient_storage"] = (
                exporter.export_enable_repos_rs(dnf_repolist)
            )

        # Cloud agent packages are only handled on RHEL.
        installed_packages = loader.get_rpm_installed_packages(cmd_runner)
        if installed_packages is not None:
            result["ha_cluster_install_cloud_agents"] = (
                exporter.export_install_cloud_agents(installed_packages)
            )

    return result


def export_pcsd_configuration() -> Dict[str, Any]:
    """
    Export pcsd configuration managed by the role
    """
    result: dict[str, Any] = dict()

    pcs_permissions = loader.get_pcsd_local_cluster_permissions()
    if pcs_permissions is not None:
        result["ha_cluster_pcs_permission_list"] = pcs_permissions

    return result


def export_cluster_configuration(module: AnsibleModule) -> Dict[str, Any]:
    """
    Export existing HA cluster configuration
    """
    # Until pcs is able to export the whole configuration in one go, we need to
    # put it together from separate parts provided by pcs. Some parts are only
    # available in recent pcs versions. Check pcs capabilities.
    result: dict[str, Any] = dict()
    cmd_runner = get_cmd_runner(module)

    corosync_enabled = loader.is_service_enabled(cmd_runner, "corosync")
    pacemaker_enabled = loader.is_service_enabled(cmd_runner, "pacemaker")
    result["ha_cluster_start_on_boot"] = exporter.export_start_on_boot(
        corosync_enabled, pacemaker_enabled
    )

    # Corosync config is available via CLI since pcs-0.10.8, via API v2 since
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
    result["ha_cluster_cluster_name"] = exporter.export_corosync_cluster_name(
        corosync_conf_pcs
    )
    result["ha_cluster_transport"] = exporter.export_corosync_transport(
        corosync_conf_pcs
    )
    exported_totem = exporter.export_corosync_totem(corosync_conf_pcs)
    if exported_totem:
        result["ha_cluster_totem"] = exported_totem
    exported_quorum = exporter.export_corosync_quorum(corosync_conf_pcs)
    if exported_quorum:
        result["ha_cluster_quorum"] = exported_quorum

    # Convert nodes definition to role format
    result["ha_cluster_node_options"] = exporter.export_cluster_nodes(
        corosync_conf_pcs, known_hosts_pcs
    )

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
            ha_cluster_result.update(**export_os_configuration(module))
            ha_cluster_result.update(**export_pcsd_configuration())
            ha_cluster_result.update(**export_cluster_configuration(module))
            ha_cluster_result["ha_cluster_cluster_present"] = True
        else:
            # Exporting qnetd configuration will be added later here. It will
            # probably call export_os and export_pcsd.
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
