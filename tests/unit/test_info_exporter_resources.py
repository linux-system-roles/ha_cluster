# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import json
import os.path
from unittest import TestCase

from .ha_cluster_info import exporter

FIXTURE_EMPTY_RESOURCES = {  # type: ignore
    "primitives": [],
    "groups": [],
    "clones": [],
    "bundles": [],
}

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


class ExportResources(TestCase):
    def test_uses_standard_invalid_src_dealing(self) -> None:
        resource_data = {  # type: ignore
            "groups": [],
            "clones": [],
            "bundles": [],
        }
        stonith_data = FIXTURE_EMPTY_RESOURCES

        with self.assertRaises(exporter.InvalidSrc) as cm:
            exporter.export_resource_primitive_list(resource_data, stonith_data)
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
        with self.assertRaises(exporter.InvalidSrc) as cm:
            exporter.export_resource_primitive_list(resource_data, stonith_data)
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
        self.assertEqual(
            exporter.export_resource_primitive_list(
                resources=FIXTURE_EMPTY_RESOURCES,
                stonith=FIXTURE_EMPTY_RESOURCES,
            ),
            [],
        )

    def test_member_id_in_bundles(self) -> None:
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
        self.assertEqual(
            exporter.export_resource_bundle_list(resource_data),
            [
                {"id": "B 1", "container": {"type": "docker"}},
                {"id": "B 2", "container": {"type": "docker"}},
                {"id": "B 3", "container": {"type": "docker"}},
                {
                    "id": "B 4",
                    "container": {"type": "docker"},
                    "resource_id": "A",
                },
            ],
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
        self.assertEqual(
            exporter.export_resource_bundle_list(resource_data),
            [
                {"id": "B 1", "container": {"type": "docker"}},
                {"id": "B 2", "container": {"type": "docker"}},
            ],
        )

    def test_max_features(self) -> None:
        def read_file(fname: str) -> str:
            with open(os.path.join(CURRENT_DIR, fname), encoding="utf-8") as f:
                return f.read()

        resource_data = json.loads(read_file("resources.json"))
        stonith_data = json.loads(read_file("stonith.json"))
        expected = json.loads(read_file("resources-export.json"))

        self.assertEqual(
            exporter.export_resource_primitive_list(
                resource_data, stonith_data
            ),
            expected["ha_cluster_resource_primitives"],
        )
        self.assertEqual(
            exporter.export_resource_group_list(resource_data),
            expected["ha_cluster_resource_groups"],
        )
        self.assertEqual(
            exporter.export_resource_clone_list(resource_data),
            expected["ha_cluster_resource_clones"],
        )
        self.assertEqual(
            exporter.export_resource_bundle_list(resource_data),
            expected["ha_cluster_resource_bundles"],
        )
