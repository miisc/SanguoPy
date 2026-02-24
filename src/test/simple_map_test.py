#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单的地图系统测试脚本
直接测试MapSystem的初始化和基本功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from map_system.core.map_system import MapSystem

print("开始测试MapSystem...")

try:
    # 创建MapSystem实例
    map_system = MapSystem()
    print("✓ MapSystem初始化成功")
    
    # 添加城市
    map_system.add_city(
        "city_001", "长安", (100, 200), "player", 100000
    )
    print("✓ 添加城市成功")
    
    # 添加道路
    map_system.add_road(
        "road_001", "长安-洛阳官道", "city_001", "city_001", "官道"
    )
    print("✓ 添加道路成功")
    
    # 初始化地图系统
    map_system.initialize()
    print("✓ 初始化地图系统成功")
    
    print("所有测试都通过了！")
except Exception as e:
    print(f"✗ 测试失败: {e}")
    import traceback
    traceback.print_exc()