# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# SPDX-License-Identifier: MIT

# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

from typing import Any, Dict, List
from unittest import TestCase

from .ha_cluster_info import exporter


class ExportClusterNodes(TestCase):
    maxDiff = None

    def assert_missing_node_key(
        self, corosync_data: Dict[str, Any], key: str, issue_location: str
    ) -> None:
        with self.assertRaises(exporter.InvalidSrc) as cm:
            exporter.export_cluster_nodes(corosync_data, {})
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data_desc="corosync configuration",
                data=corosync_data,
                issue_location=issue_location,
                issue_desc=f"Missing key '{key}'",
            ),
        )

    def test_missing_key(self) -> None:
        corosync_data: Dict[str, Any] = dict()
        with self.assertRaises(exporter.InvalidSrc) as cm:
            exporter.export_cluster_nodes(corosync_data, {})
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data_desc="corosync configuration",
                data=corosync_data,
                issue_location="",
                issue_desc="Missing key 'nodes'",
            ),
        )

    def test_no_nodes(self) -> None:
        self.assertEqual(
            exporter.export_cluster_nodes(dict(nodes=[]), {}),
            [],
        )

    def test_corosync_nodes_missing_keys(self) -> None:
        corosync_data: Dict[str, Any] = dict(nodes=[dict()])
        self.assert_missing_node_key(corosync_data, "name", "/nodes/0")

        corosync_data = dict(nodes=[dict(name="nodename")])
        self.assert_missing_node_key(corosync_data, "addrs", "/nodes/0")

        corosync_data = dict(nodes=[dict(name="nodename", addrs=[dict()])])
        self.assert_missing_node_key(corosync_data, "link", "/nodes/0/addrs/0")

        corosync_data = dict(
            nodes=[dict(name="nodename", addrs=[dict(link="0")])]
        )
        self.assert_missing_node_key(corosync_data, "addr", "/nodes/0/addrs/0")

        corosync_data = dict(
            nodes=[
                dict(name="nodename", addrs=[dict(link="0", addr="addr1")]),
                dict(name="node2"),
            ]
        )
        self.assert_missing_node_key(corosync_data, "addrs", "/nodes/1")

    def test_corosync_nodes_one_link(self) -> None:
        corosync_data: Dict[str, Any] = dict(
            nodes=[
                dict(
                    name="node1",
                    nodeid=1,
                    addrs=[dict(addr="node1addr", link="0", type="IPv4")],
                ),
                dict(
                    name="node2",
                    nodeid=2,
                    addrs=[dict(addr="node2addr", link="0", type="FQDN")],
                ),
            ]
        )
        role_data = exporter.export_cluster_nodes(corosync_data, {})
        self.assertEqual(
            role_data,
            [
                dict(node_name="node1", corosync_addresses=["node1addr"]),
                dict(node_name="node2", corosync_addresses=["node2addr"]),
            ],
        )

    def test_corosync_nodes_multiple_links(self) -> None:
        corosync_data: Dict[str, Any] = dict(
            nodes=[
                dict(
                    name="node1",
                    nodeid=1,
                    addrs=[
                        dict(addr="node1addr1", link="0", type="IPv4"),
                        dict(addr="node1addr2", link="1", type="IPv6"),
                    ],
                ),
                dict(
                    name="node2",
                    nodeid=2,
                    addrs=[
                        dict(addr="node2addr1", link="0", type="IPv4"),
                        dict(addr="node2addr2", link="1", type="IPv6"),
                    ],
                ),
            ]
        )
        role_data = exporter.export_cluster_nodes(corosync_data, {})
        self.assertEqual(
            role_data,
            [
                dict(
                    node_name="node1",
                    corosync_addresses=["node1addr1", "node1addr2"],
                ),
                dict(
                    node_name="node2",
                    corosync_addresses=["node2addr1", "node2addr2"],
                ),
            ],
        )

    def test_corosync_nodes_no_address(self) -> None:
        corosync_data: Dict[str, Any] = dict(
            nodes=[
                dict(
                    name="node1",
                    nodeid=1,
                    addrs=[],
                ),
            ]
        )
        role_data = exporter.export_cluster_nodes(corosync_data, {})
        self.assertEqual(
            role_data,
            [
                dict(node_name="node1", corosync_addresses=[]),
            ],
        )

    def test_pcs_nodes_no_cluster_nodes(self) -> None:
        corosync_data: Dict[str, Any] = dict(nodes=[])
        pcs_data = dict(node1="node1A")
        role_data = exporter.export_cluster_nodes(corosync_data, pcs_data)
        self.assertEqual(
            role_data,
            [],
        )

    def test_pcs_nodes(self) -> None:
        corosync_data: Dict[str, Any] = dict(
            nodes=[
                dict(
                    name="node1",
                    nodeid=1,
                    addrs=[dict(addr="node1addr", link="0", type="FQDN")],
                ),
                dict(
                    name="node2",
                    nodeid=2,
                    addrs=[dict(addr="node2addr", link="0", type="FQDN")],
                ),
            ]
        )
        pcs_data = dict(node1="node1A", node3="node3A")
        role_data = exporter.export_cluster_nodes(corosync_data, pcs_data)
        self.assertEqual(
            role_data,
            [
                dict(
                    node_name="node1",
                    corosync_addresses=["node1addr"],
                    pcs_address="node1A",
                ),
                dict(
                    node_name="node2",
                    corosync_addresses=["node2addr"],
                ),
            ],
        )


