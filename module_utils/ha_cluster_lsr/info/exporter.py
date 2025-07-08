# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# make ansible-test happy, even though the module requires Python 3
from __future__ import absolute_import, division, print_function

# make ansible-test happy, even though the module requires Python 3
# pylint: disable=invalid-name
__metaclass__ = type

from contextlib import contextmanager
from typing import Any, Dict, Iterator, List, Optional, Tuple


class InvalidSrc(Exception):
    """
    Cannot extract result from sources
    """

    def __init__(
        self,
        data_desc: str,
        data: Dict[str, Any],
        issue_location: str,
        issue_desc: str,
    ):
        self.data = data
        self.data_desc = data_desc
        self.issue_location = issue_location
        self.issue_desc = issue_desc

    @property
    def kwargs(self) -> Dict[str, Any]:
        """
        Arguments given to the constructor
        """
        return dict(
            data=self.data,
            data_desc=self.data_desc,
            issue_location=self.issue_location,
            issue_desc=self.issue_desc,
        )


def _dict_to_nv_list(input_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Convert a dict to a list of dicts with keys 'name' and 'value'
    """
    return [dict(name=name, value=value) for name, value in input_dict.items()]


@contextmanager
def _handle_missing_key(
    data: Dict[str, Any], data_desc: str, issue_location: str = ""
) -> Iterator[None]:
    try:
        yield
    except KeyError as e:
        raise InvalidSrc(
            data_desc,
            data,
            issue_location,
            f"Missing key '{e.args[0]}'",
        ) from e


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


def export_manage_firewall(zone_config: Dict[str, Any]) -> bool:
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


def export_corosync_cluster_name(corosync_conf_dict: Dict[str, Any]) -> str:
    """
    Extract cluster name form corosync config in pcs format

    corosync_conf_dict -- corosync config structure provided by pcs
    """
    with _handle_missing_key(corosync_conf_dict, "corosync configuration"):
        return corosync_conf_dict["cluster_name"]


def export_corosync_transport(
    corosync_conf_dict: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Export transport options in role format from corosync config in pcs format

    corosync_conf_dict -- corosync config structure provided by pcs
    """
    with _handle_missing_key(corosync_conf_dict, "corosync configuration"):
        transport = dict(type=corosync_conf_dict["transport"].lower())
        if corosync_conf_dict["transport_options"]:
            transport["options"] = _dict_to_nv_list(
                corosync_conf_dict["transport_options"]
            )
        if corosync_conf_dict["links_options"]:
            link_list = []
            for link_dict in corosync_conf_dict["links_options"].values():
                # linknumber is an index in links_options, but it is present in
                # link_dict as well
                link_list.append(_dict_to_nv_list(link_dict))
            transport["links"] = link_list
        if corosync_conf_dict["compression_options"]:
            transport["compression"] = _dict_to_nv_list(
                corosync_conf_dict["compression_options"]
            )
        if corosync_conf_dict["crypto_options"]:
            transport["crypto"] = _dict_to_nv_list(
                corosync_conf_dict["crypto_options"]
            )
        return transport


def export_corosync_totem(corosync_conf_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Export totem options in role format from corosync config in pcs format

    corosync_conf_dict -- corosync config structure provided by pcs
    """
    with _handle_missing_key(corosync_conf_dict, "corosync configuration"):
        result: Dict[str, Any] = dict()
        if corosync_conf_dict["totem_options"]:
            result["options"] = _dict_to_nv_list(
                corosync_conf_dict["totem_options"]
            )
        return result


def export_corosync_quorum(
    corosync_conf_dict: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Export quorum options in role format from corosync config in pcs format

    corosync_conf_dict -- corosync config structure provided by pcs
    """
    with _handle_missing_key(corosync_conf_dict, "corosync configuration"):
        result: Dict[str, Any] = dict()
        if corosync_conf_dict["quorum_options"]:
            result["options"] = _dict_to_nv_list(
                corosync_conf_dict["quorum_options"]
            )
        return result


def export_cluster_nodes(
    corosync_conf_dict: Dict[str, Any], pcs_node_addr: Dict[str, str]
) -> List[Dict[str, Any]]:
    """
    Transform node configuration from pcs format to role format

    corosync_conf_dict -- corosync config structure provided by pcs
    pcs_node_addr -- dict holding pcs address for cluster nodes
    """
    with _handle_missing_key(corosync_conf_dict, "corosync configuration"):
        node_list: List[Dict[str, Any]] = []
        corosync_nodes = corosync_conf_dict["nodes"]
        if not corosync_nodes:
            return node_list
        for index, node_dict in enumerate(corosync_nodes):
            # corosync node configuration
            with _handle_missing_key(
                corosync_conf_dict,
                "corosync configuration",
                f"/node/{index}",
            ):
                one_node = dict(
                    node_name=node_dict["name"],
                    corosync_addresses=[
                        addr_dict["addr"]
                        for addr_dict in sorted(
                            node_dict["addrs"],
                            key=lambda item: item["link"],
                        )
                    ],
                )
            # pcs node configuration
            if one_node["node_name"] in pcs_node_addr:
                one_node["pcs_address"] = pcs_node_addr[one_node["node_name"]]
            # finish one node export
            node_list.append(one_node)
        return node_list


def export_pcs_permission_list(
    pcs_settings_conf_dict: Dict[str, Any],
) -> Optional[List[Dict[str, Any]]]:
    """
    Extract local cluster permissions from pcs_settings config or None on error

    pcs_settings -- JSON parsed pcs_settings.conf
    """
    # Currently, only format version 2 is in use, so we don't check for file
    # format version
    result: List[Dict[str, Any]] = []
    with _handle_missing_key(pcs_settings_conf_dict, "pcs_settings.conf"):
        permission_dict = pcs_settings_conf_dict["permissions"]
        if not isinstance(permission_dict, dict):
            return None
        permission_list = permission_dict["local_cluster"]
        if not isinstance(permission_list, list):
            return None
        for permission_item in permission_list:
            result.append(
                {
                    "type": permission_item["type"],
                    "name": permission_item["name"],
                    "allow_list": list(permission_item["allow"]),
                }
            )
        return result
