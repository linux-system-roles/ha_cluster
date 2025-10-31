# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# make ansible-test happy, even though the module requires Python 3
from __future__ import absolute_import, division, print_function

# make ansible-test happy, even though the module requires Python 3
# pylint: disable=invalid-name
__metaclass__ = type

from typing import Any, Dict

from .options import to_options
from .wrap_src import SrcDict, invalid_part


def export_resource_set(resource_set_src: SrcDict) -> Dict[str, Any]:
    """
    Convert a single resource set from pcs format to system roles format
    """
    if not resource_set_src["resources_ids"]:
        raise invalid_part(
            resource_set_src,
            "Resource set without resource_ids",
        )
    resource_set = {"resource_ids": resource_set_src["resources_ids"]}

    options = to_options(
        resource_set_src,
        "ordering",
        "action",
        "role",
        "score",
        "kind",
        "sequential",
        ("require_all", "require-all"),
    )
    if options:
        resource_set["options"] = options

    return resource_set
