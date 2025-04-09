# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import json
from textwrap import dedent
from typing import Any
from unittest import TestCase, mock

from .firewall_mock import get_fw_mock
from .ha_cluster_info import loader


class IsRhelOrClone(TestCase):
    file_path = "/etc/os-release"

    def _assert_is_rhel(self, mock_data: str, is_rhel: bool) -> None:
        with mock.patch(
            "ha_cluster_lsr.info.loader.open",
            mock.mock_open(read_data=mock_data),
        ) as mock_open:
            self.assertEqual(loader.is_rhel_or_clone(), is_rhel)
            mock_open.assert_called_once_with(
                self.file_path, "r", encoding="utf-8", errors="replace"
            )

    def test_is_rhel(self) -> None:
        platform_list = [
            "platform:el8",
            "platform:el9",
            "platform:el10",
        ]
        for platform in platform_list:
            with self.subTest(platform=platform):
                mock_data = f'PLATFORM_ID="{platform}"\n'
                self._assert_is_rhel(mock_data, True)

    def test_is_not_rhel(self) -> None:
        platform_list = [
            "platform:f42",
            "",
        ]
        for platform in platform_list:
            with self.subTest(platform=platform):
                mock_data = f'PLATFORM_ID="{platform}"\n'
                self._assert_is_rhel(mock_data, False)

    def test_missing_platform_id_line(self) -> None:
        mock_data = 'NAME="Debian GNU/Linux"\nID=debian\n'
        self._assert_is_rhel(mock_data, False)

    def test_unable_to_read_os_release_file(self) -> None:
        with mock.patch(
            "ha_cluster_lsr.info.loader.open",
            mock.mock_open(),
        ) as mock_open:
            mock_open.side_effect = FileNotFoundError
            self.assertEqual(loader.is_rhel_or_clone(), False)


class GetDnfRepolist(TestCase):
    def test_success(self) -> None:
        # pylint: disable=line-too-long
        dnf_output = dedent(
            """\
            Updating Subscription Management repositories.
            repo id                                  repo name
            rhel-10-for-x86_64-appstream-rpms        Red Hat Enterprise Linux 10 for x86_64 - AppStream (RPMs)
            rhel-10-for-x86_64-baseos-rpms           Red Hat Enterprise Linux 10 for x86_64 - BaseOS (RPMs)
            rhel-10-for-x86_64-highavailability-rpms Red Hat Enterprise Linux 10 for x86_64 - High Availability (RPMs)
            """
        )
        runner_mock = mock.Mock()
        runner_mock.return_value = (0, dnf_output, "")

        self.assertEqual(loader.get_dnf_repolist(runner_mock), dnf_output)
        runner_mock.assert_called_once_with(["dnf", "repolist"], {})

    def test_error(self) -> None:
        runner_mock = mock.Mock()
        runner_mock.return_value = (1, "some output", "some error")

        self.assertIsNone(loader.get_dnf_repolist(runner_mock))
        runner_mock.assert_called_once_with(["dnf", "repolist"], {})


class GetRpmInstalledPackages(TestCase):
    def _assert_packages(
        self, runner_mock: Any, expected_packages: Any
    ) -> None:
        self.assertEqual(
            loader.get_rpm_installed_packages(runner_mock),
            expected_packages,
        )
        runner_mock.assert_called_once_with(
            ["rpm", "--query", "--all", "--queryformat", "%{NAME}\\n"], {}
        )

    def test_success(self) -> None:
        package_list = [
            "package_1",
            "package_2",
            "package_3",
        ]
        rpm_output = "\n".join(package_list)
        runner_mock = mock.Mock()
        runner_mock.return_value = (0, rpm_output, "")
        self._assert_packages(runner_mock, package_list)

    def test_rpm_error(self) -> None:
        package_list = [
            "package_1",
            "package_2",
            "package_3",
        ]
        rpm_output = "\n".join(package_list)
        runner_mock = mock.Mock()
        runner_mock.return_value = (1, rpm_output, "an error")
        self._assert_packages(runner_mock, None)


