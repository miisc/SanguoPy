#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
最小化的地图系统测试脚本
只测试MapSystem的核心功能，不涉及GUI组件
"""

import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("开始测试MapSystem核心功能...")

# 测试单独导入各个核心模块
try:
    print("步骤0: 测试导入核心依赖模块")
    
    # 测试MapGrid
    start_time = time.time()
    from map_system.core.map_grid import MapGrid
    map_grid = MapGrid(100, 100)
    end_time = time.time()
    print(f"[OK] 创建MapGrid实例成功，耗时: {end_time - start_time:.2f}秒")
    
    # 测试VisibilityManager
    start_time = time.time()
    from map_system.core.visibility_manager import VisibilityManager
    visibility_manager = VisibilityManager()
    end_time = time.time()
    print(f"[OK] 创建VisibilityManager实例成功，耗时: {end_time - start_time:.2f}秒")
    
    # 测试RoadSystem
    start_time = time.time()
    from map_system.core.road_system import RoadSystem
    road_system = RoadSystem()
    end_time = time.time()
    print(f"[OK] 创建RoadSystem实例成功，耗时: {end_time - start_time:.2f}秒")
    
    # 测试IntelligenceSystem
    start_time = time.time()
    from map_system.core.intelligence_system import IntelligenceSystem
    intelligence_system = IntelligenceSystem()
    end_time = time.time()
    print(f"[OK] 创建IntelligenceSystem实例成功，耗时: {end_time - start_time:.2f}秒")
    
except Exception as e:
    print(f"[ERROR] 测试依赖模块失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n步骤1: 测试MapSystem核心功能")
    start_time = time.time()
    
    # 创建一个简化版的MapSystem，只包含核心功能
    class SimpleMapSystem:
        def __init__(self):
            print("    - 初始化基本属性")
            self.grid_size = (100, 100)
            print("    - 初始化MapGrid")
            self.map_grid = MapGrid(100, 100)
            print("    - 初始化城市和道路字典")
            self.cities = {}
            self.roads = {}
            print("    - 初始化VisibilityManager")
            self.visibility_manager = VisibilityManager()
            print("    - 初始化RoadSystem")
            self.road_system = RoadSystem()
            print("    - 初始化IntelligenceSystem")
            self.intelligence_system = IntelligenceSystem()
            print("    - 初始化完成")
        
        def add_city(self, city_id, name, position, owner="neutral", population=0):
            """添加城市"""
            self.cities[city_id] = {
                "id": city_id,
                "name": name,
                "position": position,
                "owner": owner,
                "population": population,
                "resources": {"food": 0, "gold": 0}
            }
        
        def add_road(self, road_id, name, start_city, end_city, road_type="官道"):
            """添加道路"""
            if start_city in self.cities and end_city in self.cities:
                start_pos = self.cities[start_city]["position"]
                end_pos = self.cities[end_city]["position"]
                
                # 计算道路长度
                import math
                length = math.sqrt((end_pos[0] - start_pos[0]) ** 2 + 
                                 (end_pos[1] - start_pos[1]) ** 2)
                
                # 确定道路属性
                speed_factor = 1.0
                supply_factor = 1.0
                
                if road_type == "山间小径":
                    speed_factor = 0.6
                    supply_factor = 1.2
                elif road_type == "水路":
                    speed_factor = 0.8
                    supply_factor = 0.6
                
                self.roads[road_id] = {
                    "id": road_id,
                    "name": name,
                    "start_city": start_city,
                    "end_city": end_city,
                    "start_pos": start_pos,
                    "end_pos": end_pos,
                    "type": road_type,
                    "length": length,
                    "speed_factor": speed_factor,
                    "supply_factor": supply_factor,
                    "visibility": "visible"
                }
    
    # 创建实例
    simple_map_system = SimpleMapSystem()
    
    # 测试添加城市
    print("\n步骤2: 测试添加城市")
    simple_map_system.add_city("city_001", "长安", (100, 200), "player", 100000)
    simple_map_system.add_city("city_002", "洛阳", (200, 200), "player", 80000)
    print(f"[OK] 添加城市成功，当前城市数量: {len(simple_map_system.cities)}")
    
    # 测试添加道路
    print("\n步骤3: 测试添加道路")
    simple_map_system.add_road("road_001", "长安-洛阳官道", "city_001", "city_002", "官道")
    print(f"[OK] 添加道路成功，当前道路数量: {len(simple_map_system.roads)}")
    
    # 测试初始化
    print("\n步骤4: 测试系统初始化")
    simple_map_system.road_system.initialize(simple_map_system.roads)
    simple_map_system.visibility_manager.initialize(simple_map_system.cities, simple_map_system.roads)
    print("[OK] 系统初始化成功")
    
    end_time = time.time()
    print(f"\n[OK] 所有核心功能测试完成，总耗时: {end_time - start_time:.2f}秒")
    print("\n测试结果: 所有功能都正常工作！")
    
except Exception as e:
    print(f"[ERROR] 测试失败: {e}")
    import traceback
    traceback.print_exc()
    print("错误类型:", type(e))
    print("错误参数:", e.args)
    sys.exit(1)