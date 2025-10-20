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
                        }
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
