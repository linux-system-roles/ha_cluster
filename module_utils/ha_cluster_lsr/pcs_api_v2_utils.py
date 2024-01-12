# -*- coding: utf-8 -*-

# Copyright (C) 2023 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# make ansible-test happy, even though the module requires Python 3.9
from __future__ import absolute_import, division, print_function

# make ansible-test happy, even though the module requires Python 3.9
# pylint: disable=invalid-name
__metaclass__ = type
# pylint: enable=invalid-name

import sys
import traceback

# Add paths to pcs bundled libraries to make Dacite available
sys.path.insert(0, "/usr/lib64/pcs/pcs_bundled/packages/")
sys.path.insert(0, "/usr/lib/pcs/pcs_bundled/packages/")

from http.client import HTTPResponse
from json import JSONDecodeError
from typing import Any, Mapping, Optional, Union

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url

try:
    from dacite import DaciteError
except ImportError:
    HAS_DACITE = False
    DACITE_IMPORT_ERROR: Optional[str] = traceback.format_exc()
else:
    HAS_DACITE = True
    DACITE_IMPORT_ERROR = None

try:
    from pcs.common.async_tasks.dto import (
        CommandDto,
        CommandOptionsDto,
        TaskResultDto,
    )
    from pcs.common.async_tasks.types import TaskFinishType, TaskKillReason
    from pcs.common.interface.dto import from_dict, to_dict
    from pcs.common.reports import ReportItemDto, ReportItemSeverity
except ImportError:
    HAS_PCS = False
    PCS_IMPORT_ERROR: Optional[str] = traceback.format_exc()

    # These classes need to be available and imported above to do linting
    # properly, linters can be safely silenced for these stubs.

    # pylint: disable=missing-class-docstring
    # pylint: disable=too-few-public-methods
    class CommandOptionsDto:  # type: ignore
        def __init__(self, **kwargs):  # type: ignore
            pass

    class ReportItemDto:  # type: ignore
        pass

    class TaskResultDto:  # type: ignore
        pass

    class CommandDto:  # type: ignore
        pass

else:
    HAS_PCS = True
    PCS_IMPORT_ERROR = None

PCSD_SOCKET = "/var/run/pcsd.socket"
API_ENDPOINT = "http://doesntmatter/api/v2/task/run"


CommandParams = Mapping[str, Any]


class ApiError(Exception):
    # pylint: disable=missing-class-docstring
    def __init__(self, msg: str):
        self.msg = msg


class ResponseFormatError(ApiError):
    # pylint: disable=missing-class-docstring
    pass


class TaskFailedError(ApiError):
    # pylint: disable=missing-class-docstring
    def __init__(self, msg: str, api_result: Mapping[str, Any]):
        super().__init__(msg)
        self.api_result = api_result


def cmd_options_params_definition() -> dict[str, Any]:
    """
    Provide ansible module params definition for cmd_options option
    """
    return dict(
        type="dict",
        default=dict(),
        options=dict(
            request_timeout=dict(type="int", required=False),
            effective_username=dict(type="str", required=False),
            effective_groups=dict(type="list", elements="str", required=False),
        ),
    )


def get_command_options_dto(module: AnsibleModule) -> CommandOptionsDto:
    """
    Extract command options from parameters passed to ansible module
    """
    cmd_options = module.params.get("cmd_options", dict())
    return CommandOptionsDto(
        request_timeout=cmd_options.get("request_timeout"),
        effective_username=cmd_options.get("effective_username"),
        effective_groups=cmd_options.get("effective_groups"),
    )


def report_item_to_dict(
    report_item: ReportItemDto,
) -> dict[str, Union[None, str, Mapping[str, Any]]]:
    """
    Convert report item structure to a dict passed back to ansible
    """
    message = report_item.message.message
    if report_item.context:
        message = f"{report_item.context.node}: {message}"
    message = f"{report_item.severity.level}: {message}"
    return dict(
        code=report_item.message.code,
        message=message,
        payload=report_item.message.payload,
        severity=report_item.severity.level,
        force_code=report_item.severity.force_code,
        node=report_item.context.node if report_item.context else None,
    )


def api_result_to_dict(api_result: TaskResultDto) -> dict[str, Any]:
    """
    Convert API result structure to a dict passed back to ansible
    """
    return dict(
        task_ident=api_result.task_ident,
        command=to_dict(api_result.command),
        task_finish_type=str(api_result.task_finish_type),
        result=api_result.result,
        reports=[
            report_item_to_dict(report_item)
            for report_item in api_result.reports
        ],
        kill_reason=(
            str(api_result.kill_reason) if api_result.kill_reason else None
        ),
    )


def parse_api_response(
    module: AnsibleModule, response_data: bytes
) -> TaskResultDto:
    """
    Process API response, return parsed API call result or raise ApiError
    """
    # pylint: disable=too-many-return-statements
    try:
        api_result_dto = from_dict(
            TaskResultDto, module.from_json(response_data)
        )
    except (JSONDecodeError, DaciteError) as exc:
        raise ResponseFormatError(
            f"Unable to parse API response: {exc}\n{response_data!r}"
        ) from exc

    # handle errors
    if api_result_dto.task_finish_type == TaskFinishType.FAIL:
        raise TaskFailedError("Task failed", api_result_to_dict(api_result_dto))
    if api_result_dto.task_finish_type == TaskFinishType.KILL:
        if api_result_dto.kill_reason == TaskKillReason.COMPLETION_TIMEOUT:
            raise TaskFailedError(
                "Task processing timed out", api_result_to_dict(api_result_dto)
            )
        raise TaskFailedError("Task killed", api_result_to_dict(api_result_dto))
    if api_result_dto.task_finish_type == TaskFinishType.UNHANDLED_EXCEPTION:
        raise TaskFailedError(
            "Unhandled exception", api_result_to_dict(api_result_dto)
        )

    # search for errors in reports and fail if the command failed
    error_list = [
        str(report_item_to_dict(report_item)["message"])
        for report_item in api_result_dto.reports
        if report_item.severity.level == ReportItemSeverity.ERROR
    ]
    if error_list:
        raise TaskFailedError(
            "\n".join([error for error in error_list if error]),
            api_result_to_dict(api_result_dto),
        )

    return api_result_dto


def call_api_raw(
    module: AnsibleModule, api_command: CommandDto
) -> tuple[HTTPResponse, dict[str, Any]]:
    """
    Execute an API call
    """
    response, info = fetch_url(
        module,
        force=True,  # do not get a cached response
        unix_socket=PCSD_SOCKET,
        url=API_ENDPOINT,
        method="POST",
        headers={"Content-Type": "application/json"},
        data=module.jsonify(to_dict(api_command)),
    )
    return response, info


def call_api(module: AnsibleModule, api_command: CommandDto) -> TaskResultDto:
    """
    Call API and process common errors, parse response
    """
    response, info = call_api_raw(module, api_command)
    # handle returned API errors
    if info["status"] >= 400:
        raise ResponseFormatError(info["body"])
    if response is None:
        if "msg" in info:
            raise ResponseFormatError(info["msg"])
        raise ResponseFormatError(str(info))
    return parse_api_response(module, response.read())
