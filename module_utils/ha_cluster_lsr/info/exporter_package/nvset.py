# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# make ansible-test happy, even though the module requires Python 3
from __future__ import absolute_import, division, print_function

# make ansible-test happy, even though the module requires Python 3
# pylint: disable=invalid-name
__metaclass__ = type

from typing import Any, Callable, Dict, List, Optional

Nvset = Dict[str, Any]
Attrs = List[Dict[str, List[Dict[str, Any]]]]


def dict_to_nv_list(input_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Convert a dict to a list of dicts with keys 'name' and 'value'
    """
    return [dict(name=name, value=value) for name, value in input_dict.items()]


def nvset_to_attrs(
    nvset: Nvset,
    skip_keys: Optional[List[str]] = None,
    value_transform: Optional[Callable[[Any], Any]] = None,
) -> List[Dict[str, Any]]:
    """Returns attrs taken from the nvset"""

    skip_keys = skip_keys if skip_keys else []
    return [
        dict(
            name=nvpair_src["name"],
            value=(
                value_transform(nvpair_src["value"])
                if value_transform
                else nvpair_src["value"]
            ),
        )
        for nvpair_src in nvset["nvpairs"]
        if nvpair_src["name"] not in skip_keys
    ]


def first_attrs(
    nvsets: List[Nvset],
    skip_keys: Optional[List[str]] = None,
    value_transform: Optional[Callable[[Any], Any]] = None,
) -> Attrs:
    """Returns attrs taken from the first nvset"""
    if len(nvsets) < 1:
        return []

    if len(nvsets[0]["nvpairs"]) < 1:
        return []
    return [dict(attrs=nvset_to_attrs(nvsets[0], skip_keys, value_transform))]


def first_utilization_attrs(nvsets: List[Nvset]) -> Attrs:
    """
    Returns utilizations taken from the first nvset.
    Utilizations are special concept with special limitation - values must be
    integer.
    """
    return first_attrs(nvsets, value_transform=int)
