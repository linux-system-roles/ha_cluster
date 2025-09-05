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
PCS_CMD = ["pcs", "property", "config", "--output-format=json"]
CMD_CLUSTER_PROPERTIES_CONF = mock.call(PCS_CMD, **CMD_OPTIONS)


class ExportPropertiesConfiguration(TestCase):
    maxDiff = None

    def test_success(self) -> None:
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
                    ],
                },
            ]
        }
        with mocked_module(
            [
                (
                    CMD_CLUSTER_PROPERTIES_CONF,
                    (0, json.dumps(properties_data), ""),
                ),
            ]
        ) as module_mock:
            self.assertEqual(
                ha_cluster_info.export_cluster_properties_configuration(
                    module_mock,
                    ha_cluster_info.Capability.CLUSTER_PROPERTIES_OUTPUT.value,
                ),
                {
                    "ha_cluster_cluster_properties": [
                        {
                            "attrs": [
                                {
                                    "name": "cluster-delay",
                                    "value": "3",
                                },
                            ]
                        }
                    ],
                },
            )

    def test_no_capabilities(self) -> None:
        with mocked_module([]) as module_mock:
            self.assertEqual(
                ha_cluster_info.export_cluster_properties_configuration(
                    module_mock, pcs_capabilities=[]
                ),
                {},
            )

    def test_pcs_cmd_fail(self) -> None:
        with self.assertRaises(ha_cluster_info.loader.CliCommandError) as cm:
            with mocked_module(
                [(CMD_CLUSTER_PROPERTIES_CONF, (1, "", "Error"))]
            ) as module_mock:
                ha_cluster_info.export_cluster_properties_configuration(
                    module_mock,
                    ha_cluster_info.Capability.CLUSTER_PROPERTIES_OUTPUT.value,
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
