# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# make ansible-test happy, even though the module requires Python 3
from __future__ import absolute_import, division, print_function

# make ansible-test happy, even though the module requires Python 3
# pylint: disable=invalid-name
__metaclass__ = type

from typing import Any, Dict, List, Optional, Tuple

from .nvset import dict_to_nv_list
from .wrap_src import (
    SrcDict,
    invalid_part,
    is_none,
    wrap_src_for_rich_report,
)

_PACEMAKER_TRUE = ["true", "on", "yes", "y", "1"]

_PRIMITIVE_OPERATION_SKIP_KEYS = [
    "id",
    "name",
    "meta_attributes",
    "instance_attributes",
]
_BUNDLE_CONTAINER_KEY_MAP = {
    "promoted_max": "promoted-max",
    "replicas_per_host": "replicas-per-host",
    "run_command": "run-command",
}
_BUNDLE_NETWORK_KEY_MAP = {
    "add_host": "add-host",
    "control_port": "control-port",
    "host_interface": "host-interface",
    "host_netmask": "host-netmask",
    "ip_range_start": "ip-range-start",
}
_BUNDLE_PORT_MAP_SKIP_KEYS = ["id"]
_BUNDLE_PORT_MAP_KEY_MAP = {
    "internal_port": "internal-port",
}
_BUNDLE_STORAGE_MAP_SKIP_KEYS = ["id"]
_BUNDLE_STORAGE_MAP_KEY_MAP = {
    "source_dir": "source-dir",
    "source_dir_root": "source-dir-root",
    "target_dir": "target-dir",
}

_AttrsSrc = List[Dict[str, Any]]
_Attrs = List[Dict[str, List[Dict[str, Any]]]]


def _nv_list(
    input_dict: Dict[str, Any],
    skip_keys: Optional[List[str]] = None,
    key_map: Optional[Dict[str, str]] = None,
) -> List[Dict[str, Any]]:
    if key_map is None:
        key_map = {}
    if skip_keys is None:
        skip_keys = []

    return dict_to_nv_list(
        {
            (key_map[key] if key in key_map else key): value
            for key, value in input_dict.items()
            if not (is_none(value) or key in skip_keys)
        }
    )


def _attrs(nvsets: _AttrsSrc) -> _Attrs:
    if len(nvsets) < 1:
        return []

    if len(nvsets[0]["nvpairs"]) < 1:
        return []

    return [
        dict(
            attrs=[
                dict(name=nvpair_src["name"], value=nvpair_src["value"])
                for nvpair_src in nvsets[0]["nvpairs"]
            ]
        )
    ]


