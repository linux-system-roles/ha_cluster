# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import sys
from importlib import import_module
from typing import Any, Dict, List
from unittest import TestCase

sys.modules["ansible.module_utils.ha_cluster_lsr"] = import_module(
    "ha_cluster_lsr"
)

from ha_cluster_lsr.info import exporter


class DictToNvList(TestCase):
    # pylint: disable=protected-access
    def test_no_item(self) -> None:
        self.assertEqual(
            exporter._dict_to_nv_list(dict()),
            [],
        )

    def test_one_item(self) -> None:
        self.assertEqual(
            exporter._dict_to_nv_list(dict(one="1")),
            [dict(name="one", value="1")],
        )

    def test_two_items(self) -> None:
        self.assertEqual(
            exporter._dict_to_nv_list(dict(one="1", two="2")),
            [dict(name="one", value="1"), dict(name="two", value="2")],
        )


class ExportCorosyncConf(TestCase):
    maxDiff = None

    def assert_missing_key(self, data: Dict[str, Any], key: str) -> None:
        with self.assertRaises(exporter.JsonMissingKey) as cm:
            exporter.export_corosync_options(data)
        self.assertEqual(
            cm.exception.kwargs,
            dict(data=data, key=key, data_desc="corosync configuration"),
        )

    def test_missing_keys(self) -> None:
        self.assert_missing_key(dict(), "cluster_name")
        self.assert_missing_key(dict(cluster_name="x"), "transport")
        self.assert_missing_key(
            dict(cluster_name="x", transport="x"), "transport_options"
        )
        self.assert_missing_key(
            dict(cluster_name="x", transport="x", transport_options=dict()),
            "links_options",
        )
        self.assert_missing_key(
            dict(
                cluster_name="x",
                transport="x",
                transport_options=dict(),
                links_options=dict(),
            ),
            "compression_options",
        )
        self.assert_missing_key(
            dict(
                cluster_name="x",
                transport="x",
                transport_options=dict(),
                links_options=dict(),
                compression_options=dict(),
            ),
            "crypto_options",
        )
        self.assert_missing_key(
            dict(
                cluster_name="x",
                transport="x",
                transport_options=dict(),
                links_options=dict(),
                compression_options=dict(),
                crypto_options=dict(),
            ),
            "totem_options",
        )
        self.assert_missing_key(
            dict(
                cluster_name="x",
                transport="x",
                transport_options=dict(),
                links_options=dict(),
                compression_options=dict(),
                crypto_options=dict(),
                totem_options=dict(),
            ),
            "quorum_options",
        )

    def test_minimal(self) -> None:
        pcs_data = dict(
            cluster_name="my-cluster",
            transport="KNET",
            transport_options=dict(),
            links_options=dict(),
            compression_options=dict(),
            crypto_options=dict(),
            totem_options=dict(),
            quorum_options=dict(),
        )
        role_data = exporter.export_corosync_options(pcs_data)
        self.assertEqual(
            role_data,
            dict(
                ha_cluster_cluster_name="my-cluster",
                ha_cluster_transport=dict(type="knet"),
            ),
        )

    def test_simple_options_mirroring(self) -> None:
        pcs_data = dict(
            cluster_name="my-cluster",
            transport="KNET",
            totem_options=dict(totem1="a", totem2="b"),
            transport_options=dict(transport1="c", transport2="d"),
            compression_options=dict(compression1="e", compression2="f"),
            crypto_options=dict(crypto1="g", crypto2="h"),
            quorum_options=dict(quorum1="i", quorum2="j"),
            links_options=dict(),
        )
        role_data = exporter.export_corosync_options(pcs_data)
        self.assertEqual(
            role_data,
            dict(
                ha_cluster_cluster_name="my-cluster",
                ha_cluster_transport=dict(
                    type="knet",
                    options=[
                        dict(name="transport1", value="c"),
                        dict(name="transport2", value="d"),
                    ],
                    compression=[
                        dict(name="compression1", value="e"),
                        dict(name="compression2", value="f"),
                    ],
                    crypto=[
                        dict(name="crypto1", value="g"),
                        dict(name="crypto2", value="h"),
                    ],
                ),
                ha_cluster_totem=dict(
                    options=[
                        dict(name="totem1", value="a"),
                        dict(name="totem2", value="b"),
                    ],
                ),
                ha_cluster_quorum=dict(
                    options=[
                        dict(name="quorum1", value="i"),
                        dict(name="quorum2", value="j"),
                    ],
                ),
            ),
        )

    def test_one_link(self) -> None:
        pcs_data = dict(
            cluster_name="my-cluster",
            transport="KNET",
            transport_options=dict(),
            links_options={"0": dict(name1="value1", name2="value2")},
            compression_options=dict(),
            crypto_options=dict(),
            totem_options=dict(),
            quorum_options=dict(),
        )
        role_data = exporter.export_corosync_options(pcs_data)
        self.assertEqual(
            role_data,
            dict(
                ha_cluster_cluster_name="my-cluster",
                ha_cluster_transport=dict(
                    type="knet",
                    links=[
                        [
                            dict(name="name1", value="value1"),
                            dict(name="name2", value="value2"),
                        ]
                    ],
                ),
            ),
        )

    def test_more_links(self) -> None:
        pcs_data = dict(
            cluster_name="my-cluster",
            transport="KNET",
            transport_options=dict(),
            links_options={
                "0": dict(linknumber="0", name0="value0"),
                "7": dict(linknumber="7", name7="value7"),
                "3": dict(linknumber="3", name3="value3"),
            },
            compression_options=dict(),
            crypto_options=dict(),
            totem_options=dict(),
            quorum_options=dict(),
        )
        role_data = exporter.export_corosync_options(pcs_data)
        self.assertEqual(
            role_data,
            dict(
                ha_cluster_cluster_name="my-cluster",
                ha_cluster_transport=dict(
                    type="knet",
                    links=[
                        [
                            dict(name="linknumber", value="0"),
                            dict(name="name0", value="value0"),
                        ],
                        [
                            dict(name="linknumber", value="7"),
                            dict(name="name7", value="value7"),
                        ],
                        [
                            dict(name="linknumber", value="3"),
                            dict(name="name3", value="value3"),
                        ],
                    ],
                ),
            ),
        )


