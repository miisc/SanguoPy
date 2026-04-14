#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MapSystem pathing regression tests."""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from map_system.core.map_system import MapSystem


def test_direct_road_path_not_empty_after_add_road():
    m = MapSystem()
    m.initialize()
    m.add_city("a", "长安", (0, 0), "player", 10000)
    m.add_city("b", "洛阳", (10, 0), "player", 9000)
    m.add_road("r1", "长安-洛阳", "a", "b", "官道")

    path = m.calculate_movement_path("a", "b")
    assert path == ["r1"]


def test_path_becomes_empty_after_remove_road():
    m = MapSystem()
    m.initialize()
    m.add_city("a", "长安", (0, 0), "player", 10000)
    m.add_city("b", "洛阳", (10, 0), "player", 9000)
    m.add_road("r1", "长安-洛阳", "a", "b", "官道")
    m.remove_road("r1")

    path = m.calculate_movement_path("a", "b")
    assert path == []
