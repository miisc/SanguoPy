#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
游戏控制器
协调游戏模型和视图的交互
"""

from PyQt5.QtCore import QObject, pyqtSignal
from game.game_model import GameModel
from game.court_meeting import CourtMeetingSystem
from game.temp_command_policy import TempCommandPolicy


class GameController(QObject):
    """游戏控制器类"""
    
    # 信号定义
    game_updated = pyqtSignal()  # 游戏状态更新信号
    resources_updated = pyqtSignal(dict)  # 资源更新信号
    time_advanced = pyqtSignal(dict)  # 时间推进信号
    monthly_court_due = pyqtSignal(dict)  # 月度朝会到期信号
    court_meeting_requested = pyqtSignal()  # 朝会请求信号
    
    def __init__(self):
        """初始化游戏控制器"""
        super().__init__()
        self.game_model = GameModel()
        self.court_meeting_system = CourtMeetingSystem(self.game_model)
        self._event_type_last_trigger_xun = {}
        self._temp_command_last_used_xun = {}
        self._temp_command_used_count_by_xun = {}
        self._temp_command_quota_by_xun = {}
        self._event_queue = []
        self.temp_command_policy = TempCommandPolicy()
        
        # 连接朝会系统信号
        self.court_meeting_system.meeting_completed.connect(self._on_court_meeting_completed)
    
    def start_new_game(self):
        """开始新游戏"""
        # 初始化游戏数据
        self.game_model = GameModel()
        self.court_meeting_system = CourtMeetingSystem(self.game_model)
        self._event_type_last_trigger_xun = {}
        self._temp_command_last_used_xun = {}
        self._temp_command_used_count_by_xun = {}
        self._temp_command_quota_by_xun = {}
        
        # 连接朝会系统信号
        self.court_meeting_system.meeting_completed.connect(self._on_court_meeting_completed)
        
        # 发出游戏更新信号
        self.game_updated.emit()
        self.resources_updated.emit(self.game_model.get_resources())
    
    def advance_time(self):
        """推进游戏时间"""
        # 获取当前游戏信息
        current_info = self.game_model.get_game_info()
        current_day = current_info["day"]
        
        self.game_model.advance_time()
        
        # 获取更新后的游戏信息
        new_info = self.game_model.get_game_info()
        new_day = new_info["day"]
        
        # 检查是否是月初一，触发月度朝会信号
        if new_day == 1 and current_day != 1:  # 从非月初变为月初，表示跨月
            self.monthly_court_due.emit(new_info)
        
        # 发出时间推进信号
        self.time_advanced.emit(new_info)
        self.game_updated.emit()
    
    def get_game_info(self):
        """获取游戏信息"""
        return self.game_model.get_game_info()
    
    def get_resources(self):
        """获取资源信息"""
        return self.game_model.get_resources()
    
    def get_factions(self):
        """获取势力信息"""
        return self.game_model.get_factions()
    
    def get_cities(self):
        """获取城池信息"""
        return self.game_model.get_cities()
    
    def get_generals(self):
        """获取武将信息"""
        return self.game_model.get_generals()
    
    def request_court_meeting(self):
        """请求召开朝会"""
        # 检查是否可以召开朝会
        if self.court_meeting_system.can_hold_meeting():
            self.court_meeting_requested.emit()
            return True
        return False
    
    def start_court_meeting(self):
        """开始朝会"""
        return self.court_meeting_system.start_meeting()
    
    def get_court_meeting_data(self):
        """获取朝会数据"""
        return self.court_meeting_system.get_meeting_data()
    
    def get_monthly_court_data(self):
        """获取月度朝会数据"""
        return self.court_meeting_system.get_monthly_meeting_data()
    
    def get_emergency_court_data(self):
        """获取紧急朝会数据"""
        return self.court_meeting_system.get_emergency_meeting_data()
    
    def get_participant_info(self, participant_id):
        """获取参与官员的详细信息"""
        return self.court_meeting_system.get_participant_info(participant_id)
    
    def get_participants_for_meeting(self):
        """获取当前朝会的参与者列表"""
        return self.court_meeting_system.get_participants_for_meeting()
    
    def make_monthly_decision(self, decision_id):
        """做出月度朝会决策"""
        result = self.court_meeting_system.make_monthly_decision(decision_id)
        
        # 更新游戏资源
        if result and "resource_changes" in result:
            self.game_model.update_resources(result["resource_changes"])
            self.resources_updated.emit(self.game_model.get_resources())
        
        return result
    
    def make_emergency_decision(self, decision_id):
        """做出紧急朝会决策"""
        result = self.court_meeting_system.make_emergency_decision(decision_id)
        
        # 更新游戏资源
        if result and "resource_changes" in result:
            self.game_model.update_resources(result["resource_changes"])
            self.resources_updated.emit(self.game_model.get_resources())
        
        return result
    
    def make_court_decision(self, decision_id):
        """做出朝会决策"""
        result = self.court_meeting_system.make_decision(decision_id)
        
        # 更新游戏资源
        if result and "resource_changes" in result:
            self.game_model.update_resources(result["resource_changes"])
            self.resources_updated.emit(self.game_model.get_resources())
        
        return result

    def get_temp_command_quota(self, current_authority: int, cost_per_command: int = 10) -> int:
        """按当前诏令权威动态计算每旬可用临时指令次数。"""
        if cost_per_command <= 0:
            raise ValueError("cost_per_command must be positive")
        if current_authority <= 0:
            return 0
        return current_authority // cost_per_command

    def trigger_emergency_meeting(self, event: dict) -> dict:
        """触发紧急朝会：立即中断当前执行阶段并进入紧急朝会。"""
        if not self.is_major_emergency_event(event):
            return {"interrupted": False, "entered_emergency_meeting": False}

        self.game_model.game_data["game_info"]["paused"] = True

        event_template = None
        event_id = event.get("event_id")
        if event_id:
            from game.event_template_loader import EventTemplateLoader
            raw = EventTemplateLoader.get_template(event_id)
            if raw:
                event_template = EventTemplateLoader.to_court_topic(raw)

        self.court_meeting_system.get_emergency_meeting_data(event_template=event_template)
        return {"interrupted": True, "entered_emergency_meeting": True}

    def is_major_emergency_event(self, event: dict) -> bool:
        """按量化规则判断是否属于可触发紧急朝会的重大事件。"""
        if not isinstance(event, dict):
            return False

        event_type = event.get("type")
        if event_type not in {"military", "disaster"}:
            return False

        major_military_codes = {
            "border_city_under_siege",
            "enemy_force_near_border",
            "main_supply_route_blocked",
            "army_supply_less_than_1_xun",
            "chokepoint_status_changed",
        }
        major_disaster_codes = {
            "drought_index_high",
            "flood_level_major",
            "epidemic_outbreak",
            "capital_order_or_supply_critical",
        }

        severity = event.get("severity")
        code = event.get("code")

        if severity == "major":
            return True
        if event_type == "military":
            return code in major_military_codes
        return code in major_disaster_codes

    def execute_temp_command(
        self,
        authority: int,
        command_type: str,
        current_xun: int,
        is_whitelisted: bool,
        trigger_met: bool,
        cost: int = 10,
        cooldown_xun: int = 1,
    ) -> dict:
        """按既定顺序校验并执行朝会外临时指令。"""
        if not is_whitelisted:
            return {"success": False, "reason": "not_whitelisted", "new_authority": authority}

        if not trigger_met:
            return {"success": False, "reason": "trigger_not_met", "new_authority": authority}

        if authority < cost:
            return {"success": False, "reason": "insufficient_authority", "new_authority": authority}

        quota = self._temp_command_quota_by_xun.get(current_xun)
        if quota is None:
            quota = self.get_temp_command_quota(authority, cost)
            self._temp_command_quota_by_xun[current_xun] = quota
        used = self._temp_command_used_count_by_xun.get(current_xun, 0)
        if used >= quota:
            return {"success": False, "reason": "over_quota", "new_authority": authority}

        last_xun = self._temp_command_last_used_xun.get(command_type)
        if last_xun is not None and (current_xun - last_xun) < cooldown_xun:
            return {"success": False, "reason": "in_cooldown", "new_authority": authority}

        new_authority = authority - cost
        if new_authority < 0:
            return {"success": False, "reason": "insufficient_authority", "new_authority": authority}

        self._temp_command_last_used_xun[command_type] = current_xun
        self._temp_command_used_count_by_xun[current_xun] = used + 1
        return {"success": True, "reason": "ok", "new_authority": new_authority}

    def issue_temp_command(
        self,
        command_type: str,
        current_xun: int,
        is_whitelisted: bool,
        trigger_met: bool,
        cost: int = 10,
        cooldown_xun: int = 1,
    ) -> dict:
        """从模型读取并写回诏令权威，执行朝会外临时指令。"""
        court_resources = self.game_model.game_data.setdefault(
            "court_resources", {"zhaoling_authority": 50}
        )
        authority = court_resources.get("zhaoling_authority", 50)
        result = self.execute_temp_command(
            authority=authority,
            command_type=command_type,
            current_xun=current_xun,
            is_whitelisted=is_whitelisted,
            trigger_met=trigger_met,
            cost=cost,
            cooldown_xun=cooldown_xun,
        )
        court_resources["zhaoling_authority"] = result["new_authority"]
        return result

    def issue_command_from_policy(
        self,
        command_id: str,
        current_xun: int,
        active_event_codes: set = None,
    ) -> dict:
        """从策略 JSON 自动推导白名单/触发/费用/冷却，执行朝会外临时指令。"""
        if active_event_codes is None:
            active_event_codes = set()

        is_whitelisted = self.temp_command_policy.is_whitelisted(command_id)
        trigger_met = self.temp_command_policy.is_trigger_met(command_id, active_event_codes)
        cost = self.temp_command_policy.get_command_cost(command_id)
        cooldown = self.temp_command_policy.get_command_cooldown(command_id)

        court_resources = self.game_model.game_data.setdefault(
            "court_resources", {"zhaoling_authority": 50}
        )
        authority = court_resources.get("zhaoling_authority", 50)
        result = self.execute_temp_command(
            authority=authority,
            command_type=command_id,
            current_xun=current_xun,
            is_whitelisted=is_whitelisted,
            trigger_met=trigger_met,
            cost=cost,
            cooldown_xun=cooldown,
        )
        court_resources["zhaoling_authority"] = result["new_authority"]
        return result

    def push_event(self, event: dict) -> None:
        """向事件队列推入事件；若为重大事件，立即触发紧急朝会。"""
        self._event_queue.append(event)
        if self.is_major_emergency_event(event):
            self.trigger_emergency_meeting(event)

    def can_trigger_event(self, event_type: str, event_id: str, current_xun: int, cooldown_xun: int = 1) -> bool:
        """按事件类型判断冷却可触发性。"""
        _ = event_id  # 事件冷却按类型，不按ID。
        last = self._event_type_last_trigger_xun.get(event_type)
        if last is None:
            return True
        return (current_xun - last) >= cooldown_xun

    def register_event_trigger(self, event_type: str, event_id: str, current_xun: int) -> None:
        """登记事件触发时间（按事件类型）。"""
        _ = event_id  # 事件冷却按类型，不按ID。
        self._event_type_last_trigger_xun[event_type] = current_xun
    
    def _on_court_meeting_completed(self, meeting_result):
        """朝会完成处理"""
        # 将朝会结果添加到游戏记录
        self.game_model.add_court_meeting(meeting_result)
        
        # 发出游戏更新信号
        self.game_updated.emit()
    
    def save_game(self, filename):
        """保存游戏"""
        self.game_model.save_game(filename)
    
    def reset_game(self):
        """重置游戏"""
        # 重新初始化游戏模型和朝会系统
        self.game_model = GameModel()
        self.court_meeting_system = CourtMeetingSystem(self.game_model)
        self._event_type_last_trigger_xun = {}
        self._temp_command_last_used_xun = {}
        self._temp_command_used_count_by_xun = {}
        self._temp_command_quota_by_xun = {}
        self.court_meeting_system.meeting_completed.connect(self._on_court_meeting_completed)
        
        # 发出游戏更新信号
        self.game_updated.emit()
        self.resources_updated.emit(self.game_model.get_resources())
      
    def load_game(self, filename):
        """加载游戏"""
        self.game_model.load_game(filename)
        
        # 重新初始化朝会系统并连接信号
        self.court_meeting_system = CourtMeetingSystem(self.game_model)
        self._event_type_last_trigger_xun = {}
        self._temp_command_last_used_xun = {}
        self._temp_command_used_count_by_xun = {}
        self._temp_command_quota_by_xun = {}
        self.court_meeting_system.meeting_completed.connect(self._on_court_meeting_completed)
        
        # 发出游戏更新信号
        self.game_updated.emit()
        self.resources_updated.emit(self.game_model.get_resources())