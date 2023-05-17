# -*- coding: utf-8 -*-

# Copyright (C) 2023 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import json
from typing import Any
from unittest import TestCase, mock

from ha_cluster_lsr import pcs_api_v2_utils
from pcs.common.async_tasks.dto import (
    CommandDto,
    CommandOptionsDto,
    TaskResultDto,
)
from pcs.common.async_tasks.types import (
    TaskFinishType,
    TaskKillReason,
    TaskState,
)
from pcs.common.interface.dto import to_dict
from pcs.common.reports import ReportItemSeverity
from pcs.common.reports.dto import (
    ReportItemContextDto,
    ReportItemDto,
    ReportItemMessageDto,
    ReportItemSeverityDto,
)
from pcs.common.reports.types import ForceCode, MessageCode

from . import fixture

fixture_api_result_command_dict: dict[str, Any] = {
    "command_name": "test-command",
    "params": {},
    "options": {
        "effective_groups": None,
        "effective_username": None,
        "request_timeout": None,
    },
}
fixture_api_result_dict_minimal: dict[str, Any] = {
    "task_ident": "identifier",
    "command": fixture_api_result_command_dict,
    "task_finish_type": str(TaskFinishType.SUCCESS),
    "result": None,
    "reports": [],
    "kill_reason": None,
}


class ReportItemToDict(TestCase):
    def test_minimal(self) -> None:
        dto = ReportItemDto(
            severity=ReportItemSeverityDto(
                level=ReportItemSeverity.WARNING,
                force_code=None,
            ),
            message=ReportItemMessageDto(
                code=MessageCode("CODE"),
                message="text message",
                payload={},
            ),
            context=None,
        )
        self.assertEqual(
            pcs_api_v2_utils.report_item_to_dict(dto),
            {
                "code": "CODE",
                "force_code": None,
                "message": "WARNING: text message",
                "node": None,
                "payload": {},
                "severity": "WARNING",
            },
        )

    def test_all_params(self) -> None:
        payload = {"param1": "value1", "param2": "value2"}
        dto = ReportItemDto(
            severity=ReportItemSeverityDto(
                level=ReportItemSeverity.ERROR,
                force_code=ForceCode("FORCE"),
            ),
            message=ReportItemMessageDto(
                code=MessageCode("CODE"),
                message="text message",
                payload=payload,
            ),
            context=ReportItemContextDto(node="node1"),
        )
        self.assertEqual(
            pcs_api_v2_utils.report_item_to_dict(dto),
            {
                "code": "CODE",
                "force_code": "FORCE",
                "message": "ERROR: node1: text message",
                "node": "node1",
                "payload": payload,
                "severity": "ERROR",
            },
        )


class ApiResultToDict(TestCase):
    maxDiff = None

    def test_minimal(self) -> None:
        self.assertEqual(
            pcs_api_v2_utils.api_result_to_dict(fixture.task_result_dto()),
            fixture_api_result_dict_minimal,
        )

    def test_all_params(self) -> None:
        result = {"some": "result", "with": ["complex", "value"]}
        dto = TaskResultDto(
            task_ident="identifier",
            command=CommandDto(
                command_name="test-command",
                params={"param1": "value1", "param2": "value2"},
                options=CommandOptionsDto(
                    request_timeout=10,
                    effective_username="user",
                    effective_groups=["group1", "group2"],
                ),
            ),
            reports=[
                ReportItemDto(
                    severity=ReportItemSeverityDto(
                        level=ReportItemSeverity.INFO,
                        force_code=None,
                    ),
                    message=ReportItemMessageDto(
                        code=MessageCode("CODE"),
                        message=f"text message {i}",
                        payload={},
                    ),
                    context=None,
                )
                for i in range(2)
            ],
            state=TaskState.FINISHED,
            task_finish_type=TaskFinishType.KILL,
            kill_reason=TaskKillReason.COMPLETION_TIMEOUT,
            result=result,
        )
        self.assertEqual(
            pcs_api_v2_utils.api_result_to_dict(dto),
            {
                "task_ident": "identifier",
                "command": {
                    "command_name": "test-command",
                    "params": {"param1": "value1", "param2": "value2"},
                    "options": {
                        "request_timeout": 10,
                        "effective_username": "user",
                        "effective_groups": ["group1", "group2"],
                    },
                },
                "task_finish_type": str(TaskFinishType.KILL),
                "result": result,
                "reports": [
                    {
                        "code": "CODE",
                        "force_code": None,
                        "message": f"INFO: text message {i}",
                        "node": None,
                        "payload": {},
                        "severity": "INFO",
                    }
                    for i in range(2)
                ],
                "kill_reason": str(TaskKillReason.COMPLETION_TIMEOUT),
            },
        )


