#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import json
import sys
from copy import deepcopy
from importlib import import_module
from typing import Any, Dict
from unittest import TestCase, mock

sys.modules["ansible.module_utils.ha_cluster_lsr"] = import_module(
    "ha_cluster_lsr"
)

import ha_cluster_info


class DictToNvList(TestCase):
    def test_no_item(self) -> None:
        self.assertEqual(
            ha_cluster_info.dict_to_nv_list(dict()),
            [],
        )

    def test_one_item(self) -> None:
        self.assertEqual(
            ha_cluster_info.dict_to_nv_list(dict(one="1")),
            [dict(name="one", value="1")],
        )

    def test_two_items(self) -> None:
        self.assertEqual(
            ha_cluster_info.dict_to_nv_list(dict(one="1", two="2")),
            [dict(name="one", value="1"), dict(name="two", value="2")],
        )


class IsServiceEnabled(TestCase):
    def setUp(self) -> None:
        self.module_mock = mock.Mock()
        self.module_mock.run_command = mock.Mock()

    def test_is_enabled(self) -> None:
        self.module_mock.run_command.return_value = (0, "enabled", "")
        self.assertTrue(
            ha_cluster_info.is_service_enabled(self.module_mock, "corosync")
        )
        self.module_mock.run_command.assert_called_once_with(
            ["systemctl", "is-enabled", "corosync.service"],
            check_rc=False,
            environ_update={"LC_ALL": "C"},
        )

    def test_is_disabled(self) -> None:
        self.module_mock.run_command.return_value = (1, "disabled", "")
        self.assertFalse(
            ha_cluster_info.is_service_enabled(self.module_mock, "pacemaker")
        )
        self.module_mock.run_command.assert_called_once_with(
            ["systemctl", "is-enabled", "pacemaker.service"],
            check_rc=False,
            environ_update={"LC_ALL": "C"},
        )

    def test_unexpected_output(self) -> None:
        self.module_mock.run_command.return_value = (4, "not-found", "")
        self.assertFalse(
            ha_cluster_info.is_service_enabled(self.module_mock, "pcmk")
        )
        self.module_mock.run_command.assert_called_once_with(
            ["systemctl", "is-enabled", "pcmk.service"],
            check_rc=False,
            environ_update={"LC_ALL": "C"},
        )


class CallPcsCli(TestCase):
    def setUp(self) -> None:
        self.module_mock = mock.Mock()
        self.module_mock.run_command = mock.Mock()

    def test_success(self) -> None:
        self.module_mock.run_command.return_value = (
            0,
            """{"json": "test data", "foo": "bar"}""",
            "",
        )
        self.assertEqual(
            ha_cluster_info.call_pcs_cli(
                self.module_mock, ["cluster", "config"]
            ),
            dict(json="test data", foo="bar"),
        )
        self.module_mock.run_command.assert_called_once_with(
            ["pcs", "cluster", "config"],
            check_rc=False,
            environ_update={"LC_ALL": "C"},
        )

    def test_pcs_error(self) -> None:
        self.module_mock.run_command.return_value = (
            1,
            "some stdout message",
            "some stderr message",
        )
        with self.assertRaises(ha_cluster_info.PcsCliRunError) as cm:
            ha_cluster_info.call_pcs_cli(
                self.module_mock, ["cluster", "config"]
            )
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                pcs_command=["pcs", "cluster", "config"],
                stdout="some stdout message",
                stderr="some stderr message",
                rc=1,
            ),
        )
        self.module_mock.run_command.assert_called_once_with(
            ["pcs", "cluster", "config"],
            check_rc=False,
            environ_update={"LC_ALL": "C"},
        )

    def test_json_error(self) -> None:
        self.module_mock.run_command.return_value = (
            0,
            "not a json",
            "",
        )
        with self.assertRaises(ha_cluster_info.PcsCliJsonError) as cm:
            ha_cluster_info.call_pcs_cli(
                self.module_mock, ["cluster", "config"]
            )
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                json_error="Expecting value: line 1 column 1 (char 0)",
                pcs_command=["pcs", "cluster", "config"],
                stdout="not a json",
                stderr="",
                rc=0,
            ),
        )
        self.module_mock.run_command.assert_called_once_with(
            ["pcs", "cluster", "config"],
            check_rc=False,
            environ_update={"LC_ALL": "C"},
        )


