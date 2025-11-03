# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

from unittest import TestCase

from .fixture_constraints import EMPTY_CONSTRAINTS
from .ha_cluster_info import exporter


class ExportLocationConstraintsLocation(TestCase):
    maxDiff = None

    def test_uses_standard_invalid_src_dealing(self) -> None:
        constraints_data = {}  # type: ignore
        with self.assertRaises(exporter.InvalidSrc) as cm:
            exporter.export_location_constraints(constraints_data)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data=constraints_data,
                data_desc="constraints configuration",
                issue_location="",
                issue_desc="Missing key 'location'",
            ),
        )

    def test_empty_location_constraints(self) -> None:
        self.assertEqual(
            [], exporter.export_location_constraints(EMPTY_CONSTRAINTS)
        )

    def test_export_location_constraints_multiple_ignore_set(self) -> None:
        self.assertEqual(
            [
                {
                    "resource": {"id": "resource1"},
                    "node": "node1",
                    "id": "location-resource1-INFINITY",
                },
                {
                    "resource": {"id": "resource2", "role": "Started"},
                    "node": "node2",
                    "id": "location-resource2-node2-50",
                    "options": [
                        {"name": "resource-discovery", "value": "never"},
                        {"name": "score", "value": "50"},
                    ],
                },
            ],
            exporter.export_location_constraints(
                {
                    **EMPTY_CONSTRAINTS,
                    "location": [
                        {
                            "resource_id": "resource1",
                            "resource_pattern": None,
                            "role": None,
                            "attributes": {
                                "constraint_id": "location-resource1-INFINITY",
                                "score": None,
                                "node": "node1",
                                "rules": [],
                                "lifetime": [],
                                "resource_discovery": None,
                            },
                        },
                        {
                            "resource_id": "resource2",
                            "resource_pattern": None,
                            "role": "Started",
                            "attributes": {
                                "constraint_id": "location-resource2-node2-50",
                                "score": "50",
                                "node": "node2",
                                "rules": [],
                                "lifetime": [],
                                "resource_discovery": "never",
                            },
                        },
                    ],
                    "location_set": [
                        {
                            "resource_sets": [
                                {
                                    "id": "location-set-resource-set-0",
                                    "resources": ["resource1", "resource2"],
                                    "options": {},
                                }
                            ],
                            "attributes": {
                                "constraint_id": "location-resource2-node2-50",
                                "score": "50",
                                "node": "node2",
                                "rules": [],
                                "lifetime": [],
                                "resource_discovery": None,
                            },
                        }
                    ],
                }
            ),
        )

    def test_export_location_constraints_with_rule(self) -> None:
        self.assertEqual(
            [
                {
                    "resource": {
                        "id": "resource1",
                        "role": "Promoted",
                    },
                    "id": "location-resource1-INFINITY",
                    # Only one rule is supported in the ha_cluster role.
                    # So just the first rule is exported.
                    "rule": "#uname eq node1",
                    "options": [
                        {"name": "score", "value": "INFINITY"},
                    ],
                },
                {
                    "resource": {
                        "id": "resource2",
                    },
                    "id": "location-resource2-INFINITY",
                    # Only one rule is supported in the ha_cluster role.
                    # So just the first rule is exported.
                    "rule": "#uname eq node1",
                    "options": [
                        {"name": "score-attribute", "value": "some-attr"},
                    ],
                },
            ],
            exporter.export_location_constraints(
                {
                    **EMPTY_CONSTRAINTS,
                    "location": [
                        {
                            "resource_id": "resource1",
                            "resource_pattern": None,
                            "role": None,
                            "attributes": {
                                "constraint_id": "location-resource1-INFINITY",
                                "score": None,
                                "node": None,
                                "rules": [
                                    {
                                        "id": "location-resource1-rule-rule",
                                        "as_string": "#uname eq node1",
                                        "options": {
                                            "role": "Promoted",
                                            "score": "INFINITY",
                                        },
                                    },
                                    {
                                        "id": "location-resource1-rule-rule2",
                                        "as_string": "#uname eq node2",
                                        "options": {},
                                    },
                                ],
                                "lifetime": [],
                                "resource_discovery": None,
                            },
                        },
                        {
                            "resource_id": "resource2",
                            "resource_pattern": None,
                            "role": None,
                            "attributes": {
                                "constraint_id": "location-resource2-INFINITY",
                                "score": None,
                                "node": None,
                                "rules": [
                                    {
                                        "id": "location-resource2-rule-rule",
                                        "as_string": "#uname eq node1",
                                        "options": {
                                            "score-attribute": "some-attr",
                                        },
                                    },
                                ],
                                "lifetime": [],
                                "resource_discovery": None,
                            },
                        },
                    ],
                }
            ),
        )

    def test_no_node_no_rule(self) -> None:
        constraints_data = {  # type: ignore
            **EMPTY_CONSTRAINTS,
            "location": [
                {
                    "resource_id": "resource1",
                    "resource_pattern": None,
                    "role": None,
                    "attributes": {
                        "constraint_id": "location-resource1-INFINITY",
                        "score": "INFINITY",
                        "node": None,
                        "rules": [],
                        "lifetime": [],
                        "resource_discovery": None,
                    },
                }
            ],
        }
        with self.assertRaises(exporter.InvalidSrc) as cm:
            exporter.export_location_constraints(constraints_data)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data=constraints_data,
                data_desc="constraints configuration",
                issue_location="/location/0",
                issue_desc="Location constraint has neither node nor rule",
            ),
        )

    def test_both_node_and_rule(self) -> None:
        constraints_data = {  # type: ignore
            **EMPTY_CONSTRAINTS,
            "location": [
                {
                    "resource_id": "resource1",
                    "resource_pattern": None,
                    "role": None,
                    "attributes": {
                        "constraint_id": "location-resource1-INFINITY",
                        "score": "INFINITY",
                        "node": "node1",
                        "rules": [
                            {
                                "id": "location-resource1-rule-rule",
                                "as_string": "#uname eq node1",
                                "options": {},
                            }
                        ],
                        "lifetime": [],
                        "resource_discovery": None,
                    },
                }
            ],
        }
        with self.assertRaises(exporter.InvalidSrc) as cm:
            exporter.export_location_constraints(constraints_data)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data=constraints_data,
                data_desc="constraints configuration",
                issue_location="/location/0",
                issue_desc="Location constraint has both node and rule",
            ),
        )

    def test_no_resource_no_pattern(self) -> None:
        constraints_data = {  # type: ignore
            **EMPTY_CONSTRAINTS,
            "location": [
                {
                    "resource_id": "x",
                    "resource_pattern": "y",
                    "role": None,
                    "attributes": {
                        "constraint_id": "location-resource1-INFINITY",
                        "score": "INFINITY",
                        "node": "node1",
                        "rules": [],
                        "lifetime": [],
                        "resource_discovery": None,
                    },
                }
            ],
        }
        with self.assertRaises(exporter.InvalidSrc) as cm:
            exporter.export_location_constraints(constraints_data)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data=constraints_data,
                data_desc="constraints configuration",
                issue_location="/location/0",
                issue_desc="Location constraint has both resource_id and resource_pattern",
            ),
        )

    def test_both_resource_and_pattern(self) -> None:
        constraints_data = {  # type: ignore
            **EMPTY_CONSTRAINTS,
            "location": [
                {
                    "resource_id": None,
                    "resource_pattern": None,
                    "role": None,
                    "attributes": {
                        "constraint_id": "location-resource1-INFINITY",
                        "score": "INFINITY",
                        "node": "node1",
                        "rules": [],
                        "lifetime": [],
                        "resource_discovery": None,
                    },
                }
            ],
        }
        with self.assertRaises(exporter.InvalidSrc) as cm:
            exporter.export_location_constraints(constraints_data)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data=constraints_data,
                data_desc="constraints configuration",
                issue_location="/location/0",
                issue_desc="Location constraint has neither resource_id nor resource_pattern",
            ),
        )
