#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests — FactionAI
F11: Non-player factions run monthly decisions; each maintains independent
faction_dimensions. Player dimensions are never modified by AI turns.

Run: pytest src/test/unit/test_faction_ai.py -v
"""
import sys
import os
import pytest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


@pytest.fixture
def model():
    from game.game_model import GameModel
    with patch("game.game_model.os.path.exists", return_value=False):
        m = GameModel()
    # Ensure player dimensions exist
    m.game_data.setdefault("dimensions", {
        "military": 50, "economy": 50, "technology": 50,
        "public_order": 50, "diplomacy": 50,
    })
    return m


class TestFactionAI:
    """F11: FactionAI drives non-player faction monthly decisions."""

    def test_faction_dimensions_initial_values(self, model):
        """All factions in faction_dimensions start at 50 for each of the 5 dims."""
        fd = model.game_data["faction_dimensions"]
        for faction_id in ("wei", "shu", "wu"):
            assert faction_id in fd, f"{faction_id} missing from faction_dimensions"
            for dim in ("military", "economy", "technology", "public_order", "diplomacy"):
                assert fd[faction_id][dim] == 50, \
                    f"{faction_id}.{dim} should be 50, got {fd[faction_id][dim]}"

    def test_faction_alignment_in_factions_data(self, model):
        """Each faction has an alignment field (hawk/dove/pragmatist)."""
        factions = model.game_data["factions"]
        expected = {"wei": "hawk", "shu": "pragmatist", "wu": "dove"}
        for faction_id, alignment in expected.items():
            assert factions[faction_id].get("alignment") == alignment, \
                f"{faction_id} alignment should be {alignment}"

    def test_run_monthly_decision_changes_faction_dims(self, model):
        """FactionAI.run_monthly_decision changes the AI faction's dimensions."""
        from game.faction_ai import FactionAI
        ai = FactionAI(model)
        before = dict(model.game_data["faction_dimensions"]["shu"])
        ai.run_monthly_decision("shu")
        after = model.game_data["faction_dimensions"]["shu"]
        # At least one dimension should have changed (topics always have non-zero effects)
        assert after != before, "shu faction_dimensions unchanged after AI monthly decision"

    def test_ai_does_not_affect_player_dimensions(self, model):
        """AI faction decision must not modify game_data['dimensions'] (player dims)."""
        from game.faction_ai import FactionAI
        ai = FactionAI(model)
        player_before = dict(model.game_data["dimensions"])
        ai.run_monthly_decision("shu")
        ai.run_monthly_decision("wu")
        assert model.game_data["dimensions"] == player_before, \
            "Player dimensions were modified by AI faction decision"

    def test_advance_time_triggers_ai_for_non_player_factions(self, model):
        """advance_time through month boundary triggers AI decisions for shu and wu."""
        shu_before = dict(model.game_data["faction_dimensions"]["shu"])
        wu_before = dict(model.game_data["faction_dimensions"]["wu"])
        wei_player_before = dict(model.game_data["dimensions"])

        # Advance through a full month (30 days)
        model.game_data["game_info"]["day"] = 30
        model.advance_time()  # triggers month boundary

        assert model.game_data["faction_dimensions"]["shu"] != shu_before, \
            "shu dims unchanged after month boundary"
        assert model.game_data["faction_dimensions"]["wu"] != wu_before, \
            "wu dims unchanged after month boundary"
        assert model.game_data["dimensions"] == wei_player_before, \
            "Player (wei) dims changed by AI advance"