def _operations(
    operation_list_src: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    operation_list = []
    for operation_src in operation_list_src:
        attrs = _nv_list(
            operation_src,
            skip_keys=_PRIMITIVE_OPERATION_SKIP_KEYS,
        )
        if not attrs:
            raise invalid_part(operation_src, "No attributes in operation")
        operation_list.append(dict(action=operation_src["name"], attrs=attrs))
    return operation_list


def _agent(agent_src: Dict[str, Any]) -> str:
    return ":".join(
        [
            agent_src["standard"],
            agent_src["provider"],
            agent_src["type"],
        ]
        if agent_src["provider"]
        else [
            agent_src["standard"],
            agent_src["type"],
        ]
    )


def _primitive(
    primitive_src: Dict[str, Any], use_utilization: bool = True
) -> Dict[str, Any]:
    primitive = dict(
        id=primitive_src["id"],
        # Use just operations taken from CIB. We need exactly what in CIB and
        # there is no gain trying to incorporate `copy_operations_from_agent`.
        copy_operations_from_agent=False,
        agent=_agent(primitive_src["agent_name"]),
    )

    instance_attrs = _attrs(primitive_src.get("instance_attributes", []))
    if instance_attrs:
        primitive["instance_attrs"] = instance_attrs

    meta_attrs = _attrs(primitive_src.get("meta_attributes", []))
    if meta_attrs:
        primitive["meta_attrs"] = meta_attrs

    if use_utilization:
        utilization = _attrs(primitive_src.get("utilization", []))
        if utilization:
            primitive["utilization"] = utilization

    operations = _operations(primitive_src.get("operations", []))
    if operations:
        primitive["operations"] = operations
    return primitive


def _container(bundle_src: Dict[str, Any]) -> Dict[str, Any]:
    container = dict(type=bundle_src["container_type"])
    options = _nv_list(
        bundle_src.get("container_options", {}),
        key_map=_BUNDLE_CONTAINER_KEY_MAP,
    )
    if options:
        container["options"] = options
    return container


def _meta_attrs_promotable(meta_attrs_src: _AttrsSrc) -> Tuple[_Attrs, bool]:
    if len(meta_attrs_src) == 0:
        return [], False

    first_set, remaining_sets = meta_attrs_src[0], meta_attrs_src[1:]

    promoted_pair = None
    remaining_pairs = []

    for pair in first_set["nvpairs"]:
        if pair["name"] == "promotable":
            promoted_pair = pair
        else:
            remaining_pairs.append(pair)

    return (
        _attrs([{**first_set, "nvpairs": remaining_pairs}] + remaining_sets),
        bool(
            promoted_pair and promoted_pair["value"].lower() in _PACEMAKER_TRUE
        ),
    )


@wrap_src_for_rich_report(
    dict(resources="resources configuration", stonith="stonith configuration")
)
def export_resource_primitive_list(
    resources: SrcDict, stonith: SrcDict
) -> List[Dict[str, Any]]:
    """Export primitive resources from `pcs resource configuration` output"""
    result = []

    # Export stonith first: stonith needs to be configured first, otherwise
    # resources won't start due to missing stonith.
    for primitive_src in stonith["primitives"]:
        result.append(_primitive(primitive_src, use_utilization=False))

    for primitive_src in resources["primitives"]:
        result.append(_primitive(primitive_src))

    return result


@wrap_src_for_rich_report(dict(resources="resources configuration"))
def export_resource_group_list(resources: SrcDict) -> List[Dict[str, Any]]:
    """Export resource groups from `pcs resource configuration` output"""
    result = []
    for group_src in resources["groups"]:
        group = dict(
            id=group_src["id"],
            resource_ids=group_src["member_ids"],
        )
        meta_attrs = _attrs(group_src.get("meta_attributes", []))
        if meta_attrs:
            group["meta_attrs"] = meta_attrs
        result.append(group)
    return result


@wrap_src_for_rich_report(dict(resources="resources configuration"))
def export_resource_clone_list(resources: SrcDict) -> List[Dict[str, Any]]:
    """Export resource clones from `pcs resource configuration` output"""
    result = []
    for clone_src in resources["clones"]:
        clone = dict(
            id=clone_src["id"],
            resource_id=clone_src["member_id"],
        )
        meta_attrs, promotable = _meta_attrs_promotable(
            clone_src.get("meta_attributes", [])
        )
        if promotable:
            clone["promotable"] = True
        if meta_attrs:
            clone["meta_attrs"] = meta_attrs
        result.append(clone)

    return result


@wrap_src_for_rich_report(dict(resources="resources configuration"))
def export_resource_bundle_list(resources: SrcDict) -> List[Dict[str, Any]]:
    """Export resource bundles from `pcs resource configuration` output"""
    result = []
    for bundle_src in resources["bundles"]:
        # Theoretically, in CIB can be a bundle with a container type that is
        # not supported by pcs (pcs does not allow to create such bundle).
        # In this case, pcs ignores this bundle and skip it in some listings.
        # Unfortunately, in our source the bundle is not skipped but just
        # damaged by omitting `container_type`. So, skip such bundle here.
        if "container_type" not in bundle_src or is_none(
            bundle_src["container_type"]
        ):
            continue

        bundle = dict(id=bundle_src["id"])

        member_id = bundle_src.get("member_id", None)
        if member_id:
            bundle["resource_id"] = member_id

        bundle["container"] = _container(bundle_src)

        meta_attrs = _attrs(bundle_src.get("meta_attributes", []))
        if meta_attrs:
            bundle["meta_attrs"] = meta_attrs

        network_options = _nv_list(
            bundle_src.get("network", {}) or {},  # network can be None
            key_map=_BUNDLE_NETWORK_KEY_MAP,
        )
        if network_options:
            bundle["network_options"] = network_options

        port_map_list = [
            _nv_list(
                port_map,
                skip_keys=_BUNDLE_PORT_MAP_SKIP_KEYS,
                key_map=_BUNDLE_PORT_MAP_KEY_MAP,
            )
            for port_map in bundle_src.get("port_mappings", [])
        ]
        if port_map_list:
            bundle["port_map"] = port_map_list

        storage_map_list = [
            _nv_list(
                storage_map,
                skip_keys=_BUNDLE_STORAGE_MAP_SKIP_KEYS,
                key_map=_BUNDLE_STORAGE_MAP_KEY_MAP,
            )
            for storage_map in bundle_src.get("storage_mappings", [])
        ]
        if storage_map_list:
            bundle["storage_map"] = storage_map_list

        result.append(bundle)

    return result
