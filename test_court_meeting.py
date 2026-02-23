#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for court meeting functionality
"""

import sys
from PyQt5.QtWidgets import QApplication
from src.ui.ui_base_frame import UIBaseFrame

def test_court_meeting():
    """测试朝会功能"""
    app = QApplication(sys.argv)
    
    # 创建UI基础框架
    frame = UIBaseFrame()
    
    # 模拟朝会数据
    meeting_data = {
        "type": "monthly",
        "year": 190,
        "season": 1,
        "topic": {
            "title": "国库空虚",
            "description": "国库空虚，需要采取措施增加收入",
            "background": "连年征战导致国库空虚",
            "options": [
                {"id": "option_1", "text": "增加税收"},
                {"id": "option_2", "text": "削减开支"},
                {"id": "option_3", "text": "发行货币"}
            ]
        }
    }
    
    # 显示朝会
    frame.show_court_meeting(meeting_data)
    
    # 显示窗口
    frame.show()
    
    # 运行应用
    sys.exit(app.exec_())

if __name__ == "__main__":
    test_court_meeting()