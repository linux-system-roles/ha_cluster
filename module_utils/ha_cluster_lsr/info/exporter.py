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
from typing import Any, Dict, Iterator, List


class JsonMissingKey(Exception):
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


def _dict_to_nv_list(input_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Convert a dict to a list of dicts with keys 'name' and 'value'
    """
    return [dict(name=name, value=value) for name, value in input_dict.items()]


@contextmanager
def _handle_missing_key(data: Dict[str, Any], data_desc: str) -> Iterator[None]:
    try:
        yield
    except KeyError as e:
        raise JsonMissingKey(e.args[0], data, data_desc) from e


def export_start_on_boot(
    corosync_enabled: bool, pacemaker_enabled: bool
) -> bool:
    """
    Transform cluster servis status to start_on_boot
    """
    return corosync_enabled or pacemaker_enabled


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
                f"corosync configuration for node on index {index}",
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
