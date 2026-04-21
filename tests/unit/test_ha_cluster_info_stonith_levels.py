# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# SPDX-License-Identifier: MIT

# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import json
from unittest import TestCase, mock

from .fixture_stonith_levels import EMPTY_STONITH_LEVELS
from .ha_cluster_info import ha_cluster_info, mocked_module

CMD_OPTIONS = dict(environ_update={"LC_ALL": "C"}, check_rc=False)
PCS_CMD = ["pcs", "stonith", "level", "config", "--output-format=json"]
CMD_STONITH_LEVELS_CONF = mock.call(PCS_CMD, **CMD_OPTIONS)


class ExportStonithLevelsConfiguration(TestCase):
    maxDiff = None

    def test_success(self) -> None:
        stonith_levels_data = {
            "target_node": [
                {
                    "id": "fl-node1-1",
                    "target": "node1",
                    "index": 1,
                    "devices": ["fence_xvm1", "fence_xvm2"],
                },
                {
                    "id": "fl-node1-2",
                    "target": "node1",
                    "index": 2,
                    "devices": ["fence_kdump"],
                },
            ],
            "target_regex": [
                {
                    "id": "fl-regex-1",
                    "target_pattern": "node-.*",
                    "index": 1,
                    "devices": ["fence_xvm3"],
                },
            ],
            "target_attribute": [
                {
                    "id": "fl-attr-1",
                    "target_attribute": "rack",
                    "target_value": "1",
                    "index": 1,
                    "devices": ["fence_xvm4"],
                },
            ],
        }
        with mocked_module(
            [
                (
                    CMD_STONITH_LEVELS_CONF,
                    (0, json.dumps(stonith_levels_data), ""),
                ),
            ]
        ) as module_mock:
            self.assertEqual(
                ha_cluster_info.export_stonith_levels_configuration(
                    module_mock,
                    [
                        ha_cluster_info.Capability.STONITH_LEVELS_OUTPUT.value,
                    ],
                ),
                {
                    "ha_cluster_stonith_levels": [
                        {
                            "level": 1,
                            "target": "node1",
                            "resource_ids": ["fence_xvm1", "fence_xvm2"],
                        },
                        {
                            "level": 2,
                            "target": "node1",
                            "resource_ids": ["fence_kdump"],
                        },
                        {
                            "level": 1,
                            "target_pattern": "node-.*",
                            "resource_ids": ["fence_xvm3"],
                        },
                        {
                            "level": 1,
                            "target_attribute": "rack",
                            "target_value": "1",
                            "resource_ids": ["fence_xvm4"],
                        },
                    ],
                },
            )

    def test_success_empty(self) -> None:
        with mocked_module(
            [
                (
                    CMD_STONITH_LEVELS_CONF,
                    (0, json.dumps(EMPTY_STONITH_LEVELS), ""),
                ),
            ]
        ) as module_mock:
            self.assertEqual(
                ha_cluster_info.export_stonith_levels_configuration(
                    module_mock,
                    [
                        ha_cluster_info.Capability.STONITH_LEVELS_OUTPUT.value,
                    ],
                ),
                {},
            )

    def test_no_capabilities(self) -> None:
        with mocked_module([]) as module_mock:
            self.assertEqual(
                ha_cluster_info.export_stonith_levels_configuration(
                    module_mock, pcs_capabilities=[]
                ),
                {},
            )

    def test_pcs_cmd_fail(self) -> None:
        with self.assertRaises(ha_cluster_info.loader.CliCommandError) as cm:
            with mocked_module(
                [(CMD_STONITH_LEVELS_CONF, (1, "", "Error"))]
            ) as module_mock:
                ha_cluster_info.export_stonith_levels_configuration(
                    module_mock,
                    [
                        ha_cluster_info.Capability.STONITH_LEVELS_OUTPUT.value,
                    ],
                )
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                pcs_command=PCS_CMD,
                stdout="",
                stderr="Error",
                rc=1,
            ),
        )
