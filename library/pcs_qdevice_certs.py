#!/usr/bin/python
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

DOCUMENTATION = r"""
---
module: pcs_qdevice_certs
short_description: Setup qdevice certificates on a node
description: >
    This module sets up qdevice certificates for a given qnetd host and cluster
    name on a cluster node. Check mode is supported.
author:
    - Tomas Jelinek (@tomjelinek)
requirements:
    - pcs-0.11.4 or newer installed on managed nodes
    - python 3.9 or newer (it is a dependency of pcs anyway)
options:
    qnetd_host:
        description: address of a qnetd host
        required: true
        type: str
    cluster_name:
        description: name of the cluster the node belongs to
        required: true
        type: str
    cmd_options:
        description: pcs API v2 command options
        type: dict
        default: {}
        suboptions:
            request_timeout:
                description: request timeout
                type: int
            effective_username:
                description: drop privileges to the specified user
                type: str
            effective_groups:
                description: drop privileges to the specified user groups
                type: list
                elements: str
"""

EXAMPLES = r"""
- name: Configure qdevice certificates
  pcs_qdevice_certs:
    qnetd_host: qnetd-node
    cluster_name: my-cluster
"""

RETURN = r"""
pcs_result:
    description: Result of the pcs API call
    type: dict
    returned: when the command is valid and accepted by API
    contains:
        task_ident:
            description: Pcs internal task ID, for debugging purposes.
            type: str
            returned: when the command is valid and accepted by API
        task_finish_type:
            description: Denotes whether the command finished successfully.
            type: str
            returned: when the command is valid and accepted by API
        result:
            description: >
                Data returned by the command. The field does not have any
                useful meaning in this module.
            type: bool
            returned: when the command is valid and accepted by API
        reports:
            description: Messages produced by the command being processed.
            type: list
            elements: dict
            returned: when the command is valid and accepted by API
            contains:
                code:
                    description: Message type identifier.
                    type: str
                message:
                    description: Human-readable representation of the message.
                    type: str
                payload:
                    description: Parameters of the message.
                    type: dict
                severity:
                    description: Severity of the message.
                    type: str
                force_code:
                    description: Means to override the message.
                    type: str
                node:
                    description: Node the message originates from or None.
                    type: str
        kill_reason:
            description: Denotes why the command was killed, if that happened.
            type: str
            returned: when the command is valid and accepted by API
"""

import traceback

from ansible.module_utils.basic import AnsibleModule

# pylint: disable=no-name-in-module
from ansible.module_utils.ha_cluster_lsr import pcs_api_v2_utils as api_utils

# pylint: enable=no-name-in-module
try:
    from pcs.common.async_tasks.dto import CommandDto, CommandOptionsDto
except ImportError:
    HAS_PCS = False
    PCS_IMPORT_ERROR = traceback.format_exc()

    class CommandOptionsDto(object):
        def __init__(self, **kwargs):
            pass

    class CommandDto(object):
        pass

else:
    HAS_PCS = True
    PCS_IMPORT_ERROR = None


def run_module() -> None:
    """
    Top level module function
    """
    module_args = dict(
        qnetd_host=dict(type="str", required=True),
        cluster_name=dict(type="str", required=True),
        cmd_options=api_utils.cmd_options_params_definition(),
    )
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    command_params = dict(
        qnetd_host=module.params["qnetd_host"],
        cluster_name=module.params["cluster_name"],
    )
    pcs(module, command_params, api_utils.get_command_options_dto(module))


def pcs(
    module: AnsibleModule,
    command_params: api_utils.CommandParams,
    command_options: CommandOptionsDto,
) -> None:
    """
    Use pcs api to configure qdevice certificates
    """
    # pylint: disable= too-many-return-statements
    check_command = CommandDto(
        command_name="quorum.device_net_certificate_check_local",
        params=command_params,
        options=command_options,
    )
    try:
        check_response = api_utils.call_api(module, check_command)
        if check_response.result is True:
            return module.exit_json(
                changed=False,
                pcs_result=api_utils.api_result_to_dict(check_response),
            )
        if module.check_mode:
            return module.exit_json(
                changed=True,
                pcs_result=api_utils.api_result_to_dict(check_response),
            )
    except api_utils.TaskFailedError as exc:
        return module.fail_json(
            msg=exc.msg, changed=False, pcs_result=exc.api_result
        )
    except api_utils.ApiError as exc:
        return module.fail_json(msg=exc.msg)

    setup_command = CommandDto(
        command_name="quorum.device_net_certificate_setup_local",
        params=command_params,
        options=command_options,
    )
    try:
        setup_response = api_utils.call_api(module, setup_command)
        return module.exit_json(
            changed=True,
            pcs_result=api_utils.api_result_to_dict(setup_response),
        )
    except api_utils.TaskFailedError as exc:
        return module.fail_json(
            msg=exc.msg, changed=True, pcs_result=exc.api_result
        )
    except api_utils.ApiError as exc:
        return module.fail_json(msg=exc.msg)


def main() -> None:
    """
    Entry point
    """
    run_module()


if __name__ == "__main__":
    main()
