# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

from textwrap import dedent
from typing import Any, Dict
from unittest import TestCase

from .ha_cluster_info import exporter, exporter_package


class DictToNvList(TestCase):
    # pylint: disable=protected-access
    def test_no_item(self) -> None:
        self.assertEqual(
            exporter_package.nvset.dict_to_nv_list(dict()),
            [],
        )

    def test_one_item(self) -> None:
        self.assertEqual(
            exporter_package.nvset.dict_to_nv_list(dict(one="1")),
            [dict(name="one", value="1")],
        )

    def test_two_items(self) -> None:
        self.assertEqual(
            exporter_package.nvset.dict_to_nv_list(dict(one="1", two="2")),
            [dict(name="one", value="1"), dict(name="two", value="2")],
        )


class ExportEnableReposHa(TestCase):
    def test_enabled(self) -> None:
        # pylint: disable=line-too-long
        dnf_repolist = dedent(
            """\
            Updating Subscription Management repositories.
            repo id                                  repo name
            rhel-10-for-x86_64-appstream-rpms        Red Hat Enterprise Linux 10 for x86_64 - AppStream (RPMs)
            rhel-10-for-x86_64-baseos-rpms           Red Hat Enterprise Linux 10 for x86_64 - BaseOS (RPMs)
            rhel-10-for-x86_64-highavailability-rpms Red Hat Enterprise Linux 10 for x86_64 - High Availability (RPMs)
            """
        )
        self.assertTrue(exporter.export_enable_repos_ha(dnf_repolist))

    def test_not_enabled(self) -> None:
        dnf_repolist = dedent(
            """\
            repo id                repo name
            fedora                 Fedora 41 - x86_64
            fedora-cisco-openh264  Fedora 41 openh264 (From Cisco) - x86_64
            updates                Fedora 41 - x86_64 - Updates
            """
        )
        self.assertFalse(exporter.export_enable_repos_ha(dnf_repolist))


class ExportEnableReposRs(TestCase):
    def test_enabled(self) -> None:
        # pylint: disable=line-too-long
        dnf_repolist = dedent(
            """\
            Updating Subscription Management repositories.
            repo id                                  repo name
            rhel-9-for-x86_64-appstream-rpms         Red Hat Enterprise Linux 9 for x86_64 - AppStream (RPMs)
            rhel-9-for-x86_64-baseos-rpms            Red Hat Enterprise Linux 9 for x86_64 - BaseOS (RPMs)
            rhel-9-for-x86_64-highavailability-rpms  Red Hat Enterprise Linux 9 for x86_64 - High Availability (RPMs)
            rhel-9-for-x86_64-resilientstorage-rpms  Red Hat Enterprise Linux 9 for x86_64 - Resilient Storage (RPMs)
            """
        )
        self.assertTrue(exporter.export_enable_repos_rs(dnf_repolist))

    def test_not_enabled(self) -> None:
        # pylint: disable=line-too-long
        dnf_repolist = dedent(
            """\
            Updating Subscription Management repositories.
            repo id                                  repo name
            rhel-10-for-x86_64-appstream-rpms        Red Hat Enterprise Linux 10 for x86_64 - AppStream (RPMs)
            rhel-10-for-x86_64-baseos-rpms           Red Hat Enterprise Linux 10 for x86_64 - BaseOS (RPMs)
            rhel-10-for-x86_64-highavailability-rpms Red Hat Enterprise Linux 10 for x86_64 - High Availability (RPMs)
            """
        )
        self.assertFalse(exporter.export_enable_repos_rs(dnf_repolist))


class ExportInstallCloudAgents(TestCase):
    def test_not_installed(self) -> None:
        rpm_packages = ["package1", "package2"]
        self.assertFalse(exporter.export_install_cloud_agents(rpm_packages))

    def test_installed(self) -> None:
        rpm_packages = ["package1", "package2", "resource-agents-cloud"]
        self.assertTrue(exporter.export_install_cloud_agents(rpm_packages))


class ExportManageFirewall(TestCase):
    def test_true_by_service(self) -> None:
        self.assertTrue(
            exporter.export_manage_firewall(
                {
                    "services": ["service1", "high-availability"],
                    "ports": [],
                }
            )
        )

    def test_true_by_port(self) -> None:
        self.assertTrue(
            exporter.export_manage_firewall(
                {
                    "services": ["service1"],
                    "ports": [("1229", "tcp")],
                }
            )
        )

    def test_false(self) -> None:
        self.assertFalse(
            exporter.export_manage_firewall(
                {
                    "services": ["service1", "availability"],
                    "ports": [("1229", "udp")],
                }
            )
        )


