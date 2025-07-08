# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# make ansible-test happy, even though the module requires Python 3
from __future__ import absolute_import, division, print_function

# make ansible-test happy, even though the module requires Python 3
# pylint: disable=invalid-name
__metaclass__ = type

from .exporter_package import nvset, wrap_src
from .exporter_package.corosync_conf import (
    export_cluster_nodes,
    export_corosync_cluster_name,
    export_corosync_quorum,
    export_corosync_totem,
    export_corosync_transport,
)
from .exporter_package.resources import (
    export_resource_bundle_list,
    export_resource_clone_list,
    export_resource_group_list,
    export_resource_primitive_list,
)
from .exporter_package.various import (
    export_enable_repos_ha,
    export_enable_repos_rs,
    export_install_cloud_agents,
    export_manage_firewall,
    export_manage_selinux,
    export_pcs_permission_list,
    export_start_on_boot,
)
from .exporter_package.wrap_src import InvalidSrc

__all__ = [
    "export_cluster_nodes",
    "export_corosync_cluster_name",
    "export_corosync_quorum",
    "export_corosync_totem",
    "export_corosync_transport",
    "export_enable_repos_ha",
    "export_enable_repos_rs",
    "export_install_cloud_agents",
    "export_manage_firewall",
    "export_manage_selinux",
    "export_pcs_permission_list",
    "export_resource_bundle_list",
    "export_resource_clone_list",
    "export_resource_group_list",
    "export_resource_primitive_list",
    "export_start_on_boot",
    "InvalidSrc",
    # For testing purposes. This is a quick dirty solution of `empty init`
    # requirement and should be cleaned up later.
    "wrap_src",
    "nvset",
]
