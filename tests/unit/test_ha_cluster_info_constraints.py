# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import json
from unittest import TestCase, mock

from .fixture_constraints import EMPTY_CONSTRAINTS
from .ha_cluster_info import ha_cluster_info, mocked_module

CMD_OPTIONS = dict(environ_update={"LC_ALL": "C"}, check_rc=False)
PCS_CMD = ["pcs", "constraint", "--all", "--output-format=json"]
CMD_CONSTRAINTS_CONF = mock.call(PCS_CMD, **CMD_OPTIONS)


class ExportConstraintsConfiguration(TestCase):
    maxDiff = None

    def test_success(self) -> None:
        constraints_data = {
            **EMPTY_CONSTRAINTS,
            "location": [
                {
                    "resource_id": "resource1",
                    "resource_pattern": None,
                    "role": None,
                    "attributes": {
                        "constraint_id": "location-resource1-node1-INFINITY",
                        "node": "node1",
                        "score": "INFINITY",
                        "rules": [],
                        "lifetime": [],
                        "resource_discovery": None,
                    },
                }
            ],
            "colocation": [
                {
                    "resource_id": "resource1",
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
            "colocation_set": [
                {
                    "resource_sets": [
                        {
                            "set_id": "colocation-set-mixed-set",
                            "sequential": None,
                            "require_all": None,
                            "ordering": None,
                            "action": None,
                            "role": None,
                            "score": None,
                            "kind": None,
                            "resources_ids": ["resource3", "resource4"],
                        },
                    ],
                    "attributes": {
                        "constraint_id": "colocation-set-mixed",
                        "score": "15",
                        "influence": None,
                        "lifetime": [],
                    },
                }
            ],
            "order": [
                {
                    "first_resource_id": "resource5",
                    "then_resource_id": "resource6",
                    "first_action": "start",
                    "then_action": "start",
                    "first_resource_instance": None,
                    "then_resource_instance": None,
                    "attributes": {
                        "constraint_id": "order-resource5-resource6-100",
                        "symmetrical": False,
                        "require_all": None,
                        "score": "100",
                        "kind": None,
                    },
                }
            ],
            "order_set": [
                {
                    "resource_sets": [
                        {
                            "set_id": "order-set-resource",
                            "sequential": None,
                            "require_all": None,
                            "ordering": None,
                            "action": None,
                            "role": None,
                            "score": None,
                            "kind": None,
                            "resources_ids": ["resource1", "resource2"],
                        },
                    ],
                    "attributes": {
                        "constraint_id": "order-set",
                        "symmetrical": None,
                        "require_all": None,
                        "score": None,
                        "kind": "Optional",
                    },
                },
            ],
            "ticket": [
                {
                    "resource_id": "resource7",
                    "role": None,
                    "attributes": {
                        "constraint_id": "ticket-resource7-ticket1",
                        "ticket": "ticket1",
                        "loss_policy": "demote",
                    },
                }
            ],
            "ticket_set": [
                {
                    "resource_sets": [
                        {
                            "set_id": "ticket-set-resource",
                            "sequential": None,
                            "require_all": None,
                            "ordering": None,
                            "action": None,
                            "role": None,
                            "score": None,
                            "kind": None,
                            "resources_ids": ["resource1", "resource2"],
                        },
                    ],
                    "attributes": {
                        "constraint_id": "ticket-set",
                        "ticket": "ticket2",
                        "loss_policy": "fence",
                    },
                },
            ],
        }
        with mocked_module(
            [
                (
                    CMD_CONSTRAINTS_CONF,
                    (0, json.dumps(constraints_data), ""),
                ),
            ]
        ) as module_mock:
            self.assertEqual(
                ha_cluster_info.export_constraints_configuration(
                    module_mock,
                    [ha_cluster_info.Capability.CONSTRAINTS_OUTPUT.value],
                ),
                {
                    "ha_cluster_constraints_location": [
                        {
                            "id": "location-resource1-node1-INFINITY",
                            "resource": {"id": "resource1"},
                            "node": "node1",
                            "options": [
                                {
                                    "name": "score",
                                    "value": "INFINITY",
                                }
                            ],
                        }
                    ],
                    "ha_cluster_constraints_colocation": [
                        {
                            "id": "colocation-resource1-resource2-80",
                            "resource_leader": {"id": "resource1"},
                            "resource_follower": {"id": "resource2"},
                            "options": [
                                {
                                    "name": "score",
                                    "value": "80",
                                }
                            ],
                        },
                        {
                            "id": "colocation-set-mixed",
                            "resource_sets": [
                                {
                                    "resource_ids": ["resource3", "resource4"],
                                },
                            ],
                            "options": [
                                {
                                    "name": "score",
                                    "value": "15",
                                }
                            ],
                        },
                    ],
                    "ha_cluster_constraints_order": [
                        {
                            "id": "order-resource5-resource6-100",
                            "resource_first": {
                                "id": "resource5",
                                "action": "start",
                            },
                            "resource_then": {
                                "id": "resource6",
                                "action": "start",
                            },
                            "options": [
                                {
                                    "name": "score",
                                    "value": "100",
                                },
                                {
                                    "name": "symmetrical",
                                    "value": "false",
                                },
                            ],
                        },
                        {
                            "id": "order-set",
                            "resource_sets": [
                                {
                                    "resource_ids": ["resource1", "resource2"],
                                },
                            ],
                            "options": [
                                {"name": "kind", "value": "Optional"},
                            ],
                        },
                    ],
                    "ha_cluster_constraints_ticket": [
                        {
                            "id": "ticket-resource7-ticket1",
                            "resource": {"id": "resource7"},
                            "ticket": "ticket1",
                            "options": [
                                {
                                    "name": "loss-policy",
                                    "value": "demote",
                                }
                            ],
                        },
                        {
                            "id": "ticket-set",
                            "resource_sets": [
                                {
                                    "resource_ids": ["resource1", "resource2"],
                                },
                            ],
                            "ticket": "ticket2",
                            "options": [
                                {"name": "loss-policy", "value": "fence"},
                            ],
                        },
                    ],
                },
            )

    def test_success_empty_constraints(self) -> None:
        with mocked_module(
            [
                (
                    CMD_CONSTRAINTS_CONF,
                    (0, json.dumps(EMPTY_CONSTRAINTS), ""),
                ),
            ]
        ) as module_mock:
            self.assertEqual(
                ha_cluster_info.export_constraints_configuration(
                    module_mock,
                    [ha_cluster_info.Capability.CONSTRAINTS_OUTPUT.value],
                ),
                {},
            )

    def test_no_capabilities(self) -> None:
        with mocked_module([]) as module_mock:
            self.assertEqual(
                ha_cluster_info.export_constraints_configuration(
                    module_mock, pcs_capabilities=[]
                ),
                {},
            )

    def test_pcs_cmd_fail(self) -> None:
        with self.assertRaises(ha_cluster_info.loader.CliCommandError) as cm:
            with mocked_module(
                [(CMD_CONSTRAINTS_CONF, (1, "", "Error"))]
            ) as module_mock:
                ha_cluster_info.export_constraints_configuration(
                    module_mock,
                    [ha_cluster_info.Capability.CONSTRAINTS_OUTPUT.value],
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
