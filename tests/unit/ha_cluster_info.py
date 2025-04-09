#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

import sys
from importlib import import_module

sys.modules["ansible.module_utils.ha_cluster_lsr"] = import_module(
    "ha_cluster_lsr"
)
sys.modules["ansible.module_utils.ha_cluster_lsr.info"] = import_module(
    "ha_cluster_lsr.info"
)

ha_cluster_info = import_module("ha_cluster_info")
exporter = getattr(import_module("ha_cluster_lsr.info"), "exporter")
loader = getattr(import_module("ha_cluster_lsr.info"), "loader")
