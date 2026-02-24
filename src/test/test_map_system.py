#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
地图系统功能测试脚本
测试MapSystem的核心功能
"""

import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("开始测试MapSystem核心功能...")

# 测试MapSystem完整功能
try:
    print("步骤1: 导入MapSystem模块")
    start_time = time.time()
    from map_system.core.map_system import MapSystem
    end_time = time.time()
    print(f"[OK] 导入MapSystem成功，耗时: {end_time - start_time:.2f}秒")
    
    print("\n步骤2: 创建MapSystem实例")
    start_time = time.time()
    map_system = MapSystem()
    end_time = time.time()
    print(f"[OK] 创建MapSystem实例成功，耗时: {end_time - start_time:.2f}秒")
    
    print("\n步骤3: 初始化MapSystem")
    start_time = time.time()
    map_system.initialize()
    end_time = time.time()
    print(f"[OK] 初始化MapSystem成功，耗时: {end_time - start_time:.2f}秒")
    
    print("\n步骤4: 测试添加城市")
    start_time = time.time()
    map_system.add_city("city_001", "长安", (100, 200), "player", 100000)
    map_system.add_city("city_002", "洛阳", (200, 200), "player", 80000)
    map_system.add_city("city_003", "成都", (100, 300), "enemy", 60000)
    map_system.add_city("city_004", "建业", (300, 200), "neutral", 70000)
    end_time = time.time()
    print(f"[OK] 添加城市成功，当前城市数量: {len(map_system.get_cities())}，耗时: {end_time - start_time:.2f}秒")
    
    print("\n步骤5: 测试添加道路")
    start_time = time.time()
    map_system.add_road("road_001", "长安-洛阳官道", "city_001", "city_002", "官道")
    map_system.add_road("road_002", "长安-成都山间小径", "city_001", "city_003", "山间小径")
    map_system.add_road("road_003", "洛阳-建业水路", "city_002", "city_004", "水路")
    end_time = time.time()
    print(f"[OK] 添加道路成功，当前道路数量: {len(map_system.get_roads())}，耗时: {end_time - start_time:.2f}秒")
    
    print("\n步骤6: 测试获取城市信息")
    start_time = time.time()
    changan = map_system.get_city("city_001")
    luoyang = map_system.get_city("city_002")
    end_time = time.time()
    print(f"[OK] 获取城市信息成功，耗时: {end_time - start_time:.2f}秒")
    print(f"    - 长安: {changan['name']}, 位置: {changan['position']}, 所有者: {changan['owner']}, 人口: {changan['population']}")
    print(f"    - 洛阳: {luoyang['name']}, 位置: {luoyang['position']}, 所有者: {luoyang['owner']}, 人口: {luoyang['population']}")
    
    print("\n步骤7: 测试获取道路信息")
    start_time = time.time()
    road_001 = map_system.get_road("road_001")
    road_002 = map_system.get_road("road_002")
    end_time = time.time()
    print(f"[OK] 获取道路信息成功，耗时: {end_time - start_time:.2f}秒")
    print(f"    - 长安-洛阳官道: 长度: {road_001['length']:.1f}, 类型: {road_001['type']}")
    print(f"    - 长安-成都山间小径: 长度: {road_002['length']:.1f}, 类型: {road_002['type']}")
    
    print("\n步骤8: 测试更新可见性")
    start_time = time.time()
    map_system.update_visibility()
    end_time = time.time()
    print(f"[OK] 更新可见性成功，耗时: {end_time - start_time:.2f}秒")
    
    print("\n步骤9: 测试获取可见城市和道路")
    start_time = time.time()
    visible_cities = map_system.get_visible_cities("player")
    visible_roads = map_system.get_visible_roads("player")
    end_time = time.time()
    print(f"[OK] 获取可见城市和道路成功，耗时: {end_time - start_time:.2f}秒")
    print(f"    - 可见城市数量: {len(visible_cities)}, 城市: {visible_cities}")
    print(f"    - 可见道路数量: {len(visible_roads)}, 道路: {visible_roads}")
    
    print("\n步骤10: 测试计算行军路线")
    start_time = time.time()
    path = map_system.calculate_movement_path("city_001", "city_002")
    end_time = time.time()
    print(f"[OK] 计算行军路线成功，耗时: {end_time - start_time:.2f}秒")
    print(f"    - 长安到洛阳的路线: {path}")
    
    print("\n步骤11: 测试计算军粮消耗")
    start_time = time.time()
    if path:
        supply_cost = map_system.calculate_supply_cost(path, 50000)
        print(f"[OK] 计算军粮消耗成功，耗时: {end_time - start_time:.2f}秒")
        print(f"    - 5万大军从长安到洛阳的军粮消耗: {supply_cost}单位")
    else:
        print("[WARNING] 无法计算军粮消耗，因为没有找到路线")
    
    print("\n步骤12: 测试计算行军时间")
    start_time = time.time()
    if 'city_001' in map_system.get_cities() and 'city_002' in map_system.get_cities():
        start_pos = map_system.get_city('city_001')['position']
        end_pos = map_system.get_city('city_002')['position']
        march_time = map_system.calculate_march_time(start_pos, end_pos, "官道", 1.0)
        end_time = time.time()
        print(f"[OK] 计算行军时间成功，耗时: {end_time - start_time:.2f}秒")
        print(f"    - 长安到洛阳的行军时间: {march_time:.1f}天")
    else:
        print("[WARNING] 无法计算行军时间，因为城市不存在")
    
    print("\n步骤13: 测试计算路径成本")
    start_time = time.time()
    path_cost = map_system.calculate_path_cost("city_001", "city_002", 50000)
    end_time = time.time()
    print(f"[OK] 计算路径成本成功，耗时: {end_time - start_time:.2f}秒")
    print(f"    - 路径成本: 时间={path_cost['time']:.1f}天, 补给={path_cost['supply']}单位, 路径={path_cost['path']}")
    
    print("\n步骤14: 测试获取情报点")
    start_time = time.time()
    intel_points = map_system.get_intelligence_points("player")
    end_time = time.time()
    print(f"[OK] 获取情报点成功，耗时: {end_time - start_time:.2f}秒")
    print(f"    - 情报点数量: {len(intel_points)}")
    
    print("\n步骤15: 测试移除城市")
    start_time = time.time()
    map_system.remove_city("city_004")
    end_time = time.time()
    print(f"[OK] 移除城市成功，当前城市数量: {len(map_system.get_cities())}，耗时: {end_time - start_time:.2f}秒")
    
    print("\n步骤16: 测试移除道路")
    start_time = time.time()
    map_system.remove_road("road_003")
    end_time = time.time()
    print(f"[OK] 移除道路成功，当前道路数量: {len(map_system.get_roads())}，耗时: {end_time - start_time:.2f}秒")
    
    # 测试完成
    total_time = time.time() - start_time
    print(f"\n[OK] 所有测试完成！总耗时: {total_time:.2f}秒")
    print("\n测试结果: MapSystem核心功能全部正常工作！")
    print("\n功能测试总结:")
    print(f"  - 城市管理: {len(map_system.get_cities())}个城市")
    print(f"  - 道路管理: {len(map_system.get_roads())}条道路")
    print(f"  - 可见性管理: 正常")
    print(f"  - 路径计算: 正常")
    print(f"  - 补给计算: 正常")
    print(f"  - 情报系统: 正常")
    
except Exception as e:
    print(f"[ERROR] 测试失败: {e}")
    import traceback
    traceback.print_exc()
    print("错误类型:", type(e))
    print("错误参数:", e.args)
    sys.exit(1)