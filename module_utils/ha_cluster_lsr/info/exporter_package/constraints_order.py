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

from .options import to_options
from .resource_set import export_resource_set
from .wrap_src import SrcDict, invalid_part, wrap_src_for_rich_report


def _first(order_src: SrcDict) -> Dict[str, Any]:
    if not order_src["first_resource_id"]:
        raise invalid_part(
            order_src,
            "Order is missing first_resource_id",
        )

    resource = {"id": order_src["first_resource_id"]}

    if order_src["first_action"]:
        resource["action"] = order_src["first_action"]

    return resource


def _then(order_src: SrcDict) -> Dict[str, Any]:
    if not order_src["then_resource_id"]:
        raise invalid_part(
            order_src,
            "Order is missing then_resource_id",
        )

    resource = {"id": order_src["then_resource_id"]}

    if order_src["then_action"]:
        resource["action"] = order_src["then_action"]

    return resource


def _options(attributes_src: SrcDict) -> List[Any]:
    return to_options(
        attributes_src,
        "score",
        "kind",
        "symmetrical",
        ("require_all", "require-all"),
    )


def _order(order_src: SrcDict) -> Dict[str, Any]:
    order = {
        "id": order_src["attributes"]["constraint_id"],
        "resource_first": _first(order_src),
        "resource_then": _then(order_src),
    }

    options = _options(order_src["attributes"])
    if options:
        order["options"] = options

    return order


def _order_set(order_set_src: SrcDict) -> Dict[str, Any]:
    if not order_set_src["resource_sets"]:
        raise invalid_part(order_set_src, "Order is missing resource_sets")

    order_set = {
        "id": order_set_src["attributes"]["constraint_id"],
        "resource_sets": [
            export_resource_set(resource_set)
            for resource_set in order_set_src["resource_sets"]
        ],
    }

    options = _options(order_set_src["attributes"])
    if options:
        order_set["options"] = options

    return order_set


@wrap_src_for_rich_report(dict(constraints="constraints configuration"))
def export_order_constraints(constraints: SrcDict) -> List[Dict[str, Any]]:
    """
    Export order constraints from `pcs constraint --all --output-format=json`
    output
    """
    return [_order(order) for order in constraints["order"]] + [
        _order_set(order_set) for order_set in constraints["order_set"]
    ]
