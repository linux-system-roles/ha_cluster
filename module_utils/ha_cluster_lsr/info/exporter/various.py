# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# make ansible-test happy, even though the module requires Python 3
from __future__ import absolute_import, division, print_function

# make ansible-test happy, even though the module requires Python 3
# pylint: disable=invalid-name
__metaclass__ = type

from typing import Any, Dict, List, Tuple

from .wrap_src import SrcDict, wrap_src_for_rich_report


def export_enable_repos_ha(dnf_repolist: str) -> bool:
    """
    Check whether high availability repository is enabled based on dnf repolist

    dnf_repolist -- text output of 'dnf repolist'
    """
    repo_strings = ["highavailability", "HighAvailability"]
    return any(repo in dnf_repolist for repo in repo_strings)


def export_enable_repos_rs(dnf_repolist: str) -> bool:
    """
    Check whether resilient storage repository is enabled based on dnf repolist

    dnf_repolist -- text output of 'dnf repolist'
    """
    repo_strings = ["resilientstorage"]
    return any(repo in dnf_repolist for repo in repo_strings)


def export_install_cloud_agents(installed_packages: List[str]) -> bool:
    """
    Check whether cloud agent packages are installed

    installed packages -- list of names of installed packages
    """
    # List of cloud agent packages is taken from vars/RedHat_*.yml and
    # vars/CentOS_*.yml
    # They are hardcoded here to avoid dependency on pyyaml which may or may
    # not be available.
    # We don't need to check for architecture - a package not available for an
    # architecture will never be listed as installed on that architecture.
    cloud_agent_packages = {
        "fence-agents-aliyun",
        "fence-agents-aws",
        "fence-agents-azure-arm",
        "fence-agents-compute",
        "fence-agents-gce",
        "fence-agents-ibm-powervs",
        "fence-agents-ibm-vpc",
        "fence-agents-kubevirt",
        "fence-agents-openstack",
        "resource-agents-aliyun",
        "resource-agents-cloud",
        "resource-agents-gcp",
    }
    return bool(cloud_agent_packages.intersection(installed_packages))


def export_start_on_boot(
    corosync_enabled: bool, pacemaker_enabled: bool
) -> bool:
    """
    Transform cluster servis status to start_on_boot
    """
    return corosync_enabled or pacemaker_enabled


def export_manage_firewall(zone_config: SrcDict) -> bool:
    """
    Export whether HA cluster is enabled in firewall

    zone_config -- configuration of a firewall zone
    """
    return (
        "high-availability" in zone_config["services"]
        or ("1229", "tcp") in zone_config["ports"]
    )


def export_manage_selinux(
    ha_ports_used: List[Tuple[str, str]],
    ha_ports_selinux: Tuple[List[str], List[str]],
) -> bool:
    """
    Export whether HA cluster ports are managed by selinux

    ha_ports_used -- ports used by HA cluster
    ha_ports_selinux -- ports labelled for HA cluster in selinux
    """
    # convert selinux ports to the same format as used ports
    ports_selinux_tuples = [(port, "tcp") for port in ha_ports_selinux[0]] + [
        (port, "udp") for port in ha_ports_selinux[1]
    ]
    return bool(frozenset(ports_selinux_tuples) & frozenset(ha_ports_used))


@wrap_src_for_rich_report(dict(pcs_settings_conf_dict="pcs_settings.conf"))
def export_pcs_permission_list(
    pcs_settings_conf_dict: SrcDict,
) -> List[Dict[str, Any]]:
    """
    Extract local cluster permissions from pcs_settings config or None on error

    pcs_settings -- JSON parsed pcs_settings.conf
    """
    # Currently, only format version 2 is in use, so we don't check for file
    # format version
    return [
        {
            "type": permission["type"],
            "name": permission["name"],
            "allow_list": list(permission["allow"]),
        }
        for permission in pcs_settings_conf_dict["permissions"]["local_cluster"]
    ]
