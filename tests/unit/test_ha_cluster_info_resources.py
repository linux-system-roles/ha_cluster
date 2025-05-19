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

FIXTURE_CAPABILITIES = ["pcmk.resource.config.output-formats"]

FIXTURE_EMPTY_RESOURCES = {  # type: ignore
    "primitives": [],
    "groups": [],
    "clones": [],
    "bundles": [],
}


class ExportResourcesConfiguration(TestCase):
    maxDiff = None

    def test_uses_standard_invalid_src_dealing(self) -> None:
        resource_data = {  # type: ignore
            "groups": [],
            "clones": [],
            "bundles": [],
        }
        stonith_data = {  # type: ignore
            "groups": [],
            "clones": [],
            "bundles": [],
        }
        with (
            self.assertRaises(ha_cluster_info.exporter.InvalidSrc) as cm,
            mocked_module(
                [
                    (CMD_RESOURCE_CONF, (0, json.dumps(resource_data), "")),
                    (CMD_STONITH_CONF, (0, json.dumps(stonith_data), "")),
                ]
            ) as module_mock,
        ):
            ha_cluster_info.export_resources_configuration(
                module_mock, FIXTURE_CAPABILITIES
            )
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
        resource_data = {
            "primitives": [
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
            "groups": [],
            "clones": [],
            "bundles": [],
        }
        stonith_data = FIXTURE_EMPTY_RESOURCES
        with (
            self.assertRaises(ha_cluster_info.exporter.InvalidSrc) as cm,
            mocked_module(
                [
                    (CMD_RESOURCE_CONF, (0, json.dumps(resource_data), "")),
                    (CMD_STONITH_CONF, (0, json.dumps(stonith_data), "")),
                ]
            ) as module_mock,
        ):
            ha_cluster_info.export_resources_configuration(
                module_mock, FIXTURE_CAPABILITIES
            )
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data=resource_data,
                data_desc="resources configuration",
                issue_location="/primitives/0/operations/0",
                issue_desc="No attributes in operation",
            ),
        )

    def test_no_resources(self) -> None:
        resource_data = FIXTURE_EMPTY_RESOURCES
        stonith_data = FIXTURE_EMPTY_RESOURCES
        with mocked_module(
            [
                (CMD_RESOURCE_CONF, (0, json.dumps(resource_data), "")),
                (CMD_STONITH_CONF, (0, json.dumps(stonith_data), "")),
            ]
        ) as module_mock:
            self.assertEqual(
                ha_cluster_info.export_resources_configuration(
                    module_mock, FIXTURE_CAPABILITIES
                ),
                {},
            )

    def test_no_member_id_in_bundles(self) -> None:
        resource_data = {  # type: ignore
            "primitives": [
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
                            "interval": "30s",
                        }
                    ],
                }
            ],
            "groups": [],
            "clones": [],
            "bundles": [
                {"id": "B 1", "container_type": "docker"},
                {"id": "B 2", "container_type": "docker", "member_id": None},
                {"id": "B 3", "container_type": "docker", "member_id": ""},
                {"id": "B 4", "container_type": "docker", "member_id": "A"},
            ],
        }
        stonith_data = FIXTURE_EMPTY_RESOURCES
        with mocked_module(
            [
                (CMD_RESOURCE_CONF, (0, json.dumps(resource_data), "")),
                (CMD_STONITH_CONF, (0, json.dumps(stonith_data), "")),
            ]
        ) as module_mock:
            self.assertEqual(
                ha_cluster_info.export_resources_configuration(
                    module_mock, FIXTURE_CAPABILITIES
                ),
                {
                    "ha_cluster_resource_primitives": [
                        {
                            "id": "A",
                            "agent": "ocf:pacemaker:Stateful",
                            "copy_operations_from_agent": False,
                            "operations": [
                                {
                                    "action": "migrate_from",
                                    "attrs": [
                                        {"name": "interval", "value": "30s"}
                                    ],
                                },
                            ],
                        }
                    ],
                    "ha_cluster_resource_bundles": [
                        {"id": "B 1", "container": {"type": "docker"}},
                        {"id": "B 2", "container": {"type": "docker"}},
                        {"id": "B 3", "container": {"type": "docker"}},
                        {
                            "id": "B 4",
                            "container": {"type": "docker"},
                            "resource_id": "A",
                        },
                    ],
                },
            )

    def test_skip_bundle_without_container_type(self) -> None:
        resource_data = {  # type: ignore
            "primitives": [],
            "groups": [],
            "clones": [],
            "bundles": [
                {"id": "B 1", "container_type": "docker"},
                {"id": "B-without-container-type"},
                {
                    "id": "B-with-container-type-none",
                    "container_type": None,
                },
                {"id": "B 2", "container_type": "docker"},
            ],
        }
        stonith_data = FIXTURE_EMPTY_RESOURCES
        with mocked_module(
            [
                (CMD_RESOURCE_CONF, (0, json.dumps(resource_data), "")),
                (CMD_STONITH_CONF, (0, json.dumps(stonith_data), "")),
            ]
        ) as module_mock:
            self.assertEqual(
                ha_cluster_info.export_resources_configuration(
                    module_mock, FIXTURE_CAPABILITIES
                ),
                {
                    "ha_cluster_resource_bundles": [
                        {"id": "B 1", "container": {"type": "docker"}},
                        {"id": "B 2", "container": {"type": "docker"}},
                    ]
                },
            )

    def test_no_capabilities(self) -> None:
        with mocked_module([]) as module_mock:
            self.assertEqual(
                ha_cluster_info.export_resources_configuration(
                    module_mock, pcs_capabilities=[]
                ),
                {},
            )

    def test_max_features(self) -> None:
        def open_file(file_name: str):  # type: ignore
            return open(os.path.join(CURRENT_DIR, file_name), encoding="utf-8")

        with (
            open_file("resources.json") as resources_json,
            open_file("stonith.json") as stonith_json,
            open_file("resources-export.json") as expected_export,
            mocked_module(
                [
                    (CMD_RESOURCE_CONF, (0, resources_json.read(), "")),
                    (CMD_STONITH_CONF, (0, stonith_json.read(), "")),
                ]
            ) as module_mock,
        ):
            self.assertEqual(
                ha_cluster_info.export_resources_configuration(
                    module_mock, FIXTURE_CAPABILITIES
                ),
                json.load(expected_export),
            )

    def test_no_capabilites(self) -> None:
        with mocked_module([]) as module_mock:
            self.assertEqual(
                ha_cluster_info.export_resources_configuration(
                    module_mock, pcs_capabilities=[]
                ),
                {},
            )
