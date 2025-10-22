# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

from unittest import TestCase

from .fixture_constraints import EMPTY_CONSTRAINTS
from .ha_cluster_info import exporter


class ExportOrderConstraints(TestCase):
    maxDiff = None

    def test_uses_standard_invalid_src_dealing(self) -> None:
        constraints_data = {}  # type: ignore
        with self.assertRaises(exporter.InvalidSrc) as cm:
            exporter.export_order_constraints(constraints_data)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data=constraints_data,
                data_desc="constraints configuration",
                issue_location="",
                issue_desc="Missing key 'order'",
            ),
        )

    def test_empty_order_constraints(self) -> None:
        self.assertEqual(
            [], exporter.export_order_constraints(EMPTY_CONSTRAINTS)
        )

    def test_export_order_constraints_multiple(self) -> None:
        self.assertEqual(
            [
                {
                    "id": "order-simple",
                    "resource_first": {"id": "resource1", "action": "start"},
                    "resource_then": {"id": "resource2", "action": "promote"},
                    "options": [
                        {"name": "score", "value": "50"},
                        {"name": "symmetrical", "value": "true"},
                    ],
                },
                {
                    "id": "order-set-basic",
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
                        {"name": "kind", "value": "Optional"},
                    ],
                },
                {
                    "id": "order-set-full",
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
                        {"name": "symmetrical", "value": "false"},
                        {"name": "require-all", "value": "false"},
                    ],
                },
            ],
            exporter.export_order_constraints(
                {
                    **EMPTY_CONSTRAINTS,
                    "order": [
                        {
                            "first_resource_id": "resource1",
                            "then_resource_id": "resource2",
                            "first_action": "start",
                            "then_action": "promote",
                            "first_resource_instance": None,
                            "then_resource_instance": None,
                            "attributes": {
                                "constraint_id": "order-simple",
                                "symmetrical": True,
                                "require_all": None,
                                "score": "50",
                                "kind": None,
                            },
                        }
                    ],
                    "order_set": [
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
                                "constraint_id": "order-set-basic",
                                "symmetrical": None,
                                "require_all": None,
                                "score": None,
                                "kind": "Optional",
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
                                "constraint_id": "order-set-full",
                                "symmetrical": False,
                                "require_all": False,
                                "score": "INFINITY",
                                "kind": None,
                            },
                        },
                    ],
                }
            ),
        )

    def test_minimal_order_constraint(self) -> None:
        self.assertEqual(
            [
                {
                    "id": "order-minimal",
                    "resource_first": {"id": "resource1"},
                    "resource_then": {"id": "resource2"},
                }
            ],
            exporter.export_order_constraints(
                {
                    **EMPTY_CONSTRAINTS,
                    "order": [
                        {
                            "first_resource_id": "resource1",
                            "then_resource_id": "resource2",
                            "first_action": None,
                            "then_action": None,
                            "first_resource_instance": None,
                            "then_resource_instance": None,
                            "attributes": {
                                "constraint_id": "order-minimal",
                                "symmetrical": None,
                                "require_all": None,
                                "score": None,
                                "kind": None,
                            },
                        }
                    ],
                }
            ),
        )

    def test_no_first_resource_id(self) -> None:
        constraints_data = {  # type: ignore
            **EMPTY_CONSTRAINTS,
            "order": [
                {
                    "first_resource_id": None,
                    "then_resource_id": "resource2",
                    "first_action": "start",
                    "then_action": "start",
                    "first_resource_instance": None,
                    "then_resource_instance": None,
                    "attributes": {
                        "constraint_id": "constraint1",
                        "symmetrical": True,
                        "require_all": None,
                        "score": "50",
                        "kind": None,
                    },
                }
            ],
        }
        with self.assertRaises(exporter.InvalidSrc) as cm:
            exporter.export_order_constraints(constraints_data)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data=constraints_data,
                data_desc="constraints configuration",
                issue_location="/order/0",
                issue_desc="Order is missing first_resource_id",
            ),
        )

    def test_no_then_resource_id(self) -> None:
        constraints_data = {  # type: ignore
            **EMPTY_CONSTRAINTS,
            "order": [
                {
                    "first_resource_id": "resource1",
                    "then_resource_id": None,
                    "first_action": "start",
                    "then_action": "start",
                    "first_resource_instance": None,
                    "then_resource_instance": None,
                    "attributes": {
                        "constraint_id": "constraint1",
                        "symmetrical": True,
                        "require_all": None,
                        "score": "50",
                        "kind": None,
                    },
                }
            ],
        }
        with self.assertRaises(exporter.InvalidSrc) as cm:
            exporter.export_order_constraints(constraints_data)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data=constraints_data,
                data_desc="constraints configuration",
                issue_location="/order/0",
                issue_desc="Order is missing then_resource_id",
            ),
        )

    def test_no_resource_set(self) -> None:
        constraints_data = {  # type: ignore
            **EMPTY_CONSTRAINTS,
            "order_set": [
                {
                    "resource_sets": [],
                    "attributes": {
                        "constraint_id": "constraint1",
                        "symmetrical": True,
                        "require_all": None,
                        "score": None,
                        "kind": None,
                    },
                }
            ],
        }
        with self.assertRaises(exporter.InvalidSrc) as cm:
            exporter.export_order_constraints(constraints_data)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data=constraints_data,
                data_desc="constraints configuration",
                issue_location="/order_set/0",
                issue_desc="Order is missing resource_sets",
            ),
        )

    def test_no_resource_ids(self) -> None:
        constraints_data = {  # type: ignore
            **EMPTY_CONSTRAINTS,
            "order_set": [
                {
                    "resource_sets": [
                        {
                            "set_id": "set-bad",
                            "sequential": None,
                            "require_all": None,
                            "ordering": None,
                            "action": None,
                            "role": None,
                            "score": None,
                            "kind": None,
                            "resources_ids": [],
                        }
                    ],
                    "attributes": {
                        "constraint_id": "constraint1",
                        "symmetrical": True,
                        "require_all": None,
                        "score": None,
                        "kind": None,
                    },
                }
            ],
        }
        with self.assertRaises(exporter.InvalidSrc) as cm:
            exporter.export_order_constraints(constraints_data)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data=constraints_data,
                data_desc="constraints configuration",
                issue_location="/order_set/0/resource_sets/0",
                issue_desc="Resource set without resource_ids",
            ),
        )
