# -*- coding: utf-8 -*-

# Copyright (C) 2023 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import json
import sys
from importlib import import_module
from unittest import TestCase, mock

sys.modules["ansible.module_utils.ha_cluster_lsr"] = import_module(
    "ha_cluster_lsr"
)

import pcs_api_v2
from pcs.common.async_tasks.dto import CommandDto, CommandOptionsDto
from pcs.common.interface.dto import to_dict

from . import fixture


class Pcs(TestCase):
    cmd_name = "some pcs command"
    cmd_params = dict(some="option", another=["opti", "owns"])
    cmd_options = CommandOptionsDto(request_timeout=60)
    cmd_dto = CommandDto(cmd_name, cmd_params, cmd_options)

    def setUp(self) -> None:
        self.module_mock = mock.Mock()
        self.module_mock.from_json = json.loads

        call_api_patcher = mock.patch("pcs_api_v2.api_utils.call_api_raw")
        self.call_api_mock = call_api_patcher.start()
        self.addCleanup(call_api_patcher.stop)

    def assert_api_called(self) -> None:
        self.call_api_mock.assert_called_once_with(
            self.module_mock, self.cmd_dto
        )

    def test_success(self) -> None:
        self.call_api_mock.return_value = (
            fixture.response_from_dto(
                fixture.task_result_dto(
                    result=dict(some="result"), command=self.cmd_dto
                )
            ),
            dict(status=200, body="some body data"),
        )

        pcs_api_v2.pcs(
            self.module_mock, self.cmd_name, self.cmd_params, self.cmd_options
        )

        self.assert_api_called()
        self.module_mock.exit_json.assert_called_once_with(
            changed=True,
            pcs_result=dict(
                task_ident="identifier",
                command={
                    "command_name": self.cmd_name,
                    "params": self.cmd_params,
                    "options": to_dict(self.cmd_options),
                },
                task_finish_type="TaskFinishType.SUCCESS",
                result={"some": "result"},
                reports=[],
                kill_reason=None,
            ),
        )
        self.module_mock.fail_json.assert_not_called()

    def test_http_error(self) -> None:
        self.call_api_mock.return_value = (
            fixture.response("doesn't matter"),
            dict(status=404, body="some body data"),
        )

        pcs_api_v2.pcs(
            self.module_mock, self.cmd_name, self.cmd_params, self.cmd_options
        )

        self.assert_api_called()
        self.module_mock.exit_json.assert_not_called()
        self.module_mock.fail_json.assert_called_once_with(msg="some body data")

    def test_api_error(self) -> None:
        self.call_api_mock.return_value = (
            fixture.response("not valid json"),
            dict(status=200, body="some body data"),
        )

        pcs_api_v2.pcs(
            self.module_mock, self.cmd_name, self.cmd_params, self.cmd_options
        )

        self.assert_api_called()
        self.module_mock.exit_json.assert_not_called()
        self.module_mock.fail_json.assert_called_once_with(
            msg=(
                "Unable to parse API response: Expecting value: line 1 column 1 "
                "(char 0)\n'not valid json'"
            )
        )
