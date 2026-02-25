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
                "has_location": False,
                "options": [
                    {
                        "id": "increase_tax",
                        "title": "提高税率",
                        "description": "将税率提高10%，可增加国库收入，但可能降低民忠。",
                        "effects": {
                            "gold": 2000,
                            "people": -5
                        }
                    },
                    {
                        "id": "maintain_tax",
                        "title": "维持现状",
                        "description": "保持当前税率不变，维持民心稳定。",
                        "effects": {
                            "gold": 0,
                            "people": 0
                        }
                    },
                    {
                        "id": "reduce_tax",
                        "title": "降低税率",
                        "description": "降低税率以安抚民心，但国库收入会减少。",
                        "effects": {
                            "gold": -1000,
                            "people": 5
                        }
                    }
                ]
            },
            {
                "id": "military_expansion",
                "title": "军事扩张",
                "description": "是否应该扩大军队规模以增强国防实力？",
                "background": "邻国频繁调动军队，边境安全受到威胁。",
                "related_city": "luoyang",
                "has_location": True,
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
                            "defense": 5
                        }
                    },
                    {
                        "id": "diplomatic_solution",
                        "title": "外交解决",
                        "description": "通过外交手段缓解紧张局势，避免军事对抗。",
                        "effects": {
                            "gold": -1000,
                            "diplomacy": 5
                        }
                    }
                ]
            },
            {
                "id": "infrastructure",
                "title": "基础设施建设",
                "description": "是否应该投资基础设施建设以促进经济发展？",
                "background": "国内基础设施落后，影响经济发展和民生改善。",
                "related_city": "chengdu",
                "has_location": True,
                "options": [
                    {
                        "id": "major_investment",
                        "title": "大规模投资",
                        "description": "投入大量资金建设道路、水利等基础设施。",
                        "effects": {
                            "gold": -5000,
                            "economy": 5,
                            "people": 3
                        }
                    },
                    {
                        "id": "moderate_investment",
                        "title": "适度投资",
                        "description": "投入适量资金，重点建设关键基础设施。",
                        "effects": {
                            "gold": -2500,
                            "economy": 3,
                            "people": 2
                        }
                    },
                    {
                        "id": "delay_investment",
                        "title": "暂缓投资",
                        "description": "暂时搁置基础设施建设，优先保障军费开支。",
                        "effects": {
                            "gold": 0,
                            "military": 2
                        }
                    }
                ]
            },
            {
                "id": "agricultural_development",
                "title": "农业发展",
                "description": "是否应该投资农业发展以提高粮食产量？",
                "background": "今年收成不佳，粮食储备不足，需要制定农业发展政策。",
                "has_location": False,
                "options": [
                    {
                        "id": "irrigation_project",
                        "title": "兴修水利",
                        "description": "投资修建灌溉设施，提高农业产量。",
                        "effects": {
                            "gold": -3000,
                            "food": 5000,
                            "economy": 3
                        }
                    },
                    {
                        "id": "farmer_support",
                        "title": "扶持农桑",
                        "description": "减免农民赋税，鼓励农业生产。",
                        "effects": {
                            "gold": -2000,
                            "food": 3000,
                            "people": 5
                        }
                    },
                    {
                        "id": "technology_improvement",
                        "title": "推广农技",
                        "description": "推广先进农耕技术，提高单位产量。",
                        "effects": {
                            "gold": -1500,
                            "tech": 3,
                            "food": 2000
                        }
                    }
                ]
            },
            {
                "id": "trade_policy",
                "title": "贸易政策",
                "description": "是否应该开放对外贸易以增加收入？",
                "background": "周边国家商品丰富，开放贸易可增加收入，但也带来风险。",
                "has_location": False,
                "options": [
                    {
                        "id": "open_trade",
                        "title": "开放贸易",
                        "description": "开放边境贸易，增加财政收入。",
                        "effects": {
                            "gold": 4000,
                            "diplomacy": 3,
                            "defense": -2
                        }
                    },
                    {
                        "id": "controlled_trade",
                        "title": "管制贸易",
                        "description": "限制贸易范围，确保国家安全。",
                        "effects": {
                            "gold": 2000,
                            "diplomacy": 1,
                            "defense": 2
                        }
                    },
                    {
                        "id": "closed_policy",
                        "title": "闭关锁国",
                        "description": "禁止对外贸易，自给自足。",
                        "effects": {
                            "gold": -1000,
                            "defense": 3,
                            "economy": -3
                        }
                    }
                ]
            },
            {
                "id": "education_reform",
                "title": "教育改革",
                "description": "是否应该投资教育以培养人才？",
                "background": "国家缺乏治理人才，需要重视教育培养。",
                "has_location": False,
                "options": [
                    {
                        "id": "establish_schools",
                        "title": "兴办学校",
                        "description": "在全国设立学校，培养人才。",
                        "effects": {
                            "gold": -2500,
                            "tech": 5,
                            "people": 2
                        }
                    },
                    {
                        "id": "talent_recruitment",
                        "title": "招贤纳士",
                        "description": "发布招贤令，吸引天下人才。",
                        "effects": {
                            "gold": -2000,
                            "people": -2,
                            "tech": 3
                        }
                    },
                    {
                        "id": "civil_service_exam",
                        "title": "科举取士",
                        "description": "建立科举制度，选拔优秀人才。",
                        "effects": {
                            "gold": -1500,
                            "tech": 3,
                            "people": 1
                        }
                    }
                ]
            },
            {
                "id": "pass_garrison",
                "title": "关隘驻守",
                "description": "虎牢关地处要冲，近日探报显示敌方有异动，是否增兵驻守？",
                "background": "虎牢关扼守中原咽喉，地势险要，历来为兵家必争之地。斥候来报，关外出现大队敌军旗帜，形势紧迫。",
                "has_location": True,
                "related_position": [27, 26],
                "options": [
                    {
                        "id": "reinforce_pass",
                        "title": "增兵驻守",
                        "description": "从各处调兵，大规模增援虎牢关守军，严阵以待。",
                        "effects": {
                            "soldiers": -3000,
                            "gold": -2000,
                            "defense": 8
                        }
                    },
                    {
                        "id": "hold_current",
                        "title": "维持现状",
                        "description": "关隘现有守军尚可应对，静观其变，待敌意图明朗再行定夺。",
                        "effects": {
                            "defense": 2,
                            "gold": 0
                        }
                    },
                    {
                        "id": "send_scouts",
                        "title": "遣使侦察",
                        "description": "派出精锐斥候深入敌境，摸清虚实后再作部署，避免劳师动众。",
                        "effects": {
                            "gold": -500,
                            "defense": 1,
                            "diplomacy": 1
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
    
    def get_current_topic(self) -> Optional[Dict[str, Any]]:
        """获取当前议题"""
        if not self.current_meeting or "topics" not in self.current_meeting:
            return None
        
        current_index = self.current_meeting.get("current_topic_index", 0)
        topics = self.current_meeting["topics"]
        
        if 0 <= current_index < len(topics):
            return topics[current_index]
        return None
    
    def get_monthly_meeting_data(self) -> Optional[Dict[str, Any]]:
        """获取月度朝会数据"""
        # 如果没有活跃的朝会，创建一个新的月度朝会
        if not self.meeting_active:
            self._create_monthly_meeting()
        
        # 确保返回的数据包含当前议题
        if self.current_meeting:
            meeting_data = self.current_meeting.copy()
            
            # 如果是多议题模式，添加当前议题
            if "topics" in self.current_meeting:
                current_topic = self.get_current_topic()
                if current_topic:
                    meeting_data["topic"] = current_topic
                else:
                    # 即使获取不到当前议题，也至少返回基本数据
                    pass
            
            return meeting_data
        
        return self.current_meeting
    
    def get_emergency_meeting_data(self) -> Optional[Dict[str, Any]]:
        """获取紧急朝会数据"""
        # 如果没有活跃的朝会，创建一个新的紧急朝会
        if not self.meeting_active:
            self._create_emergency_meeting()
        
        return self.current_meeting
    
    def make_monthly_decision(self, option_id: str) -> Dict[str, Any]:
        """做出月度朝会决策"""
        if not self.meeting_active or not self.current_meeting:
            return {"success": False, "message": "没有活跃的朝会"}
        
        current_topic = self.get_current_topic()
        if not current_topic:
            return {"success": False, "message": "没有当前议题"}
        
        selected_option = None
        # 查找选中的选项
        for option in current_topic["options"]:
            if option["id"] == option_id:
                selected_option = option
                break
        
        if not selected_option:
            return {"success": False, "message": "无效的决策选项"}
        
        # 记录决策
        decision = {
            "topic_id": current_topic["id"],
            "topic_title": current_topic["title"],
            "option_id": option_id,
            "option_title": selected_option["title"],
            "effects": selected_option["effects"]
        }
        
        # 添加到决策列表
        self.current_meeting["decisions"].append(decision)
        
        # 移动到下一个议题
        total_topics = len(self.current_meeting["topics"])
        current_index = self.current_meeting["current_topic_index"]
        
        if current_index < total_topics - 1:
            # 还有议题未处理，移动到下一个议题
            self.current_meeting["current_topic_index"] += 1
            
            # 为下一个议题生成意见
            next_topic = self.current_meeting["topics"][current_index + 1]
            self.current_meeting["opinions"] = self._generate_opinions(
                next_topic,
                self.current_meeting["participants"]
            )
            
            # 返回继续处理的标志
            return {
                "success": True,
                "decision": decision,
                "has_more_topics": True,
                "current_topic_index": current_index + 1,
                "total_topics": total_topics,
                "message": f"已处理第{current_index + 1}个议题，还有{total_topics - current_index - 1}个议题待处理"
            }
        else:
            # 所有议题都已处理完毕
            self.current_meeting["completed"] = True
            self.meeting_active = False
            
            # 完成朝会
            meeting_result = self.current_meeting.copy()
            resource_changes = self._calculate_total_effects()
            meeting_result["resource_changes"] = resource_changes
            
            # 发出朝会完成信号
            self.meeting_completed.emit(meeting_result)
            
            # 重置当前朝会
            self.current_meeting = None
            
            return {
                "success": True,
                "decision": decision,
                "has_more_topics": False,
                "message": "所有议题处理完毕，朝会结束",
                "resource_changes": resource_changes
            }
    
    def _calculate_total_effects(self) -> Dict[str, int]:
        """计算所有决策的总体效果"""
        total_effects = {}
        
        if self.current_meeting and "decisions" in self.current_meeting:
            for decision in self.current_meeting["decisions"]:
                effects = decision.get("effects", {})
                for key, value in effects.items():
                    if key in total_effects:
                        total_effects[key] += value
                    else:
                        total_effects[key] = value
        
        return total_effects
    
    def make_emergency_decision(self, option_id: str) -> Dict[str, Any]:
        """做出紧急朝会决策"""
        return self.make_decision(option_id)
    
    def _create_monthly_meeting(self):
        """创建月度朝会"""
        # 获取游戏时间信息
        game_info = self.game_model.get_game_info()
        year = game_info.get("year", 190)
        season = game_info.get("season", 1)
        
        # 选择多个议题
        topics = self._select_multiple_monthly_topics()
        
        # 创建月度朝会数据
        self.current_meeting = {
            "id": f"monthly_{year}_{season}",
            "type": "monthly",
            "year": year,
            "season": season,
            "topics": topics,  # 多个议题
            "current_topic_index": 0,  # 当前处理的议题索引
            "decisions": [],  # 存储所有决策
            "participants": [],
            "opinions": [],
            "completed": False
        }
        
        # 获取参与者
        self.current_meeting["participants"] = self._get_participants()
        
        # 为第一个议题生成意见
        if topics:
            self.current_meeting["opinions"] = self._generate_opinions(
                topics[0], 
                self.current_meeting["participants"]
            )
        
        # 标记朝会为活跃状态
        self.meeting_active = True
        
        # 发出朝会开始信号
        self.meeting_started.emit(self.current_meeting)
    
    def _select_multiple_monthly_topics(self):
        """选择多个月度朝会议题"""
        # 从议题模板中随机选择3-5个议题
        num_topics = random.randint(3, 5)
        selected_topics = random.sample(self.topic_templates, min(num_topics, len(self.topic_templates)))
        return selected_topics
    
    def _create_emergency_meeting(self):
        """创建紧急朝会"""
        # 获取游戏时间信息
        game_info = self.game_model.get_game_info()
        year = game_info.get("year", 190)
        season = game_info.get("season", 1)
        
        # 创建紧急朝会数据
        self.current_meeting = {
            "id": f"emergency_{year}_{season}_{random.randint(1000, 9999)}",
            "type": "emergency",
            "year": year,
            "season": season,
            "topic": self._select_emergency_topic(),
            "participants": [],
            "opinions": [],
            "completed": False
        }
        
        # 获取参与者和意见
        self.current_meeting["participants"] = self._get_participants()
        self.current_meeting["opinions"] = self._generate_opinions(
            self.current_meeting["topic"], 
            self.current_meeting["participants"]
        )
        
        # 标记朝会为活跃状态
        self.meeting_active = True
        
        # 发出朝会开始信号
        self.meeting_started.emit(self.current_meeting)
    
    def _select_monthly_topic(self) -> Dict[str, Any]:
        """选择月度朝会议题"""
        # 月度朝会议题模板
        monthly_topics = [
            {
                "id": "monthly_tax",
                "title": "月度财政报告",
                "description": "本月财政收入与支出情况如何？是否需要调整财政政策？",
                "background": "每月初，需要审查上月财政情况，决定本月财政政策。",
                "has_location": False,
                "options": [
                    {
                        "id": "increase_tax",
                        "title": "增加税收",
                        "description": "提高税率，增加国库收入，但可能影响民心。",
                        "effects": {"economy": 5, "people": -3}
                    },
                    {
                        "id": "maintain_tax",
                        "title": "维持现状",
                        "description": "保持当前税率，维持稳定。",
                        "effects": {"economy": 0, "people": 0}
                    },
                    {
                        "id": "reduce_tax",
                        "title": "减税惠民",
                        "description": "降低税率，减轻民众负担，提升民心。",
                        "effects": {"economy": -3, "people": 5}
                    }
                ]
            },
            {
                "id": "monthly_military",
                "title": "月度军事报告",
                "description": "本月军事训练与防务情况如何？是否需要加强军事力量？",
                "background": "每月初，需要审查军事状况，决定本月军事政策。",
                "related_city": "luoyang",
                "has_location": True,
                "options": [
                    {
                        "id": "increase_military",
                        "title": "加强军备",
                        "description": "增加军事投入，提升军队战斗力。",
                        "effects": {"military": 5, "economy": -3}
                    },
                    {
                        "id": "maintain_military",
                        "title": "维持现状",
                        "description": "保持当前军事投入水平。",
                        "effects": {"military": 0, "economy": 0}
                    },
                    {
                        "id": "reduce_military",
                        "title": "裁减军备",
                        "description": "减少军事投入，节省开支。",
                        "effects": {"military": -3, "economy": 3}
                    }
                ]
            }
        ]
        
        # 随机选择一个议题
        return random.choice(monthly_topics)
    
    def _select_emergency_topic(self) -> Dict[str, Any]:
        """选择紧急朝会议题"""
        # 紧急朝会议题模板
        emergency_topics = [
            {
                "id": "emergency_disaster",
                "title": "自然灾害",
                "description": "境内发生自然灾害，需要紧急应对！",
                "background": "突如其来的自然灾害威胁着民众的生命财产安全，需要立即采取行动。",
                "related_position": [20, 12],
                "has_location": True,
                "options": [
                    {
                        "id": "emergency_relief",
                        "title": "紧急赈灾",
                        "description": "立即调拨物资赈灾，稳定民心。",
                        "effects": {"people": 5, "economy": -5}
                    },
                    {
                        "id": "organized_relief",
                        "title": "有序赈灾",
                        "description": "组织有序的赈灾工作，平衡各方利益。",
                        "effects": {"people": 2, "economy": -2}
                    },
                    {
                        "id": "minimal_relief",
                        "title": "最低限度赈灾",
                        "description": "只提供最基本的赈灾，节省资源。",
                        "effects": {"people": -2, "economy": 2}
                    }
                ]
            },
            {
                "id": "emergency_border",
                "title": "边境警报",
                "description": "边境发现敌军活动，需要紧急应对！",
                "background": "边境哨所传来紧急军情，发现敌军大规模调动，可能威胁边境安全。",
                "related_city": "luoyang",
                "has_location": True,
                "options": [
                    {
                        "id": "immediate_defense",
                        "title": "立即防御",
                        "description": "立即调集军队加强边境防御。",
                        "effects": {"military": 3, "economy": -3}
                    },
                    {
                        "id": "diplomatic_response",
                        "title": "外交回应",
                        "description": "通过外交途径解决边境紧张局势。",
                        "effects": {"diplomacy": 3, "military": -1}
                    },
                    {
                        "id": "monitor_situation",
                        "title": "监视局势",
                        "description": "密切监视敌军动向，暂不采取行动。",
                        "effects": {"military": -2, "diplomacy": 1}
                    }
                ]
            }
        ]
        
        # 随机选择一个议题
        return random.choice(emergency_topics)
    

    
    def get_emergency_meeting_data(self) -> Optional[Dict[str, Any]]:
        """获取紧急朝会数据"""
        # 如果没有活跃的朝会，创建一个新的紧急朝会
        if not self.meeting_active:
            self._create_emergency_meeting()
        
        return self.current_meeting
    

    
    def make_emergency_decision(self, option_id: str) -> Dict[str, Any]:
        """做出紧急朝会决策"""
        return self.make_decision(option_id)
    

    
    def _create_emergency_meeting(self):
        """创建紧急朝会"""
        # 获取游戏时间信息
        game_info = self.game_model.get_game_info()
        year = game_info.get("year", 190)
        season = game_info.get("season", 1)
        
        # 创建紧急朝会数据
        self.current_meeting = {
            "id": f"emergency_{year}_{season}_{random.randint(1000, 9999)}",
            "type": "emergency",
            "year": year,
            "season": season,
            "topic": self._select_emergency_topic(),
            "participants": [],
            "opinions": [],
            "completed": False
        }
        
        # 获取参与者和意见
        self.current_meeting["participants"] = self._get_participants()
        self.current_meeting["opinions"] = self._generate_opinions(
            self.current_meeting["topic"], 
            self.current_meeting["participants"]
        )
        
        # 标记朝会为活跃状态
        self.meeting_active = True
        
        # 发出朝会开始信号
        self.meeting_started.emit(self.current_meeting)
    
    def _select_monthly_topic(self) -> Dict[str, Any]:
        """选择月度朝会议题"""
        # 月度朝会议题模板
        monthly_topics = [
            {
                "id": "monthly_tax",
                "title": "月度财政报告",
                "description": "本月财政收入与支出情况如何？是否需要调整财政政策？",
                "background": "每月初，需要审查上月财政情况，决定本月财政政策。",
                "options": [
                    {
                        "id": "increase_tax",
                        "title": "增加税收",
                        "description": "提高税率，增加国库收入，但可能影响民心。",
                        "effects": {"economy": 5, "people": -3}
                    },
                    {
                        "id": "maintain_tax",
                        "title": "维持现状",
                        "description": "保持当前税率，维持稳定。",
                        "effects": {"economy": 0, "people": 0}
                    },
                    {
                        "id": "reduce_tax",
                        "title": "减税惠民",
                        "description": "降低税率，减轻民众负担，提升民心。",
                        "effects": {"economy": -3, "people": 5}
                    }
                ]
            },
            {
                "id": "monthly_military",
                "title": "月度军事报告",
                "description": "本月军事训练与防务情况如何？是否需要加强军事力量？",
                "background": "每月初，需要审查军事状况，决定本月军事政策。",
                "options": [
                    {
                        "id": "increase_military",
                        "title": "加强军备",
                        "description": "增加军事投入，提升军队战斗力。",
                        "effects": {"military": 5, "economy": -3}
                    },
                    {
                        "id": "maintain_military",
                        "title": "维持现状",
                        "description": "保持当前军事投入水平。",
                        "effects": {"military": 0, "economy": 0}
                    },
                    {
                        "id": "reduce_military",
                        "title": "裁减军备",
                        "description": "减少军事投入，节省开支。",
                        "effects": {"military": -3, "economy": 3}
                    }
                ]
            }
        ]
        
        # 随机选择一个议题
        return random.choice(monthly_topics)
    
    def _select_emergency_topic(self) -> Dict[str, Any]:
        """选择紧急朝会议题"""
        # 紧急朝会议题模板
        emergency_topics = [
            {
                "id": "emergency_disaster",
                "title": "自然灾害",
                "description": "境内发生自然灾害，需要紧急应对！",
                "background": "突如其来的自然灾害威胁着民众的生命财产安全，需要立即采取行动。",
                "options": [
                    {
                        "id": "emergency_relief",
                        "title": "紧急赈灾",
                        "description": "立即调拨物资赈灾，稳定民心。",
                        "effects": {"people": 5, "economy": -5}
                    },
                    {
                        "id": "organized_relief",
                        "title": "有序赈灾",
                        "description": "组织有序的赈灾工作，平衡各方利益。",
                        "effects": {"people": 2, "economy": -2}
                    },
                    {
                        "id": "minimal_relief",
                        "title": "最低限度赈灾",
                        "description": "只提供最基本的赈灾，节省资源。",
                        "effects": {"people": -2, "economy": 2}
                    }
                ]
            },
            {
                "id": "emergency_border",
                "title": "边境警报",
                "description": "边境发现敌军活动，需要紧急应对！",
                "background": "边境哨所传来紧急军情，发现敌军大规模调动，可能威胁边境安全。",
                "options": [
                    {
                        "id": "immediate_defense",
                        "title": "立即防御",
                        "description": "立即调集军队加强边境防御。",
                        "effects": {"military": 3, "economy": -3}
                    },
                    {
                        "id": "diplomatic_response",
                        "title": "外交回应",
                        "description": "通过外交途径解决边境紧张局势。",
                        "effects": {"diplomacy": 3, "military": -1}
                    },
                    {
                        "id": "monitor_situation",
                        "title": "监视局势",
                        "description": "密切监视敌军动向，暂不采取行动。",
                        "effects": {"military": -2, "diplomacy": 1}
                    }
                ]
            }
        ]
        
        # 随机选择一个议题
        return random.choice(emergency_topics)
    
    def make_decision(self, option_id: str) -> Dict[str, Any]:
        """做出朝会决策"""
        if not self.meeting_active or not self.current_meeting:
            return {"success": False, "message": "没有活跃的朝会"}
        
        # 检查是否是传统格式（单个议题）还是新格式（多个议题）
        if "topics" in self.current_meeting:
            # 这是多议题格式，使用当前议题
            current_topic = self.get_current_topic()
            if not current_topic:
                return {"success": False, "message": "没有当前议题"}
            topic = current_topic
        else:
            # 这是传统格式（单个议题）
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
        elif topic["id"] == "agricultural_development":
            # 农业发展相关决策
            preferred_option_index = random.randint(0, 2)
        elif topic["id"] == "trade_policy":
            # 贸易政策相关决策
            preferred_option_index = random.randint(0, 2)
        elif topic["id"] == "education_reform":
            # 教育改革相关决策
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
            "support_level": random.randint(60, 100),  # 支持度
            "personality": self._get_personality_description(participant),
            "expertise": self._get_expertise_description(topic)
        }
    
    def _get_personality_description(self, participant):
        """获取官员性格描述"""
        personalities = [
            "忠诚可靠",
            "足智多谋",
            "刚直不阿",
            "善于理财",
            "精通军事",
            "博学多才",
            "善于外交",
            "勤政爱民",
            "经验丰富",
            "年轻有为"
        ]
        return random.choice(personalities)
    
    def _get_expertise_description(self, topic):
        """获取官员专业领域描述"""
        expertise_map = {
            "tax_increase": ["财政", "经济", "税收"],
            "military_expansion": ["军事", "国防", "战略"],
            "infrastructure": ["工程", "建设", "规划"],
            "agricultural_development": ["农业", "民生", "土地"],
            "trade_policy": ["外交", "商业", "贸易"],
            "education_reform": ["文教", "人才", "学术"]
        }
        
        topic_key = topic["id"]
        if topic_key in expertise_map:
            return random.choice(expertise_map[topic_key])
        else:
            return "综合"
    
    def get_participant_info(self, participant_id):
        """获取参与官员的详细信息"""
        generals = self.game_model.get_generals()
        if participant_id in generals:
            general = generals[participant_id]
            return {
                "id": general["id"],
                "name": general["name"],
                "title": general.get("title", "官员"),
                "intelligence": general.get("intelligence", 50),
                "politics": general.get("politics", 50),
                "loyalty": general.get("loyalty", 80),
                "military": general.get("military", 50),
                "description": general.get("description", "一位忠诚的朝廷官员"),
                "personality": self._get_personality_description(general)
            }
        return None
    
    def get_participants_for_meeting(self):
        """获取当前朝会的参与者列表"""
        if self.current_meeting and "participants" in self.current_meeting:
            return self.current_meeting["participants"]
        return []