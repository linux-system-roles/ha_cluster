# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

from unittest import TestCase, mock

from .ha_cluster_info import ha_cluster_info


class ExportPcsdConfiguration(TestCase):
    maxDiff = None

    @mock.patch("ha_cluster_info.loader.get_pcsd_settings_conf")
    def test_permissions_defined(
        self, mock_load_pcsd_permissions: mock.Mock
    ) -> None:
        mock_load_pcsd_permissions.return_value = {
            "permissions": {
                "local_cluster": [
                    {
                        "type": "group",
                        "name": "haclient",
                        "allow": ["grant", "read", "write"],
                    },
                    {
                        "type": "user",
                        "name": "admin",
                        "allow": ["full"],
                    },
                ]
            }
        }

        self.assertEqual(
            ha_cluster_info.export_pcsd_configuration(),
            {
                "ha_cluster_pcs_permission_list": [
                    {
                        "type": "group",
                        "name": "haclient",
                        "allow_list": ["grant", "read", "write"],
                    },
                    {
                        "type": "user",
                        "name": "admin",
                        "allow_list": ["full"],
                    },
                ]
            },
        )

    @mock.patch("ha_cluster_info.loader.get_pcsd_settings_conf")
    def test_empty_permissions_defined(
        self, mock_load_pcsd_permissions: mock.Mock
    ) -> None:
        mock_load_pcsd_permissions.return_value = {
            "permissions": {
                "local_cluster": [],
            }
        }

        self.assertEqual(
            ha_cluster_info.export_pcsd_configuration(),
            {
                "ha_cluster_pcs_permission_list": [],
            },
        )

    @mock.patch("ha_cluster_info.loader.get_pcsd_settings_conf")
    def test_permission_load_error(
        self, mock_load_pcsd_permissions: mock.Mock
    ) -> None:
        mock_load_pcsd_permissions.return_value = None

        self.assertEqual(
            ha_cluster_info.export_pcsd_configuration(),
            {},
        )

    @mock.patch("ha_cluster_info.loader.get_pcsd_settings_conf")
    def test_permission_load_bad_format(
        self, mock_load_pcsd_permissions: mock.Mock
    ) -> None:
        mock_load_pcsd_permissions.return_value = {
            "permissions": {
                "local": [
                    {
                        "type": "group",
                        "name": "haclient",
                        "allow": ["grant", "read", "write"],
                    },
                ]
            }
        }

        with self.assertRaises(ha_cluster_info.exporter.InvalidSrc) as cm:
            ha_cluster_info.export_pcsd_configuration()
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data_desc="pcs_settings.conf",
                data=mock_load_pcsd_permissions.return_value,
                issue_location="/permissions",
                issue_desc="Missing key 'local_cluster'",
            ),
        )
