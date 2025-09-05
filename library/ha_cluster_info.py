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
    - pcs-0.10.14 or pcs-0.11.3 or newer for exporting resources configuration
    - pcs-0.10.17 or pcs-0.11.6 or newer for exporting cluster properties
      configuration
    - pcs-0.12.0a1 or newer for exporting resources defaults and resources
      operation defaults
    - python3-firewall for exporting ha_cluster_manage_firewall
    - python3-policycoreutils for exporting ha_cluster_manage_selinux
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
        - ha_cluster_manage_firewall
        - ha_cluster_manage_selinux
        - ha_cluster_cluster_present
        - ha_cluster_cluster_properties
        - ha_cluster_start_on_boot
        - ha_cluster_install_cloud_agents
        - ha_cluster_pcs_permission_list
        - ha_cluster_cluster_name
        - ha_cluster_transport
        - ha_cluster_totem
        - ha_cluster_quorum
        - ha_cluster_node_options - currently only node_name,
          corosync_addresses and pcs_address are present
        - ha_cluster_resource_primitives
        - ha_cluster_resource_groups
        - ha_cluster_resource_clones
        - ha_cluster_resource_bundles
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
        - ha_cluster_pcsd_certificates
        - ha_cluster_regenerate_keys
        - HORIZONTALLINE
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from ansible.module_utils.basic import AnsibleModule

# pylint: disable=no-name-in-module
from ansible.module_utils.ha_cluster_lsr.info import exporter, loader

try:
    # firewall module doesn't provide type hints
    from firewall.client import FirewallClient  # type:ignore

    HAS_FIREWALL = True
except ImportError:
    # create the class so it can be replaced by a mock in unit tests
    class FirewallClient:  # type: ignore
        # pylint: disable=missing-class-docstring
        # pylint: disable=too-few-public-methods
        pass

    HAS_FIREWALL = False

try:
    # selinux module doesn't provide type hints
    from seobject import portRecords as SelinuxPortRecords  # type: ignore

    HAS_SELINUX = True
except ImportError:
    # create the class so it can be replaced by a mock in unit tests
    class SelinuxPortRecords:  # type: ignore
        # pylint: disable=missing-class-docstring
        # pylint: disable=too-few-public-methods
        pass

    HAS_SELINUX = False


class Capability(Enum):
    """Enumeration of capabilities used here"""

    RESOURCE_OUTPUT = "pcmk.resource.config.output-formats"
    CLUSTER_PROPERTIES_OUTPUT = "pcmk.properties.cluster.config.output-formats"
    RESOURCE_DEFAULTS_OUTPUT = (
        "pcmk.properties.resource-defaults.config.output-formats"
    )
    RESOURCE_OP_DEFAULTS_OUTPUT = (
        "pcmk.properties.operation-defaults.config.output-formats"
    )


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

    if HAS_FIREWALL:
        fw_client = FirewallClient()
        fw_config = loader.get_firewall_config(fw_client)
        manage_firewall = False
        if fw_config is not None:
            manage_firewall = exporter.export_manage_firewall(fw_config)
            result["ha_cluster_manage_firewall"] = manage_firewall

        # ha_cluster_manage_selinux is irrelevant when running the role if
        # ha_cluster_manage_firewall is not True
        if HAS_SELINUX and manage_firewall:
            selinux_ports = SelinuxPortRecords()
            ha_ports_firewall = loader.get_firewall_ha_cluster_ports(fw_client)
            ha_ports_selinux = loader.get_selinux_ha_cluster_ports(
                selinux_ports
            )
            if ha_ports_firewall is not None and ha_ports_selinux is not None:
                result["ha_cluster_manage_selinux"] = (
                    exporter.export_manage_selinux(
                        ha_ports_firewall, ha_ports_selinux
                    )
                )

    return result


def export_pcsd_configuration() -> Dict[str, Any]:
    """
    Export pcsd configuration managed by the role
    """
    result: dict[str, Any] = dict()

    pcsd_settings_dict = loader.get_pcsd_settings_conf()
    if pcsd_settings_dict is not None:
        result["ha_cluster_pcs_permission_list"] = (
            exporter.export_pcs_permission_list(pcsd_settings_dict)
        )

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


