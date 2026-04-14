#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests — CourtMeetingSystem
覆盖：状态机流转、提案合法性、决策应用、防重入

运行：pytest src/test/unit/test_court_meeting.py -v
"""
import sys
import os
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


@pytest.fixture
def model():
    from game.game_model import GameModel
    with patch("game.game_model.os.path.exists", return_value=False):
        return GameModel()


@pytest.fixture
def cms(model):
    """不依赖 Qt 事件循环的 CourtMeetingSystem"""
    from game.court_meeting import CourtMeetingSystem
    system = CourtMeetingSystem.__new__(CourtMeetingSystem)
    system.game_model = model

    # mock Qt signals
    system.meeting_started = MagicMock()
    system.meeting_started.emit = MagicMock()
    system.meeting_completed = MagicMock()
    system.meeting_completed.emit = MagicMock()

    system.current_meeting = None
    system.meeting_active = False

    # 直接从正常初始化实例中拿模板
    real = CourtMeetingSystem.__new__(CourtMeetingSystem)
    real.game_model = model
    real.meeting_started = MagicMock()
    real.meeting_started.emit = MagicMock()
    real.meeting_completed = MagicMock()
    real.meeting_completed.emit = MagicMock()
    real.current_meeting = None
    real.meeting_active = False
    real.__init__(model)  # 仅用来填充 topic_templates
    system.topic_templates = real.topic_templates
    return system


# ---------------------------------------------------------------------------
# can_hold_meeting / 状态机守卫
# ---------------------------------------------------------------------------

class TestCanHoldMeeting:
    def test_can_hold_when_no_previous_meeting(self, cms):
        """初始状态下可以召开朝会"""
        assert cms.can_hold_meeting() is True

    def test_cannot_hold_when_meeting_active(self, cms):
        """朝会进行中不能再次召开"""
        cms.meeting_active = True
        assert cms.can_hold_meeting() is False

    def test_cannot_hold_same_season_twice(self, cms, model):
        """同一年同一季节不能召开第二次朝会"""
        model.game_data["game_info"]["year"] = 190
        model.game_data["game_info"]["season"] = 1
        model.game_data["last_court_meeting"] = {"year": 190, "season": 1}
        assert cms.can_hold_meeting() is False

    def test_can_hold_different_season(self, cms, model):
        """不同季节可以召开"""
        model.game_data["game_info"]["year"] = 190
        model.game_data["game_info"]["season"] = 2
        model.game_data["last_court_meeting"] = {"year": 190, "season": 1}
        assert cms.can_hold_meeting() is True


# ---------------------------------------------------------------------------
# start_meeting 返回结构
# ---------------------------------------------------------------------------

class TestStartMeeting:
    def test_returns_success_true(self, cms):
        result = cms.start_meeting()
        assert result["success"] is True

    def test_meeting_contains_topic(self, cms):
        result = cms.start_meeting()
        assert "topic" in result["meeting"]

    def test_meeting_topic_has_options(self, cms):
        result = cms.start_meeting()
        topic = result["meeting"]["topic"]
        assert "options" in topic
        assert len(topic["options"]) >= 2, "每个提案至少应有2个选项"

    def test_meeting_is_active_after_start(self, cms):
        cms.start_meeting()
        assert cms.meeting_active is True

    def test_start_emits_meeting_started_signal(self, cms):
        cms.start_meeting()
        cms.meeting_started.emit.assert_called_once()

    def test_cannot_start_when_already_active(self, cms):
        cms.start_meeting()
        result = cms.start_meeting()
        assert result["success"] is False


# ---------------------------------------------------------------------------
# 提案模板合法性（对所有内置模板）
# ---------------------------------------------------------------------------

class TestTopicTemplateValidity:
    def test_all_templates_have_required_fields(self, cms):
        required_fields = {"id", "title", "description", "options"}
        for tpl in cms.topic_templates:
            missing = required_fields - set(tpl.keys())
            assert not missing, f"模板 {tpl.get('id')} 缺少字段: {missing}"

    def test_all_options_have_effects(self, cms):
        for tpl in cms.topic_templates:
            for opt in tpl["options"]:
                assert "effects" in opt, f"选项 {opt.get('id')} 缺少 effects"
                assert isinstance(opt["effects"], dict)

    def test_all_options_have_id_and_title(self, cms):
        for tpl in cms.topic_templates:
            for opt in tpl["options"]:
                assert "id" in opt and "title" in opt


# ---------------------------------------------------------------------------
# 决策效果应用（make_monthly_decision / apply_decision 路径）
# ---------------------------------------------------------------------------

class TestDecisionEffects:
    def _start_and_get_first_option_id(self, cms):
        result = cms.start_meeting()
        # 月度路径：需要将 topic 置入 topics 列表
        meeting = result["meeting"]
        meeting["topics"] = [meeting["topic"]]
        meeting["current_topic_index"] = 0
        cms.current_meeting = meeting
        return meeting["topic"]["options"][0]["id"]

    def test_make_decision_returns_success(self, cms, model):
        option_id = self._start_and_get_first_option_id(cms)
        result = cms.make_monthly_decision(option_id)
        assert result["success"] is True, f"决策失败: {result.get('message')}"

    def test_invalid_option_returns_failure(self, cms):
        self._start_and_get_first_option_id(cms)
        result = cms.make_monthly_decision("nonexistent_option_99")
        assert result["success"] is False

    def test_no_active_meeting_returns_failure(self, cms):
        result = cms.make_monthly_decision("any_option")
        assert result["success"] is False


class TestLLMOpinionGeneration:
    def test_use_llm_output_when_available(self, cms):
        cms.llm_integration = MagicMock()
        cms.llm_integration.generate_with_system_prompt.return_value = "臣请行减税安民之策。"

        topic = cms.topic_templates[0]
        participant = {
            "id": "zhugeliang",
            "name": "诸葛亮",
            "loyalty": 95,
            "intelligence": 100,
            "politics": 88,
            "strength": 38,
        }

        opinion = cms._generate_single_opinion(topic, participant)
        assert opinion["opinion"] == "臣请行减税安民之策。"
        cms.llm_integration.generate_with_system_prompt.assert_called_once()

    def test_fallback_template_when_llm_errors(self, cms):
        cms.llm_integration = MagicMock()
        cms.llm_integration.generate_with_system_prompt.side_effect = RuntimeError("llm unavailable")

        topic = cms.topic_templates[0]
        participant = {
            "id": "zhangfei",
            "name": "张飞",
            "loyalty": 95,
            "intelligence": 23,
            "politics": 11,
            "strength": 98,
        }

        opinion = cms._generate_single_opinion(topic, participant)
        assert "臣张飞认为应当" in opinion["opinion"]
        assert opinion["personality"] == "勇武果决"


class TestEmergencyFlow:
    def test_get_emergency_meeting_data_auto_creates_when_inactive(self, cms):
        cms.meeting_active = False
        data = cms.get_emergency_meeting_data()
        assert data is not None
        assert data.get("type") == "emergency"
        assert cms.meeting_active is True

    def test_make_emergency_decision_success(self, cms):
        data = cms.get_emergency_meeting_data()
        option_id = data["topic"]["options"][0]["id"]
        result = cms.make_emergency_decision(option_id)
        assert result["success"] is True
        assert "resource_changes" in result

    def test_make_decision_rejects_invalid_option(self, cms):
        cms.get_emergency_meeting_data()
        result = cms.make_decision("invalid_option")
        assert result["success"] is False


class TestParticipantInfo:
    def test_get_participant_info_missing_returns_none(self, cms):
        assert cms.get_participant_info("missing") is None

    def test_get_participants_for_meeting_returns_empty_when_no_meeting(self, cms):
        cms.current_meeting = None
        assert cms.get_participants_for_meeting() == []


# ---------------------------------------------------------------------------
# F3 — 提案 dimension_effects 与五维数值结算联动
# ---------------------------------------------------------------------------

class TestCourtDecisionDimensionEffects:
    """F3: make_decision 和 make_monthly_decision 必须将 dimension_effects 写入 GameModel。"""

    def _make_emergency_meeting_with_dimension_effects(self, cms, dimension_effects: dict):
        """创建含 dimension_effects 的紧急朝会，返回第一个选项 id。"""
        data = cms.get_emergency_meeting_data()
        option = data["topic"]["options"][0]
        option["dimension_effects"] = dimension_effects
        return option["id"]

    def test_make_decision_applies_dimension_effects_to_model(self, cms, model):
        model.game_data["dimensions"] = {
            "military": 50, "economy": 50, "technology": 50,
            "public_order": 50, "diplomacy": 50,
        }
        option_id = self._make_emergency_meeting_with_dimension_effects(
            cms, {"military": 10, "economy": -20}
        )
        result = cms.make_decision(option_id)
        assert result["success"] is True
        dims = model.game_data["dimensions"]
        assert dims["military"] == 60
        assert dims["economy"] == 30

    def test_make_decision_clamps_dimension_effects(self, cms, model):
        model.game_data["dimensions"] = {
            "military": 95, "economy": 5, "technology": 50,
            "public_order": 50, "diplomacy": 50,
        }
        option_id = self._make_emergency_meeting_with_dimension_effects(
            cms, {"military": 20, "economy": -30}
        )
        result = cms.make_decision(option_id)
        assert result["success"] is True
        dims = model.game_data["dimensions"]
        assert dims["military"] == 100
        assert dims["economy"] == 0

    def test_make_decision_without_dimension_effects_does_not_modify_dimensions(self, cms, model):
        model.game_data["dimensions"] = {"military": 50, "economy": 50,
                                          "technology": 50, "public_order": 50, "diplomacy": 50}
        data = cms.get_emergency_meeting_data()
        option = data["topic"]["options"][0]
        option.pop("dimension_effects", None)
        result = cms.make_decision(option["id"])
        assert result["success"] is True
        assert model.game_data["dimensions"]["military"] == 50

    def test_make_monthly_decision_applies_dimension_effects(self, cms, model):
        model.game_data["dimensions"] = {
            "military": 50, "economy": 50, "technology": 50,
            "public_order": 50, "diplomacy": 50,
        }
        # get_monthly_meeting_data auto-creates the monthly meeting (shallow copy — topics list is shared)
        data = cms.get_monthly_meeting_data()
        for topic in data["topics"]:
            for opt in topic["options"]:
                opt["dimension_effects"] = {"diplomacy": 5}

        while True:
            current = cms.get_current_topic()
            if not current:
                break
            option_id = current["options"][0]["id"]
            result = cms.make_monthly_decision(option_id)
            if not result.get("has_more_topics", True):
                break

        assert model.game_data["dimensions"]["diplomacy"] > 50


# ---------------------------------------------------------------------------
# F7 — 朝会提案库：≥30 条，四类各 ≥6，选项含 dimension_effects
# ---------------------------------------------------------------------------

class TestCourtTopicLibrary:
    """F7: COURT_TOPICS_MVP.json provides ≥30 topics across 4 categories."""

    @pytest.fixture
    def topics(self):
        from game.court_topic_loader import CourtTopicLoader
        CourtTopicLoader._topics = None  # reset class-level cache
        return CourtTopicLoader.load_topics()

    def test_pool_has_at_least_30_topics(self, topics):
        assert len(topics) >= 30, f"Only {len(topics)} topics loaded"

    def test_each_category_has_at_least_six_topics(self, topics):
        from collections import Counter
        counts = Counter(t["category"] for t in topics)
        for cat in ("military", "economy", "diplomacy", "internal"):
            assert counts[cat] >= 6, f"category '{cat}' has only {counts[cat]} topics"

    def test_each_topic_has_valid_options_with_dimension_effects(self, topics):
        for topic in topics:
            tid = topic.get("id", "?")
            assert 2 <= len(topic["options"]) <= 4, f"{tid}: wrong option count"
            for opt in topic["options"]:
                assert "dimension_effects" in opt, f"{tid}/{opt.get('id')}: missing dimension_effects"
                assert "description" in opt, f"{tid}/{opt.get('id')}: missing description"
                assert "effects" in opt, f"{tid}/{opt.get('id')}: missing effects"

    def test_court_system_uses_full_topic_pool(self, cms):
        """CourtMeetingSystem.__init__ loads topics from JSON via CourtTopicLoader."""
        assert len(cms.topic_templates) >= 30
