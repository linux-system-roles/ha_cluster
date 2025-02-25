# -*- coding: utf-8 -*-

# Copyright (C) 2025 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

from typing import List, Tuple
from unittest.mock import Mock


def get_fw_mock(
    services: List[str], ports: List[Tuple[str, str]], exception: bool = False
) -> Mock:
    """
    Provide FirewallClient mock including inner structure
    """
    zone_settings_mock = Mock(spec=["getServices", "getPorts"])
    zone_settings_mock.getServices.return_value = services
    zone_settings_mock.getPorts.return_value = ports

    zone_mock = Mock(spec=["getSettings"])
    zone_mock.getSettings.return_value = zone_settings_mock
    if exception:
        zone_mock.getSettings.side_effect = Exception

    service_settings_mock = Mock(spec=["getPorts"])
    service_settings_mock.getPorts.return_value = [
        ("2224", "tcp"),
        ("3121", "tcp"),
        ("5403", "tcp"),
        ("5404", "udp"),
        ("5405-5412", "udp"),
        ("9929", "tcp"),
        ("9929", "udp"),
        ("21064", "tcp"),
    ]

    service_mock = Mock(spec=["getSettings"])
    service_mock.getSettings.return_value = service_settings_mock
    if exception:
        service_mock.getSettings.side_effect = Exception

    config_mock = Mock(spec=["getZoneByName", "getServiceByName"])
    config_mock.getZoneByName.return_value = zone_mock
    config_mock.getServiceByName.return_value = service_mock

    fw_mock = Mock(spec=["config", "getDefaultZone"])
    fw_mock.getDefaultZone.return_value = "myzone"
    fw_mock.config.return_value = config_mock

    return fw_mock