class ExportClusterNodesWithAttrs(TestCase):
    maxDiff = None
    node1 = "node1"

    def export(self, node_attrs_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        return exporter.export_cluster_nodes(
            corosync_conf_dict=dict(
                nodes=[
                    dict(
                        name=self.node1,
                        addrs=[dict(addr="addr1", link="0")],
                    )
                ]
            ),
            pcs_node_addr={},
            node_attrs_config=node_attrs_config,
        )

    def test_node_attrs_invalid_src(self) -> None:
        node_attrs: Dict[str, Any] = {}
        with self.assertRaises(exporter.InvalidSrc) as cm:
            self.export(node_attrs_config=node_attrs)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data=node_attrs,
                data_desc="node attributes and utilization configuration",
                issue_location="",
                issue_desc="Missing key 'nodes'",
            ),
        )

    def test_node_attrs_empty(self) -> None:
        self.assertEqual(
            self.export(node_attrs_config=dict(nodes=[])),
            [dict(node_name="node1", corosync_addresses=["addr1"])],
        )

    def test_node_attrs_both(self) -> None:
        nodes_export = self.export(
            node_attrs_config=dict(
                nodes=[
                    dict(
                        uname=self.node1,
                        instance_attributes=[
                            dict(
                                id="ia-node1",
                                nvpairs=[
                                    dict(id="ia1", name="attr1", value="val1"),
                                    dict(id="ia2", name="attr2", value="val2"),
                                ],
                            ),
                        ],
                        utilization=[
                            dict(
                                id="util-node1",
                                nvpairs=[
                                    dict(id="u1", name="cpu", value="4"),
                                    dict(id="u2", name="memory", value="4096"),
                                ],
                            ),
                        ],
                    ),
                ]
            )
        )
        self.assertEqual(
            nodes_export,
            [
                dict(
                    node_name=self.node1,
                    corosync_addresses=["addr1"],
                    attributes=[
                        dict(
                            attrs=[
                                dict(name="attr1", value="val1"),
                                dict(name="attr2", value="val2"),
                            ],
                        ),
                    ],
                    utilization=[
                        dict(
                            attrs=[
                                dict(name="cpu", value=4),
                                dict(name="memory", value=4096),
                            ],
                        ),
                    ],
                ),
            ],
        )
        for attr in nodes_export[0]["utilization"][0]["attrs"]:
            self.assertIsInstance(attr["value"], int)

    def test_node_attrs_neither(self) -> None:
        self.assertEqual(
            self.export(
                node_attrs_config=dict(
                    nodes=[
                        dict(
                            uname=self.node1,
                            instance_attributes=[],
                            utilization=[],
                        ),
                    ]
                )
            ),
            [dict(node_name=self.node1, corosync_addresses=["addr1"])],
        )

    def test_node_attrs_utilization_non_numeric(self) -> None:
        node_attrs: Dict[str, Any] = dict(
            nodes=[
                dict(
                    uname=self.node1,
                    instance_attributes=[],
                    utilization=[
                        dict(
                            id="util-node1",
                            nvpairs=[
                                dict(id="u1", name="cpu", value="err"),
                            ],
                        ),
                    ],
                ),
            ]
        )
        with self.assertRaises(exporter.InvalidSrc) as cm:
            self.export(node_attrs_config=node_attrs)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data=node_attrs,
                data_desc="node attributes and utilization configuration",
                issue_location="/nodes/0/utilization/0/nvpairs/0/value",
                issue_desc="invalid literal for int() with base 10: 'err'",
            ),
        )

    def test_node_attrs_multiple_nodes(self) -> None:
        node2 = "node2"
        node3 = "node3"
        self.assertEqual(
            exporter.export_cluster_nodes(
                corosync_conf_dict=dict(
                    nodes=[
                        dict(
                            name=self.node1,
                            addrs=[dict(addr="addr1", link="0")],
                        ),
                        dict(name=node2, addrs=[dict(addr="addr2", link="0")]),
                        dict(name=node3, addrs=[dict(addr="addr3", link="0")]),
                    ]
                ),
                pcs_node_addr={},
                node_attrs_config=dict(
                    nodes=[
                        dict(
                            uname=self.node1,
                            instance_attributes=[
                                dict(
                                    id="ia-node1",
                                    nvpairs=[
                                        dict(
                                            id="ia1", name="attr1", value="val1"
                                        ),
                                    ],
                                ),
                            ],
                            utilization=[],
                        ),
                        dict(
                            uname=node2,
                            instance_attributes=[],
                            utilization=[
                                dict(
                                    id="util-node2",
                                    nvpairs=[
                                        dict(id="u1", name="cpu", value="2"),
                                    ],
                                ),
                            ],
                        ),
                        dict(
                            uname=node3,
                            instance_attributes=[],
                            utilization=[],
                        ),
                    ]
                ),
            ),
            [
                dict(
                    node_name=self.node1,
                    corosync_addresses=["addr1"],
                    attributes=[
                        dict(
                            attrs=[dict(name="attr1", value="val1")],
                        ),
                    ],
                ),
                dict(
                    node_name=node2,
                    corosync_addresses=["addr2"],
                    utilization=[
                        dict(
                            attrs=[dict(name="cpu", value=2)],
                        ),
                    ],
                ),
                dict(node_name=node3, corosync_addresses=["addr3"]),
            ],
        )
