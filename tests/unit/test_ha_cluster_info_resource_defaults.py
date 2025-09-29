# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import json
from unittest import TestCase, mock

from .ha_cluster_info import ha_cluster_info, mocked_module

CMD_OPTIONS = dict(environ_update={"LC_ALL": "C"}, check_rc=False)
PCS_CMD = ["pcs", "resource", "defaults", "config", "--output-format=json"]
CMD_RESOURCE_DEFAULTS_CONF = mock.call(PCS_CMD, **CMD_OPTIONS)
PCS_OP_CMD = [
    "pcs",
    "resource",
    "op",
    "defaults",
    "config",
    "--output-format=json",
]
CMD_RESOURCE_OP_DEFAULTS_CONF = mock.call(PCS_OP_CMD, **CMD_OPTIONS)


class ExportResourceDefaultsConfiguration(TestCase):
    maxDiff = None

    def test_success(self) -> None:
        defaults_data = {  # type: ignore
            "instance_attributes": [],
            "meta_attributes": [
                {
                    "id": "id-1",
                    "options": {},
                    "rule": None,
                    "nvpairs": [
                        {
                            "id": "build-resource-stickiness",
                            "name": "resource-stickiness",
                            "value": "1",
                        }
                    ],
                },
            ],
        }
        with mocked_module(
            [
                (
                    CMD_RESOURCE_DEFAULTS_CONF,
                    (0, json.dumps(defaults_data), ""),
                ),
            ]
        ) as module_mock:
            self.assertEqual(
                ha_cluster_info.export_resource_defaults_configuration(
                    module_mock,
                    [ha_cluster_info.Capability.RESOURCE_DEFAULTS_OUTPUT.value],
                ),
                {
                    "ha_cluster_resource_defaults": {
                        "meta_attrs": [
                            {
                                "id": "id-1",
                                "attrs": [
                                    {
                                        "name": "resource-stickiness",
                                        "value": "1",
                                    },
                                ],
                            },
                        ]
                    }
                },
            )

    def test_no_capabilities(self) -> None:
        with mocked_module([]) as module_mock:
            self.assertEqual(
                ha_cluster_info.export_resource_defaults_configuration(
                    module_mock, pcs_capabilities=[]
                ),
                {},
            )


class ExportResourceOpDefaultsConfiguration(TestCase):
    maxDiff = None

    def test_success(self) -> None:
        defaults_data = {  # type: ignore
            "instance_attributes": [],
            "meta_attributes": [
                {
                    "id": "id-x",
                    "options": {},
                    "rule": None,
                    "nvpairs": [
                        {
                            "id": "build-a",
                            "name": "a",
                            "value": "b",
                        }
                    ],
                },
            ],
        }
        with mocked_module(
            [
                (
                    CMD_RESOURCE_OP_DEFAULTS_CONF,
                    (0, json.dumps(defaults_data), ""),
                ),
            ]
        ) as module_mock:
            self.assertEqual(
                ha_cluster_info.export_resource_op_defaults_configuration(
                    module_mock,
                    [
                        ha_cluster_info.Capability.RESOURCE_OP_DEFAULTS_OUTPUT.value
                    ],
                ),
                {
                    "ha_cluster_resource_operation_defaults": {
                        "meta_attrs": [
                            {
                                "id": "id-x",
                                "attrs": [
                                    {
                                        "name": "a",
                                        "value": "b",
                                    },
                                ],
                            },
                        ]
                    }
                },
            )

    def test_no_capabilities_op(self) -> None:
        with mocked_module([]) as module_mock:
            self.assertEqual(
                ha_cluster_info.export_resource_op_defaults_configuration(
                    module_mock, pcs_capabilities=[]
                ),
                {},
            )
