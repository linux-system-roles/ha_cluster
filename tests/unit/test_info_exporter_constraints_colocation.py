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
                        "role": "Promoted",
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
                {
                    "id": "colocation-set-basic",
                    "resource_sets": [
                        {
                            "resource_ids": ["resource1", "resource2"],
                        },
                        {
                            "resource_ids": ["resource3", "resource4"],
                            "options": [
                                {"name": "role", "value": "Started"},
                                {"name": "sequential", "value": "false"},
                            ],
                        },
                    ],
                    "options": [
                        {"name": "score", "value": "10"},
                    ],
                },
                {
                    "id": "colocation-set-full",
                    "resource_sets": [
                        {
                            "resource_ids": ["resource1", "resource2"],
                            "options": [
                                {"name": "ordering", "value": "group"},
                                {"name": "action", "value": "start"},
                                {"name": "role", "value": "Promoted"},
                                {"name": "score", "value": "100"},
                                {"name": "kind", "value": "Optional"},
                                {"name": "sequential", "value": "true"},
                                {"name": "require-all", "value": "false"},
                            ],
                        },
                    ],
                    "options": [
                        {"name": "score", "value": "INFINITY"},
                        {"name": "influence", "value": "demote"},
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
                            "resource_role": "Promoted",
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
                    "colocation_set": [
                        {
                            "resource_sets": [
                                {
                                    "set_id": "set-basic",
                                    "sequential": None,
                                    "require_all": None,
                                    "ordering": None,
                                    "action": None,
                                    "role": None,
                                    "score": None,
                                    "kind": None,
                                    "resources_ids": ["resource1", "resource2"],
                                },
                                {
                                    "set_id": "set-basic-2",
                                    "sequential": False,
                                    "require_all": None,
                                    "ordering": None,
                                    "action": None,
                                    "role": "Started",
                                    "score": None,
                                    "kind": None,
                                    "resources_ids": ["resource3", "resource4"],
                                },
                            ],
                            "attributes": {
                                "constraint_id": "colocation-set-basic",
                                "score": "10",
                                "influence": None,
                                "lifetime": [],
                            },
                        },
                        {
                            "resource_sets": [
                                {
                                    "set_id": "set-full",
                                    "sequential": True,
                                    "require_all": False,
                                    "ordering": "group",
                                    "action": "start",
                                    "role": "Promoted",
                                    "score": "100",
                                    "kind": "Optional",
                                    "resources_ids": ["resource1", "resource2"],
                                },
                            ],
                            "attributes": {
                                "constraint_id": "colocation-set-full",
                                "score": "INFINITY",
                                "influence": "demote",
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
                        "constraint_id": "constraint1",
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
                        "constraint_id": "constraint1",
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

    def test_no_resource_set(self) -> None:
        constraints_data = {  # type: ignore
            **EMPTY_CONSTRAINTS,
            "colocation_set": [
                {
                    "resource_sets": [],
                    "attributes": {
                        "constraint_id": "constraint1",
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
                issue_location="/colocation_set/0",
                issue_desc="Colocation is missing resource_sets",
            ),
        )
