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

from .nvset import dict_to_nv_list
from .wrap_src import SrcDict, wrap_src_for_rich_report


@wrap_src_for_rich_report(dict(corosync_conf_dict="corosync configuration"))
def export_corosync_cluster_name(corosync_conf_dict: SrcDict) -> str:
    """
    Extract cluster name form corosync config in pcs format

    corosync_conf_dict -- corosync config structure provided by pcs
    """
    return corosync_conf_dict["cluster_name"]


@wrap_src_for_rich_report(dict(corosync_conf_dict="corosync configuration"))
def export_corosync_transport(corosync_conf_dict: SrcDict) -> Dict[str, Any]:
    """
    Export transport options in role format from corosync config in pcs format

    corosync_conf_dict -- corosync config structure provided by pcs
    """
    transport = dict(type=corosync_conf_dict["transport"].lower())
    if corosync_conf_dict["transport_options"]:
        transport["options"] = dict_to_nv_list(
            corosync_conf_dict["transport_options"]
        )
    if corosync_conf_dict["links_options"]:
        transport["links"] = [
            # linknumber is an index in links_options, but it is present in
            # link_dict as well
            dict_to_nv_list(link_dict)
            for link_dict in corosync_conf_dict["links_options"].values()
        ]
    if corosync_conf_dict["compression_options"]:
        transport["compression"] = dict_to_nv_list(
            corosync_conf_dict["compression_options"]
        )
    if corosync_conf_dict["crypto_options"]:
        transport["crypto"] = dict_to_nv_list(
            corosync_conf_dict["crypto_options"]
        )
    return transport


@wrap_src_for_rich_report(dict(corosync_conf_dict="corosync configuration"))
def export_corosync_totem(corosync_conf_dict: SrcDict) -> Dict[str, Any]:
    """
    Export totem options in role format from corosync config in pcs format

    corosync_conf_dict -- corosync config structure provided by pcs
    """
    result: Dict[str, Any] = dict()
    if corosync_conf_dict["totem_options"]:
        result["options"] = dict_to_nv_list(corosync_conf_dict["totem_options"])
    return result


@wrap_src_for_rich_report(dict(corosync_conf_dict="corosync configuration"))
def export_corosync_quorum(corosync_conf_dict: SrcDict) -> Dict[str, Any]:
    """
    Export quorum options in role format from corosync config in pcs format

    corosync_conf_dict -- corosync config structure provided by pcs
    """
    result: Dict[str, Any] = dict()
    if corosync_conf_dict["quorum_options"]:
        result["options"] = dict_to_nv_list(
            corosync_conf_dict["quorum_options"]
        )
    return result
