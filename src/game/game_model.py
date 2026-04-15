#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
游戏数据模型
管理游戏状态、资源和核心数据
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

class GameModel:
    """游戏数据模型类"""
    
    def __init__(self):
        """初始化游戏模型"""
        self.game_data = {
            "game_info": {
                "year": 190,  # 起始年份
                "month": 1,   # 月份 (1-12)
                "day": 1,     # 日期 (1-30)
                "season": 1,  # 季节 (1-4)，按季度计算
                "turn": 1,    # 回合数
                "current_faction": "wei",  # 当前势力
                "paused": False
            },
            "resources": {
                "gold": 10000,
                "food": 50000,
                "population": 100000,
                "soldiers": 5000
            },
            "court_resources": {
                "zhaoling_authority": 50,
                "intel_points": 20
            },
            "factions": {
                "wei": {"name": "魏", "color": "#0000FF", "capital": "luoyang", "alignment": "hawk"},
                "shu": {"name": "蜀", "color": "#008000", "capital": "chengdu", "alignment": "pragmatist"},
                "wu":  {"name": "吴", "color": "#FF0000", "capital": "jianye",  "alignment": "dove"}
            },
            "cities": {},
            "generals": {},
            "armies": {},
            "intel_unlocks": [],
            "faction_dimensions": {
                faction_id: {"military": 50, "economy": 50, "technology": 50,
                             "public_order": 50, "diplomacy": 50}
                for faction_id in ("wei", "shu", "wu")
            },
            "court_meetings": [],
            "last_court_meeting": None
        }
        
        # 加载初始数据
        self._load_initial_data()
    
    def _load_initial_data(self):
        """加载初始游戏数据"""
        # 加载城池数据
        cities_file = os.path.join("data", "cities.json")
        if os.path.exists(cities_file):
            with open(cities_file, 'r', encoding='utf-8') as f:
                self.game_data["cities"] = json.load(f)
        
        # 加载武将数据
        generals_file = os.path.join("data", "generals.json")
        if os.path.exists(generals_file):
            with open(generals_file, 'r', encoding='utf-8') as f:
                self.game_data["generals"] = json.load(f)
    
    def get_game_info(self) -> Dict[str, Any]:
        """获取游戏基本信息"""
        return self.game_data["game_info"]
    
    def get_resources(self) -> Dict[str, int]:
        """获取资源信息"""
        return self.game_data["resources"]

    def get_court_resources(self) -> Dict[str, int]:
        """获取宫廷资源信息。"""
        return self.game_data["court_resources"]

    def _recover_monthly_zhaoling_authority(self):
        """每月初一恢复诏令权威，按 5% 四舍五入并封顶 100。"""
        court_resources = self.game_data.setdefault("court_resources", {"zhaoling_authority": 50})
        current = court_resources.get("zhaoling_authority", 50)
        recovery = int((current * 0.05) + 0.5)
        court_resources["zhaoling_authority"] = min(100, current + recovery)
    
    def _consume_food_per_xun(self):
        """每旬消耗粮食：1 food per soldier，下限 0。首次归零时推送紧急事件。"""
        resources = self.game_data["resources"]
        soldiers = resources.get("soldiers", 0)
        food = resources.get("food", 0)
        new_food = max(0, food - soldiers)
        resources["food"] = new_food
        if food > 0 and new_food == 0:
            self._push_food_shortage_event()

    def _push_food_shortage_event(self):
        """推送粮草告急紧急朝会事件。"""
        info = self.game_data["game_info"]
        meeting = {
            "id": f"food_shortage_{info['year']}_{info['month']}_{info['day']}",
            "event_type": "food_shortage",
            "title": "粮草告急",
            "description": "军粮已耗尽，大军面临断粮危机，请陛下速做决断！",
            "is_emergency": True,
        }
        self.add_court_meeting(meeting)

    def _run_ai_factions_monthly(self):
        """月初为所有非玩家势力运行 AI 月度决策。"""
        from game.faction_ai import FactionAI
        player_faction = self.game_data["game_info"].get("current_faction", "wei")
        ai = FactionAI(self)
        for faction_id in self.game_data["factions"]:
            if faction_id != player_faction:
                ai.run_monthly_decision(faction_id)

    def _recover_monthly_intel_points(self):
        """每月初一恢复 5 情报点，上限 100。"""
        court_resources = self.game_data.setdefault("court_resources", {})
        current = court_resources.get("intel_points", 20)
        court_resources["intel_points"] = min(100, current + 5)

    def _expire_intel_unlocks(self):
        """清除已过期的情报解锁条目。"""
        info = self.game_data["game_info"]
        year, month = info["year"], info["month"]
        self.game_data["intel_unlocks"] = [
            u for u in self.game_data.get("intel_unlocks", [])
            if (u["expires_year"], u["expires_month"]) > (year, month)
        ]

    def unlock_city_intel(self, city_id: str, duration_months: int, cost: int = 5) -> bool:
        """消耗 `cost` 情报点，临时解锁城市情报（duration_months 个月内可见）。
        情报点不足时返回 False，不扣点。
        """
        court_resources = self.game_data.setdefault("court_resources", {})
        current = court_resources.get("intel_points", 0)
        if current < cost:
            return False
        court_resources["intel_points"] = current - cost

        info = self.game_data["game_info"]
        exp_month = info["month"] + duration_months
        exp_year = info["year"] + (exp_month - 1) // 12
        exp_month = ((exp_month - 1) % 12) + 1

        # 替换同一城市已有的解锁（刷新时效）
        unlocks = self.game_data.setdefault("intel_unlocks", [])
        self.game_data["intel_unlocks"] = [u for u in unlocks if u["city_id"] != city_id]
        self.game_data["intel_unlocks"].append({
            "city_id": city_id,
            "expires_year": exp_year,
            "expires_month": exp_month,
        })
        return True

    def _is_city_intel_unlocked(self, city_id: str) -> bool:
        """检查城市是否处于有效情报解锁期内。"""
        info = self.game_data["game_info"]
        year, month = info["year"], info["month"]
        for u in self.game_data.get("intel_unlocks", []):
            if u["city_id"] == city_id:
                return (u["expires_year"], u["expires_month"]) > (year, month)
        return False


    def update_resources(self, resources: Dict[str, int]):
        """更新资源"""
        for key, value in resources.items():
            if key in self.game_data["resources"]:
                self.game_data["resources"][key] += value

    def apply_dimension_effects(self, effects: Dict[str, int]):
        """应用五维数值变化并裁剪到 [0, 100]。"""
        dimensions = self.game_data.setdefault(
            "dimensions",
            {
                "military": 50,
                "economy": 50,
                "technology": 50,
                "public_order": 50,
                "diplomacy": 50,
            },
        )

        valid_keys = {"military", "economy", "technology", "public_order", "diplomacy"}
        for key, delta in effects.items():
            if key in valid_keys:
                new_value = dimensions.get(key, 50) + delta
                dimensions[key] = max(0, min(100, new_value))
    
    def get_factions(self) -> Dict[str, Dict[str, str]]:
        """获取势力信息"""
        return self.game_data["factions"]
    
    def get_cities(self) -> Dict[str, Dict[str, Any]]:
        """获取城池信息（全量原始数据，不做迷雾过滤）。"""
        return self.game_data["cities"]

    def get_cities_for_player(self, faction: str) -> Dict[str, Dict[str, Any]]:
        """返回城池信息，对迷雾中的非己方城市屏蔽 faction 与 soldiers。
        MVP 可见规则：city["faction"] == faction 即为己方可见城市。
        返回副本，不修改 game_data。
        """
        result = {}
        for city_id, city in self.game_data["cities"].items():
            if city.get("faction") == faction or self._is_city_intel_unlocked(city_id):
                result[city_id] = dict(city)
            else:
                masked = dict(city)
                masked["faction"] = None
                masked["soldiers"] = None
                result[city_id] = masked
        return result
    
    def get_generals(self) -> Dict[str, Dict[str, Any]]:
        """获取武将信息"""
        return self.game_data["generals"]
    
    def get_court_meetings(self) -> List[Dict[str, Any]]:
        """获取朝会记录"""
        return self.game_data["court_meetings"]
    
    def add_court_meeting(self, court_meeting: Dict[str, Any]):
        """添加朝会记录"""
        self.game_data["court_meetings"].append(court_meeting)
        self.game_data["last_court_meeting"] = court_meeting
    
    def advance_time(self):
        """推进游戏时间"""
        day = self.game_data["game_info"]["day"]
        month = self.game_data["game_info"]["month"]
        year = self.game_data["game_info"]["year"]
        
        # 日期推进
        day += 1
        crossed_month = False
        if day > 30:  # 假设每个月都是30天
            day = 1
            month += 1
            crossed_month = True
            if month > 12:
                month = 1
                year += 1
        
        self.game_data["game_info"]["day"] = day
        self.game_data["game_info"]["month"] = month
        # 更新季度（季节）信息，每3个月为一季
        season = ((month - 1) // 3) + 1
        self.game_data["game_info"]["season"] = season
        self.game_data["game_info"]["year"] = year
        self.game_data["game_info"]["turn"] += 1

        crossed_xun = (day in (10, 20)) or crossed_month
        if crossed_xun:
            self._consume_food_per_xun()

        if crossed_month:
            self._recover_monthly_zhaoling_authority()
            self._recover_monthly_intel_points()
            self._expire_intel_unlocks()
            self._run_ai_factions_monthly()
    
    def save_game(self, filename: str):
        """保存游戏"""
        save_data = {
            "save_time": datetime.now().isoformat(),
            "game_data": self.game_data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
    
    def load_game(self, filename: str):
        """加载游戏"""
        with open(filename, 'r', encoding='utf-8') as f:
            save_data = json.load(f)
            self.game_data = save_data["game_data"]