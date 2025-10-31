# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# make ansible-test happy, even though the module requires Python 3
from __future__ import absolute_import, division, print_function

# make ansible-test happy, even though the module requires Python 3
# pylint: disable=invalid-name
__metaclass__ = type

from typing import Any, Dict, List, Tuple, Union

from .wrap_src import SrcDict, cleanup_wrap


def create_option(name: str, value: Any) -> Dict[str, Any]:
    """Returns option in role format"""
    return {"name": name, "value": value}


def to_options(
    src: SrcDict, *name_list: Union[str, Tuple[str, str]]
) -> List[Any]:
    """Takes options by name_list from src and returns them in role's format."""
    options = []
    for n in name_list:
        key, name = n if isinstance(n, tuple) else (n, n)
        if key not in src:
            continue

        # Support common case with boolean.
        if isinstance(cleanup_wrap(src[key]), bool):
            options.append(create_option(name, str(src[key]).lower()))
            continue

        if src[key]:
            options.append(create_option(name, src[key]))

    return options
