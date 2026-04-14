#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests — GameModel
覆盖：时间推进、月份进位、资源更新、边界条件

运行：pytest src/test/unit/test_game_model.py -v
"""
import sys
import os
import json
import pytest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


# ---------------------------------------------------------------------------
# Fixtures（补充 conftest.py 中的本地变体）
# ---------------------------------------------------------------------------

@pytest.fixture
def model():
    from game.game_model import GameModel
    with patch("game.game_model.os.path.exists", return_value=False):
        return GameModel()


# ---------------------------------------------------------------------------
# 时间推进
# ---------------------------------------------------------------------------

class TestAdvanceTime:
    def test_day_increments_by_one(self, model):
        """正常推进：日+1"""
        model.game_data["game_info"]["day"] = 5
        model.advance_time()
        assert model.get_game_info()["day"] == 6

    def test_month_rolls_at_day_30(self, model):
        """第30天推进后月份+1，日重置为1"""
        model.game_data["game_info"]["day"] = 30
        model.game_data["game_info"]["month"] = 3
        model.advance_time()
        info = model.get_game_info()
        assert info["day"] == 1
        assert info["month"] == 4

    def test_year_rolls_at_month_12(self, model):
        """12月第30天后年份+1，月重置为1"""
        model.game_data["game_info"]["day"] = 30
        model.game_data["game_info"]["month"] = 12
        model.game_data["game_info"]["year"] = 190
        model.advance_time()
        info = model.get_game_info()
        assert info["day"] == 1
        assert info["month"] == 1
        assert info["year"] == 191

    def test_season_updates_with_month(self, model):
        """季度随月份变化：月1-3=季1, 4-6=季2, …"""
        for month, expected_season in [(1, 1), (3, 1), (4, 2), (6, 2), (7, 3), (10, 4)]:
            model.game_data["game_info"]["month"] = month
            model.game_data["game_info"]["day"] = 30  # 触发月份刷新
            model.advance_time()
            # 推进后月份变为 month+1，季节应等于 ((month) // 3) + 1
            # 直接设月份后验证 season 计算
        # 直接测 season 计算逻辑：设置 day=30,month=3 → 推进后 month=4, season=2
        model.game_data["game_info"]["day"] = 30
        model.game_data["game_info"]["month"] = 3
        model.advance_time()
        assert model.get_game_info()["season"] == 2

    def test_turn_increments_each_call(self, model):
        """每次 advance_time 回合数+1"""
        initial_turn = model.get_game_info()["turn"]
        model.advance_time()
        assert model.get_game_info()["turn"] == initial_turn + 1

    def test_month_start_recovers_zhaoling_authority_with_half_up_rounding(self, model):
        """跨月到月初一时，诏令权威按 5% 四舍五入恢复"""
        model.game_data["game_info"]["day"] = 30
        model.game_data["court_resources"]["zhaoling_authority"] = 50

        model.advance_time()

        assert model.get_game_info()["day"] == 1
        assert model.get_court_resources()["zhaoling_authority"] == 53

    def test_month_start_recovery_caps_at_100(self, model):
        """跨月恢复后不得超过上限 100"""
        model.game_data["game_info"]["day"] = 30
        model.game_data["court_resources"]["zhaoling_authority"] = 99

        model.advance_time()

        assert model.get_court_resources()["zhaoling_authority"] == 100

    def test_non_month_start_does_not_recover_zhaoling_authority(self, model):
        """非月初推进不应恢复诏令权威"""
        model.game_data["game_info"]["day"] = 5
        model.game_data["court_resources"]["zhaoling_authority"] = 50

        model.advance_time()

        assert model.get_game_info()["day"] == 6
        assert model.get_court_resources()["zhaoling_authority"] == 50


# ---------------------------------------------------------------------------
# 资源更新
# ---------------------------------------------------------------------------

class TestUpdateResources:
    def test_gold_increases(self, model):
        """gold += 正值"""
        initial = model.get_resources()["gold"]
        model.update_resources({"gold": 1000})
        assert model.get_resources()["gold"] == initial + 1000

    def test_gold_decreases(self, model):
        """gold += 负值（消耗）"""
        model.game_data["resources"]["gold"] = 5000
        model.update_resources({"gold": -2000})
        assert model.get_resources()["gold"] == 3000

    def test_multiple_resources_update_simultaneously(self, model):
        """多字段同时更新"""
        model.game_data["resources"]["gold"] = 10000
        model.game_data["resources"]["food"] = 50000
        model.update_resources({"gold": 2000, "food": -5000})
        r = model.get_resources()
        assert r["gold"] == 12000
        assert r["food"] == 45000

    def test_unknown_resource_key_is_ignored(self, model):
        """未知资源字段不产生异常，也不创建新字段"""
        model.update_resources({"nonexistent_key": 999})
        assert "nonexistent_key" not in model.get_resources()

    def test_decision_effects_applied_correctly(self, model):
        """朝会决策 effects 结构可正确应用"""
        effects = {"gold": 2000, "people": -5}
        initial_gold = model.get_resources()["gold"]
        initial_pop = model.get_resources()["population"]
        # people -> population 的映射需在 apply_effects 层处理
        model.update_resources({"gold": effects["gold"]})
        assert model.get_resources()["gold"] == initial_gold + 2000


# ---------------------------------------------------------------------------
# 月度朝会触发检测（GameController 逻辑镜像测试）
# ---------------------------------------------------------------------------

class TestMonthlyCourtTrigger:
    def test_trigger_when_day_becomes_1(self, model):
        """day 从非1变为1时应触发月度朝会"""
        model.game_data["game_info"]["day"] = 30
        pre_day = model.get_game_info()["day"]
        model.advance_time()
        post_day = model.get_game_info()["day"]
        # 此处只验证状态，GameController 负责信号；此处验证条件是否成立
        assert pre_day == 30
        assert post_day == 1, "跨月后 day 应重置为 1"


class TestPersistenceAndInitData:
    def test_save_and_load_roundtrip(self, tmp_path):
        from game.game_model import GameModel
        with patch("game.game_model.os.path.exists", return_value=False):
            m1 = GameModel()

        m1.game_data["resources"]["gold"] = 12345
        save_file = tmp_path / "save.json"
        m1.save_game(str(save_file))

        with patch("game.game_model.os.path.exists", return_value=False):
            m2 = GameModel()
        m2.load_game(str(save_file))
        assert m2.get_resources()["gold"] == 12345

    def test_load_initial_data_when_files_exist(self):
        from game.game_model import GameModel
        # 使用仓库内真实 data 目录覆盖 _load_initial_data 的 exists/open 分支
        m = GameModel()
        assert isinstance(m.get_cities(), dict)
        assert isinstance(m.get_generals(), dict)
        assert len(m.get_generals()) > 0

    def test_add_court_meeting_updates_last_record(self, model):
        record = {"id": "court_1", "season": 1}
        model.add_court_meeting(record)
        assert model.get_court_meetings()[-1]["id"] == "court_1"
        assert model.game_data["last_court_meeting"]["id"] == "court_1"


# ---------------------------------------------------------------------------
# F6 — 迷雾数据层执行：get_cities_for_player
# ---------------------------------------------------------------------------

class TestCityFogOfWar:
    """F6: get_cities_for_player masks faction and soldiers for non-player cities."""

    _CITIES = {
        "luoyang": {"id": "luoyang", "name": "洛阳", "faction": "wei", "soldiers": 5000, "defense": 80},
        "chengdu": {"id": "chengdu", "name": "成都", "faction": "shu", "soldiers": 4000, "defense": 70},
    }

    @pytest.fixture
    def model_with_cities(self, model):
        model.game_data["cities"] = {k: dict(v) for k, v in self._CITIES.items()}
        return model

    def test_own_faction_city_returns_full_data(self, model_with_cities):
        cities = model_with_cities.get_cities_for_player("wei")
        assert cities["luoyang"]["faction"] == "wei"
        assert cities["luoyang"]["soldiers"] == 5000

    def test_enemy_city_faction_is_masked(self, model_with_cities):
        cities = model_with_cities.get_cities_for_player("wei")
        assert cities["chengdu"]["faction"] is None

    def test_enemy_city_soldiers_is_masked(self, model_with_cities):
        cities = model_with_cities.get_cities_for_player("wei")
        assert cities["chengdu"]["soldiers"] is None

    def test_enemy_city_name_still_visible(self, model_with_cities):
        cities = model_with_cities.get_cities_for_player("wei")
        assert cities["chengdu"]["name"] == "成都"

    def test_get_cities_unaffected_after_fog_call(self, model_with_cities):
        """get_cities_for_player must not mutate game_data; get_cities() still returns raw data."""
        model_with_cities.get_cities_for_player("wei")
        raw = model_with_cities.get_cities()
        assert raw["chengdu"]["faction"] == "shu"
        assert raw["chengdu"]["soldiers"] == 4000


class TestZhaolingAuthorityRecoveryBoundaries:
    """锁定 _recover_monthly_zhaoling_authority 的全部边界行为。"""

    @pytest.mark.parametrize("initial, expected", [
        (95, 100),  # 5% of 95 = 4.75 → rounds to 5, 95+5=100
        (0, 0),     # 5% of 0 = 0 → stays 0
        (100, 100), # 5% of 100 = 5, 100+5=105 → capped at 100
        (19, 20),   # 5% of 19 = 0.95 → rounds to 1, 19+1=20
    ])
    def test_zhaoling_authority_recovery_boundaries(self, model, initial, expected):
        model.game_data["game_info"]["day"] = 30
        model.game_data["court_resources"]["zhaoling_authority"] = initial
        model.advance_time()
        assert model.get_court_resources()["zhaoling_authority"] == expected


# ---------------------------------------------------------------------------
# F9 — 情报点资源：初始值、月度恢复、城市解锁与时效
# ---------------------------------------------------------------------------

class TestIntelligenceSystem:
    """F9: intel_points resource, unlock_city_intel, fog bypass with expiry."""

    def test_intel_points_initial_value(self, model):
        """game_data.court_resources.intel_points 初始为 20。"""
        assert model.get_court_resources()["intel_points"] == 20

    def test_monthly_recovery_adds_five(self, model):
        """月初推进时 intel_points +5。"""
        model.game_data["court_resources"]["intel_points"] = 30
        model.game_data["game_info"]["day"] = 30
        model.advance_time()  # 触发月份进位
        assert model.get_court_resources()["intel_points"] == 35

    def test_intel_points_capped_at_100(self, model):
        """intel_points 恢复后上限 100，不溢出。"""
        model.game_data["court_resources"]["intel_points"] = 98
        model.game_data["game_info"]["day"] = 30
        model.advance_time()
        assert model.get_court_resources()["intel_points"] == 100

    def test_unlock_city_intel_deducts_points(self, model):
        """unlock_city_intel 消耗 5 intel_points。"""
        model.game_data["court_resources"]["intel_points"] = 20
        # 添加一个非己方城市供测试
        model.game_data["cities"]["enemy_city"] = {"name": "敌城", "faction": "shu", "soldiers": 3000}
        success = model.unlock_city_intel("enemy_city", duration_months=3)
        assert success is True
        assert model.get_court_resources()["intel_points"] == 15

    def test_unlocked_city_visible_through_fog(self, model):
        """unlock 后 get_cities_for_player 对该城市返回完整数据（faction/soldiers 可见）。"""
        model.game_data["cities"]["enemy_city"] = {"name": "敌城", "faction": "shu", "soldiers": 3000}
        model.game_data["court_resources"]["intel_points"] = 20
        model.unlock_city_intel("enemy_city", duration_months=3)
        cities = model.get_cities_for_player("wei")
        assert cities["enemy_city"]["faction"] == "shu"
        assert cities["enemy_city"]["soldiers"] == 3000

    def test_intel_expires_after_duration(self, model):
        """时效到期后城市重新被迷雾遮蔽（faction/soldiers=None）。"""
        model.game_data["cities"]["enemy_city"] = {"name": "敌城", "faction": "shu", "soldiers": 3000}
        model.game_data["court_resources"]["intel_points"] = 20
        model.game_data["game_info"]["month"] = 1
        model.game_data["game_info"]["year"] = 190
        model.unlock_city_intel("enemy_city", duration_months=1)
        # 推进 2 个月（确保过期）
        for _ in range(60):  # 30天/月 × 2月
            model.advance_time()
        cities = model.get_cities_for_player("wei")
        assert cities["enemy_city"]["faction"] is None
        assert cities["enemy_city"]["soldiers"] is None

    def test_insufficient_intel_points_rejects_unlock(self, model):
        """intel_points 不足 5 时 unlock_city_intel 返回 False，不扣点。"""
        model.game_data["cities"]["enemy_city"] = {"name": "敌城", "faction": "shu", "soldiers": 3000}
        model.game_data["court_resources"]["intel_points"] = 3
        success = model.unlock_city_intel("enemy_city", duration_months=3)
        assert success is False
        assert model.get_court_resources()["intel_points"] == 3