class ExportStartOnBoot(TestCase):
    @mock.patch("ha_cluster_info.is_service_enabled")
    def test_main(self, mock_is_enabled: mock.Mock) -> None:
        module = mock.Mock()
        mock_is_enabled.side_effect = [False, False]
        self.assertFalse(ha_cluster_info.export_start_on_boot(module))

        mock_is_enabled.side_effect = [True, False]
        self.assertTrue(ha_cluster_info.export_start_on_boot(module))

        mock_is_enabled.side_effect = [False, True]
        self.assertTrue(ha_cluster_info.export_start_on_boot(module))

        mock_is_enabled.side_effect = [True, True]
        self.assertTrue(ha_cluster_info.export_start_on_boot(module))


class ExportCorosyncConf(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.module_mock = mock.Mock()
        self.module_mock.run_command = mock.Mock()

    def assert_missing_key(self, data: Dict[str, Any], key: str) -> None:
        self.module_mock.run_command.reset_mock()
        self.module_mock.run_command.return_value = (0, json.dumps(data), "")
        with self.assertRaises(ha_cluster_info.PcsJsonMissingKey) as cm:
            ha_cluster_info.export_corosync_conf(self.module_mock)
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
        self.assert_missing_key(
            dict(
                cluster_name="x",
                transport="x",
                transport_options=dict(),
                links_options=dict(),
                compression_options=dict(),
                crypto_options=dict(),
                totem_options=dict(),
                quorum_options=dict(),
            ),
            "nodes",
        )

    def call_pcs(self, pcs_data: Dict[str, Any]) -> Dict[str, Any]:
        self.module_mock.run_command.return_value = (
            0,
            json.dumps(pcs_data),
            "",
        )
        return ha_cluster_info.export_corosync_conf(self.module_mock)

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
            nodes=[],
        )
        role_data = self.call_pcs(pcs_data)
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
            nodes=[],
        )
        role_data = self.call_pcs(pcs_data)
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
            nodes=[],
        )
        role_data = self.call_pcs(pcs_data)
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
            nodes=[],
        )
        role_data = self.call_pcs(pcs_data)
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

    def test_nodes_one_link(self) -> None:
        pcs_data = dict(
            cluster_name="my-cluster",
            transport="KNET",
            transport_options=dict(),
            links_options=dict(),
            compression_options=dict(),
            crypto_options=dict(),
            totem_options=dict(),
            quorum_options=dict(),
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
            ],
        )
        role_data = self.call_pcs(pcs_data)
        self.assertEqual(
            role_data,
            dict(
                ha_cluster_cluster_name="my-cluster",
                ha_cluster_transport=dict(type="knet"),
                ha_cluster_node_options=[
                    dict(node_name="node1", corosync_addresses=["node1addr"]),
                    dict(node_name="node2", corosync_addresses=["node2addr"]),
                ],
            ),
        )

    def test_nodes_multiple_links(self) -> None:
        pcs_data = dict(
            cluster_name="my-cluster",
            transport="KNET",
            transport_options=dict(),
            links_options=dict(),
            compression_options=dict(),
            crypto_options=dict(),
            totem_options=dict(),
            quorum_options=dict(),
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
            ],
        )
        role_data = self.call_pcs(pcs_data)
        self.assertEqual(
            role_data,
            dict(
                ha_cluster_cluster_name="my-cluster",
                ha_cluster_transport=dict(type="knet"),
                ha_cluster_node_options=[
                    dict(node_name="node1", corosync_addresses=["node1addr"]),
                    dict(node_name="node2", corosync_addresses=["node2addr"]),
                ],
            ),
        )

    def test_nodes_no_address(self) -> None:
        pcs_data = dict(
            cluster_name="my-cluster",
            transport="KNET",
            transport_options=dict(),
            links_options=dict(),
            compression_options=dict(),
            crypto_options=dict(),
            totem_options=dict(),
            quorum_options=dict(),
            nodes=[
                dict(
                    name="node1",
                    nodeid=1,
                    addrs=[],
                ),
            ],
        )
        role_data = self.call_pcs(pcs_data)
        self.assertEqual(
            role_data,
            dict(
                ha_cluster_cluster_name="my-cluster",
                ha_cluster_transport=dict(type="knet"),
                ha_cluster_node_options=[
                    dict(node_name="node1", corosync_addresses=[]),
                ],
            ),
        )

    def assert_missing_key_nodes(
        self, data: Dict[str, Any], key: str, index: str = "0"
    ) -> None:
        self.module_mock.run_command.reset_mock()
        self.module_mock.run_command.return_value = (0, json.dumps(data), "")
        with self.assertRaises(ha_cluster_info.PcsJsonMissingKey) as cm:
            ha_cluster_info.export_corosync_conf(self.module_mock)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data=data,
                key=key,
                data_desc=f"corosync configuration for node on index {index}",
            ),
        )

    def test_nodes_missing_keys(self) -> None:
        pcs_data = dict(
            cluster_name="my-cluster",
            transport="KNET",
            transport_options=dict(),
            links_options=dict(),
            compression_options=dict(),
            crypto_options=dict(),
            totem_options=dict(),
            quorum_options=dict(),
            nodes=[dict(foo="bar")],
        )

        pcs_data["nodes"] = [
            dict(),
        ]
        self.assert_missing_key_nodes(pcs_data, "name")

        pcs_data["nodes"] = [
            dict(name="nodename"),
        ]
        self.assert_missing_key_nodes(pcs_data, "addrs")

        pcs_data["nodes"] = [
            dict(name="nodename", addrs=[dict()]),
        ]
        self.assert_missing_key_nodes(pcs_data, "link")

        pcs_data["nodes"] = [
            dict(name="nodename", addrs=[dict(link="0")]),
        ]
        self.assert_missing_key_nodes(pcs_data, "addr")


