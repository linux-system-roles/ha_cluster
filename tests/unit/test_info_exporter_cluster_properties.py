# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

from unittest import TestCase

from .ha_cluster_info import exporter


class ExportClusterProperties(TestCase):
    maxDiff = None

    def test_uses_standard_invalid_src_dealing(self) -> None:
        properties_data = {}  # type: ignore
        with self.assertRaises(exporter.InvalidSrc) as cm:
            exporter.export_cluster_properties(properties_data)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data=properties_data,
                data_desc="cluster properties configuration",
                issue_location="",
                issue_desc="Missing key 'nvsets'",
            ),
        )

    def test_export_multiple_nvpairs(self) -> None:
        properties_data = {  # type: ignore
            "nvsets": [
                {
                    "id": "cib-bootstrap-options",
                    "options": {},
                    "rule": None,
                    "nvpairs": [
                        {
                            "id": "cib-bootstrap-options-cluster-infrastructure",
                            "name": "cluster-delay",
                            "value": "3",
                        },
                        {
                            "id": "cib-bootstrap-options-maintenance-mode",
                            "name": "maintenance-mode",
                            "value": "0",
                        },
                    ],
                }
            ]
        }
        self.assertEqual(
            [
                {
                    "attrs": [
                        {
                            "name": "cluster-delay",
                            "value": "3",
                        },
                        {
                            "name": "maintenance-mode",
                            "value": "0",
                        },
                    ]
                }
            ],
            exporter.export_cluster_properties(properties_data),
        )

    def test_export_only_first_set(self) -> None:
        properties_data = {  # type: ignore
            "nvsets": [
                {
                    "id": "cib-bootstrap-options",
                    "options": {},
                    "rule": None,
                    "nvpairs": [
                        {
                            "id": "cib-bootstrap-options-cluster-delay",
                            "name": "cluster-delay",
                            "value": "3",
                        },
                    ],
                },
                {
                    "id": "cib-bootstrap-options2",
                    "options": {},
                    "rule": None,
                    "nvpairs": [
                        {
                            "id": "cib-bootstrap-options-maintenance-mode",
                            "name": "maintenance-mode",
                            "value": "0",
                        },
                    ],
                },
            ]
        }
        self.assertEqual(
            [
                {
                    "attrs": [
                        {
                            "name": "cluster-delay",
                            "value": "3",
                        }
                    ]
                }
            ],
            exporter.export_cluster_properties(properties_data),
        )

    def test_skip_readonly_properties(self) -> None:
        properties_data = {  # type: ignore
            "nvsets": [
                {
                    "id": "cib-bootstrap-options",
                    "options": {},
                    "rule": None,
                    "nvpairs": [
                        {
                            "id": "cib-bootstrap-options-cluster-infrastructure",
                            "name": "cluster-infrastructure",
                            "value": "corosync",
                        },
                        {
                            "id": "cib-bootstrap-options-cluster-name",
                            "name": "cluster-name",
                            "value": "abc",
                        },
                        {
                            "id": "cib-bootstrap-options-dc-version",
                            "name": "dc-version",
                            "value": "3.0.0-2.el10-3704d6c",
                        },
                        {
                            "id": "cib-bootstrap-options-have-watchdog",
                            "name": "have-watchdog",
                            "value": "false",
                        },
                        {
                            "id": "cib-bootstrap-options-last-lrm-refresh",
                            "name": "last-lrm-refresh",
                            "value": "0",
                        },
                        {
                            "id": "cib-bootstrap-options-cluster-infrastructure",
                            "name": "cluster-delay",
                            "value": "3",
                        },
                        {
                            "id": "cib-bootstrap-options-stonith-watchdog-timeout",
                            "name": "stonith-watchdog-timeout",
                            "value": "10",
                        },
                    ],
                }
            ]
        }
        self.assertEqual(
            [
                {
                    "attrs": [
                        {
                            "name": "cluster-delay",
                            "value": "3",
                        },
                        {
                            "name": "stonith-watchdog-timeout",
                            "value": "10",
                        },
                    ]
                }
            ],
            exporter.export_cluster_properties(properties_data),
        )