def export_resources_configuration(
    module: AnsibleModule, pcs_capabilities: List[str]
) -> Dict[str, Any]:
    """
    Export existing HA cluster resources
    """

    if Capability.RESOURCE_OUTPUT.value not in pcs_capabilities:
        return dict()

    cmd_runner = get_cmd_runner(module)
    resources = loader.get_resources_configuration(cmd_runner)
    stonith = loader.get_stonith_configuration(cmd_runner)
    primitives = exporter.export_resource_primitive_list(resources, stonith)
    groups = exporter.export_resource_group_list(resources)
    clones = exporter.export_resource_clone_list(resources)
    bundles = exporter.export_resource_bundle_list(resources)

    result: dict[str, Any] = dict()
    if primitives:
        result["ha_cluster_resource_primitives"] = primitives
    if groups:
        result["ha_cluster_resource_groups"] = groups
    if clones:
        result["ha_cluster_resource_clones"] = clones
    if bundles:
        result["ha_cluster_resource_bundles"] = bundles
    return result


def export_cluster_properties_configuration(
    module: AnsibleModule, pcs_capabilities: List[str]
) -> Dict[str, Any]:
    """
    Export existing HA cluster properties
    """

    if Capability.CLUSTER_PROPERTIES_OUTPUT.value not in pcs_capabilities:
        return dict()

    cmd_runner = get_cmd_runner(module)
    pcs_properties = loader.get_cluster_properties_configuration(cmd_runner)
    properties = exporter.export_cluster_properties(pcs_properties)

    result: dict[str, Any] = dict()
    if properties:
        result["ha_cluster_cluster_properties"] = properties

    return result


def export_resource_defaults_configuration(
    module: AnsibleModule, pcs_capabilities: List[str]
) -> Dict[str, Any]:
    """
    Export existing HA cluster resource defaults
    """

    if Capability.RESOURCE_DEFAULTS_OUTPUT.value not in pcs_capabilities:
        return dict()

    cmd_runner = get_cmd_runner(module)
    pcs_defaults = loader.get_resource_defaults_configuration(cmd_runner)
    defaults = exporter.export_resource_defaults(pcs_defaults)

    result: dict[str, Any] = dict()
    if defaults:
        result["ha_cluster_resource_defaults"] = defaults

    return result


def export_resource_op_defaults_configuration(
    module: AnsibleModule, pcs_capabilities: List[str]
) -> Dict[str, Any]:
    """
    Export existing HA cluster resource operations defaults
    """

    if Capability.RESOURCE_OP_DEFAULTS_OUTPUT.value not in pcs_capabilities:
        return dict()

    cmd_runner = get_cmd_runner(module)
    pcs_defaults = loader.get_resource_op_defaults_configuration(cmd_runner)
    defaults = exporter.export_resource_op_defaults(pcs_defaults)

    result: dict[str, Any] = dict()
    if defaults:
        result["ha_cluster_resource_operation_defaults"] = defaults

    return result


def get_pcs_capabilities(module: AnsibleModule) -> List[str]:
    """
    Extract pcsd pcs_capabilities from pcs version info
    """
    _version, capabilities = loader.get_pcs_version_info(get_cmd_runner(module))
    return capabilities


def main() -> None:
    """
    Top level module function
    """
    module_args: Dict[str, Any] = dict()
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    module_result: Dict[str, Any] = dict()
    ha_cluster_result: Dict[str, Any] = dict()
    module_result["ha_cluster"] = ha_cluster_result

    pcs_capabilities = get_pcs_capabilities(module)

    try:
        if loader.has_corosync_conf():
            ha_cluster_result.update(**export_os_configuration(module))
            ha_cluster_result.update(**export_pcsd_configuration())
            ha_cluster_result.update(**export_cluster_configuration(module))
            ha_cluster_result.update(
                **export_resources_configuration(module, pcs_capabilities)
            )
            ha_cluster_result.update(
                **export_cluster_properties_configuration(
                    module, pcs_capabilities
                )
            )
            ha_cluster_result.update(
                **export_resource_defaults_configuration(
                    module, pcs_capabilities
                )
            )
            ha_cluster_result.update(
                **export_resource_op_defaults_configuration(
                    module, pcs_capabilities
                )
            )
            ha_cluster_result["ha_cluster_cluster_present"] = True
        else:
            # Exporting qnetd configuration will be added later here. It will
            # probably call export_os and export_pcsd.
            ha_cluster_result["ha_cluster_cluster_present"] = False
        module.exit_json(**module_result)
    except exporter.InvalidSrc as e:
        issue_location = f" ({e.issue_location})" if e.issue_location else ""
        module.fail_json(
            msg=(
                f"Invalid data in pcs {e.data_desc} JSON output{issue_location}"
                f": {e.issue_desc}"
            ),
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