class LoadPcsdKnownHosts(TestCase):
    file_path = "/var/lib/pcsd/known-hosts"

    @mock.patch("ha_cluster_info.os.path.exists")
    def test_file_not_present(self, mock_exists: mock.Mock) -> None:
        mock_exists.return_value = False
        self.assertEqual(ha_cluster_info.load_pcsd_known_hosts(), dict())
        mock_exists.assert_called_once_with(self.file_path)

    @mock.patch("ha_cluster_info.os.path.exists")
    def test_json_error(self, mock_exists: mock.Mock) -> None:
        mock_exists.return_value = True
        mock_data = "not a json"
        with mock.patch(
            "ha_cluster_info.open", mock.mock_open(read_data=mock_data)
        ) as mock_open:
            with self.assertRaises(ha_cluster_info.PcsJsonParseError) as cm:
                ha_cluster_info.load_pcsd_known_hosts()
            self.assertEqual(
                cm.exception.kwargs,
                dict(
                    data="not logging data",
                    data_desc="known hosts",
                    error="Expecting value: line 1 column 1 (char 0)",
                ),
            )
            mock_open.assert_called_once_with(
                self.file_path, "r", encoding="utf-8"
            )
        mock_exists.assert_called_once_with(self.file_path)

    @mock.patch("ha_cluster_info.os.path.exists")
    def test_json_empty(self, mock_exists: mock.Mock) -> None:
        mock_exists.return_value = True
        mock_data = "{}"
        with mock.patch(
            "ha_cluster_info.open", mock.mock_open(read_data=mock_data)
        ) as mock_open:
            self.assertEqual(
                ha_cluster_info.load_pcsd_known_hosts(),
                dict(),
            )
            mock_open.assert_called_once_with(
                self.file_path, "r", encoding="utf-8"
            )
        mock_exists.assert_called_once_with(self.file_path)

    @mock.patch("ha_cluster_info.os.path.exists")
    def test_extract(self, mock_exists: mock.Mock) -> None:
        mock_exists.return_value = True
        mock_data = json.dumps(
            dict(
                known_hosts=dict(
                    node1=dict(),
                    node2=dict(dest_list=[]),
                    node3=dict(dest_list=[dict()]),
                    node4=dict(dest_list=[dict(addr="node4A")]),
                    node5=dict(dest_list=[dict(port="10005")]),
                    node6=dict(dest_list=[dict(addr="node6A", port="10006")]),
                    node7=dict(
                        dest_list=[dict(addr="2001:db8::7", port="10007")]
                    ),
                    node8=dict(
                        dest_list=[
                            dict(addr="192.0.2.8", port="10008"),
                            dict(addr="node8B"),
                        ]
                    ),
                )
            )
        )
        with mock.patch(
            "ha_cluster_info.open", mock.mock_open(read_data=mock_data)
        ) as mock_open:
            self.assertEqual(
                ha_cluster_info.load_pcsd_known_hosts(),
                dict(
                    node4="node4A",
                    node6="node6A:10006",
                    node7="[2001:db8::7]:10007",
                    node8="192.0.2.8:10008",
                ),
            )
            mock_open.assert_called_once_with(
                self.file_path, "r", encoding="utf-8"
            )
        mock_exists.assert_called_once_with(self.file_path)


