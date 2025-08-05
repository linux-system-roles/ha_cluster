# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import json
import os.path
from unittest import TestCase, mock

from .ha_cluster_info import ha_cluster_info, mocked_module

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

CMD_OPTIONS = dict(environ_update={"LC_ALL": "C"}, check_rc=False)
CMD_RESOURCE_CONF = mock.call(
    ["pcs", "resource", "config", "--output-format=json"], **CMD_OPTIONS
)
CMD_STONITH_CONF = mock.call(
    ["pcs", "stonith", "config", "--output-format=json"], **CMD_OPTIONS
)

FIXTURE_CAPABILITIES = ["pcmk.resource.config.output-formats"]


class ExportResourcesConfiguration(TestCase):
    maxDiff = None

    def test_max_features(self) -> None:
        def read_file(fname: str) -> str:
            with open(os.path.join(CURRENT_DIR, fname), encoding="utf-8") as f:
                return f.read()

        with mocked_module(
            [
                (CMD_RESOURCE_CONF, (0, read_file("resources.json"), "")),
                (CMD_STONITH_CONF, (0, read_file("stonith.json"), "")),
            ]
        ) as module_mock:
            self.assertEqual(
                ha_cluster_info.export_resources_configuration(
                    module_mock, FIXTURE_CAPABILITIES
                ),
                json.loads(read_file("resources-export.json")),
            )

    def test_no_capabilities(self) -> None:
        with mocked_module([]) as module_mock:
            self.assertEqual(
                ha_cluster_info.export_resources_configuration(
                    module_mock, pcs_capabilities=[]
                ),
                {},
            )

    def test_pcs_cmd_fail(self) -> None:
        with self.assertRaises(ha_cluster_info.loader.CliCommandError) as cm:
            with mocked_module(
                [(CMD_RESOURCE_CONF, (1, "", "Error"))]
            ) as module_mock:
                ha_cluster_info.export_resources_configuration(
                    module_mock, FIXTURE_CAPABILITIES
                )
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                pcs_command=[
                    "pcs",
                    "resource",
                    "config",
                    "--output-format=json",
                ],
                stdout="",
                stderr="Error",
                rc=1,
            ),
        )
