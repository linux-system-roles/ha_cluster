# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# make ansible-test happy, even though the module requires Python 3
from __future__ import absolute_import, division, print_function

# make ansible-test happy, even though the module requires Python 3
# pylint: disable=invalid-name
__metaclass__ = type

from typing import Any, Dict, List


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


def export_corosync_options(
    corosync_conf_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Transform corosync config from pcs format to role format excluding nodes

    corosync_conf_dict -- corosync config structure provided by pcs
    """
    result: Dict[str, Any] = dict()
    try:
        result["ha_cluster_cluster_name"] = corosync_conf_dict["cluster_name"]

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
        result["ha_cluster_transport"] = transport

        if corosync_conf_dict["totem_options"]:
            result["ha_cluster_totem"] = dict(
                options=_dict_to_nv_list(corosync_conf_dict["totem_options"])
            )

        if corosync_conf_dict["quorum_options"]:
            result["ha_cluster_quorum"] = dict(
                options=_dict_to_nv_list(corosync_conf_dict["quorum_options"])
            )
    except KeyError as e:
        raise JsonMissingKey(
            e.args[0], corosync_conf_dict, "corosync configuration"
        ) from e
    return result


def export_cluster_nodes(
    corosync_conf_nodes: List[Dict[str, Any]], pcs_node_addr: Dict[str, str]
) -> List[Dict[str, Any]]:
    """
    Transform node configuration from pcs format to role format

    corosync_conf_dict -- corosync config structure provided by pcs
    pcs_node_addr -- dict holding pcs address for cluster nodes
    """
    node_list: List[Dict[str, Any]] = []
    if not corosync_conf_nodes:
        return node_list
    for index, node_dict in enumerate(corosync_conf_nodes):
        # corosync node configuration
        try:
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
        except KeyError as e:
            raise JsonMissingKey(
                e.args[0],
                dict(nodes=corosync_conf_nodes),
                f"corosync configuration for node on index {index}",
            ) from e
        # pcs node configuration
        if one_node["node_name"] in pcs_node_addr:
            one_node["pcs_address"] = pcs_node_addr[one_node["node_name"]]
        # finish one node export
        node_list.append(one_node)
    return node_list