class MergeKnownHosts(TestCase):
    maxDiff = None

    def test_no_known_hosts(self) -> None:
        data = dict(
            ha_cluster_node_options=[
                dict(node_name="node1", corosync_addresses=["node1addr"]),
                dict(node_name="node2", corosync_addresses=["node2addr"]),
            ],
        )
        expected_result = deepcopy(data)
        ha_cluster_info.merge_known_hosts(data, dict())
        self.assertEqual(data, expected_result)

    def test_no_node_options(self) -> None:
        data: Dict[str, Any] = dict()
        ha_cluster_info.merge_known_hosts(data, dict(node1="node1A"))
        self.assertEqual(data, dict())

    def test_merge(self) -> None:
        data = dict(
            ha_cluster_node_options=[
                dict(node_name="node1", corosync_addresses=["node1addr"]),
                dict(node_name="node2", corosync_addresses=["node2addr"]),
                dict(node_name="node4", pcs_address="node4addr"),
            ],
            other_key="is not touched",
        )
        known_hosts = dict(node1="node1A", node3="node3A", node4="node4A")
        ha_cluster_info.merge_known_hosts(data, known_hosts)
        self.assertEqual(
            data,
            dict(
                ha_cluster_node_options=[
                    dict(
                        node_name="node1",
                        corosync_addresses=["node1addr"],
                        pcs_address="node1A",
                    ),
                    dict(
                        node_name="node2",
                        corosync_addresses=["node2addr"],
                    ),
                    dict(node_name="node4", pcs_address="node4A"),
                ],
                other_key="is not touched",
            ),
        )


class ExportClusterConfiguration(TestCase):
    maxDiff = None

    @mock.patch("ha_cluster_info.load_pcsd_known_hosts")
    @mock.patch("ha_cluster_info.export_corosync_conf")
    @mock.patch("ha_cluster_info.export_start_on_boot")
    def test_export(
        self,
        mock_export_start_on_boot: mock.Mock,
        mock_export_corosync_conf: mock.Mock,
        mock_load_pcsd_known_hosts: mock.Mock,
    ) -> None:
        module_mock = mock.Mock()
        mock_export_start_on_boot.return_value = True
        mock_export_corosync_conf.return_value = dict(
            ha_cluster_cluster_name="my-cluster",
            ha_cluster_transport=dict(type="knet"),
            ha_cluster_node_options=[
                dict(node_name="node1", corosync_addresses=["node1addr"]),
                dict(node_name="node2", corosync_addresses=["node2addr"]),
            ],
        )
        mock_load_pcsd_known_hosts.return_value = dict(
            node1="node1pcs",
            node2="node2pcs",
        )
        self.assertEqual(
            ha_cluster_info.export_cluster_configuration(module_mock),
            dict(
                ha_cluster_start_on_boot=True,
                ha_cluster_cluster_name="my-cluster",
                ha_cluster_transport=dict(type="knet"),
                ha_cluster_node_options=[
                    dict(
                        node_name="node1",
                        corosync_addresses=["node1addr"],
                        pcs_address="node1pcs",
                    ),
                    dict(
                        node_name="node2",
                        corosync_addresses=["node2addr"],
                        pcs_address="node2pcs",
                    ),
                ],
            ),
        )