class ExportManageSelinux(TestCase):
    def test_true_by_tcp(self) -> None:
        firewall_ports = [("3456", "tcp"), ("45670", "udp")]
        selinux_ports = (["2345", "3456"], ["4567", "5678"])
        self.assertTrue(
            exporter.export_manage_selinux(firewall_ports, selinux_ports)
        )

    def test_true_by_udp(self) -> None:
        firewall_ports = [("34560", "tcp"), ("4567", "udp")]
        selinux_ports = (["2345", "3456"], ["4567", "5678"])
        self.assertTrue(
            exporter.export_manage_selinux(firewall_ports, selinux_ports)
        )

    def test_false(self) -> None:
        firewall_ports = [("34560", "tcp"), ("45670", "udp")]
        selinux_ports = (["2345", "3456"], ["4567", "5678"])
        self.assertFalse(
            exporter.export_manage_selinux(firewall_ports, selinux_ports)
        )


class ExportStartOnBoot(TestCase):
    def test_main(self) -> None:
        self.assertFalse(exporter.export_start_on_boot(False, False))
        self.assertTrue(exporter.export_start_on_boot(False, True))
        self.assertTrue(exporter.export_start_on_boot(True, False))
        self.assertTrue(exporter.export_start_on_boot(True, True))


class ExportCorosyncClusterName(TestCase):
    maxDiff = None

    def test_missing_key(self) -> None:
        corosync_data: Dict[str, Any] = dict()
        with self.assertRaises(exporter.InvalidSrc) as cm:
            exporter.export_corosync_cluster_name(corosync_data)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data_desc="corosync configuration",
                data=corosync_data,
                issue_location="",
                issue_desc="Missing key 'cluster_name'",
            ),
        )

    def test_minimal(self) -> None:
        corosync_data: Dict[str, Any] = dict(
            cluster_name="my-cluster",
        )
        role_data = exporter.export_corosync_cluster_name(corosync_data)
        self.assertEqual(role_data, "my-cluster")


class ExportCorosyncTransport(TestCase):
    maxDiff = None

    def assert_missing_key(
        self, corosync_data: Dict[str, Any], key: str
    ) -> None:
        with self.assertRaises(exporter.InvalidSrc) as cm:
            exporter.export_corosync_transport(corosync_data)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data_desc="corosync configuration",
                data=corosync_data,
                issue_location="",
                issue_desc=f"Missing key '{key}'",
            ),
        )

    def test_missing_key(self) -> None:
        self.assert_missing_key(
            dict(),
            "transport",
        )
        self.assert_missing_key(
            dict(
                transport="x",
            ),
            "transport_options",
        )
        self.assert_missing_key(
            dict(
                transport="x",
                transport_options=dict(),
            ),
            "links_options",
        )
        self.assert_missing_key(
            dict(
                transport="x",
                transport_options=dict(),
                links_options=dict(),
            ),
            "compression_options",
        )
        self.assert_missing_key(
            dict(
                transport="x",
                transport_options=dict(),
                links_options=dict(),
                compression_options=dict(),
            ),
            "crypto_options",
        )

    def test_minimal(self) -> None:
        corosync_data: Dict[str, Any] = dict(
            transport="KNET",
            transport_options=dict(),
            links_options=dict(),
            compression_options=dict(),
            crypto_options=dict(),
        )
        role_data = exporter.export_corosync_transport(corosync_data)
        self.assertEqual(role_data, dict(type="knet"))

    def test_simple_options_mirroring(self) -> None:
        corosync_data: Dict[str, Any] = dict(
            transport="KNET",
            transport_options=dict(transport1="c", transport2="d"),
            compression_options=dict(compression1="e", compression2="f"),
            crypto_options=dict(crypto1="g", crypto2="h"),
            links_options=dict(),
        )
        role_data = exporter.export_corosync_transport(corosync_data)
        self.assertEqual(
            role_data,
            dict(
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
        )

    def test_one_link(self) -> None:
        corosync_data: Dict[str, Any] = dict(
            transport="KNET",
            transport_options=dict(),
            links_options={"0": dict(name1="value1", name2="value2")},
            compression_options=dict(),
            crypto_options=dict(),
        )
        role_data = exporter.export_corosync_transport(corosync_data)
        self.assertEqual(
            role_data,
            dict(
                type="knet",
                links=[
                    [
                        dict(name="name1", value="value1"),
                        dict(name="name2", value="value2"),
                    ]
                ],
            ),
        )

    def test_more_links(self) -> None:
        corosync_data: Dict[str, Any] = dict(
            transport="KNET",
            transport_options=dict(),
            links_options={
                "0": dict(linknumber="0", name0="value0"),
                "7": dict(linknumber="7", name7="value7"),
                "3": dict(linknumber="3", name3="value3"),
            },
            compression_options=dict(),
            crypto_options=dict(),
        )
        role_data = exporter.export_corosync_transport(corosync_data)
        self.assertEqual(
            role_data,
            dict(
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
        )


class ExportCorosyncTotem(TestCase):
    maxDiff = None

    def test_missing_key(self) -> None:
        corosync_data: Dict[str, Any] = dict()
        with self.assertRaises(exporter.InvalidSrc) as cm:
            exporter.export_corosync_totem(corosync_data)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data=corosync_data,
                data_desc="corosync configuration",
                issue_location="",
                issue_desc="Missing key 'totem_options'",
            ),
        )

    def test_minimal(self) -> None:
        corosync_data: Dict[str, Any] = dict(
            totem_options=dict(),
        )
        role_data = exporter.export_corosync_totem(corosync_data)
        self.assertEqual(role_data, dict())

    def test_simple_options_mirroring(self) -> None:
        corosync_data: Dict[str, Any] = dict(
            totem_options=dict(totem1="a", totem2="b"),
        )
        role_data = exporter.export_corosync_totem(corosync_data)
        self.assertEqual(
            role_data,
            dict(
                options=[
                    dict(name="totem1", value="a"),
                    dict(name="totem2", value="b"),
                ],
            ),
        )


