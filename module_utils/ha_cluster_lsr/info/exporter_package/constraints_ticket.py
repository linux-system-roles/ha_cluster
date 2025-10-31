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


def _resource(ticket_src: SrcDict) -> Dict[str, Any]:
    if not ticket_src["resource_id"]:
        raise invalid_part(
            ticket_src,
            "Ticket constraint is missing resource_id",
        )

    resource = {"id": ticket_src["resource_id"]}

    if ticket_src["role"]:
        resource["role"] = ticket_src["role"]

    return resource


def _options(attributes_src: SrcDict) -> List[Any]:
    return to_options(attributes_src, ("loss_policy", "loss-policy"))


def _ensure_ticket_attr(ticket_src: SrcDict) -> None:
    if not ticket_src["attributes"]["ticket"]:
        raise invalid_part(
            ticket_src,
            "Ticket constraint is missing ticket attribute",
        )


def _ticket(ticket_src: SrcDict) -> Dict[str, Any]:
    _ensure_ticket_attr(ticket_src)

    ticket = {
        "id": ticket_src["attributes"]["constraint_id"],
        "resource": _resource(ticket_src),
        "ticket": ticket_src["attributes"]["ticket"],
    }

    options = _options(ticket_src["attributes"])
    if options:
        ticket["options"] = options

    return ticket


def _ticket_set(ticket_set_src: SrcDict) -> Dict[str, Any]:
    if not ticket_set_src["resource_sets"]:
        raise invalid_part(
            ticket_set_src, "Ticket constraint is missing resource_sets"
        )

    _ensure_ticket_attr(ticket_set_src)

    ticket_set = {
        "id": ticket_set_src["attributes"]["constraint_id"],
        "resource_sets": [
            export_resource_set(resource_set)
            for resource_set in ticket_set_src["resource_sets"]
        ],
        "ticket": ticket_set_src["attributes"]["ticket"],
    }

    options = _options(ticket_set_src["attributes"])
    if options:
        ticket_set["options"] = options

    return ticket_set


@wrap_src_for_rich_report(dict(constraints="constraints configuration"))
def export_ticket_constraints(constraints: SrcDict) -> List[Dict[str, Any]]:
    """
    Export ticket constraints from `pcs constraint --all --output-format=json`
    output
    """
    return [_ticket(ticket) for ticket in constraints["ticket"]] + [
        _ticket_set(ticket_set) for ticket_set in constraints["ticket_set"]
    ]
