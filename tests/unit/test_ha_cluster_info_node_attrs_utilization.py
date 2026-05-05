# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# SPDX-License-Identifier: MIT

# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import json
from unittest import TestCase, mock

from .ha_cluster_info import ha_cluster_info, mocked_cmd_runner

EMPTY_NODE_CONFIG = {"nodes": []}  # type: ignore

CMD_OPTIONS = dict(environ_update={"LC_ALL": "C"}, check_rc=False)
PCS_CMD = ["pcs", "node", "attribute", "--output-format=json"]
CMD_NODE_ATTRS_CONF = mock.call(PCS_CMD, **CMD_OPTIONS)

COROSYNC_CONF_DATA = dict(
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
            addrs=[dict(addr="node2addr", link="0", type="IPv4")],
        ),
    ],
)


class ExportNodeAttrsUtilizationConfiguration(TestCase):
    maxDiff = None

    @mock.patch("ha_cluster_info.loader.get_pcsd_known_hosts")
    def test_success(
        self,
        mock_load_pcsd_known_hosts: mock.Mock,
    ) -> None:
        mock_load_pcsd_known_hosts.return_value = dict()
        node_attrs_data = {
            "nodes": [
                {
                    "uname": "node1",
                    "instance_attributes": [
                        {
                            "id": "ia-node1",
                            "nvpairs": [
                                {"id": "ia1", "name": "attr1", "value": "val1"},
                            ],
                        },
                    ],
                    "utilization": [
                        {
                            "id": "util-node1",
                            "nvpairs": [
                                {"id": "u1", "name": "cpu", "value": "2"},
                            ],
                        },
                    ],
                },
                {
                    "uname": "node2",
                    "instance_attributes": [],
                    "utilization": [],
                },
            ],
        }
        with mocked_cmd_runner(
            [(CMD_NODE_ATTRS_CONF, (0, json.dumps(node_attrs_data), ""))]
        ) as cmd_runner:
            result = ha_cluster_info.export_node_options_configuration(
                cmd_runner,
                COROSYNC_CONF_DATA,
                [ha_cluster_info.Capability.NODE_ATTRIBUTES_OUTPUT.value],
            )
        self.assertEqual(
            result,
            {
                "ha_cluster_node_options": [
                    {
                        "node_name": "node1",
                        "corosync_addresses": ["node1addr"],
                        "attributes": [
                            {"attrs": [{"name": "attr1", "value": "val1"}]},
                        ],
                        "utilization": [
                            {"attrs": [{"name": "cpu", "value": 2}]},
                        ],
                    },
                    {
                        "node_name": "node2",
                        "corosync_addresses": ["node2addr"],
                    },
                ],
            },
        )

    @mock.patch("ha_cluster_info.loader.get_pcsd_known_hosts")
    def test_success_empty(
        self,
        mock_load_pcsd_known_hosts: mock.Mock,
    ) -> None:
        mock_load_pcsd_known_hosts.return_value = dict()
        with mocked_cmd_runner(
            [(CMD_NODE_ATTRS_CONF, (0, json.dumps(EMPTY_NODE_CONFIG), ""))]
        ) as cmd_runner:
            result = ha_cluster_info.export_node_options_configuration(
                cmd_runner,
                COROSYNC_CONF_DATA,
                [ha_cluster_info.Capability.NODE_ATTRIBUTES_OUTPUT.value],
            )
        self.assertEqual(
            result,
            {
                "ha_cluster_node_options": [
                    {"node_name": "node1", "corosync_addresses": ["node1addr"]},
                    {"node_name": "node2", "corosync_addresses": ["node2addr"]},
                ],
            },
        )

    @mock.patch("ha_cluster_info.loader.get_pcsd_known_hosts")
    def test_no_capabilities(
        self,
        mock_load_pcsd_known_hosts: mock.Mock,
    ) -> None:
        mock_load_pcsd_known_hosts.return_value = dict()
        with mocked_cmd_runner([]) as cmd_runner:
            result = ha_cluster_info.export_node_options_configuration(
                cmd_runner,
                COROSYNC_CONF_DATA,
                pcs_capabilities=[],
            )
        self.assertEqual(
            result,
            {
                "ha_cluster_node_options": [
                    {"node_name": "node1", "corosync_addresses": ["node1addr"]},
                    {"node_name": "node2", "corosync_addresses": ["node2addr"]},
                ],
            },
        )

    @mock.patch("ha_cluster_info.loader.get_pcsd_known_hosts")
    def test_pcs_cmd_fail(
        self,
        mock_load_pcsd_known_hosts: mock.Mock,
    ) -> None:
        mock_load_pcsd_known_hosts.return_value = dict()
        with self.assertRaises(ha_cluster_info.loader.CliCommandError) as cm:
            with mocked_cmd_runner(
                [(CMD_NODE_ATTRS_CONF, (1, "", "Error"))]
            ) as cmd_runner:
                ha_cluster_info.export_node_options_configuration(
                    cmd_runner,
                    COROSYNC_CONF_DATA,
                    [ha_cluster_info.Capability.NODE_ATTRIBUTES_OUTPUT.value],
                )
        self.assertEqual(
            cm.exception.kwargs,
            dict(pcs_command=PCS_CMD, stdout="", stderr="Error", rc=1),
        )
