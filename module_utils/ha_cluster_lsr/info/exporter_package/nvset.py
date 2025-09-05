# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# make ansible-test happy, even though the module requires Python 3
from __future__ import absolute_import, division, print_function

# make ansible-test happy, even though the module requires Python 3
# pylint: disable=invalid-name
__metaclass__ = type

from typing import Any, Dict, List, Optional

Nvset = Dict[str, Any]
Attrs = List[Dict[str, List[Dict[str, Any]]]]


def dict_to_nv_list(input_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Convert a dict to a list of dicts with keys 'name' and 'value'
    """
    return [dict(name=name, value=value) for name, value in input_dict.items()]


def first_attrs(
    nvsets: List[Nvset],
    skip_keys: Optional[List[str]] = None,
) -> Attrs:
    """Returns attrs taken from the first nvset"""
    if len(nvsets) < 1:
        return []

    if len(nvsets[0]["nvpairs"]) < 1:
        return []

    skip_keys = skip_keys if skip_keys else []

    return [
        dict(
            attrs=[
                dict(name=nvpair_src["name"], value=nvpair_src["value"])
                for nvpair_src in nvsets[0]["nvpairs"]
                if nvpair_src["name"] not in skip_keys
            ]
        )
    ]
