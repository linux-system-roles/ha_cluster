#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import json
import os.path
from unittest import TestCase, mock

from .ha_cluster_info import ha_cluster_info, mocked_module

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

CMD_OPTIONS = dict(environ_update={"LC_ALL": "C"}, check_rc=False)
CMD_RESOURCE_CONF = mock.call(
    ["pcs", "resource", "config", "--output-format=json"], **CMD_OPTIONS
)
CMD_STONITH_CONF = mock.call(
    ["pcs", "stonith", "config", "--output-format=json"], **CMD_OPTIONS
)


class ExportResourcesConfiguration(TestCase):
    maxDiff = None

    def test_uses_standard_invalid_src_dealing(self) -> None:
        resource_data = dict(  # type: ignore
            groups=[],
            clones=[],
            bundles=[],
        )
        stonith_data = dict(  # type: ignore
            groups=[],
            clones=[],
            bundles=[],
        )
        with (
            self.assertRaises(ha_cluster_info.exporter.InvalidSrc) as cm,
            mocked_module(
                [
                    (CMD_RESOURCE_CONF, (0, json.dumps(resource_data), "")),
                    (CMD_STONITH_CONF, (0, json.dumps(stonith_data), "")),
                ]
            ) as module_mock,
        ):
            ha_cluster_info.export_resources_configuration(module_mock)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data=resource_data,
                data_desc="resources configuration",
                issue_location="",
                issue_desc="Missing key 'primitives'",
            ),
        )

    def test_invalid_src_on_operation_without_attr(self) -> None:
        resource_data = dict(
            primitives=[
                {
                    "id": "A",
                    "agent_name": {
                        "standard": "ocf",
                        "provider": "pacemaker",
                        "type": "Stateful",
                    },
                    "operations": [
                        {
                            "id": "A-migrate_from",
                            "name": "migrate_from",
                            "interval": None,
                            "description": None,
                            "start_delay": None,
                            "interval_origin": None,
                            "timeout": None,
                            "enabled": None,
                            "record_pending": None,
                            "role": None,
                            "on_fail": None,
                            "meta_attributes": [],
                            "instance_attributes": [],
                        }
                    ],
                }
            ],
            groups=[],
            clones=[],
            bundles=[],
        )
        stonith_data = dict(  # type: ignore
            primitives=[],
            groups=[],
            clones=[],
            bundles=[],
        )
        with (
            self.assertRaises(ha_cluster_info.exporter.InvalidSrc) as cm,
            mocked_module(
                [
                    (CMD_RESOURCE_CONF, (0, json.dumps(resource_data), "")),
                    (CMD_STONITH_CONF, (0, json.dumps(stonith_data), "")),
                ]
            ) as module_mock,
        ):
            ha_cluster_info.export_resources_configuration(module_mock)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data=resource_data,
                data_desc="resources configuration",
                issue_location="/primitives/0/operations/0",
                issue_desc="No attributes in operation",
            ),
        )

    def test_no_primitives(self) -> None:
        resource_data = dict(  # type: ignore
            primitives=[],
            groups=[],
            clones=[],
            bundles=[],
        )
        stonith_data = dict(  # type: ignore
            primitives=[],
            groups=[],
            clones=[],
            bundles=[],
        )
        with mocked_module(
            [
                (CMD_RESOURCE_CONF, (0, json.dumps(resource_data), "")),
                (CMD_STONITH_CONF, (0, json.dumps(stonith_data), "")),
            ]
        ) as module_mock:
            self.assertEqual(
                ha_cluster_info.export_resources_configuration(module_mock),
                dict(),
            )

    def test_max_features(self) -> None:
        with (
            open(
                os.path.join(CURRENT_DIR, "resources.json"), encoding="utf-8"
            ) as resources_json,
            open(
                os.path.join(CURRENT_DIR, "stonith.json"), encoding="utf-8"
            ) as stonith_json,
            mocked_module(
                [
                    (CMD_RESOURCE_CONF, (0, resources_json.read(), "")),
                    (CMD_STONITH_CONF, (0, stonith_json.read(), "")),
                ]
            ) as module_mock,
        ):
            self.assertEqual(
                ha_cluster_info.export_resources_configuration(module_mock),
                dict(
                    ha_cluster_resource_primitives=[
                        dict(
                            id="A",
                            agent="ocf:pacemaker:Stateful",
                            copy_operations_from_agent=False,
                            operations=[
                                {
                                    "action": "migrate_from",
                                    "attrs": [
                                        {"name": "interval", "value": "0s"},
                                        {"name": "timeout", "value": "20s"},
                                    ],
                                },
                                {
                                    "action": "migrate_to",
                                    "attrs": [
                                        {"name": "interval", "value": "0s"},
                                        {"name": "timeout", "value": "20s"},
                                    ],
                                },
                                {
                                    "action": "monitor",
                                    "attrs": [
                                        {"name": "interval", "value": "10s"},
                                        {"name": "timeout", "value": "20s"},
                                    ],
                                },
                                {
                                    "action": "reload",
                                    "attrs": [
                                        {"name": "interval", "value": "0s"},
                                        {"name": "timeout", "value": "20s"},
                                    ],
                                },
                                {
                                    "action": "reload-agent",
                                    "attrs": [
                                        {"name": "interval", "value": "0s"},
                                        {"name": "timeout", "value": "20s"},
                                    ],
                                },
                                {
                                    "action": "start",
                                    "attrs": [
                                        {"name": "interval", "value": "0s"},
                                        {"name": "timeout", "value": "20s"},
                                    ],
                                },
                                {
                                    "action": "stop",
                                    "attrs": [
                                        {"name": "interval", "value": "0s"},
                                        {"name": "timeout", "value": "20s"},
                                    ],
                                },
                            ],
                            instance_attrs=[
                                {
                                    "attrs": [
                                        {"name": "fake", "value": "some-value"}
                                    ]
                                }
                            ],
                            meta_attrs=[
                                {
                                    "attrs": [
                                        {
                                            "name": "target-role",
                                            "value": "Stopped",
                                        }
                                    ]
                                }
                            ],
                            utilization=[
                                {
                                    "attrs": [
                                        {
                                            "name": "cpu",
                                            "value": "1",
                                        }
                                    ]
                                }
                            ],
                        ),
                        dict(
                            id="B",
                            agent="systemd:crond",
                            copy_operations_from_agent=False,
                            operations=[
                                {
                                    "action": "monitor",
                                    "attrs": [
                                        {"name": "interval", "value": "60s"},
                                        {"name": "timeout", "value": "100s"},
                                    ],
                                },
                                {
                                    "action": "start",
                                    "attrs": [
                                        {"name": "interval", "value": "0s"},
                                        {"name": "timeout", "value": "100s"},
                                    ],
                                },
                                {
                                    "action": "stop",
                                    "attrs": [
                                        {"name": "interval", "value": "0s"},
                                        {"name": "timeout", "value": "100s"},
                                    ],
                                },
                            ],
                        ),
                        dict(
                            id="C",
                            agent="ocf:pacemaker:Stateful",
                            copy_operations_from_agent=False,
                            operations=[
                                {
                                    "action": "demote",
                                    "attrs": [
                                        {"name": "interval", "value": "0s"},
                                        {"name": "timeout", "value": "10s"},
                                    ],
                                },
                                {
                                    "action": "monitor",
                                    "attrs": [
                                        {"name": "interval", "value": "10s"},
                                        {"name": "timeout", "value": "20s"},
                                        {"name": "role", "value": "Promoted"},
                                    ],
                                },
                                {
                                    "action": "monitor",
                                    "attrs": [
                                        {"name": "interval", "value": "11s"},
                                        {"name": "timeout", "value": "20s"},
                                        {"name": "role", "value": "Unpromoted"},
                                    ],
                                },
                                {
                                    "action": "notify",
                                    "attrs": [
                                        {"name": "interval", "value": "0s"},
                                        {"name": "timeout", "value": "5s"},
                                    ],
                                },
                                {
                                    "action": "promote",
                                    "attrs": [
                                        {"name": "interval", "value": "0s"},
                                        {"name": "timeout", "value": "10s"},
                                    ],
                                },
                                {
                                    "action": "reload-agent",
                                    "attrs": [
                                        {"name": "interval", "value": "0s"},
                                        {"name": "timeout", "value": "10s"},
                                    ],
                                },
                                {
                                    "action": "start",
                                    "attrs": [
                                        {"name": "interval", "value": "0s"},
                                        {"name": "timeout", "value": "20s"},
                                    ],
                                },
                                {
                                    "action": "stop",
                                    "attrs": [
                                        {"name": "interval", "value": "0s"},
                                        {"name": "timeout", "value": "20s"},
                                    ],
                                },
                            ],
                        ),
                        dict(
                            id="D",
                            agent="ocf:pacemaker:Stateful",
                            copy_operations_from_agent=False,
                            operations=[
                                {
                                    "action": "demote",
                                    "attrs": [
                                        {"name": "interval", "value": "0s"},
                                        {"name": "timeout", "value": "10s"},
                                    ],
                                },
                                {
                                    "action": "monitor",
                                    "attrs": [
                                        {"name": "interval", "value": "10s"},
                                        {"name": "timeout", "value": "20s"},
                                        {"name": "role", "value": "Promoted"},
                                    ],
                                },
                                {
                                    "action": "monitor",
                                    "attrs": [
                                        {"name": "interval", "value": "11s"},
                                        {"name": "timeout", "value": "20s"},
                                        {"name": "role", "value": "Unpromoted"},
                                    ],
                                },
                                {
                                    "action": "notify",
                                    "attrs": [
                                        {"name": "interval", "value": "0s"},
                                        {"name": "timeout", "value": "5s"},
                                    ],
                                },
                                {
                                    "action": "promote",
                                    "attrs": [
                                        {"name": "interval", "value": "0s"},
                                        {"name": "timeout", "value": "10s"},
                                    ],
                                },
                                {
                                    "action": "reload-agent",
                                    "attrs": [
                                        {"name": "interval", "value": "0s"},
                                        {"name": "timeout", "value": "10s"},
                                    ],
                                },
                                {
                                    "action": "start",
                                    "attrs": [
                                        {"name": "interval", "value": "0s"},
                                        {"name": "timeout", "value": "20s"},
                                    ],
                                },
                                {
                                    "action": "stop",
                                    "attrs": [
                                        {"name": "interval", "value": "0s"},
                                        {"name": "timeout", "value": "20s"},
                                    ],
                                },
                            ],
                        ),
                        dict(
                            id="E",
                            agent="ocf:pacemaker:Stateful",
                            copy_operations_from_agent=False,
                            operations=[
                                {
                                    "action": "demote",
                                    "attrs": [
                                        {"name": "interval", "value": "0s"},
                                        {"name": "timeout", "value": "10s"},
                                    ],
                                },
                                {
                                    "action": "monitor",
                                    "attrs": [
                                        {"name": "interval", "value": "10s"},
                                        {"name": "timeout", "value": "20s"},
                                        {"name": "role", "value": "Promoted"},
                                    ],
                                },
                                {
                                    "action": "monitor",
                                    "attrs": [
                                        {"name": "interval", "value": "11s"},
                                        {"name": "timeout", "value": "20s"},
                                        {"name": "role", "value": "Unpromoted"},
                                    ],
                                },
                                {
                                    "action": "notify",
                                    "attrs": [
                                        {"name": "interval", "value": "0s"},
                                        {"name": "timeout", "value": "5s"},
                                    ],
                                },
                                {
                                    "action": "promote",
                                    "attrs": [
                                        {"name": "interval", "value": "0s"},
                                        {"name": "timeout", "value": "10s"},
                                    ],
                                },
                                {
                                    "action": "reload-agent",
                                    "attrs": [
                                        {"name": "interval", "value": "0s"},
                                        {"name": "timeout", "value": "10s"},
                                    ],
                                },
                                {
                                    "action": "start",
                                    "attrs": [
                                        {"name": "interval", "value": "0s"},
                                        {"name": "timeout", "value": "20s"},
                                    ],
                                },
                                {
                                    "action": "stop",
                                    "attrs": [
                                        {"name": "interval", "value": "0s"},
                                        {"name": "timeout", "value": "20s"},
                                    ],
                                },
                            ],
                        ),
                        dict(
                            id="F1",
                            agent="stonith:fence_xvm",
                            copy_operations_from_agent=False,
                            instance_attrs=[
                                {"attrs": [{"name": "timeout", "value": "35"}]}
                            ],
                            meta_attrs=[
                                {
                                    "attrs": [
                                        {
                                            "name": "target-role",
                                            "value": "Stopped",
                                        }
                                    ]
                                }
                            ],
                            operations=[
                                {
                                    "action": "monitor",
                                    "attrs": [
                                        {"name": "interval", "value": "60s"},
                                    ],
                                },
                            ],
                        ),
                    ],
                    ha_cluster_resource_groups=[
                        dict(
                            id="G1",
                            resource_ids=["C", "D"],
                            meta_attrs=[
                                {
                                    "attrs": [
                                        {
                                            "name": "is-managed",
                                            "value": "true",
                                        },
                                        {
                                            "name": "target-role",
                                            "value": "Started",
                                        },
                                    ]
                                }
                            ],
                        ),
                        dict(
                            id="G2",
                            resource_ids=["E"],
                        ),
                    ],
                ),
            )
