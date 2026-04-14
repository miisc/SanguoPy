#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NPC persona differentiation tests for MVP."""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from game.court_meeting import CourtMeetingSystem


class _FakeModel:
    def get_generals(self):
        return {}


def _build_system():
    return CourtMeetingSystem(_FakeModel())


def test_personality_is_stable_for_same_participant():
    system = _build_system()
    participant = {"id": "zhugeliang", "intelligence": 100, "politics": 88, "strength": 38, "loyalty": 95}

    values = {system._get_personality_description(participant) for _ in range(6)}
    assert len(values) == 1


def test_personality_differs_for_distinct_archetypes():
    system = _build_system()
    strategist = {"id": "zhugeliang", "intelligence": 100, "politics": 88, "strength": 38, "loyalty": 95}
    warrior = {"id": "zhangfei", "intelligence": 23, "politics": 11, "strength": 98, "loyalty": 95}

    p1 = system._get_personality_description(strategist)
    p2 = system._get_personality_description(warrior)
    assert p1 != p2
