# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# make ansible-test happy, even though the module requires Python 3
from __future__ import absolute_import, division, print_function

# make ansible-test happy, even though the module requires Python 3
# pylint: disable=invalid-name
__metaclass__ = type

from typing import Any, Dict, Optional

from .nvset import Nvset, nvset_to_attrs
from .wrap_src import SrcDict, wrap_src_for_rich_report


def _meta_attrs_set(nvset: Nvset) -> Optional[Dict[str, Any]]:
    meta_attrs_set = {"id": nvset["id"]}

    attrs = nvset_to_attrs(nvset)
    if attrs:
        meta_attrs_set["attrs"] = attrs

    score = nvset["options"].get("score", None)
    if score:
        meta_attrs_set["score"] = score

    if nvset["rule"]:
        meta_attrs_set["rule"] = nvset["rule"]["as_string"]

    return meta_attrs_set


def _defaults(defaults: SrcDict) -> Optional[Dict[str, Any]]:
    """Export primitive resources from `pcs resource configuration` output"""

    if len(defaults["meta_attributes"]) < 1:
        return None

    meta_attrs = []
    for nvset in defaults["meta_attributes"]:
        meta_attrs_set = _meta_attrs_set(nvset)
        if meta_attrs_set:
            meta_attrs.append(meta_attrs_set)

    return {"meta_attrs": meta_attrs} if meta_attrs else None


@wrap_src_for_rich_report(dict(defaults="resource defaults configuration"))
def export_resource_defaults(defaults: SrcDict) -> Optional[Dict[str, Any]]:
    """Export resource defaults from `pcs resource defaults config` output"""
    return _defaults(defaults)


@wrap_src_for_rich_report(
    dict(defaults="resource operation defaults configuration")
)
def export_resource_op_defaults(defaults: SrcDict) -> Optional[Dict[str, Any]]:
    """
    Export resource operation defaults from `pcs resource op defaults config`
    output
    """
    return _defaults(defaults)
