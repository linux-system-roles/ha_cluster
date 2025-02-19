#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import json
import sys
from importlib import import_module
from textwrap import dedent
from typing import Any, Dict, List, Tuple
from unittest import TestCase, mock

sys.modules["ansible.module_utils.ha_cluster_lsr"] = import_module(
    "ha_cluster_lsr"
)

import ha_cluster_info


class ExportClusterConfiguration(TestCase):
    maxDiff = None

    @staticmethod
    def fixture_expected_runner_calls() -> List[mock._Call]:
        common_args = dict(check_rc=False, environ_update={"LC_ALL": "C"})
        return [
            mock.call(
                ["systemctl", "is-enabled", "corosync.service"], **common_args
            ),
            mock.call(
                ["systemctl", "is-enabled", "pacemaker.service"], **common_args
            ),
            mock.call(
                ["pcs", "cluster", "config", "--output-format=json"],
                **common_args,
            ),
        ]

    def assert_export_minimal(
        self,
        mock_load_pcsd_known_hosts: mock.Mock,
        corosync_enabled: bool,
        pacemaker_enabled: bool,
        cluster_start_on_boot: bool,
    ) -> None:
        module_mock = mock.Mock()
        module_mock.run_command = mock.Mock()
        runner_mock = module_mock.run_command

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
        runner_mock.side_effect = [
            (0 if corosync_enabled else 1, "", ""),
            (0 if pacemaker_enabled else 1, "", ""),
            (0, json.dumps(corosync_conf_data), ""),
        ]

        mock_load_pcsd_known_hosts.return_value = dict()

        self.assertEqual(
            ha_cluster_info.export_cluster_configuration(module_mock),
            dict(
                ha_cluster_start_on_boot=cluster_start_on_boot,
                ha_cluster_cluster_name="my-cluster",
                ha_cluster_transport=dict(type="knet"),
                ha_cluster_node_options=[
                    dict(
                        node_name="node1",
                        corosync_addresses=["node1addr"],
                    ),
                ],
            ),
        )

        expected_calls = self.fixture_expected_runner_calls()
        runner_mock.assert_has_calls(expected_calls)
        self.assertEqual(runner_mock.call_count, len(expected_calls))

        mock_load_pcsd_known_hosts.assert_called_once_with()

    @mock.patch("ha_cluster_info.loader.get_pcsd_known_hosts")
    def test_export_minimal_enabled(
        self,
        mock_load_pcsd_known_hosts: mock.Mock,
    ) -> None:
        self.assert_export_minimal(
            mock_load_pcsd_known_hosts, True, False, True
        )

    @mock.patch("ha_cluster_info.loader.get_pcsd_known_hosts")
    def test_export_minimal_disabled(
        self,
        mock_load_pcsd_known_hosts: mock.Mock,
    ) -> None:
        self.assert_export_minimal(
            mock_load_pcsd_known_hosts, False, False, False
        )

    @mock.patch("ha_cluster_info.loader.get_pcsd_known_hosts")
    def test_export(
        self,
        mock_load_pcsd_known_hosts: mock.Mock,
    ) -> None:
        module_mock = mock.Mock()
        module_mock.run_command = mock.Mock()
        runner_mock = module_mock.run_command

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
        runner_mock.side_effect = [
            (0, "", ""),
            (0, "", ""),
            (0, json.dumps(corosync_conf_data), ""),
        ]

        mock_load_pcsd_known_hosts.return_value = dict(
            node1="node1pcs",
            node2="node2pcs",
        )

        self.assertEqual(
            ha_cluster_info.export_cluster_configuration(module_mock),
            dict(
                ha_cluster_start_on_boot=True,
                ha_cluster_cluster_name="my-cluster",
                ha_cluster_transport=dict(
                    type="knet",
                    options=[dict(name="transport_key", value="transport_val")],
                ),
                ha_cluster_totem=dict(
                    options=[dict(name="totem_key", value="totem_val")],
                ),
                ha_cluster_quorum=dict(
                    options=[dict(name="quorum_key", value="quorum_val")],
                ),
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

        expected_calls = self.fixture_expected_runner_calls()
        runner_mock.assert_has_calls(expected_calls)
        self.assertEqual(runner_mock.call_count, len(expected_calls))

        mock_load_pcsd_known_hosts.assert_called_once_with()

    @mock.patch("ha_cluster_info.loader.get_pcsd_known_hosts")
    def test_missing_corosync_nodes_key(
        self,
        mock_load_pcsd_known_hosts: mock.Mock,
    ) -> None:
        module_mock = mock.Mock()
        module_mock.run_command = mock.Mock()
        runner_mock = module_mock.run_command

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
        runner_mock.side_effect = [
            (0, "", ""),
            (0, "", ""),
            (0, json.dumps(corosync_conf_data), ""),
        ]

        mock_load_pcsd_known_hosts.return_value = dict(
            node1="node1pcs",
            node2="node2pcs",
        )

        with self.assertRaises(ha_cluster_info.exporter.JsonMissingKey) as cm:
            ha_cluster_info.export_cluster_configuration(module_mock)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data=corosync_conf_data,
                key="nodes",
                data_desc="corosync configuration",
            ),
        )

        expected_calls = self.fixture_expected_runner_calls()
        runner_mock.assert_has_calls(expected_calls)
        self.assertEqual(runner_mock.call_count, len(expected_calls))

        mock_load_pcsd_known_hosts.assert_called_once_with()


