# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

from unittest import TestCase

from .fixture_constraints import EMPTY_CONSTRAINTS
from .ha_cluster_info import exporter


class ExportColocationConstraints(TestCase):
    maxDiff = None

    def test_uses_standard_invalid_src_dealing(self) -> None:
        constraints_data = {}  # type: ignore
        with self.assertRaises(exporter.InvalidSrc) as cm:
            exporter.export_colocation_constraints(constraints_data)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data=constraints_data,
                data_desc="constraints configuration",
                issue_location="",
                issue_desc="Missing key 'colocation'",
            ),
        )

    def test_empty_colocation_constraints(self) -> None:
        self.assertEqual(
            [], exporter.export_colocation_constraints(EMPTY_CONSTRAINTS)
        )

    def test_export_colocation_constraints_multiple(self) -> None:
        self.assertEqual(
            [
                {
                    "id": "colocation-resource1-resource2-100",
                    "resource_leader": {"id": "resource1"},
                    "resource_follower": {"id": "resource2"},
                    "options": [
                        {"name": "score", "value": "100"},
                    ],
                },
                {
                    "id": "colocation-resource3-resource4--50",
                    "resource_leader": {
                        "id": "resource3",
                        "role": "Master",
                    },
                    "resource_follower": {
                        "id": "resource4",
                        "role": "Started",
                    },
                    "options": [
                        {"name": "score", "value": "-50"},
                        {"name": "influence", "value": "stop"},
                    ],
                },
            ],
            exporter.export_colocation_constraints(
                {
                    **EMPTY_CONSTRAINTS,
                    "colocation": [
                        {
                            "resource_id": "resource1",
                            "with_resource_id": "resource2",
                            "resource_role": None,
                            "resource_instance": None,
                            "with_resource_role": None,
                            "with_resource_instance": None,
                            "node_attribute": None,
                            "attributes": {
                                "constraint_id": "colocation-resource1-resource2-100",
                                "score": "100",
                                "influence": None,
                                "lifetime": [],
                            },
                        },
                        {
                            "resource_id": "resource3",
                            "with_resource_id": "resource4",
                            "node_attribute": None,
                            "resource_role": "Master",
                            "with_resource_role": "Started",
                            "resource_instance": None,
                            "with_resource_instance": None,
                            "attributes": {
                                "constraint_id": "colocation-resource3-resource4--50",
                                "score": "-50",
                                "influence": "stop",
                                "lifetime": [],
                            },
                        },
                    ],
                }
            ),
        )

    def test_no_resource_id(self) -> None:
        constraints_data = {  # type: ignore
            **EMPTY_CONSTRAINTS,
            "colocation": [
                {
                    "resource_id": None,
                    "with_resource_id": "resource2",
                    "node_attribute": None,
                    "resource_role": None,
                    "with_resource_role": None,
                    "resource_instance": None,
                    "with_resource_instance": None,
                    "attributes": {
                        "constraint_id": "colocation-resource1-resource2-80",
                        "score": "80",
                        "influence": None,
                        "lifetime": [],
                    },
                }
            ],
        }
        with self.assertRaises(exporter.InvalidSrc) as cm:
            exporter.export_colocation_constraints(constraints_data)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data=constraints_data,
                data_desc="constraints configuration",
                issue_location="/colocation/0",
                issue_desc="Colocation is missing resource_id",
            ),
        )

    def test_no_with_resource_id(self) -> None:
        constraints_data = {  # type: ignore
            **EMPTY_CONSTRAINTS,
            "colocation": [
                {
                    "resource_id": "resource1",
                    "with_resource_id": None,
                    "node_attribute": None,
                    "resource_role": None,
                    "with_resource_role": None,
                    "resource_instance": None,
                    "with_resource_instance": None,
                    "attributes": {
                        "constraint_id": "colocation-resource1-resource2-80",
                        "score": "80",
                        "influence": None,
                        "lifetime": [],
                    },
                }
            ],
        }
        with self.assertRaises(exporter.InvalidSrc) as cm:
            exporter.export_colocation_constraints(constraints_data)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data=constraints_data,
                data_desc="constraints configuration",
                issue_location="/colocation/0",
                issue_desc="Colocation is missing with_resource_id",
            ),
        )
