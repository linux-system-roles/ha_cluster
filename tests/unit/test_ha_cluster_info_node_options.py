# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

from unittest import TestCase, mock

from .ha_cluster_info import ha_cluster_info, mocked_cmd_runner


class ExportNodeOptionsConfiguration(TestCase):
    maxDiff = None

    @mock.patch("ha_cluster_info.loader.get_pcsd_known_hosts")
    def test_export_minimal(
        self,
        mock_load_pcsd_known_hosts: mock.Mock,
    ) -> None:
        corosync_conf_data = dict(
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
            ],
        )
        mock_load_pcsd_known_hosts.return_value = dict()
        with mocked_cmd_runner([]) as cmd_runner:
            self.assertEqual(
                ha_cluster_info.export_node_options_configuration(
                    cmd_runner, corosync_conf_data, pcs_capabilities=[]
                ),
                dict(
                    ha_cluster_node_options=[
                        dict(
                            node_name="node1",
                            corosync_addresses=["node1addr"],
                        ),
                    ],
                ),
            )
        mock_load_pcsd_known_hosts.assert_called_once_with()

    @mock.patch("ha_cluster_info.loader.get_pcsd_known_hosts")
    def test_export_with_pcs_address(
        self,
        mock_load_pcsd_known_hosts: mock.Mock,
    ) -> None:
        corosync_conf_data = dict(
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
        mock_load_pcsd_known_hosts.return_value = dict(
            node1="node1pcs",
            node2="node2pcs",
        )
        with mocked_cmd_runner([]) as cmd_runner:
            self.assertEqual(
                ha_cluster_info.export_node_options_configuration(
                    cmd_runner, corosync_conf_data, pcs_capabilities=[]
                ),
                dict(
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
        mock_load_pcsd_known_hosts.assert_called_once_with()

    @mock.patch("ha_cluster_info.loader.get_pcsd_known_hosts")
    def test_missing_corosync_nodes_key(
        self,
        mock_load_pcsd_known_hosts: mock.Mock,
    ) -> None:
        corosync_conf_data = dict(
            cluster_name="my-cluster",
            transport="KNET",
            transport_options=dict(),
            links_options=dict(),
            compression_options=dict(),
            crypto_options=dict(),
            totem_options=dict(),
            quorum_options=dict(),
        )

        mock_load_pcsd_known_hosts.return_value = dict(
            node1="node1pcs",
            node2="node2pcs",
        )

        with self.assertRaises(ha_cluster_info.exporter.InvalidSrc) as cm:
            with mocked_cmd_runner([]) as cmd_runner:
                ha_cluster_info.export_node_options_configuration(
                    cmd_runner, corosync_conf_data, pcs_capabilities=[]
                )
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data_desc="corosync configuration",
                data=corosync_conf_data,
                issue_location="",
                issue_desc="Missing key 'nodes'",
            ),
        )

        mock_load_pcsd_known_hosts.assert_called_once_with()
