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

from .options import create_option, to_options
from .wrap_src import SrcDict, invalid_part, wrap_src_for_rich_report


def _resource(location_src: SrcDict) -> Dict[str, Any]:
    if location_src["resource_id"] and location_src["resource_pattern"]:
        raise invalid_part(
            location_src,
            "Location has both resource_id and resource_pattern",
        )

    resource = {}
    if location_src["resource_id"]:
        resource["id"] = location_src["resource_id"]
    elif location_src["resource_pattern"]:
        resource["pattern"] = location_src["resource_pattern"]
    else:
        raise invalid_part(
            location_src,
            "Location has neither resource_id nor resource_pattern",
        )

    return resource


def _options(
    attributes_src: SrcDict, score: Any, score_attribute: Any
) -> List[Dict[str, Any]]:
    options = to_options(
        attributes_src, ("resource_discovery", "resource-discovery")
    )
    if score:
        options.append(create_option("score", score))
    if score_attribute:
        options.append(create_option("score-attribute", score_attribute))
    return options


def _location(location_src: SrcDict) -> Dict[str, Any]:
    attributes_src = location_src["attributes"]
    location = {
        "id": attributes_src["constraint_id"],
        "resource": _resource(location_src),
    }

    if attributes_src["node"] and attributes_src["rules"]:
        raise invalid_part(location_src, "Location has both node and rule")

    role = None
    score = None
    score_attribute = None

    if attributes_src["node"]:
        location["node"] = attributes_src["node"]
        if location_src["role"]:
            role = location_src["role"]
        if attributes_src["score"]:
            score = attributes_src["score"]

    elif attributes_src["rules"]:
        # Only one rule is supported in the ha_cluster role.
        rule = attributes_src["rules"][0]
        location["rule"] = rule["as_string"]
        if rule["options"].get("role", None):
            role = rule["options"]["role"]
        if rule["options"].get("score", None):
            score = rule["options"]["score"]
        if rule["options"].get("score-attribute", None):
            score_attribute = rule["options"]["score-attribute"]

    else:
        raise invalid_part(location_src, "Location has neither node nor rule")

    if role:
        location["resource"]["role"] = role

    options = _options(attributes_src, score, score_attribute)
    if options:
        location["options"] = options

    return location


@wrap_src_for_rich_report(dict(constraints="constraints configuration"))
def export_location_constraints(constraints: SrcDict) -> List[Dict[str, Any]]:
    """
    Export location constraints from `pcs constraint --all --output-format=json`
    output
    """
    # Location_set is ignored because it is not supported in the role.
    return [_location(location) for location in constraints["location"]]