class GetFirewallConfig(TestCase):
    def test_success(self) -> None:
        services = ["service1", "service2"]
        ports = [("12345", "tcp"), ("23456", "udp")]
        fw_mock = get_fw_mock(services, ports)

        self.assertEqual(
            loader.get_firewall_config(fw_mock),
            {"services": services, "ports": ports},
        )

    def test_error(self) -> None:
        fw_mock = get_fw_mock([], [], exception=True)
        self.assertIsNone(
            loader.get_firewall_config(fw_mock),
        )


class GetFirewallHaClusterPorts(TestCase):
    maxDiff = None

    def test_success(self) -> None:
        fw_mock = get_fw_mock([], [])

        self.assertEqual(
            loader.get_firewall_ha_cluster_ports(fw_mock),
            [
                ("2224", "tcp"),
                ("3121", "tcp"),
                ("5403", "tcp"),
                ("5404", "udp"),
                ("5405-5412", "udp"),
                ("9929", "tcp"),
                ("9929", "udp"),
                ("21064", "tcp"),
            ],
        )

    def test_error(self) -> None:
        fw_mock = get_fw_mock([], [], exception=True)
        self.assertIsNone(loader.get_firewall_ha_cluster_ports(fw_mock))


class GetSelinuxHaClusterPorts(TestCase):
    def test_success(self) -> None:
        ports_tcp = ["2345", "3456"]
        ports_udp = ["4567", "5678"]
        ports_mock = mock.Mock(spec=["get_all_by_type"])
        ports_mock.get_all_by_type.return_value = {
            ("cluster_port_t", "tcp"): ports_tcp,
            ("cluster_port_t", "udp"): ports_udp,
        }

        self.assertEqual(
            loader.get_selinux_ha_cluster_ports(ports_mock),
            (ports_tcp, ports_udp),
        )

    def test_error(self) -> None:
        ports_mock = mock.Mock(spec=["get_all_by_type"])
        ports_mock.get_all_by_type.side_effect = Exception

        self.assertIsNone(loader.get_selinux_ha_cluster_ports(ports_mock))

    def test_no_ports(self) -> None:
        ports_mock = mock.Mock(spec=["get_all_by_type"])
        ports_mock.get_all_by_type.return_value = {
            ("some_port_t", "tcp"): ["2345"],
            ("other_port_t", "udp"): ["3456"],
        }

        self.assertEqual(
            loader.get_selinux_ha_cluster_ports(ports_mock),
            ([], []),
        )


class IsServiceEnabled(TestCase):
    def setUp(self) -> None:
        self.runner_mock = mock.Mock()

    def test_is_enabled(self) -> None:
        self.runner_mock.return_value = (0, "enabled", "")
        self.assertTrue(loader.is_service_enabled(self.runner_mock, "corosync"))
        self.runner_mock.assert_called_once_with(
            ["systemctl", "is-enabled", "corosync.service"],
            {"LC_ALL": "C"},
        )

    def test_is_disabled(self) -> None:
        self.runner_mock.return_value = (1, "disabled", "")
        self.assertFalse(
            loader.is_service_enabled(self.runner_mock, "pacemaker")
        )
        self.runner_mock.assert_called_once_with(
            ["systemctl", "is-enabled", "pacemaker.service"],
            {"LC_ALL": "C"},
        )

    def test_unexpected_output(self) -> None:
        self.runner_mock.return_value = (4, "not-found", "")
        self.assertFalse(loader.is_service_enabled(self.runner_mock, "pcmk"))
        self.runner_mock.assert_called_once_with(
            ["systemctl", "is-enabled", "pcmk.service"],
            {"LC_ALL": "C"},
        )


