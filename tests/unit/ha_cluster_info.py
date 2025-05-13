#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

import sys
from contextlib import contextmanager
from importlib import import_module
from typing import Generator, List, Optional, Tuple
from unittest import mock

sys.modules["ansible.module_utils.ha_cluster_lsr"] = import_module(
    "ha_cluster_lsr"
)
sys.modules["ansible.module_utils.ha_cluster_lsr.info"] = import_module(
    "ha_cluster_lsr.info"
)

ha_cluster_info = import_module("ha_cluster_info")
exporter = getattr(import_module("ha_cluster_lsr.info"), "exporter")
loader = getattr(import_module("ha_cluster_lsr.info"), "loader")


# pylint: disable=missing-function-docstring
@contextmanager
def mocked_module(
    runner_calls: Optional[
        List[
            Tuple[
                mock._Call,
                Tuple[int, str, str],
            ]
        ]
    ] = None,
) -> Generator:
    module_mock = mock.Mock()
    module_mock.run_command = mock.Mock(
        side_effect=(
            [call[1] for call in runner_calls]
            if runner_calls is not None
            else []
        )
    )

    yield module_mock

    if runner_calls is None:
        module_mock.run_command.assert_not_called()
        return

    if module_mock.run_command.call_count != len(runner_calls):
        raise AssertionError(
            f"AnsibleModule.run_command expected to be run"
            f" {module_mock.run_command.call_count} times"
            f" but actually ran {len(runner_calls)} times"
        )

    module_mock.run_command.assert_has_calls([call[0] for call in runner_calls])
