#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
深入调试 get_monthly_meeting_data 方法
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from game.game_model import GameModel
from game.court_meeting import CourtMeetingSystem

# 修改CourtMeetingSystem类以添加调试信息
class DebugCourtMeetingSystem(CourtMeetingSystem):
    def get_monthly_meeting_data(self):
        """带调试信息的获取月度朝会数据"""
        print(f"DEBUG: get_monthly_meeting_data called")
        print(f"DEBUG: self.meeting_active = {self.meeting_active}")
        print(f"DEBUG: self.current_meeting = {self.current_meeting is not None}")
        
        # 如果没有活跃的朝会，创建一个新的月度朝会
        if not self.meeting_active:
            print("DEBUG: meeting not active, creating new one")
            self._create_monthly_meeting()

        print(f"DEBUG: After check - self.current_meeting = {self.current_meeting is not None}")
        
        # 确保返回的数据包含当前议题
        if self.current_meeting:
            print("DEBUG: self.current_meeting exists, proceeding")
            meeting_data = self.current_meeting.copy()
            
            # 如果是多议题模式，添加当前议题
            has_topics = "topics" in self.current_meeting
            print(f"DEBUG: has_topics in self.current_meeting = {has_topics}")
            
            if has_topics:
                print("DEBUG: entering topics branch")
                current_topic = self.get_current_topic()
                print(f"DEBUG: get_current_topic() returned: {current_topic}")
                
                if current_topic:
                    print(f"DEBUG: current_topic exists, adding to meeting_data")
                    meeting_data["topic"] = current_topic
                    print(f"DEBUG: meeting_data now has topic key: {'topic' in meeting_data}")
                else:
                    print("DEBUG: current_topic is None")
            
            print(f"DEBUG: returning meeting_data with keys: {list(meeting_data.keys())}")
            return meeting_data
        else:
            print("DEBUG: self.current_meeting is None, returning None")
        
        print("DEBUG: returning self.current_meeting")
        return self.current_meeting

def deep_debug():
    """深入调试"""
    print("=== 深入调试 get_monthly_meeting_data ===")
    
    # 创建游戏模型和调试版朝会系统
    game_model = GameModel()
    court_system = DebugCourtMeetingSystem(game_model)
    
    # 创建月度朝会
    print("\n1. 创建月度朝会...")
    court_system._create_monthly_meeting()
    
    # 检查初始状态
    print("\n2. 获取初始数据...")
    meeting_data = court_system.get_monthly_meeting_data()
    
    # 处理第一个议题
    if meeting_data and "topics" in meeting_data:
        current_topic = court_system.get_current_topic()
        print(f"\n3. 处理议题: {current_topic['title'] if current_topic else 'None'}")
        
        if current_topic:
            option = current_topic["options"][0]
            print(f"   选择选项: {option['title']}")
            
            result = court_system.make_monthly_decision(option["id"])
            print(f"   处理结果: success={result.get('success')}, has_more={result.get('has_more_topics')}")
            
            print(f"\n4. 处理后再获取数据...")
            new_meeting_data = court_system.get_monthly_meeting_data()

if __name__ == "__main__":
    deep_debug()