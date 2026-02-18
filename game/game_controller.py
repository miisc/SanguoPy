#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
游戏控制器
协调游戏模型和视图的交互
"""

from PyQt5.QtCore import QObject, pyqtSignal
from game.game_model import GameModel
from game.court_meeting import CourtMeetingSystem


class GameController(QObject):
    """游戏控制器类"""
    
    # 信号定义
    game_updated = pyqtSignal()  # 游戏状态更新信号
    resources_updated = pyqtSignal(dict)  # 资源更新信号
    time_advanced = pyqtSignal(dict)  # 时间推进信号
    court_meeting_requested = pyqtSignal()  # 朝会请求信号
    
    def __init__(self):
        """初始化游戏控制器"""
        super().__init__()
        self.game_model = GameModel()
        self.court_meeting_system = CourtMeetingSystem(self.game_model)
        
        # 连接朝会系统信号
        self.court_meeting_system.meeting_completed.connect(self._on_court_meeting_completed)
    
    def start_new_game(self):
        """开始新游戏"""
        # 初始化游戏数据
        self.game_model = GameModel()
        self.court_meeting_system = CourtMeetingSystem(self.game_model)
        self.court_meeting_system.meeting_completed.connect(self._on_court_meeting_completed)
        
        # 发出游戏更新信号
        self.game_updated.emit()
        self.resources_updated.emit(self.game_model.get_resources())
    
    def advance_time(self):
        """推进游戏时间"""
        self.game_model.advance_time()
        
        # 发出时间推进信号
        self.time_advanced.emit(self.game_model.get_game_info())
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
    
    def make_court_decision(self, decision_id):
        """做出朝会决策"""
        result = self.court_meeting_system.make_decision(decision_id)
        
        # 更新游戏资源
        if result and "resource_changes" in result:
            self.game_model.update_resources(result["resource_changes"])
            self.resources_updated.emit(self.game_model.get_resources())
        
        return result
    
    def _on_court_meeting_completed(self, meeting_result):
        """朝会完成处理"""
        # 将朝会结果添加到游戏记录
        self.game_model.add_court_meeting(meeting_result)
        
        # 发出游戏更新信号
        self.game_updated.emit()
    
    def save_game(self, filename):
        """保存游戏"""
        self.game_model.save_game(filename)
    
    def load_game(self, filename):
        """加载游戏"""
        self.game_model.load_game(filename)
        
        # 重新初始化朝会系统
        self.court_meeting_system = CourtMeetingSystem(self.game_model)
        self.court_meeting_system.meeting_completed.connect(self._on_court_meeting_completed)
        
        # 发出游戏更新信号
        self.game_updated.emit()
        self.resources_updated.emit(self.game_model.get_resources())