# -*- coding: utf-8 -*-

# Copyright (C) 2023 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# pylint: disable=missing-function-docstring

import json
import sys
from http.client import HTTPResponse
from unittest import mock

# Add paths to pcs bundled libraries to make Dacite available
sys.path.insert(0, "/usr/lib64/pcs/pcs_bundled/packages/")
sys.path.insert(0, "/usr/lib/pcs/pcs_bundled/packages/")

from typing import Any, Iterable, Optional

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
from pcs.common.reports.dto import ReportItemDto


def response(data: str) -> HTTPResponse:
    response_mock = mock.Mock()
    response_mock.read.return_value = data
    return response_mock


def response_from_dto(dto: TaskResultDto) -> HTTPResponse:
    return response(json.dumps(to_dict(dto)))


def task_result_dto(
    finish_type: TaskFinishType = TaskFinishType.SUCCESS,
    reports: Iterable[ReportItemDto] = (),
    kill_reason: Optional[TaskKillReason] = None,
    result: Any = None,
    command: Optional[CommandDto] = None,
) -> TaskResultDto:
    command = command or CommandDto(
        command_name="test-command",
        params={},
        options=CommandOptionsDto(),
    )
    return TaskResultDto(
        task_ident="identifier",
        command=command,
        reports=list(reports),
        state=TaskState.FINISHED,
        task_finish_type=finish_type,
        kill_reason=kill_reason,
        result=result,
    )
