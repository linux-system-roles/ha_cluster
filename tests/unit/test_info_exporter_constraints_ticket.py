# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

from unittest import TestCase

from .fixture_constraints import EMPTY_CONSTRAINTS
from .ha_cluster_info import exporter


class ExportTicketConstraints(TestCase):
    maxDiff = None

    def test_uses_standard_invalid_src_dealing(self) -> None:
        constraints_data = {}  # type: ignore
        with self.assertRaises(exporter.InvalidSrc) as cm:
            exporter.export_ticket_constraints(constraints_data)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data=constraints_data,
                data_desc="constraints configuration",
                issue_location="",
                issue_desc="Missing key 'ticket'",
            ),
        )

    def test_empty_ticket_constraints(self) -> None:
        self.assertEqual(
            [], exporter.export_ticket_constraints(EMPTY_CONSTRAINTS)
        )

    def test_export_ticket_constraints_multiple(self) -> None:
        self.assertEqual(
            [
                {
                    "id": "ticket-simple",
                    "resource": {"id": "resource1", "role": "Promoted"},
                    "ticket": "ticket1",
                    "options": [
                        {"name": "loss-policy", "value": "stop"},
                    ],
                },
                {
                    "id": "ticket-set-basic",
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
                    "ticket": "ticket2",
                    "options": [
                        {"name": "loss-policy", "value": "fence"},
                    ],
                },
                {
                    "id": "ticket-set-full",
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
                    "ticket": "ticket3",
                },
            ],
            exporter.export_ticket_constraints(
                {
                    **EMPTY_CONSTRAINTS,
                    "ticket": [
                        {
                            "resource_id": "resource1",
                            "role": "Promoted",
                            "attributes": {
                                "constraint_id": "ticket-simple",
                                "ticket": "ticket1",
                                "loss_policy": "stop",
                            },
                        }
                    ],
                    "ticket_set": [
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
                                "constraint_id": "ticket-set-basic",
                                "ticket": "ticket2",
                                "loss_policy": "fence",
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
                                "constraint_id": "ticket-set-full",
                                "ticket": "ticket3",
                                "loss_policy": None,
                            },
                        },
                    ],
                }
            ),
        )

    def test_minimal_ticket_constraint(self) -> None:
        self.assertEqual(
            [
                {
                    "id": "ticket-minimal",
                    "resource": {"id": "resource1"},
                    "ticket": "ticket1",
                }
            ],
            exporter.export_ticket_constraints(
                {
                    **EMPTY_CONSTRAINTS,
                    "ticket": [
                        {
                            "resource_id": "resource1",
                            "role": None,
                            "attributes": {
                                "constraint_id": "ticket-minimal",
                                "ticket": "ticket1",
                                "loss_policy": None,
                            },
                        }
                    ],
                }
            ),
        )

    def test_no_resource_id(self) -> None:
        constraints_data = {  # type: ignore
            **EMPTY_CONSTRAINTS,
            "ticket": [
                {
                    "resource_id": None,
                    "role": None,
                    "attributes": {
                        "constraint_id": "constraint1",
                        "ticket": "ticket1",
                        "loss_policy": "stop",
                    },
                }
            ],
        }
        with self.assertRaises(exporter.InvalidSrc) as cm:
            exporter.export_ticket_constraints(constraints_data)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data=constraints_data,
                data_desc="constraints configuration",
                issue_location="/ticket/0",
                issue_desc="Ticket is missing resource_id",
            ),
        )

    def test_no_ticket_name(self) -> None:
        constraints_data = {  # type: ignore
            **EMPTY_CONSTRAINTS,
            "ticket": [
                {
                    "resource_id": "resource1",
                    "role": None,
                    "attributes": {
                        "constraint_id": "constraint1",
                        "ticket": None,
                        "loss_policy": "stop",
                    },
                }
            ],
        }
        with self.assertRaises(exporter.InvalidSrc) as cm:
            exporter.export_ticket_constraints(constraints_data)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data=constraints_data,
                data_desc="constraints configuration",
                issue_location="/ticket/0",
                issue_desc="Ticket constraint is missing ticket attribute",
            ),
        )

    def test_no_resource_set(self) -> None:
        constraints_data = {  # type: ignore
            **EMPTY_CONSTRAINTS,
            "ticket_set": [
                {
                    "resource_sets": [],
                    "attributes": {
                        "constraint_id": "constraint1",
                        "ticket": "ticket1",
                        "loss_policy": "stop",
                    },
                }
            ],
        }
        with self.assertRaises(exporter.InvalidSrc) as cm:
            exporter.export_ticket_constraints(constraints_data)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data=constraints_data,
                data_desc="constraints configuration",
                issue_location="/ticket_set/0",
                issue_desc="Ticket is missing resource_sets",
            ),
        )

    def test_no_ticket_name_in_set(self) -> None:
        constraints_data = {  # type: ignore
            **EMPTY_CONSTRAINTS,
            "ticket_set": [
                {
                    "resource_sets": [
                        {
                            "set_id": "set-test",
                            "sequential": None,
                            "require_all": None,
                            "ordering": None,
                            "action": None,
                            "role": None,
                            "score": None,
                            "kind": None,
                            "resources_ids": ["resource1"],
                        }
                    ],
                    "attributes": {
                        "constraint_id": "constraint1",
                        "ticket": None,
                        "loss_policy": "stop",
                    },
                }
            ],
        }
        with self.assertRaises(exporter.InvalidSrc) as cm:
            exporter.export_ticket_constraints(constraints_data)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data=constraints_data,
                data_desc="constraints configuration",
                issue_location="/ticket_set/0",
                issue_desc="Ticket constraint is missing ticket attribute",
            ),
        )

    def test_no_resource_ids(self) -> None:
        constraints_data = {  # type: ignore
            **EMPTY_CONSTRAINTS,
            "ticket_set": [
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
                        "ticket": "ticket1",
                        "loss_policy": "stop",
                    },
                }
            ],
        }
        with self.assertRaises(exporter.InvalidSrc) as cm:
            exporter.export_ticket_constraints(constraints_data)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data=constraints_data,
                data_desc="constraints configuration",
                issue_location="/ticket_set/0/resource_sets/0",
                issue_desc="Resource set without resource_ids",
            ),
        )
