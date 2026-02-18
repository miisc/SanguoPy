#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
朝会系统
管理朝会流程、议题生成和决策处理
"""

import random
from typing import Dict, List, Optional, Any
from PyQt5.QtCore import QObject, pyqtSignal


class CourtMeetingSystem(QObject):
    """朝会系统类"""
    
    # 信号定义
    meeting_started = pyqtSignal(dict)  # 朝会开始信号
    meeting_completed = pyqtSignal(dict)  # 朝会完成信号
    
    def __init__(self, game_model):
        """初始化朝会系统"""
        super().__init__()
        self.game_model = game_model
        self.current_meeting = None
        self.meeting_active = False
        
        # 朝会议题模板
        self.topic_templates = [
            {
                "id": "tax_increase",
                "title": "增税政策",
                "description": "国库紧张，是否应该提高税率以增加收入？",
                "background": "由于连年征战，国库空虚，急需增加财政收入。",
                "options": [
                    {
                        "id": "increase_tax",
                        "title": "提高税率",
                        "description": "将税率提高10%，可增加国库收入，但可能降低民忠。",
                        "effects": {
                            "gold": 2000,
                            "population_satisfaction": -10
                        }
                    },
                    {
                        "id": "maintain_tax",
                        "title": "维持现状",
                        "description": "保持当前税率不变，维持民心稳定。",
                        "effects": {
                            "gold": 0,
                            "population_satisfaction": 0
                        }
                    },
                    {
                        "id": "reduce_tax",
                        "title": "降低税率",
                        "description": "降低税率以安抚民心，但国库收入会减少。",
                        "effects": {
                            "gold": -1000,
                            "population_satisfaction": 10
                        }
                    }
                ]
            },
            {
                "id": "military_expansion",
                "title": "军事扩张",
                "description": "是否应该扩大军队规模以增强国防实力？",
                "background": "邻国频繁调动军队，边境安全受到威胁。",
                "options": [
                    {
                        "id": "expand_army",
                        "title": "扩军备战",
                        "description": "招募新兵，扩大军队规模，增强国防力量。",
                        "effects": {
                            "soldiers": 2000,
                            "gold": -3000,
                            "food": -5000
                        }
                    },
                    {
                        "id": "defensive_focus",
                        "title": "加强防御",
                        "description": "不增加军队数量，但加强城防建设。",
                        "effects": {
                            "gold": -2000,
                            "defense_bonus": 10
                        }
                    },
                    {
                        "id": "diplomatic_solution",
                        "title": "外交解决",
                        "description": "通过外交手段缓解紧张局势，避免军事对抗。",
                        "effects": {
                            "gold": -1000,
                            "diplomacy_bonus": 15
                        }
                    }
                ]
            },
            {
                "id": "infrastructure",
                "title": "基础设施建设",
                "description": "是否应该投资基础设施建设以促进经济发展？",
                "background": "国内基础设施落后，影响经济发展和民生改善。",
                "options": [
                    {
                        "id": "major_investment",
                        "title": "大规模投资",
                        "description": "投入大量资金建设道路、水利等基础设施。",
                        "effects": {
                            "gold": -5000,
                            "economic_growth": 20,
                            "population_growth": 5
                        }
                    },
                    {
                        "id": "moderate_investment",
                        "title": "适度投资",
                        "description": "投入适量资金，重点建设关键基础设施。",
                        "effects": {
                            "gold": -2500,
                            "economic_growth": 10,
                            "population_growth": 2
                        }
                    },
                    {
                        "id": "delay_investment",
                        "title": "暂缓投资",
                        "description": "暂时搁置基础设施建设，优先保障军费开支。",
                        "effects": {
                            "gold": 0,
                            "military_bonus": 10
                        }
                    }
                ]
            }
        ]
    
    def can_hold_meeting(self) -> bool:
        """检查是否可以召开朝会"""
        if self.meeting_active:
            return False
        
        game_info = self.game_model.get_game_info()
        # 每季度可以召开一次朝会
        season = game_info["season"]
        last_meeting = self.game_model.game_data.get("last_court_meeting")
        
        if last_meeting:
            last_season = last_meeting.get("season", 0)
            last_year = last_meeting.get("year", 0)
            
            # 如果是同一年同一季节，不能再次召开朝会
            if last_year == game_info["year"] and last_season == season:
                return False
        
        return True
    
    def start_meeting(self) -> Dict[str, Any]:
        """开始朝会"""
        if not self.can_hold_meeting():
            return {"success": False, "message": "当前不能召开朝会"}
        
        game_info = self.game_model.get_game_info()
        
        # 选择一个议题
        topic = random.choice(self.topic_templates)
        
        # 获取参与朝会的武将
        participants = self._get_participants()
        
        # 生成朝臣意见
        opinions = self._generate_opinions(topic, participants)
        
        # 创建朝会数据
        self.current_meeting = {
            "id": f"court_{game_info['year']}_{game_info['season']}",
            "year": game_info["year"],
            "season": game_info["season"],
            "topic": topic,
            "participants": participants,
            "opinions": opinions,
            "decision": None,
            "completed": False
        }
        
        self.meeting_active = True
        
        # 发出朝会开始信号
        self.meeting_started.emit(self.current_meeting)
        
        return {
            "success": True,
            "meeting": self.current_meeting
        }
    
    def get_meeting_data(self) -> Optional[Dict[str, Any]]:
        """获取当前朝会数据"""
        return self.current_meeting
    
    def make_decision(self, option_id: str) -> Dict[str, Any]:
        """做出朝会决策"""
        if not self.meeting_active or not self.current_meeting:
            return {"success": False, "message": "没有活跃的朝会"}
        
        topic = self.current_meeting["topic"]
        selected_option = None
        
        # 查找选中的选项
        for option in topic["options"]:
            if option["id"] == option_id:
                selected_option = option
                break
        
        if not selected_option:
            return {"success": False, "message": "无效的决策选项"}
        
        # 记录决策
        self.current_meeting["decision"] = {
            "option_id": option_id,
            "option_title": selected_option["title"],
            "effects": selected_option["effects"]
        }
        self.current_meeting["completed"] = True
        
        # 应用决策效果
        resource_changes = {}
        if "gold" in selected_option["effects"]:
            resource_changes["gold"] = selected_option["effects"]["gold"]
        if "food" in selected_option["effects"]:
            resource_changes["food"] = selected_option["effects"]["food"]
        if "soldiers" in selected_option["effects"]:
            resource_changes["soldiers"] = selected_option["effects"]["soldiers"]
        
        # 完成朝会
        self.meeting_active = False
        meeting_result = self.current_meeting.copy()
        meeting_result["resource_changes"] = resource_changes
        
        # 发出朝会完成信号
        self.meeting_completed.emit(meeting_result)
        
        # 重置当前朝会
        self.current_meeting = None
        
        return {
            "success": True,
            "decision": selected_option,
            "resource_changes": resource_changes
        }
    
    def _get_participants(self) -> List[Dict[str, Any]]:
        """获取参与朝会的武将"""
        generals = self.game_model.get_generals()
        participants = []
        
        # 随机选择3-5名武将参与朝会
        general_list = list(generals.values())
        if len(general_list) > 0:
            participant_count = min(len(general_list), random.randint(3, 5))
            selected_generals = random.sample(general_list, participant_count)
            
            for general in selected_generals:
                participants.append({
                    "id": general["id"],
                    "name": general["name"],
                    "title": general.get("title", "武将"),
                    "loyalty": general.get("loyalty", 80),
                    "intelligence": general.get("intelligence", 50),
                    "politics": general.get("politics", 50)
                })
        
        return participants
    
    def _generate_opinions(self, topic: Dict[str, Any], participants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成朝臣意见"""
        opinions = []
        
        for participant in participants:
            # 根据武将属性和议题类型生成意见
            opinion = self._generate_single_opinion(topic, participant)
            opinions.append(opinion)
        
        return opinions
    
    def _generate_single_opinion(self, topic: Dict[str, Any], participant: Dict[str, Any]) -> Dict[str, Any]:
        """为单个朝臣生成意见"""
        # 简单的意见生成逻辑，根据武将属性偏好不同选项
        intelligence = participant.get("intelligence", 50)
        politics = participant.get("politics", 50)
        loyalty = participant.get("loyalty", 80)
        
        # 根据议题类型和武将属性选择偏好选项
        preferred_option_index = 0
        
        if topic["id"] == "tax_increase":
            # 政治属性高的倾向于维持或降低税率
            if politics > 60:
                preferred_option_index = random.choice([1, 2])
            else:
                preferred_option_index = random.choice([0, 1])
        elif topic["id"] == "military_expansion":
            # 忠诚度高的倾向于扩军
            if loyalty > 70:
                preferred_option_index = 0
            # 智力高的倾向于外交
            elif intelligence > 70:
                preferred_option_index = 2
            else:
                preferred_option_index = 1
        elif topic["id"] == "infrastructure":
            # 随机选择
            preferred_option_index = random.randint(0, 2)
        
        preferred_option = topic["options"][preferred_option_index]
        
        # 生成意见文本
        opinion_texts = [
            f"臣认为应当{preferred_option['title']}，这样可以{preferred_option['description'][:20]}...",
            f"陛下，臣以为{preferred_option['title']}是明智之举，因为{preferred_option['description'][:20]}...",
            f"根据当前形势，臣建议{preferred_option['title']}，此举将{preferred_option['description'][:20]}..."
        ]
        
        opinion_text = random.choice(opinion_texts)
        
        return {
            "participant_id": participant["id"],
            "participant_name": participant["name"],
            "opinion": opinion_text,
            "preferred_option": preferred_option["id"],
            "support_level": random.randint(60, 100)  # 支持度
        }