class CallPcsCli(TestCase):
    # pylint: disable=protected-access
    def test_success(self) -> None:
        runner_mock = mock.Mock()
        runner_mock.return_value = (
            0,
            """{"json": "test data", "foo": "bar"}""",
            "",
        )
        self.assertEqual(
            loader._call_pcs_cli(runner_mock, ["cluster", "config"]),
            dict(json="test data", foo="bar"),
        )
        runner_mock.assert_called_once_with(
            ["pcs", "cluster", "config"],
            {"LC_ALL": "C"},
        )

    def test_pcs_error(self) -> None:
        runner_mock = mock.Mock()
        runner_mock.return_value = (
            1,
            "some stdout message",
            "some stderr message",
        )
        with self.assertRaises(loader.CliCommandError) as cm:
            loader._call_pcs_cli(runner_mock, ["cluster", "config"])
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                pcs_command=["pcs", "cluster", "config"],
                stdout="some stdout message",
                stderr="some stderr message",
                rc=1,
            ),
        )
        runner_mock.assert_called_once_with(
            ["pcs", "cluster", "config"],
            {"LC_ALL": "C"},
        )

    def test_json_error(self) -> None:
        runner_mock = mock.Mock()
        runner_mock.return_value = (
            0,
            "not a json",
            "",
        )
        with self.assertRaises(loader.JsonParseError) as cm:
            loader._call_pcs_cli(runner_mock, ["cluster", "config"])
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data="not a json",
                data_desc="pcs cluster config",
                error="Expecting value: line 1 column 1 (char 0)",
                additional_info="",
            ),
        )
        runner_mock.assert_called_once_with(
            ["pcs", "cluster", "config"],
            {"LC_ALL": "C"},
        )


class GetCorosyncConf(TestCase):
    pcs_command = ["pcs", "cluster", "config", "--output-format=json"]
    env = {"LC_ALL": "C"}

    def test_success(self) -> None:
        runner_mock = mock.Mock()
        runner_mock.return_value = (0, """{"some": "json"}""", "")
        self.assertEqual(
            loader.get_corosync_conf(runner_mock), dict(some="json")
        )
        runner_mock.assert_called_once_with(self.pcs_command, self.env)

    def test_pcs_error(self) -> None:
        runner_mock = mock.Mock()
        runner_mock.return_value = (1, "stdout message", "stderr message")
        with self.assertRaises(loader.CliCommandError) as cm:
            loader.get_corosync_conf(runner_mock)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                pcs_command=self.pcs_command,
                stdout="stdout message",
                stderr="stderr message",
                rc=1,
            ),
        )
        runner_mock.assert_called_once_with(self.pcs_command, self.env)

    def test_json_error(self) -> None:
        runner_mock = mock.Mock()
        runner_mock.return_value = (0, "not a json", "")
        with self.assertRaises(loader.JsonParseError) as cm:
            loader.get_corosync_conf(runner_mock)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data="not a json",
                data_desc=" ".join(self.pcs_command),
                error="Expecting value: line 1 column 1 (char 0)",
                additional_info="",
            ),
        )
        runner_mock.assert_called_once_with(self.pcs_command, self.env)


