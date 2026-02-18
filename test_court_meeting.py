#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
朝会系统测试脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.game_model import GameModel
from game.court_meeting import CourtMeetingSystem

def test_court_meeting():
    """测试朝会系统"""
    print("开始测试朝会系统...")
    
    # 创建游戏模型
    game_model = GameModel()
    
    # 创建朝会系统
    court_system = CourtMeetingSystem(game_model)
    
    # 测试是否可以召开朝会
    can_hold = court_system.can_hold_meeting()
    print(f"是否可以召开朝会: {can_hold}")
    
    if can_hold:
        # 开始朝会
        meeting_result = court_system.start_meeting()
        print(f"朝会开始结果: {meeting_result['success']}")
        
        if meeting_result['success']:
            meeting_data = meeting_result['meeting']
            print(f"朝会ID: {meeting_data['id']}")
            print(f"年份: {meeting_data['year']}")
            print(f"季节: {meeting_data['season']}")
            
            topic = meeting_data['topic']
            print(f"议题标题: {topic['title']}")
            print(f"议题描述: {topic['description']}")
            
            print("\n参与朝臣:")
            for participant in meeting_data['participants']:
                print(f"- {participant['name']} ({participant['title']})")
            
            print("\n朝臣意见:")
            for opinion in meeting_data['opinions']:
                print(f"- {opinion['participant_name']}: {opinion['opinion']}")
                print(f"  支持选项: {opinion['preferred_option']}, 支持度: {opinion['support_level']}%")
            
            print("\n决策选项:")
            for i, option in enumerate(topic['options']):
                print(f"{i+1}. {option['title']}: {option['description']}")
                print(f"   效果: {option['effects']}")
            
            # 选择第一个选项进行测试
            if topic['options']:
                selected_option = topic['options'][0]
                print(f"\n选择选项: {selected_option['title']}")
                
                decision_result = court_system.make_decision(selected_option['id'])
                print(f"决策结果: {decision_result['success']}")
                
                if decision_result['success']:
                    print(f"资源变化: {decision_result['resource_changes']}")
    
    print("\n朝会系统测试完成!")

if __name__ == "__main__":
    test_court_meeting()