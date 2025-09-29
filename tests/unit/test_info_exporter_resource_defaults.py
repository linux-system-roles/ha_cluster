# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

from unittest import TestCase

from .ha_cluster_info import exporter


class ExportResourceDefaults(TestCase):
    maxDiff = None

    def test_uses_standard_invalid_src_dealing(self) -> None:
        resource_defaults_data = {}  # type: ignore
        with self.assertRaises(exporter.InvalidSrc) as cm:
            exporter.export_resource_defaults(resource_defaults_data)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data=resource_defaults_data,
                data_desc="resource defaults configuration",
                issue_location="",
                issue_desc="Missing key 'meta_attributes'",
            ),
        )

    def test_no_meta_attributes(self) -> None:
        self.assertIsNone(
            exporter.export_resource_defaults(
                {
                    "instance_attributes": [],
                    "meta_attributes": [],
                }
            )
        )

    def test_export_multiple_nvsets(self) -> None:
        resource_defaults_data = {  # type: ignore
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
                {
                    "id": "id-2",
                    "options": {},
                    "rule": None,
                    "nvpairs": [],
                },
                {
                    "id": "id-3",
                    "options": {"score": "10"},
                    "rule": {
                        "id": "some-id",
                        "type": None,
                        "in_effect": None,
                        "options": None,
                        "date_spec": None,
                        "duration": None,
                        "expressions": None,
                        "as_string": "date gt 2025-09-05",
                    },
                    "nvpairs": [
                        {
                            "id": "rsc_defaults-meta_attributes-a",
                            "name": "a",
                            "value": "b",
                        }
                    ],
                },
            ],
        }
        self.assertEqual(
            {
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
                    {
                        "id": "id-2",
                    },
                    {
                        "id": "id-3",
                        "score": "10",
                        "rule": "date gt 2025-09-05",
                        "attrs": [
                            {
                                "name": "a",
                                "value": "b",
                            },
                        ],
                    },
                ]
            },
            exporter.export_resource_defaults(resource_defaults_data),
        )
