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
module: pcs_api_v2
short_description: Exposes pcs API v2 to manage HA Cluster
description: >
    WARNING: Do not use this module directly. It is meant for role internal
    use. The module directly exposes pcs API v2 so that it is possible to use
    the API to manage HA Clusters. Since the API doesn't support check mode,
    the module doesn't support it either. It is the responsibility of the
    module user to set check mode options for all tasks using this module.
author:
    - Tomas Jelinek (@tomjelinek)
requirements:
    - pcs-0.11.4 or newer installed on managed nodes (the role handles that)
    - python 3.9 or newer (it is a dependency of pcs anyway)
options:
    cmd_name:
        description: pcs API v2 command name
        required: true
        type: str
    cmd_params:
        description: parameters of the command specified in cmd_name
        type: dict
        default: {}
    cmd_options:
        description: generic command options
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
- name: Check if qdevice certificates are already set
  pcs_api_v2:
    cmd_name: quorum.device_net_certificate_check_local
    cmd_params:
      qnetd_host: qnetd-node
      cluster_name: my-cluster
  check_mode: false
  changed_when: false
  register: __ha_cluster_qdevice_certs
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
                Data returned by the command. Data type, format and content
                depend on the command called.
            type: dict
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
from typing import Optional

from ansible.module_utils.basic import AnsibleModule

# pylint: disable=no-name-in-module
from ansible.module_utils.ha_cluster_lsr import pcs_api_v2_utils as api_utils

# pylint: enable=no-name-in-module
try:
    from pcs.common.async_tasks.dto import CommandDto, CommandOptionsDto
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

    class CommandDto:  # type: ignore
        pass

else:
    HAS_PCS = True
    PCS_IMPORT_ERROR = None


def run_module() -> None:
    """
    Top level module function
    """
    module_args = dict(
        cmd_name=dict(type="str", required=True),
        cmd_params=dict(type="dict", default=dict()),
        # 'options' has a specific meaning, so we cannot use that name and we
        # need to diverge from CommandDto
        cmd_options=api_utils.cmd_options_params_definition(),
    )
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)
    command_name = module.params["cmd_name"]
    command_params = module.params.get("cmd_params", dict())
    pcs(
        module,
        command_name,
        command_params,
        api_utils.get_command_options_dto(module),
    )


def pcs(
    module: AnsibleModule,
    command_name: str,
    command_params: api_utils.CommandParams,
    command_options: CommandOptionsDto,
) -> None:
    """
    Run pcs api command
    """
    api_command = CommandDto(command_name, command_params, command_options)
    try:
        api_result_dto = api_utils.call_api(module, api_command)
        return module.exit_json(
            # This is a generic gateway to the pcs API. It doesn't know what
            # the called command does. To be on the safe side, it always
            # returns changed = True. If a read-only command is called using
            # this module, specify changed_when in the ansible task.
            changed=True,
            pcs_result=api_utils.api_result_to_dict(api_result_dto),
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
