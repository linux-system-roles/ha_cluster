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


def _attrs(
    nvsets: List[Dict[str, Any]],
) -> List[Dict[str, List[Dict[str, Any]]]]:
    """Shortcut to transform common nvset structure to lsr variant"""
    if len(nvsets) < 1:
        return []

    return [
        dict(
            attrs=[
                dict(name=nvpair_src["name"], value=nvpair_src["value"])
                for nvpair_src in nvsets[0]["nvpairs"]
            ]
        )
    ]


def _operations(
    operation_list_src: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    operation_list = []
    for operation_src in operation_list_src:
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
        operation_list.append(dict(action=operation_src["name"], attrs=attrs))
    return operation_list


def _agent(agent_src: Dict[str, Any]) -> str:
    return ":".join(
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


def _primitive(
    primitive_src: Dict[str, Any], use_utilization: bool = True
) -> Dict[str, Any]:
    primitive = dict(
        id=primitive_src["id"],
        # Use just operation taken from CIB
        copy_operations_from_agent=False,
        agent=_agent(primitive_src["agent_name"]),
    )

    instance_attrs = _attrs(primitive_src.get("instance_attributes", []))
    if instance_attrs:
        primitive["instance_attrs"] = instance_attrs

    meta_attrs = _attrs(primitive_src.get("meta_attributes", []))
    if meta_attrs:
        primitive["meta_attrs"] = meta_attrs

    if use_utilization:
        utilization = _attrs(primitive_src.get("utilization", []))
        if utilization:
            primitive["utilization"] = utilization

    operations = _operations(primitive_src.get("operations", []))
    if operations:
        primitive["operations"] = operations
    return primitive


@wrap_src_for_rich_report(
    "resources",
    "stonith",
    data_desc=["resources configuration", "stonith configuration"],
)
def export_primitive_list(
    resources: SrcDict, stonith: SrcDict
) -> List[Dict[str, Any]]:
    """Export primitive resources from `pcs resource configuration` output"""
    result = []
    for primitive_src in resources["primitives"]:
        result.append(_primitive(primitive_src))

    for primitive_src in stonith["primitives"]:
        result.append(_primitive(primitive_src, use_utilization=False))
    return result