class ExportOsConfiguration(TestCase):
    maxDiff = None

    def assert_rhel_export(
        self,
        runner_mock_side_effect: List[Tuple[int, str, str]],
        expected_export: Dict[str, Any],
    ) -> None:
        module_mock = mock.Mock()
        module_mock.run_command = mock.Mock()
        runner_mock = module_mock.run_command
        runner_mock.side_effect = runner_mock_side_effect

        self.assertEqual(
            ha_cluster_info.export_os_configuration(module_mock),
            expected_export,
        )
        self.assertEqual(runner_mock.call_count, len(runner_mock_side_effect))

    @mock.patch("ha_cluster_info.loader.is_rhel_or_clone", lambda: True)
    def test_rhel_1(self) -> None:
        dnf_repolist = dedent(
            """\
            repo1id           Repository 1
            highavailability  Repository HA Addon
            repo2id           Repository 2
            """
        )
        rpm_packages = dedent(
            """\
            package1
            package2
            """
        )
        self.assert_rhel_export(
            [
                (0, dnf_repolist, ""),
                (0, rpm_packages, ""),
            ],
            {
                "ha_cluster_enable_repos": True,
                "ha_cluster_enable_repos_resilient_storage": False,
                "ha_cluster_install_cloud_agents": False,
            },
        )

    @mock.patch("ha_cluster_info.loader.is_rhel_or_clone", lambda: True)
    def test_rhel_2(self) -> None:
        dnf_repolist = dedent(
            """\
            repo1id           Repository 1
            resilientstorage  RS repository
            repo2id           Repository 2
            """
        )
        rpm_packages = dedent(
            """\
            package1
            resource-agents-cloud
            package2
            """
        )
        self.assert_rhel_export(
            [
                (0, dnf_repolist, ""),
                (0, rpm_packages, ""),
            ],
            {
                "ha_cluster_enable_repos": False,
                "ha_cluster_enable_repos_resilient_storage": True,
                "ha_cluster_install_cloud_agents": True,
            },
        )

    @mock.patch("ha_cluster_info.loader.is_rhel_or_clone", lambda: True)
    def test_rhel_error_repolist(self) -> None:
        rpm_packages = dedent(
            """\
            package1
            resource-agents-cloud
            package2
            """
        )
        self.assert_rhel_export(
            [
                (1, "some output", "an error"),
                (0, rpm_packages, ""),
            ],
            {
                "ha_cluster_install_cloud_agents": True,
            },
        )

    @mock.patch("ha_cluster_info.loader.is_rhel_or_clone", lambda: True)
    def test_rhel_error_pkglist(self) -> None:
        dnf_repolist = dedent(
            """\
            repo1id           Repository 1
            highavailability  Repository HA Addon
            repo2id           Repository 2
            """
        )
        self.assert_rhel_export(
            [
                (0, dnf_repolist, ""),
                (1, "some output", "an error"),
            ],
            {
                "ha_cluster_enable_repos": True,
                "ha_cluster_enable_repos_resilient_storage": False,
            },
        )

    @mock.patch("ha_cluster_info.loader.is_rhel_or_clone", lambda: False)
    def test_non_rhel(self) -> None:
        module_mock = mock.Mock()
        module_mock.run_command = mock.Mock()
        runner_mock = module_mock.run_command

        self.assertEqual(
            ha_cluster_info.export_os_configuration(module_mock),
            {},
        )
        runner_mock.assert_not_called()


class ExportPcsdConfiguration(TestCase):
    maxDiff = None

    @mock.patch("ha_cluster_info.loader.get_pcsd_settings_conf")
    def test_permissions_defined(
        self, mock_load_pcsd_permisions: mock.Mock
    ) -> None:
        mock_load_pcsd_permisions.return_value = {
            "permissions": {
                "local_cluster": [
                    {
                        "type": "group",
                        "name": "haclient",
                        "allow": ["grant", "read", "write"],
                    },
                    {
                        "type": "user",
                        "name": "admin",
                        "allow": ["full"],
                    },
                ]
            }
        }

        self.assertEqual(
            ha_cluster_info.export_pcsd_configuration(),
            {
                "ha_cluster_pcs_permission_list": [
                    {
                        "type": "group",
                        "name": "haclient",
                        "allow_list": ["grant", "read", "write"],
                    },
                    {
                        "type": "user",
                        "name": "admin",
                        "allow_list": ["full"],
                    },
                ]
            },
        )

    @mock.patch("ha_cluster_info.loader.get_pcsd_settings_conf")
    def test_empty_permissions_defined(
        self, mock_load_pcsd_permisions: mock.Mock
    ) -> None:
        mock_load_pcsd_permisions.return_value = {
            "permissions": {
                "local_cluster": [],
            }
        }

        self.assertEqual(
            ha_cluster_info.export_pcsd_configuration(),
            {
                "ha_cluster_pcs_permission_list": [],
            },
        )

    @mock.patch("ha_cluster_info.loader.get_pcsd_settings_conf")
    def test_permission_load_error(
        self, mock_load_pcsd_permisions: mock.Mock
    ) -> None:
        mock_load_pcsd_permisions.return_value = None

        self.assertEqual(
            ha_cluster_info.export_pcsd_configuration(),
            {},
        )

    @mock.patch("ha_cluster_info.loader.get_pcsd_settings_conf")
    def test_permission_load_bad_format(
        self, mock_load_pcsd_permisions: mock.Mock
    ) -> None:
        mock_load_pcsd_permisions.return_value = {
            "permissions": {
                "local": [
                    {
                        "type": "group",
                        "name": "haclient",
                        "allow": ["grant", "read", "write"],
                    },
                ]
            }
        }

        with self.assertRaises(ha_cluster_info.exporter.JsonMissingKey) as cm:
            ha_cluster_info.export_pcsd_configuration()
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data=mock_load_pcsd_permisions.return_value,
                key="local_cluster",
                data_desc="pcs_settings.conf",
            ),
        )