class ExportClusterNodes(TestCase):
    maxDiff = None

    def assert_missing_key(
        self, data: List[Dict[str, Any]], key: str, index: str = "0"
    ) -> None:
        with self.assertRaises(exporter.JsonMissingKey) as cm:
            exporter.export_cluster_nodes(data, {})
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data=dict(nodes=data),
                key=key,
                data_desc=f"corosync configuration for node on index {index}",
            ),
        )

    def test_no_nodes(self) -> None:
        self.assertEqual(exporter.export_cluster_nodes([], {}), [])

    def test_corosync_nodes_missing_keys(self) -> None:
        corosync_data: List[Dict[str, Any]] = [dict()]
        self.assert_missing_key(corosync_data, "name")

        corosync_data = [dict(name="nodename")]
        self.assert_missing_key(corosync_data, "addrs")

        corosync_data = [dict(name="nodename", addrs=[dict()])]
        self.assert_missing_key(corosync_data, "link")

        corosync_data = [dict(name="nodename", addrs=[dict(link="0")])]
        self.assert_missing_key(corosync_data, "addr")

    def test_corosync_nodes_one_link(self) -> None:
        corosync_data = [
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
        role_data = exporter.export_cluster_nodes(corosync_data, {})
        self.assertEqual(
            role_data,
            [
                dict(node_name="node1", corosync_addresses=["node1addr"]),
                dict(node_name="node2", corosync_addresses=["node2addr"]),
            ],
        )

    def test_corosync_nodes_multiple_links(self) -> None:
        corosync_data = [
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
        corosync_data = [
            dict(
                name="node1",
                nodeid=1,
                addrs=[],
            ),
        ]
        role_data = exporter.export_cluster_nodes(corosync_data, {})
        self.assertEqual(
            role_data,
            [
                dict(node_name="node1", corosync_addresses=[]),
            ],
        )

    def test_pcs_nodes_no_cluster_nodes(self) -> None:
        corosync_data: List[Dict[str, Any]] = []
        pcs_data = dict(node1="node1A")
        role_data = exporter.export_cluster_nodes(corosync_data, pcs_data)
        self.assertEqual(
            role_data,
            [],
        )

    def test_pcs_nodes(self) -> None:
        corosync_data = [
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
