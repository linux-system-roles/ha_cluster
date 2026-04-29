# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# make ansible-test happy, even though the module requires Python 3
from __future__ import absolute_import, division, print_function

# make ansible-test happy, even though the module requires Python 3
# pylint: disable=invalid-name
__metaclass__ = type

from typing import Any, Dict, List, Optional

from .nvset import first_attrs, first_utilization_attrs
from .wrap_src import SrcDict, is_none, wrap_src_for_rich_report


# The var pcs_node_addr is in an internally created format, not wrapping.
@wrap_src_for_rich_report(
    dict(
        corosync_conf_dict="corosync configuration",
        node_attrs_config="node attributes and utilization configuration",
    )
)
def export_cluster_nodes(
    corosync_conf_dict: SrcDict,
    pcs_node_addr: Dict[str, str],
    node_attrs_config: Optional[SrcDict] = None,
) -> List[Dict[str, Any]]:
    """
    Transform node configuration from pcs format to role format

    corosync_conf_dict -- corosync config structure provided by pcs
    pcs_node_addr -- dict holding pcs address for cluster nodes
    node_attrs_config -- optional node attributes and utilization config
        from `pcs node attribute --output-format=json`
    """
    node_list: List[Dict[str, Any]] = []
    corosync_nodes = corosync_conf_dict["nodes"]
    if not corosync_nodes:
        return node_list

    node_attrs_map: Dict[str, Any] = {}
    if not is_none(node_attrs_config):
        # mypy can't narrow through is_none (would need TypeIs[None] from
        # typing_extensions; not wrapping None loses InvalidSrc diagnostics)
        for attrs_src in node_attrs_config["nodes"]:  # type: ignore[index]
            node_attrs: Dict[str, Any] = {}

            attrs = first_attrs(attrs_src["instance_attributes"])
            if attrs:
                node_attrs["attributes"] = attrs

            utils = first_utilization_attrs(attrs_src["utilization"])
            if utils:
                node_attrs["utilization"] = utils

            if node_attrs:
                node_attrs_map[attrs_src["uname"]] = node_attrs

    for node_src in corosync_nodes:
        name = node_src["name"]

        node = dict(
            node_name=name,
            corosync_addresses=[
                addrs["addr"]
                for addrs in sorted(node_src["addrs"], key=lambda i: i["link"])
            ],
        )

        if name in pcs_node_addr:
            node["pcs_address"] = pcs_node_addr[name]

        if name in node_attrs_map:
            node.update(node_attrs_map[name])

        node_list.append(node)
    return node_list
