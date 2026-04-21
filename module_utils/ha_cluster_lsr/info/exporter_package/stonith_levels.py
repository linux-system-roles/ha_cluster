# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# SPDX-License-Identifier: MIT

# make ansible-test happy, even though the module requires Python 3
from __future__ import absolute_import, division, print_function

# make ansible-test happy, even though the module requires Python 3
# pylint: disable=invalid-name
__metaclass__ = type

from typing import Any, Dict, List

from .wrap_src import SrcDict, wrap_src_for_rich_report


@wrap_src_for_rich_report(dict(stonith_levels="stonith levels configuration"))
def export_stonith_levels(stonith_levels: SrcDict) -> List[Dict[str, Any]]:
    """
    Export stonith levels from `pcs stonith level config --output-format=json`
    output
    """
    return (
        [
            {
                "level": item["index"],
                "target": item["target"],
                "resource_ids": list(item["devices"]),
            }
            for item in stonith_levels["target_node"]
        ]
        + [
            {
                "level": item["index"],
                "target_pattern": item["target_pattern"],
                "resource_ids": list(item["devices"]),
            }
            for item in stonith_levels["target_regex"]
        ]
        + [
            {
                "level": item["index"],
                "target_attribute": item["target_attribute"],
                **(
                    {"target_value": item["target_value"]}
                    if item["target_value"]
                    else {}
                ),
                "resource_ids": list(item["devices"]),
            }
            for item in stonith_levels["target_attribute"]
        ]
    )
