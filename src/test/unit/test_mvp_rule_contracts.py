#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests — MVP rule contracts and implementation gaps

目标：
1) 锁定 docs/design 下的规则配置，防止需求回退。
2) 通过 strict xfail 标注尚未实现的核心行为，形成 tests-first 红灯清单。

运行：
pytest src/test/unit/test_mvp_rule_contracts.py -v
"""

import json
import os
import sys
import pytest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
DESIGN_DIR = os.path.join(ROOT, "docs", "design")


def _load_json(name: str):
    path = os.path.join(DESIGN_DIR, name)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class TestMvpJsonContracts:
    def test_temp_command_policy_dynamic_quota_formula(self):
        policy = _load_json("TEMP_COMMAND_POLICY_MVP.json")
        limits = policy["global_limits"]

        assert limits["cost_per_command"] == 10
        assert limits["max_commands_per_xun_mode"] == "dynamic_by_current_authority"
        assert limits["max_commands_per_xun_formula"] == "FLOOR(current_authority / cost_per_command)"
        assert limits["min_commands_per_xun"] == 0

    def test_temp_command_policy_never_allows_negative_authority(self):
        policy = _load_json("TEMP_COMMAND_POLICY_MVP.json")
        assert policy["authority"]["spend_rules"]["allow_negative"] is False
        assert policy["validation"]["reject_when_cost_drives_negative"] is True

    def test_llm_validation_uses_unified_dimension_boundaries(self):
        policy = _load_json("LLM_VALIDATION_POLICY_MVP.json")
        numeric = policy["numeric_rules"]

        assert numeric["tracked_dimensions"] == [
            "military",
            "economy",
            "technology",
            "public_order",
            "diplomacy",
        ]
        assert numeric["dimension_min"] == 0
        assert numeric["dimension_max"] == 100
        assert numeric["clamp_after_apply"] is True

    def test_event_templates_enforce_type_scope_cooldown(self):
        templates = _load_json("EVENT_TEMPLATES_MVP.json")
        meta = templates["meta"]

        assert meta["cooldown_scope"] == "event_type"
        assert meta["emergency_trigger_behavior"] == "interrupt_and_enter_emergency_meeting_immediately"


@pytest.fixture
def model():
    from game.game_model import GameModel

    with patch("game.game_model.os.path.exists", return_value=False):
        return GameModel()


@pytest.fixture
def controller():
    from game.game_controller import GameController

    return GameController()


class TestImplementationGaps:
    def test_dimension_values_are_clamped_between_0_and_100(self, model):
        # 目标行为：五维数值结算后必须裁剪到 [0,100]
        assert hasattr(model, "apply_dimension_effects")
        model.game_data.setdefault("dimensions", {
            "military": 95,
            "economy": 5,
            "technology": 50,
            "public_order": 10,
            "diplomacy": 80,
        })
        model.apply_dimension_effects({
            "military": 10,
            "economy": -20,
            "technology": 0,
            "public_order": -99,
            "diplomacy": 30,
        })
        dims = model.game_data["dimensions"]
        assert dims["military"] == 100
        assert dims["economy"] == 0
        assert dims["public_order"] == 0
        assert dims["diplomacy"] == 100

    def test_emergency_meeting_interrupts_execution_immediately(self, controller):
        # 目标行为：触发紧急事件时，控制器应中断执行阶段并立即进入紧急朝会。
        assert hasattr(controller, "trigger_emergency_meeting")

        controller.game_model.game_data["game_info"]["paused"] = False
        result = controller.trigger_emergency_meeting({"type": "military", "severity": "major"})

        assert result["interrupted"] is True
        assert result["entered_emergency_meeting"] is True
        assert controller.court_meeting_system.meeting_active is True

    def test_dynamic_temp_command_quota_depends_on_current_authority(self, controller):
        # 目标行为：quota = FLOOR(current_authority / 10)
        assert hasattr(controller, "get_temp_command_quota")

        q50 = controller.get_temp_command_quota(current_authority=50)
        q19 = controller.get_temp_command_quota(current_authority=19)
        q9 = controller.get_temp_command_quota(current_authority=9)

        assert q50 == 5
        assert q19 == 1
        assert q9 == 0

    def test_event_cooldown_is_scoped_by_event_type(self, controller):
        # 目标行为：同 event_type 事件共享 cooldown，不同 type 不共享。
        assert hasattr(controller, "can_trigger_event")
        assert hasattr(controller, "register_event_trigger")

        assert controller.can_trigger_event("military", "evt_border_alarm", current_xun=1) is True
        controller.register_event_trigger("military", "evt_border_alarm", current_xun=1)

        # 同类型新事件在冷却期内不可触发
        assert controller.can_trigger_event("military", "evt_supply_line_cut", current_xun=1) is False

        # 不同类型事件可触发
        assert controller.can_trigger_event("disaster", "evt_drought", current_xun=1) is True

    def test_event_type_cooldown_unlocks_after_xun_window(self, controller):
        assert controller.can_trigger_event("military", "evt_border_alarm", current_xun=1, cooldown_xun=2) is True
        controller.register_event_trigger("military", "evt_border_alarm", current_xun=1)

        # 冷却窗口内
        assert controller.can_trigger_event("military", "evt_supply_line_cut", current_xun=2, cooldown_xun=2) is False
        # 冷却窗口后
        assert controller.can_trigger_event("military", "evt_supply_line_cut", current_xun=3, cooldown_xun=2) is True

    def test_emergency_meeting_requires_major_quantified_event(self, controller):
        # 非重大军事事件：不应触发紧急朝会
        result_minor = controller.trigger_emergency_meeting(
            {"type": "military", "code": "routine_patrol", "severity": "low"}
        )
        assert result_minor["interrupted"] is False
        assert result_minor["entered_emergency_meeting"] is False

        # 重大军事事件：应触发
        result_major = controller.trigger_emergency_meeting(
            {"type": "military", "code": "border_city_under_siege", "severity": "major"}
        )
        assert result_major["interrupted"] is True
        assert result_major["entered_emergency_meeting"] is True

    def test_temp_command_spend_sequence_enforces_order(self, controller):
        assert hasattr(controller, "execute_temp_command")

        # 1) 白名单优先校验：不在白名单应直接拒绝且不扣减
        r1 = controller.execute_temp_command(
            authority=50,
            command_type="invalid_cmd",
            current_xun=1,
            is_whitelisted=False,
            trigger_met=True,
        )
        assert r1["success"] is False
        assert r1["reason"] == "not_whitelisted"
        assert r1["new_authority"] == 50

        # 2) 余额校验应早于冷却：余额不足应返回 insufficient_authority
        r2 = controller.execute_temp_command(
            authority=5,
            command_type="cmd_border_emergency_response",
            current_xun=1,
            is_whitelisted=True,
            trigger_met=True,
        )
        assert r2["success"] is False
        assert r2["reason"] == "insufficient_authority"
        assert r2["new_authority"] == 5

        # 3) 成功执行后，再次同旬触发同类命令应命中冷却
        r3 = controller.execute_temp_command(
            authority=50,
            command_type="cmd_border_emergency_response",
            current_xun=2,
            is_whitelisted=True,
            trigger_met=True,
        )
        assert r3["success"] is True
        assert r3["new_authority"] == 40

        r4 = controller.execute_temp_command(
            authority=40,
            command_type="cmd_border_emergency_response",
            current_xun=2,
            is_whitelisted=True,
            trigger_met=True,
        )
        assert r4["success"] is False
        assert r4["reason"] == "in_cooldown"
        assert r4["new_authority"] == 40

    def test_issue_temp_command_reads_and_updates_model_authority(self, controller):
        assert hasattr(controller, "issue_temp_command")

        controller.game_model.game_data["court_resources"] = {"zhaoling_authority": 50}
        result = controller.issue_temp_command(
            command_type="cmd_border_emergency_response",
            current_xun=1,
            is_whitelisted=True,
            trigger_met=True,
        )

        assert result["success"] is True
        assert result["new_authority"] == 40
        assert controller.game_model.game_data["court_resources"]["zhaoling_authority"] == 40

    def test_dynamic_quota_allows_multiple_commands_until_limit_then_blocks(self, controller):
        assert hasattr(controller, "issue_temp_command")

        controller.game_model.game_data["court_resources"] = {"zhaoling_authority": 25}

        r1 = controller.issue_temp_command(
            command_type="cmd_border_emergency_response",
            current_xun=1,
            is_whitelisted=True,
            trigger_met=True,
        )
        r2 = controller.issue_temp_command(
            command_type="cmd_supply_line_recovery",
            current_xun=1,
            is_whitelisted=True,
            trigger_met=True,
        )
        r3 = controller.issue_temp_command(
            command_type="cmd_rebellion_suppression",
            current_xun=1,
            is_whitelisted=True,
            trigger_met=True,
        )

        assert r1["success"] is True
        assert r2["success"] is True
        assert r3["success"] is False
        assert r3["reason"] == "insufficient_authority"
        assert controller.game_model.game_data["court_resources"]["zhaoling_authority"] == 5

    def test_dynamic_quota_recomputes_on_next_xun_from_remaining_authority(self, controller):
        assert hasattr(controller, "issue_temp_command")

        controller.game_model.game_data["court_resources"] = {"zhaoling_authority": 25}

        first = controller.issue_temp_command(
            command_type="cmd_border_emergency_response",
            current_xun=1,
            is_whitelisted=True,
            trigger_met=True,
        )
        second = controller.issue_temp_command(
            command_type="cmd_supply_line_recovery",
            current_xun=2,
            is_whitelisted=True,
            trigger_met=True,
        )
        third = controller.issue_temp_command(
            command_type="cmd_rebellion_suppression",
            current_xun=2,
            is_whitelisted=True,
            trigger_met=True,
        )

        assert first["success"] is True
        assert second["success"] is True
        assert third["success"] is False
        assert third["reason"] == "insufficient_authority"
        assert controller.game_model.game_data["court_resources"]["zhaoling_authority"] == 5


class TestEventQueueTriggersEmergencyMeeting:
    """F1 — 事件队列推入重大事件后自动触发紧急朝会。"""

    def test_push_major_military_event_triggers_emergency_meeting(self, controller):
        controller.game_model.game_data["game_info"]["paused"] = False
        controller.push_event({"type": "military", "severity": "major"})
        assert controller.game_model.game_data["game_info"]["paused"] is True
        assert controller.court_meeting_system.meeting_active is True

    def test_push_major_disaster_event_triggers_emergency_meeting(self, controller):
        controller.game_model.game_data["game_info"]["paused"] = False
        controller.push_event({"type": "disaster", "code": "flood_level_major"})
        assert controller.game_model.game_data["game_info"]["paused"] is True
        assert controller.court_meeting_system.meeting_active is True

    def test_push_non_major_event_does_not_trigger_meeting(self, controller):
        controller.push_event({"type": "military", "code": "routine_patrol", "severity": "low"})
        assert controller.game_model.game_data["game_info"]["paused"] is False
        assert controller.court_meeting_system.meeting_active is False

    def test_event_is_stored_in_queue(self, controller):
        event = {"type": "military", "severity": "major"}
        controller.push_event(event)
        assert event in controller._event_queue


class TestEventTemplateInEmergencyMeeting:
    """F4 — push_event 携带已知 event_id 时，紧急朝会从 EVENT_TEMPLATES_MVP.json 加载选项。"""

    def test_push_event_with_known_id_loads_template_options(self, controller):
        controller.push_event({"event_id": "evt_border_alarm", "type": "military", "severity": "major"})
        topic = controller.court_meeting_system.current_meeting["topic"]
        titles = [opt["title"] for opt in topic["options"]]
        assert "固守待援" in titles
        assert "主动出击" in titles
        assert "议和拖延" in titles

    def test_push_event_template_decision_applies_dimension_effects(self, controller):
        controller.game_model.game_data["dimensions"] = {
            "military": 50, "economy": 50, "technology": 50,
            "public_order": 50, "diplomacy": 50,
        }
        controller.push_event({"event_id": "evt_border_alarm", "type": "military", "severity": "major"})
        # option A: military +8, economy -4 (from JSON)
        result = controller.court_meeting_system.make_emergency_decision("A")
        assert result["success"] is True
        dims = controller.game_model.game_data["dimensions"]
        assert dims["military"] == 58
        assert dims["economy"] == 46

    def test_push_event_without_event_id_falls_back_to_random_topic(self, controller):
        controller.push_event({"type": "military", "severity": "major"})
        meeting = controller.court_meeting_system.current_meeting
        assert meeting is not None
        assert meeting["type"] == "emergency"
        assert len(meeting["topic"]["options"]) > 0

    def test_push_event_with_unknown_event_id_falls_back_to_random_topic(self, controller):
        controller.push_event({"event_id": "evt_nonexistent", "type": "military", "severity": "major"})
        meeting = controller.court_meeting_system.current_meeting
        assert meeting is not None
        assert meeting["type"] == "emergency"
