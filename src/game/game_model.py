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
            "factions": {
                "wei": {"name": "魏", "color": "#0000FF", "capital": "luoyang"},
                "shu": {"name": "蜀", "color": "#008000", "capital": "chengdu"},
                "wu": {"name": "吴", "color": "#FF0000", "capital": "jianye"}
            },
            "cities": {},
            "generals": {},
            "armies": {},
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
    
    def update_resources(self, resources: Dict[str, int]):
        """更新资源"""
        for key, value in resources.items():
            if key in self.game_data["resources"]:
                self.game_data["resources"][key] += value
    
    def get_factions(self) -> Dict[str, Dict[str, str]]:
        """获取势力信息"""
        return self.game_data["factions"]
    
    def get_cities(self) -> Dict[str, Dict[str, Any]]:
        """获取城池信息"""
        return self.game_data["cities"]
    
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
        if day > 30:  # 假设每个月都是30天
            day = 1
            month += 1
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