class ExportCorosyncQuorum(TestCase):
    maxDiff = None

    def test_missing_key(self) -> None:
        corosync_data: Dict[str, Any] = dict()
        with self.assertRaises(exporter.InvalidSrc) as cm:
            exporter.export_corosync_quorum(corosync_data)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data_desc="corosync configuration",
                data=corosync_data,
                issue_location="",
                issue_desc="Missing key 'quorum_options'",
            ),
        )

    def test_minimal(self) -> None:
        corosync_data: Dict[str, Any] = dict(
            quorum_options=dict(),
        )
        role_data = exporter.export_corosync_quorum(corosync_data)
        self.assertEqual(role_data, dict())

    def test_simple_options_mirroring(self) -> None:
        corosync_data: Dict[str, Any] = dict(
            quorum_options=dict(quorum1="i", quorum2="j"),
        )
        role_data = exporter.export_corosync_quorum(corosync_data)
        self.assertEqual(
            role_data,
            dict(
                options=[
                    dict(name="quorum1", value="i"),
                    dict(name="quorum2", value="j"),
                ],
            ),
        )


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


class ExportPcsPermissionList(TestCase):
    maxDiff = None

    def test_minimal(self) -> None:
        pcs_settings_dict: Dict[str, Any] = {
            "permissions": {
                "local_cluster": [],
            }
        }

        self.assertEqual(
            exporter.export_pcs_permission_list(pcs_settings_dict),
            [],
        )

    def test_success(self) -> None:
        pcs_settings_dict: Dict[str, Any] = {
            "permissions": {
                "local_cluster": [
                    {"name": "test1", "type": "user", "allow": []},
                    {"name": "test2", "type": "user", "allow": ["read"]},
                    {
                        "name": "test3",
                        "type": "group",
                        "allow": ["write", "grant"],
                    },
                ]
            }
        }

        self.assertEqual(
            exporter.export_pcs_permission_list(pcs_settings_dict),
            [
                {"name": "test1", "type": "user", "allow_list": []},
                {"name": "test2", "type": "user", "allow_list": ["read"]},
                {
                    "name": "test3",
                    "type": "group",
                    "allow_list": ["write", "grant"],
                },
            ],
        )

    def assert_missing_key(
        self,
        pcs_settings_dict: Dict[str, Any],
        key: str,
        issue_location: str = "",
    ) -> None:
        with self.assertRaises(exporter.InvalidSrc) as cm:
            exporter.export_pcs_permission_list(pcs_settings_dict)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data_desc="pcs_settings.conf",
                data=pcs_settings_dict,
                issue_location=issue_location,
                issue_desc=f"Missing key '{key}'",
            ),
        )

    def test_raises_when_permissions_not_dict(self) -> None:
        data = dict(permissions="perm1,perm2")
        with self.assertRaises(exporter.InvalidSrc) as cm:
            exporter.export_pcs_permission_list(data)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data_desc="pcs_settings.conf",
                data=data,
                issue_location="/permissions",
                issue_desc=(
                    "Expected dict with key 'local_cluster' but got 'str'"
                ),
            ),
        )

    def test_raises_when_local_cluster_not_list(self) -> None:
        data = dict(permissions=dict(local_cluster=None))
        with self.assertRaises(exporter.InvalidSrc) as cm:
            exporter.export_pcs_permission_list(data)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data_desc="pcs_settings.conf",
                data=data,
                issue_location="/permissions/local_cluster",
                issue_desc=("Expected iterable but got 'NoneType'"),
            ),
        )

    def test_missing_key(self) -> None:
        self.assert_missing_key(
            dict(),
            "permissions",
        )
        self.assert_missing_key(
            dict(permissions=dict()),
            "local_cluster",
            issue_location="/permissions",
        )
        self.assert_missing_key(
            dict(permissions=dict(local_cluster=[dict()])),
            "type",
            issue_location="/permissions/local_cluster/0",
        )
        self.assert_missing_key(
            dict(permissions=dict(local_cluster=[dict(type="user")])),
            "name",
            issue_location="/permissions/local_cluster/0",
        )
        self.assert_missing_key(
            dict(
                permissions=dict(
                    local_cluster=[dict(type="user", name="user1")]
                )
            ),
            "allow",
            issue_location="/permissions/local_cluster/0",
        )
