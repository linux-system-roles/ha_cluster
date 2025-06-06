# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

from unittest import TestCase, mock

from .ha_cluster_info import ha_cluster_info, loader, mocked_module

CMD_OPTIONS = dict(environ_update={"LC_ALL": "C"}, check_rc=False)
PCS_CMD_VERSION = ["pcs", "--version", "--full"]
CMD_VERSION = mock.call(PCS_CMD_VERSION, **CMD_OPTIONS)


class GetPcsCapabilities(TestCase):
    def test_success(self) -> None:
        capabilities = [
            "pcmk.resource.config.output-formats",
            "pcmk.resource.refresh",
        ]
        with mocked_module(
            [
                (
                    CMD_VERSION,
                    (0, "\n".join(["0.12.0", " ".join(capabilities)]), ""),
                )
            ]
        ) as module_mock:
            self.assertEqual(
                ha_cluster_info.get_pcs_capabilities(module_mock),
                capabilities,
            )

    def test_raises_on_cmd_fail(self) -> None:
        with self.assertRaises(loader.CliCommandError) as cm:
            with mocked_module([(CMD_VERSION, (1, "", ""))]) as module_mock:
                ha_cluster_info.get_pcs_capabilities(module_mock)
        self.assertEqual(
            cm.exception.kwargs,
            dict(pcs_command=PCS_CMD_VERSION, rc=1, stdout="", stderr=""),
        )

    def test_no_capabilities_on_only_version(self) -> None:
        with mocked_module([(CMD_VERSION, (0, "0.12.0", ""))]) as module_mock:
            self.assertEqual(
                ha_cluster_info.get_pcs_capabilities(module_mock),
                [],
            )
