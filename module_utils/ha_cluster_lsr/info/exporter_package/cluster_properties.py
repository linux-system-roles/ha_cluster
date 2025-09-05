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

from .nvset import first_attrs
from .wrap_src import SrcDict, wrap_src_for_rich_report

# These properties are readonly,
_CLUSTER_PROPERTIES_SKIP_KEYS = [
    "cluster-infrastructure",
    "cluster-name",
    "dc-version",
    "have-watchdog",
    "last-lrm-refresh",
]


@wrap_src_for_rich_report(dict(properties="cluster properties configuration"))
def export_cluster_properties(properties: SrcDict) -> List[Dict[str, Any]]:
    """Export cluster properties from `pcs property config` output"""

    return first_attrs(
        properties["nvsets"],
        skip_keys=_CLUSTER_PROPERTIES_SKIP_KEYS,
    )
