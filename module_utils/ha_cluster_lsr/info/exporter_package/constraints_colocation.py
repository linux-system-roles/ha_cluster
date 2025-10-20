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

from .wrap_src import SrcDict, invalid_part, wrap_src_for_rich_report


def _leader(colocation_src: SrcDict) -> Dict[str, Any]:
    if not colocation_src["resource_id"]:
        raise invalid_part(
            colocation_src,
            "Colocation is missing resource_id",
        )

    resource = {"id": colocation_src["resource_id"]}

    if colocation_src["resource_role"]:
        resource["role"] = colocation_src["resource_role"]

    return resource


def _follower(colocation_src: SrcDict) -> Dict[str, Any]:
    if not colocation_src["with_resource_id"]:
        raise invalid_part(
            colocation_src,
            "Colocation is missing with_resource_id",
        )

    resource = {"id": colocation_src["with_resource_id"]}

    if colocation_src["with_resource_role"]:
        resource["role"] = colocation_src["with_resource_role"]

    return resource


def _options(attributes_src: SrcDict) -> List[Any]:
    options = []

    if attributes_src["score"]:
        options.append(
            {
                "name": "score",
                "value": attributes_src["score"],
            }
        )

    if attributes_src["influence"]:
        options.append(
            {
                "name": "influence",
                "value": attributes_src["influence"],
            }
        )

    return options


def _colocation(colocation_src: SrcDict) -> Dict[str, Any]:
    colocation = {
        "id": colocation_src["attributes"]["constraint_id"],
        "resource_leader": _leader(colocation_src),
        "resource_follower": _follower(colocation_src),
    }

    options = _options(colocation_src["attributes"])
    if options:
        colocation["options"] = options

    return colocation


@wrap_src_for_rich_report(dict(constraints="constraints configuration"))
def export_colocation_constraints(constraints: SrcDict) -> List[Dict[str, Any]]:
    """
    Export colocation constraints from `pcs constraint --all --output-format=json`
    output
    """
    return [_colocation(colocation) for colocation in constraints["colocation"]]