class GetPcsdKnownHosts(TestCase):
    file_path = "/var/lib/pcsd/known-hosts"

    @mock.patch("ha_cluster_lsr.info.loader.os.path.exists")
    def test_file_not_present(self, mock_exists: mock.Mock) -> None:
        mock_exists.return_value = False
        self.assertEqual(loader.get_pcsd_known_hosts(), dict())
        mock_exists.assert_called_once_with(self.file_path)

    @mock.patch("ha_cluster_lsr.info.loader.os.path.exists")
    def test_json_error(self, mock_exists: mock.Mock) -> None:
        mock_exists.return_value = True
        mock_data = "not a json"
        with mock.patch(
            "ha_cluster_lsr.info.loader.open",
            mock.mock_open(read_data=mock_data),
        ) as mock_open:
            with self.assertRaises(loader.JsonParseError) as cm:
                loader.get_pcsd_known_hosts()
            self.assertEqual(
                cm.exception.kwargs,
                dict(
                    data="not logging data",
                    data_desc="known hosts",
                    error="Expecting value: line 1 column 1 (char 0)",
                    additional_info=None,
                ),
            )
            mock_open.assert_called_once_with(
                self.file_path, "r", encoding="utf-8"
            )
        mock_exists.assert_called_once_with(self.file_path)

    @mock.patch("ha_cluster_lsr.info.loader.os.path.exists")
    def test_json_empty(self, mock_exists: mock.Mock) -> None:
        mock_exists.return_value = True
        mock_data = "{}"
        with mock.patch(
            "ha_cluster_lsr.info.loader.open",
            mock.mock_open(read_data=mock_data),
        ) as mock_open:
            self.assertEqual(
                loader.get_pcsd_known_hosts(),
                dict(),
            )
            mock_open.assert_called_once_with(
                self.file_path, "r", encoding="utf-8"
            )
        mock_exists.assert_called_once_with(self.file_path)

    @mock.patch("ha_cluster_lsr.info.loader.os.path.exists")
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
            "ha_cluster_lsr.info.loader.open",
            mock.mock_open(read_data=mock_data),
        ) as mock_open:
            self.assertEqual(
                loader.get_pcsd_known_hosts(),
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


class GetPcsdSettingsConf(TestCase):
    maxDiff = None
    file_path = "/var/lib/pcsd/pcs_settings.conf"

    @mock.patch("ha_cluster_lsr.info.loader.os.path.exists")
    def test_file_not_present(self, mock_exists: mock.Mock) -> None:
        mock_exists.return_value = False
        self.assertEqual(loader.get_pcsd_settings_conf(), None)
        mock_exists.assert_called_once_with(self.file_path)

    @mock.patch("ha_cluster_lsr.info.loader.os.path.exists")
    def test_json_error(self, mock_exists: mock.Mock) -> None:
        mock_exists.return_value = True
        mock_data = "not a json"
        with mock.patch(
            "ha_cluster_lsr.info.loader.open",
            mock.mock_open(read_data=mock_data),
        ) as mock_open:
            with self.assertRaises(loader.JsonParseError) as cm:
                loader.get_pcsd_settings_conf()
            self.assertEqual(
                cm.exception.kwargs,
                dict(
                    data=mock_data,
                    data_desc="pcsd settings",
                    error="Expecting value: line 1 column 1 (char 0)",
                    additional_info=None,
                ),
            )
            mock_open.assert_called_once_with(
                self.file_path, "r", encoding="utf-8"
            )
        mock_exists.assert_called_once_with(self.file_path)

    @mock.patch("ha_cluster_lsr.info.loader.os.path.exists")
    def test_success(self, mock_exists: mock.Mock) -> None:
        mock_exists.return_value = True
        mock_data = """
            {
              "format_version": 2,
              "data_version": 3,
              "clusters": [
                {
                  "name": "rh100",
                  "nodes": ["rh100-node1"]
                }
              ],
              "permissions": {
                "local_cluster": [
                  {
                    "type": "group",
                    "name": "haclient",
                    "allow": ["grant", "read", "write"]
                  }
                ]
              }
            }
        """
        with mock.patch(
            "ha_cluster_lsr.info.loader.open",
            mock.mock_open(read_data=mock_data),
        ) as mock_open:
            self.assertEqual(
                loader.get_pcsd_settings_conf(),
                {
                    "format_version": 2,
                    "data_version": 3,
                    "clusters": [{"name": "rh100", "nodes": ["rh100-node1"]}],
                    "permissions": {
                        "local_cluster": [
                            {
                                "type": "group",
                                "name": "haclient",
                                "allow": ["grant", "read", "write"],
                            }
                        ]
                    },
                },
            )
            mock_open.assert_called_once_with(
                self.file_path, "r", encoding="utf-8"
            )
        mock_exists.assert_called_once_with(self.file_path)
