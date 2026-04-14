#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration tests — 完整朝会流程（F3-F6 端到端）
覆盖：触发 → 提案展示 → 决策 → 数值变化 → 状态归零

运行：pytest src/test/integration/test_court_flow.py -v
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
    from game.court_meeting import CourtMeetingSystem
    system = CourtMeetingSystem.__new__(CourtMeetingSystem)
    system.game_model = model
    system.meeting_started = MagicMock()
    system.meeting_started.emit = MagicMock()
    system.meeting_completed = MagicMock()
    system.meeting_completed.emit = MagicMock()
    system.current_meeting = None
    system.meeting_active = False

    real = CourtMeetingSystem.__new__(CourtMeetingSystem)
    real.game_model = model
    real.meeting_started = MagicMock()
    real.meeting_started.emit = MagicMock()
    real.meeting_completed = MagicMock()
    real.meeting_completed.emit = MagicMock()
    real.current_meeting = None
    real.meeting_active = False
    real.__init__(model)
    system.topic_templates = real.topic_templates
    return system


# ---------------------------------------------------------------------------
# 核心闭环：触发 → 决策 → 数值变化
# ---------------------------------------------------------------------------

class TestFullCourtCycle:
    def _run_one_cycle(self, cms, model):
        """执行一次完整朝会（月度路径）并返回 (result, gold_delta)"""
        gold_before = model.get_resources()["gold"]

        # 1. 开始朝会
        start_result = cms.start_meeting()
        assert start_result["success"] is True, f"朝会开始失败: {start_result}"

        # 2. 获取提案和第一个选项
        meeting = start_result["meeting"]
        topic = meeting["topic"]
        option = topic["options"][0]

        # 准备 topics 列表（make_monthly_decision 需要）
        meeting["topics"] = [topic]
        meeting["current_topic_index"] = 0
        cms.current_meeting = meeting

        # 3. 做出决策
        decision_result = cms.make_monthly_decision(option["id"])

        gold_after = model.get_resources()["gold"]
        return decision_result, gold_after - gold_before

    def test_full_cycle_succeeds(self, cms, model):
        result, _ = self._run_one_cycle(cms, model)
        assert result["success"] is True, f"决策失败: {result.get('message')}"

    def test_gold_changes_after_decision(self, cms, model):
        """决策后 gold 值发生变化（如果 effects 包含 gold）"""
        start_result = cms.start_meeting()
        meeting = start_result["meeting"]
        topic = meeting["topic"]

        # 找一个有 gold effect 的选项
        gold_option = next(
            (opt for opt in topic["options"] if "gold" in opt.get("effects", {})),
            None
        )
        if gold_option is None:
            pytest.skip("当前议题没有 gold effect，跳过此测试")

        gold_before = model.get_resources()["gold"]
        meeting["topics"] = [topic]
        meeting["current_topic_index"] = 0
        cms.current_meeting = meeting

        cms.make_monthly_decision(gold_option["id"])
        gold_after = model.get_resources()["gold"]
        expected_delta = gold_option["effects"]["gold"]
        assert gold_after == gold_before + expected_delta

    def test_model_state_consistent_after_cycle(self, cms, model):
        """朝会结束后 game_model 状态不能出现非法值（不崩溃）"""
        self._run_one_cycle(cms, model)
        info = model.get_game_info()
        resources = model.get_resources()
        assert isinstance(info["year"], int)
        assert isinstance(resources, dict)

    def test_second_meeting_blocked_same_season(self, cms, model):
        """同年同季节完成一次朝会后，不能再次召开"""
        self._run_one_cycle(cms, model)
        # 重置 meeting_active 但保留 last_court_meeting
        cms.meeting_active = False
        assert cms.can_hold_meeting() is False

    def test_twelve_months_no_crash(self, cms, model):
        """模拟12个月，每月初一触发朝会，不崩溃"""
        for month in range(1, 13):
            model.game_data["game_info"]["month"] = month
            model.game_data["game_info"]["day"] = 1
            model.game_data["game_info"]["season"] = ((month - 1) // 3) + 1
            model.game_data["last_court_meeting"] = None  # 每月重置
            cms.meeting_active = False
            cms.current_meeting = None

            result = cms.start_meeting()
            assert result["success"] is True, f"月份 {month} 朝会失败"

            meeting = result["meeting"]
            topic = meeting["topic"]
            option = topic["options"][0]
            meeting["topics"] = [topic]
            meeting["current_topic_index"] = 0
            cms.current_meeting = meeting

            d = cms.make_monthly_decision(option["id"])
            assert d["success"] is True, f"月份 {month} 决策失败"
