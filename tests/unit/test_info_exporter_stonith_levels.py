# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# SPDX-License-Identifier: MIT

# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

from unittest import TestCase

from .fixture_stonith_levels import EMPTY_STONITH_LEVELS
from .ha_cluster_info import exporter


class ExportStonithLevels(TestCase):
    maxDiff = None

    def test_uses_standard_invalid_src_dealing(self) -> None:
        stonith_levels_data = {}  # type: ignore
        with self.assertRaises(exporter.InvalidSrc) as cm:
            exporter.export_stonith_levels(stonith_levels_data)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data=stonith_levels_data,
                data_desc="stonith levels configuration",
                issue_location="",
                issue_desc="Missing key 'target_node'",
            ),
        )

    def test_empty_stonith_levels(self) -> None:
        self.assertEqual(
            [], exporter.export_stonith_levels(EMPTY_STONITH_LEVELS)
        )

    def test_export_target_node_single(self) -> None:
        self.assertEqual(
            [
                {
                    "level": 1,
                    "target": "node1",
                    "resource_ids": ["fence_xvm1"],
                },
            ],
            exporter.export_stonith_levels(
                {
                    **EMPTY_STONITH_LEVELS,
                    "target_node": [
                        {
                            "id": "fl-node1-1",
                            "target": "node1",
                            "index": 1,
                            "devices": ["fence_xvm1"],
                        },
                    ],
                }
            ),
        )

    def test_export_target_node_multiple(self) -> None:
        self.assertEqual(
            [
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
                    "target": "node2",
                    "resource_ids": ["fence_xvm1"],
                },
            ],
            exporter.export_stonith_levels(
                {
                    **EMPTY_STONITH_LEVELS,
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
                        {
                            "id": "fl-node2-1",
                            "target": "node2",
                            "index": 1,
                            "devices": ["fence_xvm1"],
                        },
                    ],
                }
            ),
        )

    def test_export_target_regex(self) -> None:
        self.assertEqual(
            [
                {
                    "level": 1,
                    "target_pattern": "node-.*",
                    "resource_ids": ["fence_xvm1"],
                },
                {
                    "level": 2,
                    "target_pattern": "node-.*",
                    "resource_ids": ["fence_kdump"],
                },
            ],
            exporter.export_stonith_levels(
                {
                    **EMPTY_STONITH_LEVELS,
                    "target_regex": [
                        {
                            "id": "fl-regex-1",
                            "target_pattern": "node-.*",
                            "index": 1,
                            "devices": ["fence_xvm1"],
                        },
                        {
                            "id": "fl-regex-2",
                            "target_pattern": "node-.*",
                            "index": 2,
                            "devices": ["fence_kdump"],
                        },
                    ],
                }
            ),
        )

    def test_export_target_attribute(self) -> None:
        self.assertEqual(
            [
                {
                    "level": 1,
                    "target_attribute": "rack",
                    "target_value": "1",
                    "resource_ids": ["fence_xvm1"],
                },
            ],
            exporter.export_stonith_levels(
                {
                    **EMPTY_STONITH_LEVELS,
                    "target_attribute": [
                        {
                            "id": "fl-attr-1",
                            "target_attribute": "rack",
                            "target_value": "1",
                            "index": 1,
                            "devices": ["fence_xvm1"],
                        },
                    ],
                }
            ),
        )

    def test_export_target_attribute_empty_value(self) -> None:
        self.assertEqual(
            [
                {
                    "level": 1,
                    "target_attribute": "rack",
                    "resource_ids": ["fence_xvm1"],
                },
            ],
            exporter.export_stonith_levels(
                {
                    **EMPTY_STONITH_LEVELS,
                    "target_attribute": [
                        {
                            "id": "fl-attr-1",
                            "target_attribute": "rack",
                            "target_value": "",
                            "index": 1,
                            "devices": ["fence_xvm1"],
                        },
                    ],
                }
            ),
        )

    def test_export_mixed(self) -> None:
        self.assertEqual(
            [
                {
                    "level": 1,
                    "target": "node1",
                    "resource_ids": ["fence_xvm1"],
                },
                {
                    "level": 1,
                    "target_pattern": "node-.*",
                    "resource_ids": ["fence_xvm2"],
                },
                {
                    "level": 1,
                    "target_attribute": "rack",
                    "target_value": "1",
                    "resource_ids": ["fence_kdump"],
                },
            ],
            exporter.export_stonith_levels(
                {
                    "target_node": [
                        {
                            "id": "fl-node1-1",
                            "target": "node1",
                            "index": 1,
                            "devices": ["fence_xvm1"],
                        },
                    ],
                    "target_regex": [
                        {
                            "id": "fl-regex-1",
                            "target_pattern": "node-.*",
                            "index": 1,
                            "devices": ["fence_xvm2"],
                        },
                    ],
                    "target_attribute": [
                        {
                            "id": "fl-attr-1",
                            "target_attribute": "rack",
                            "target_value": "1",
                            "index": 1,
                            "devices": ["fence_kdump"],
                        },
                    ],
                }
            ),
        )
