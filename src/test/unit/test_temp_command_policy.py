#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests — TempCommandPolicy loader and GameController.issue_command_from_policy

tests-first: 先写测试（红灯），再实现，直到全绿。

运行：
pytest src/test/unit/test_temp_command_policy.py -v
"""

import os
import sys
import pytest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
POLICY_PATH = os.path.join(ROOT, "docs", "design", "TEMP_COMMAND_POLICY_MVP.json")


# ──────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────

@pytest.fixture
def policy():
    from game.temp_command_policy import TempCommandPolicy
    return TempCommandPolicy(POLICY_PATH)


@pytest.fixture
def controller():
    from game.game_controller import GameController
    return GameController()


# ──────────────────────────────────────────────
# TempCommandPolicy 单元测试
# ──────────────────────────────────────────────

class TestTempCommandPolicyLoader:
    def test_loads_6_whitelist_commands(self, policy):
        """TEMP_COMMAND_POLICY_MVP.json 定义 6 条白名单指令。"""
        from game.temp_command_policy import TempCommandPolicy
        p = TempCommandPolicy(POLICY_PATH)
        # 白名单内部字典长度应为 6
        assert len(p._whitelist) == 6

    def test_known_command_is_whitelisted(self, policy):
        assert policy.is_whitelisted("cmd_border_emergency_response") is True
        assert policy.is_whitelisted("cmd_supply_line_recovery") is True
        assert policy.is_whitelisted("cmd_disaster_relief_emergency") is True
        assert policy.is_whitelisted("cmd_rebellion_suppression") is True
        assert policy.is_whitelisted("cmd_enemy_capital_intel_urgent") is True
        assert policy.is_whitelisted("cmd_multi_front_alert") is True

    def test_unknown_command_not_whitelisted(self, policy):
        assert policy.is_whitelisted("cmd_unknown_xyz") is False
        assert policy.is_whitelisted("") is False

    def test_get_command_config_returns_dict(self, policy):
        cfg = policy.get_command_config("cmd_border_emergency_response")
        assert cfg is not None
        assert cfg["command_id"] == "cmd_border_emergency_response"
        assert cfg["cost"] == 10
        assert cfg["cooldown_xun"] == 1

    def test_get_command_config_returns_none_for_unknown(self, policy):
        assert policy.get_command_config("cmd_does_not_exist") is None

    def test_get_command_cost_default(self, policy):
        assert policy.get_command_cost("cmd_border_emergency_response") == 10

    def test_get_command_cooldown_default(self, policy):
        assert policy.get_command_cooldown("cmd_border_emergency_response") == 1

    def test_cost_per_command_global_default(self, policy):
        assert policy.cost_per_command == 10


class TestTempCommandPolicyTrigger:
    def test_trigger_met_when_event_code_matches_any_of(self, policy):
        # cmd_border_emergency_response 触发条件: border_city_under_siege 或 enemy_force_near_border
        assert policy.is_trigger_met(
            "cmd_border_emergency_response",
            {"border_city_under_siege"}
        ) is True
        assert policy.is_trigger_met(
            "cmd_border_emergency_response",
            {"enemy_force_near_border"}
        ) is True

    def test_trigger_not_met_when_no_matching_event(self, policy):
        assert policy.is_trigger_met(
            "cmd_border_emergency_response",
            {"drought_index_high"}
        ) is False
        assert policy.is_trigger_met(
            "cmd_border_emergency_response",
            set()
        ) is False

    def test_trigger_not_met_for_unknown_command(self, policy):
        assert policy.is_trigger_met("cmd_unknown", {"border_city_under_siege"}) is False

    def test_trigger_met_disaster_command(self, policy):
        assert policy.is_trigger_met(
            "cmd_disaster_relief_emergency",
            {"epidemic_outbreak"}
        ) is True
        assert policy.is_trigger_met(
            "cmd_disaster_relief_emergency",
            {"border_city_under_siege"}
        ) is False

    def test_trigger_met_partial_overlap(self, policy):
        """active_event_codes 中只要有一个命中 any_of 即可。"""
        assert policy.is_trigger_met(
            "cmd_rebellion_suppression",
            {"army_mutiny_active", "drought_index_high"}
        ) is True


# ──────────────────────────────────────────────
# GameController.issue_command_from_policy 集成测试
# ──────────────────────────────────────────────

class TestIssueCommandFromPolicy:
    def test_method_exists_on_controller(self, controller):
        assert hasattr(controller, "issue_command_from_policy")

    def test_success_when_trigger_met(self, controller):
        controller.game_model.game_data["court_resources"] = {"zhaoling_authority": 50}
        result = controller.issue_command_from_policy(
            command_id="cmd_border_emergency_response",
            current_xun=1,
            active_event_codes={"border_city_under_siege"},
        )
        assert result["success"] is True
        assert result["new_authority"] == 40
        assert controller.game_model.game_data["court_resources"]["zhaoling_authority"] == 40

    def test_rejected_when_trigger_not_met(self, controller):
        controller.game_model.game_data["court_resources"] = {"zhaoling_authority": 50}
        result = controller.issue_command_from_policy(
            command_id="cmd_border_emergency_response",
            current_xun=1,
            active_event_codes=set(),  # 无触发事件
        )
        assert result["success"] is False
        assert result["reason"] == "trigger_not_met"
        assert controller.game_model.game_data["court_resources"]["zhaoling_authority"] == 50

    def test_rejected_for_non_whitelisted_command(self, controller):
        controller.game_model.game_data["court_resources"] = {"zhaoling_authority": 50}
        result = controller.issue_command_from_policy(
            command_id="cmd_not_in_whitelist",
            current_xun=1,
            active_event_codes={"some_event"},
        )
        assert result["success"] is False
        assert result["reason"] == "not_whitelisted"
        assert controller.game_model.game_data["court_resources"]["zhaoling_authority"] == 50

    def test_rejected_when_authority_insufficient(self, controller):
        controller.game_model.game_data["court_resources"] = {"zhaoling_authority": 5}
        result = controller.issue_command_from_policy(
            command_id="cmd_border_emergency_response",
            current_xun=1,
            active_event_codes={"border_city_under_siege"},
        )
        assert result["success"] is False
        assert result["reason"] == "insufficient_authority"

    def test_active_event_codes_defaults_to_empty_set(self, controller):
        """不传 active_event_codes 时，触发条件未满足，应返回 trigger_not_met。"""
        controller.game_model.game_data["court_resources"] = {"zhaoling_authority": 50}
        result = controller.issue_command_from_policy(
            command_id="cmd_border_emergency_response",
            current_xun=1,
        )
        assert result["success"] is False
        assert result["reason"] == "trigger_not_met"

    def test_cooldown_respected_across_two_xun(self, controller):
        controller.game_model.game_data["court_resources"] = {"zhaoling_authority": 50}
        codes = {"border_city_under_siege"}
        r1 = controller.issue_command_from_policy("cmd_border_emergency_response", current_xun=1, active_event_codes=codes)
        assert r1["success"] is True
        # 同旬同类型 → 冷却
        r2 = controller.issue_command_from_policy("cmd_border_emergency_response", current_xun=1, active_event_codes=codes)
        assert r2["success"] is False
        assert r2["reason"] == "in_cooldown"
        # 下一旬 → 冷却解除
        r3 = controller.issue_command_from_policy("cmd_border_emergency_response", current_xun=2, active_event_codes=codes)
        assert r3["success"] is True
