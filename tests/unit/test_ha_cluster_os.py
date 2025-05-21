# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

from textwrap import dedent
from typing import Dict
from unittest import TestCase, mock

from .firewall_mock import get_fw_mock
from .ha_cluster_info import ha_cluster_info, mocked_module

OPTIONS = dict(environ_update={}, check_rc=False)
CMD_DNF_REPORTLIST = mock.call(["dnf", "repolist"], **OPTIONS)
CMD_RPM_INSTALLED = mock.call(
    ["rpm", "--query", "--all", "--queryformat", "%{NAME}\\n"], **OPTIONS
)


class ExportOsConfiguration(TestCase):
    maxDiff = None

    @mock.patch("ha_cluster_info.loader.is_rhel_or_clone", lambda: True)
    @mock.patch("ha_cluster_info.HAS_FIREWALL", False)
    @mock.patch("ha_cluster_info.HAS_SELINUX", False)
    def test_packages_rhel_1(self) -> None:
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
        with mocked_module(
            [
                (CMD_DNF_REPORTLIST, (0, dnf_repolist, "")),
                (CMD_RPM_INSTALLED, (0, rpm_packages, "")),
            ],
        ) as module_mock:
            self.assertEqual(
                ha_cluster_info.export_os_configuration(module_mock),
                {
                    "ha_cluster_enable_repos": True,
                    "ha_cluster_enable_repos_resilient_storage": False,
                    "ha_cluster_install_cloud_agents": False,
                },
            )

    @mock.patch("ha_cluster_info.loader.is_rhel_or_clone", lambda: True)
    @mock.patch("ha_cluster_info.HAS_FIREWALL", False)
    @mock.patch("ha_cluster_info.HAS_SELINUX", False)
    def test_packages_rhel_2(self) -> None:
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
        with mocked_module(
            [
                (CMD_DNF_REPORTLIST, (0, dnf_repolist, "")),
                (CMD_RPM_INSTALLED, (0, rpm_packages, "")),
            ],
        ) as module_mock:
            self.assertEqual(
                ha_cluster_info.export_os_configuration(module_mock),
                {
                    "ha_cluster_enable_repos": False,
                    "ha_cluster_enable_repos_resilient_storage": True,
                    "ha_cluster_install_cloud_agents": True,
                },
            )

    @mock.patch("ha_cluster_info.loader.is_rhel_or_clone", lambda: True)
    @mock.patch("ha_cluster_info.HAS_FIREWALL", False)
    @mock.patch("ha_cluster_info.HAS_SELINUX", False)
    def test_packages_rhel_error_repolist(self) -> None:
        rpm_packages = dedent(
            """\
            package1
            resource-agents-cloud
            package2
            """
        )
        with mocked_module(
            [
                (CMD_DNF_REPORTLIST, (1, "some output", "an error")),
                (CMD_RPM_INSTALLED, (0, rpm_packages, "")),
            ],
        ) as module_mock:
            self.assertEqual(
                ha_cluster_info.export_os_configuration(module_mock),
                {
                    "ha_cluster_install_cloud_agents": True,
                },
            )

    @mock.patch("ha_cluster_info.loader.is_rhel_or_clone", lambda: True)
    @mock.patch("ha_cluster_info.HAS_FIREWALL", False)
    @mock.patch("ha_cluster_info.HAS_SELINUX", False)
    def test_packages_rhel_error_pkglist(self) -> None:
        dnf_repolist = dedent(
            """\
            repo1id           Repository 1
            highavailability  Repository HA Addon
            repo2id           Repository 2
            """
        )
        with mocked_module(
            [
                (CMD_DNF_REPORTLIST, (0, dnf_repolist, "")),
                (CMD_RPM_INSTALLED, (1, "some output", "an error")),
            ],
        ) as module_mock:
            self.assertEqual(
                ha_cluster_info.export_os_configuration(module_mock),
                {
                    "ha_cluster_enable_repos": True,
                    "ha_cluster_enable_repos_resilient_storage": False,
                },
            )

    @mock.patch("ha_cluster_info.loader.is_rhel_or_clone", lambda: False)
    @mock.patch("ha_cluster_info.HAS_FIREWALL", False)
    @mock.patch("ha_cluster_info.HAS_SELINUX", False)
    def test_packages_non_rhel(self) -> None:
        with mocked_module() as module_mock:
            self.assertEqual(
                ha_cluster_info.export_os_configuration(module_mock),
                {},
            )

    @mock.patch("ha_cluster_info.loader.is_rhel_or_clone", lambda: False)
    @mock.patch("ha_cluster_info.HAS_FIREWALL", True)
    @mock.patch("ha_cluster_info.HAS_SELINUX", False)
    def test_firewall_true(self) -> None:
        module_mock = mock.Mock()
        with mock.patch("ha_cluster_info.FirewallClient") as fw_class_mock:
            fw_class_mock.return_value = get_fw_mock(["high-availability"], [])
            self.assertEqual(
                ha_cluster_info.export_os_configuration(module_mock),
                {"ha_cluster_manage_firewall": True},
            )

    @mock.patch("ha_cluster_info.loader.is_rhel_or_clone", lambda: False)
    @mock.patch("ha_cluster_info.HAS_FIREWALL", True)
    @mock.patch("ha_cluster_info.HAS_SELINUX", False)
    def test_firewall_false(self) -> None:
        module_mock = mock.Mock()
        with mock.patch("ha_cluster_info.FirewallClient") as fw_class_mock:
            fw_class_mock.return_value = get_fw_mock([], [])
            self.assertEqual(
                ha_cluster_info.export_os_configuration(module_mock),
                {"ha_cluster_manage_firewall": False},
            )

    @mock.patch("ha_cluster_info.loader.is_rhel_or_clone", lambda: False)
    @mock.patch("ha_cluster_info.HAS_FIREWALL", True)
    @mock.patch("ha_cluster_info.HAS_SELINUX", False)
    def test_firewall_not_available(self) -> None:
        module_mock = mock.Mock()
        with mock.patch("ha_cluster_info.FirewallClient") as fw_class_mock:
            fw_class_mock.return_value = get_fw_mock([], [], exception=True)
            self.assertEqual(
                ha_cluster_info.export_os_configuration(module_mock),
                {},
            )

    def assert_manage_selinux(
        self, selinux_ports_mock: mock.Mock, expected_export: Dict[str, bool]
    ) -> None:
        module_mock = mock.Mock()
        with mock.patch("ha_cluster_info.FirewallClient") as fw_class_mock:
            with mock.patch(
                "ha_cluster_info.SelinuxPortRecords"
            ) as selinux_class_mock:
                fw_class_mock.return_value = get_fw_mock(
                    ["high-availability"], []
                )
                selinux_class_mock.return_value = selinux_ports_mock

                self.assertEqual(
                    ha_cluster_info.export_os_configuration(module_mock),
                    expected_export,
                )

    @mock.patch("ha_cluster_info.loader.is_rhel_or_clone", lambda: False)
    @mock.patch("ha_cluster_info.HAS_FIREWALL", True)
    @mock.patch("ha_cluster_info.HAS_SELINUX", True)
    def test_selinux_true(self) -> None:
        selinux_ports_mock = mock.Mock()
        selinux_ports_mock.get_all_by_type.return_value = {
            ("cluster_port_t", "tcp"): ["5403"],
        }
        self.assert_manage_selinux(
            selinux_ports_mock,
            {
                "ha_cluster_manage_firewall": True,
                "ha_cluster_manage_selinux": True,
            },
        )

    @mock.patch("ha_cluster_info.loader.is_rhel_or_clone", lambda: False)
    @mock.patch("ha_cluster_info.HAS_FIREWALL", True)
    @mock.patch("ha_cluster_info.HAS_SELINUX", True)
    def test_selinux_false(self) -> None:
        selinux_ports_mock = mock.Mock()
        selinux_ports_mock.get_all_by_type.return_value = {
            ("cluster_port_t", "tcp"): ["5149"],
        }
        self.assert_manage_selinux(
            selinux_ports_mock,
            {
                "ha_cluster_manage_firewall": True,
                "ha_cluster_manage_selinux": False,
            },
        )

    @mock.patch("ha_cluster_info.loader.is_rhel_or_clone", lambda: False)
    @mock.patch("ha_cluster_info.HAS_FIREWALL", True)
    @mock.patch("ha_cluster_info.HAS_SELINUX", True)
    def test_selinux_not_available(self) -> None:
        selinux_ports_mock = mock.Mock()
        selinux_ports_mock.get_all_by_type.side_effect = Exception
        self.assert_manage_selinux(
            selinux_ports_mock,
            {
                "ha_cluster_manage_firewall": True,
            },
        )
