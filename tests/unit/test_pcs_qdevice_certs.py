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

import pcs_qdevice_certs
from pcs.common.async_tasks.dto import CommandDto, CommandOptionsDto
from pcs.common.async_tasks.types import TaskFinishType
from pcs.common.interface.dto import to_dict

from . import fixture


class Pcs(TestCase):
    qnetd_host = "node-q"
    cluster_name = "test-cluster"
    cmd_params = dict(qnetd_host=qnetd_host, cluster_name=cluster_name)
    cmd_options = CommandOptionsDto(effective_username="user")
    cmd_name_check = "quorum.device_net_certificate_check_local"
    cmd_name_setup = "quorum.device_net_certificate_setup_local"
    cmd_check_dto = CommandDto(
        command_name=cmd_name_check, params=cmd_params, options=cmd_options
    )
    cmd_setup_dto = CommandDto(
        command_name=cmd_name_setup, params=cmd_params, options=cmd_options
    )

    def setUp(self) -> None:
        self.module_mock = mock.Mock()
        self.module_mock.from_json = json.loads
        self.module_mock.check_mode = False

        call_api_patcher = mock.patch("pcs_api_v2.api_utils.call_api_raw")
        self.call_api_mock = call_api_patcher.start()
        self.addCleanup(call_api_patcher.stop)

    def test_success_setup(self) -> None:
        self.call_api_mock.side_effect = [
            (
                fixture.response_from_dto(
                    fixture.task_result_dto(
                        result=False, command=self.cmd_check_dto
                    )
                ),
                dict(status=200, body="some body data"),
            ),
            (
                fixture.response_from_dto(
                    fixture.task_result_dto(command=self.cmd_setup_dto)
                ),
                dict(status=200, body="some body data"),
            ),
        ]

        pcs_qdevice_certs.pcs(
            self.module_mock, self.cmd_params, self.cmd_options
        )

        self.call_api_mock.assert_has_calls(
            [
                mock.call(self.module_mock, self.cmd_check_dto),
                mock.call(self.module_mock, self.cmd_setup_dto),
            ]
        )
        self.module_mock.exit_json.assert_called_once_with(
            changed=True,
            pcs_result=dict(
                task_ident="identifier",
                command={
                    "command_name": self.cmd_name_setup,
                    "params": self.cmd_params,
                    "options": to_dict(self.cmd_options),
                },
                task_finish_type="TaskFinishType.SUCCESS",
                result=None,
                reports=[],
                kill_reason=None,
            ),
        )
        self.module_mock.fail_json.assert_not_called()

    def assert_check_call_only(self, certs_already_configured: bool) -> None:
        self.call_api_mock.return_value = (
            fixture.response_from_dto(
                fixture.task_result_dto(
                    result=certs_already_configured,
                    command=self.cmd_check_dto,
                )
            ),
            dict(status=200, body="some body data"),
        )

        pcs_qdevice_certs.pcs(
            self.module_mock, self.cmd_params, self.cmd_options
        )

        self.call_api_mock.assert_called_once_with(
            self.module_mock, self.cmd_check_dto
        )
        self.module_mock.exit_json.assert_called_once_with(
            changed=not certs_already_configured,
            pcs_result=dict(
                task_ident="identifier",
                command={
                    "command_name": self.cmd_name_check,
                    "params": self.cmd_params,
                    "options": to_dict(self.cmd_options),
                },
                task_finish_type="TaskFinishType.SUCCESS",
                result=certs_already_configured,
                reports=[],
                kill_reason=None,
            ),
        )
        self.module_mock.fail_json.assert_not_called()

    def test_success_already_configured(self) -> None:
        self.assert_check_call_only(True)

    def test_check_mode_configured(self) -> None:
        self.module_mock.check_mode = True
        self.assert_check_call_only(True)

    def test_check_mode_not_configured(self) -> None:
        self.module_mock.check_mode = True
        self.assert_check_call_only(False)

    def test_error_check(self) -> None:
        self.call_api_mock.return_value = (
            fixture.response_from_dto(
                fixture.task_result_dto(
                    result=None,
                    finish_type=TaskFinishType.UNHANDLED_EXCEPTION,
                    command=self.cmd_check_dto,
                )
            ),
            dict(status=200, body="some body data"),
        )

        pcs_qdevice_certs.pcs(
            self.module_mock, self.cmd_params, self.cmd_options
        )
        self.call_api_mock.assert_called_once_with(
            self.module_mock, self.cmd_check_dto
        )
        self.module_mock.exit_json.assert_not_called()
        self.module_mock.fail_json.assert_called_once_with(
            msg="Unhandled exception",
            changed=False,
            pcs_result=dict(
                task_ident="identifier",
                command={
                    "command_name": self.cmd_name_check,
                    "params": self.cmd_params,
                    "options": to_dict(self.cmd_options),
                },
                task_finish_type="TaskFinishType.UNHANDLED_EXCEPTION",
                result=None,
                reports=[],
                kill_reason=None,
            ),
        )

    def test_error_setup(self) -> None:
        self.call_api_mock.side_effect = [
            (
                fixture.response_from_dto(
                    fixture.task_result_dto(
                        result=False, command=self.cmd_check_dto
                    )
                ),
                dict(status=200, body="some body data"),
            ),
            (
                fixture.response_from_dto(
                    fixture.task_result_dto(
                        result=None,
                        finish_type=TaskFinishType.UNHANDLED_EXCEPTION,
                        command=self.cmd_setup_dto,
                    )
                ),
                dict(status=200, body="some body data"),
            ),
        ]

        pcs_qdevice_certs.pcs(
            self.module_mock, self.cmd_params, self.cmd_options
        )

        self.call_api_mock.assert_has_calls(
            [
                mock.call(self.module_mock, self.cmd_check_dto),
                mock.call(self.module_mock, self.cmd_setup_dto),
            ]
        )
        self.module_mock.exit_json.assert_not_called()
        self.module_mock.fail_json.assert_called_once_with(
            msg="Unhandled exception",
            changed=True,
            pcs_result=dict(
                task_ident="identifier",
                command={
                    "command_name": self.cmd_name_setup,
                    "params": self.cmd_params,
                    "options": to_dict(self.cmd_options),
                },
                task_finish_type="TaskFinishType.UNHANDLED_EXCEPTION",
                result=None,
                reports=[],
                kill_reason=None,
            ),
        )
