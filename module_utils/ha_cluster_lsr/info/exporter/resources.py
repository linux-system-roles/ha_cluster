# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# make ansible-test happy, even though the module requires Python 3
from __future__ import absolute_import, division, print_function

# make ansible-test happy, even though the module requires Python 3
# pylint: disable=invalid-name
__metaclass__ = type

from typing import Any, Dict, List

from .nvset import dict_to_nv_list

# This module is exports InvalidSrc
# pylint: disable=unused-import
from .wrap_src import (
    InvalidSrc,
    SrcDict,
    invalid_part,
    is_none,
    wrap_src_for_rich_report,
)

_PRIMITIVE_OPERATION_NON_ATTR_KEYS = [
    "id",
    "name",
    "meta_attributes",
    "instance_attributes",
]


def nvsets_to_nv_list(nvsets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Shortcut to transform common nvset structure to lsr variant"""
    return (
        [
            dict(
                name=nvpair_src["name"],
                value=nvpair_src["value"],
            )
            for nvpair_src in nvsets[0]["nvpairs"]
        ]
        if nvsets and len(nvsets) > 0
        else []
    )


@wrap_src_for_rich_report("resources", data_desc="resources configuration")
def export_primitive_list(resources: SrcDict) -> List[Dict[str, Any]]:
    """Export primitive resources from `pcs resource configuration` output"""
    result = []
    for primitive_src in resources["primitives"]:
        agent_src = primitive_src["agent_name"]
        primitive = dict(
            id=primitive_src["id"],
            # Use just operation taken from CIB
            copy_operations_from_agent=False,
            agent=(
                ":".join(
                    [
                        agent_src["standard"],
                        agent_src["provider"],
                        agent_src["type"],
                    ]
                    if agent_src["provider"]
                    else [
                        agent_src["standard"],
                        agent_src["type"],
                    ]
                )
            ),
        )

        # instance attrs
        instance_attrs = nvsets_to_nv_list(
            primitive_src.get("instance_attributes", [])
        )
        if instance_attrs:
            primitive["instance_attrs"] = [dict(attrs=instance_attrs)]

        # meta attrs
        meta_attrs = nvsets_to_nv_list(primitive_src.get("meta_attributes", []))
        if meta_attrs:
            primitive["meta_attrs"] = [dict(attrs=meta_attrs)]

        # utilization
        utilization = nvsets_to_nv_list(primitive_src.get("utilization", []))
        if utilization:
            primitive["utilization"] = [dict(attrs=utilization)]

        # operations
        operation_list = []
        for operation_src in primitive_src.get("operations", []):
            attrs = dict_to_nv_list(
                {
                    key: value
                    for key, value in operation_src.items()
                    if key not in _PRIMITIVE_OPERATION_NON_ATTR_KEYS
                    and not is_none(value)
                }
            )
            if not attrs:
                raise invalid_part(operation_src, "No attributes in operation")
            operation_list.append(
                dict(action=operation_src["name"], attrs=attrs)
            )
        if operation_list:
            primitive["operations"] = operation_list

        result.append(primitive)
    return result
