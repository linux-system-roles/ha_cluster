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
sys.modules["ansible.module_utils.ha_cluster_lsr.info.exporter_package"] = (
    import_module("ha_cluster_lsr.info.exporter_package")
)

ha_cluster_info = import_module("ha_cluster_info")
exporter = getattr(import_module("ha_cluster_lsr.info"), "exporter")
exporter_package = getattr(
    import_module("ha_cluster_lsr.info"), "exporter_package"
)
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
    calls, side_effect = zip(*runner_calls) if runner_calls else ([], [])
    module_mock = mock.Mock(run_command=mock.Mock(side_effect=side_effect))

    yield module_mock

    if not calls:
        module_mock.run_command.assert_not_called()
        return

    module_mock.run_command.assert_has_calls(calls)

    if module_mock.run_command.call_count != len(calls):
        raise AssertionError(
            "AnsibleModule.run_command expected to be run"
            f" {len(calls)} times"
            f" but actually ran {module_mock.run_command.call_count} times."
            f"\nExpected:\n{calls}"
            f"\nActual:\n{module_mock.run_command.call_args_list}"
        )