class ParseApiResponse(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.module = mock.Mock()
        self.module.from_json = json.loads

    def test_success(self) -> None:
        result = pcs_api_v2_utils.parse_api_response(
            self.module, json.dumps(to_dict(fixture.task_result_dto())).encode()
        )
        self.assertEqual(result, fixture.task_result_dto())

    def test_response_not_json(self) -> None:
        with self.assertRaises(pcs_api_v2_utils.ResponseFormatError) as context:
            pcs_api_v2_utils.parse_api_response(self.module, b"random data")
        self.assertEqual(
            context.exception.msg,
            (
                "Unable to parse API response: Expecting value: line 1 "
                "column 1 (char 0)\nb'random data'"
            ),
        )

    def test_bad_response_structure(self) -> None:
        with self.assertRaises(pcs_api_v2_utils.ResponseFormatError) as context:
            pcs_api_v2_utils.parse_api_response(self.module, b'{"a": "b"}')
        self.assertEqual(
            context.exception.msg,
            (
                "Unable to parse API response: missing value for "
                """field "task_ident"\nb'{"a": "b"}'"""
            ),
        )

    def test_fail(self) -> None:
        with self.assertRaises(pcs_api_v2_utils.TaskFailedError) as context:
            pcs_api_v2_utils.parse_api_response(
                self.module,
                json.dumps(
                    to_dict(
                        fixture.task_result_dto(finish_type=TaskFinishType.FAIL)
                    )
                ).encode(),
            )
        self.assertEqual(context.exception.msg, "Task failed")
        self.assertEqual(
            context.exception.api_result,
            dict(
                task_ident="identifier",
                command=fixture_api_result_command_dict,
                task_finish_type="TaskFinishType.FAIL",
                result=None,
                reports=[],
                kill_reason=None,
            ),
        )

    def test_timeout(self) -> None:
        with self.assertRaises(pcs_api_v2_utils.TaskFailedError) as context:
            pcs_api_v2_utils.parse_api_response(
                self.module,
                json.dumps(
                    to_dict(
                        fixture.task_result_dto(
                            finish_type=TaskFinishType.KILL,
                            kill_reason=TaskKillReason.COMPLETION_TIMEOUT,
                        )
                    )
                ).encode(),
            )
        self.assertEqual(context.exception.msg, "Task processing timed out")
        self.assertEqual(
            context.exception.api_result,
            dict(
                task_ident="identifier",
                command=fixture_api_result_command_dict,
                task_finish_type="TaskFinishType.KILL",
                result=None,
                reports=[],
                kill_reason="TaskKillReason.COMPLETION_TIMEOUT",
            ),
        )

    def test_killed(self) -> None:
        with self.assertRaises(pcs_api_v2_utils.TaskFailedError) as context:
            pcs_api_v2_utils.parse_api_response(
                self.module,
                json.dumps(
                    to_dict(
                        fixture.task_result_dto(
                            finish_type=TaskFinishType.KILL,
                            kill_reason=TaskKillReason.USER,
                        )
                    )
                ).encode(),
            )
        self.assertEqual(context.exception.msg, "Task killed")
        self.assertEqual(
            context.exception.api_result,
            dict(
                command=fixture_api_result_command_dict,
                task_ident="identifier",
                task_finish_type="TaskFinishType.KILL",
                result=None,
                reports=[],
                kill_reason="TaskKillReason.USER",
            ),
        )

    def test_exception(self) -> None:
        with self.assertRaises(pcs_api_v2_utils.TaskFailedError) as context:
            pcs_api_v2_utils.parse_api_response(
                self.module,
                json.dumps(
                    to_dict(
                        fixture.task_result_dto(
                            finish_type=TaskFinishType.UNHANDLED_EXCEPTION,
                        )
                    )
                ).encode(),
            )
        self.assertEqual(context.exception.msg, "Unhandled exception")
        self.assertEqual(
            context.exception.api_result,
            dict(
                task_ident="identifier",
                command=fixture_api_result_command_dict,
                task_finish_type="TaskFinishType.UNHANDLED_EXCEPTION",
                result=None,
                reports=[],
                kill_reason=None,
            ),
        )

    def test_errors_reported(self) -> None:
        with self.assertRaises(pcs_api_v2_utils.TaskFailedError) as context:
            pcs_api_v2_utils.parse_api_response(
                self.module,
                json.dumps(
                    to_dict(
                        fixture.task_result_dto(
                            reports=[
                                ReportItemDto(
                                    severity=ReportItemSeverityDto(
                                        ReportItemSeverity.ERROR, None
                                    ),
                                    message=ReportItemMessageDto(
                                        code=MessageCode("ERROR_1"),
                                        message="error text message 1",
                                        payload={},
                                    ),
                                    context=None,
                                ),
                                ReportItemDto(
                                    severity=ReportItemSeverityDto(
                                        ReportItemSeverity.ERROR, None
                                    ),
                                    message=ReportItemMessageDto(
                                        code=MessageCode("ERROR_2"),
                                        message="error text message 2",
                                        payload={},
                                    ),
                                    context=None,
                                ),
                            ],
                        )
                    )
                ).encode(),
            )
        self.assertEqual(
            context.exception.msg,
            "ERROR: error text message 1\nERROR: error text message 2",
        )
        self.assertEqual(
            context.exception.api_result,
            dict(
                task_ident="identifier",
                command=fixture_api_result_command_dict,
                task_finish_type="TaskFinishType.SUCCESS",
                result=None,
                reports=[
                    {
                        "code": "ERROR_1",
                        "message": "ERROR: error text message 1",
                        "payload": {},
                        "severity": "ERROR",
                        "force_code": None,
                        "node": None,
                    },
                    {
                        "code": "ERROR_2",
                        "message": "ERROR: error text message 2",
                        "payload": {},
                        "severity": "ERROR",
                        "force_code": None,
                        "node": None,
                    },
                ],
                kill_reason=None,
            ),
        )
