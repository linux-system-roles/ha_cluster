# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

from unittest import TestCase, mock

from .ha_cluster_info import ha_cluster_info, mocked_cmd_runner

CMD_OPTIONS = dict(environ_update={"LC_ALL": "C"}, check_rc=False)

CMD_ENABLED_COROSYNC = mock.call(
    ["systemctl", "is-enabled", "corosync.service"], **CMD_OPTIONS
)
CMD_ENABLED_PCMK = mock.call(
    ["systemctl", "is-enabled", "pacemaker.service"], **CMD_OPTIONS
)


class ExportClusterConfiguration(TestCase):
    maxDiff = None

    def assert_export_minimal(
        self,
        corosync_enabled: bool,
        pacemaker_enabled: bool,
        cluster_start_on_boot: bool,
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
        with mocked_cmd_runner(
            [
                (CMD_ENABLED_COROSYNC, (0 if corosync_enabled else 1, "", "")),
                (CMD_ENABLED_PCMK, (0 if pacemaker_enabled else 1, "", "")),
            ]
        ) as cmd_runner:
            self.assertEqual(
                ha_cluster_info.export_cluster_configuration(
                    cmd_runner, corosync_conf_data
                ),
                dict(
                    ha_cluster_start_on_boot=cluster_start_on_boot,
                    ha_cluster_cluster_name="my-cluster",
                    ha_cluster_transport=dict(type="knet"),
                ),
            )

    def test_export_minimal_enabled(self) -> None:
        self.assert_export_minimal(True, False, True)

    def test_export_minimal_disabled(self) -> None:
        self.assert_export_minimal(False, False, False)

    def test_export(self) -> None:
        corosync_conf_data = dict(
            cluster_name="my-cluster",
            transport="KNET",
            transport_options=dict(transport_key="transport_val"),
            links_options=dict(),
            compression_options=dict(),
            crypto_options=dict(),
            totem_options=dict(totem_key="totem_val"),
            quorum_options=dict(quorum_key="quorum_val"),
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

        with mocked_cmd_runner(
            [
                (CMD_ENABLED_COROSYNC, (0, "", "")),
                (CMD_ENABLED_PCMK, (0, "", "")),
            ]
        ) as cmd_runner:
            self.assertEqual(
                ha_cluster_info.export_cluster_configuration(
                    cmd_runner, corosync_conf_data
                ),
                dict(
                    ha_cluster_start_on_boot=True,
                    ha_cluster_cluster_name="my-cluster",
                    ha_cluster_transport=dict(
                        type="knet",
                        options=[
                            dict(name="transport_key", value="transport_val")
                        ],
                    ),
                    ha_cluster_totem=dict(
                        options=[dict(name="totem_key", value="totem_val")],
                    ),
                    ha_cluster_quorum=dict(
                        options=[dict(name="quorum_key", value="quorum_val")],
                    ),
                ),
            )
