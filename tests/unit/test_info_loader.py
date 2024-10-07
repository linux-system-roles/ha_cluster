# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import json
import sys
from importlib import import_module
from unittest import TestCase, mock

sys.modules["ansible.module_utils.ha_cluster_lsr"] = import_module(
    "ha_cluster_lsr"
)

from ha_cluster_lsr.info import loader


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
