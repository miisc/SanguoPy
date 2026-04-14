#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
地图系统核心类
管理地图的渲染、交互和状态
"""

from typing import Dict, List, Optional, Tuple
from .map_grid import MapGrid
from .terrain import TerrainType
from .visibility_manager import VisibilityManager
from .road_system import RoadSystem
from .intelligence_system import IntelligenceSystem


class MapSystem:
    """地图系统核心类"""
    
    def __init__(self, grid_size: Tuple[int, int] = (100, 100)):
        """初始化地图系统
        
        Args:
            grid_size: 地图网格大小 (宽度, 高度)
        """
        print("  - 初始化MapSystem开始")
        self.grid_size = grid_size
        print("  - 初始化MapGrid")
        self.map_grid = MapGrid(grid_size[0], grid_size[1])
        print("  - 初始化城市和道路字典")
        self.cities = {}
        self.roads = {}
        print("  - 初始化VisibilityManager")
        self.visibility_manager = VisibilityManager()
        print("  - 初始化RoadSystem")
        self.road_system = RoadSystem()
        print("  - 初始化IntelligenceSystem")
        self.intelligence_system = IntelligenceSystem()
        print("  - 初始化MapSystem完成")
    
    def initialize(self):
        """初始化地图系统"""
        # 初始化可见性管理器
        self.visibility_manager.initialize(self.cities, self.roads)
        # 初始化道路系统
        self.road_system.initialize(self.roads)
        # 初始化情报系统
        self.intelligence_system.initialize(self.visibility_manager)
    
    def add_city(self, city_id: str, name: str, position: Tuple[int, int], 
                 owner: str = "neutral", population: int = 0):
        """添加城市
        
        Args:
            city_id: 城市ID
            name: 城市名称
            position: 城市位置 (x, y)
            owner: 所有者
            population: 人口
        """
        self.cities[city_id] = {
            "id": city_id,
            "name": name,
            "position": position,
            "owner": owner,
            "population": population,
            "resources": {"food": 0, "gold": 0}
        }
        # 更新可见性
        self.visibility_manager.update_visibility(self.cities, self.roads)
    
    def add_road(self, road_id: str, name: str, start_city: str, 
                 end_city: str, road_type: str = "官道"):
        """添加道路
        
        Args:
            road_id: 道路ID
            name: 道路名称
            start_city: 起点城市ID
            end_city: 终点城市ID
            road_type: 道路类型
        """
        # 获取城市位置
        start_pos = self.cities.get(start_city, {}).get("position")
        end_pos = self.cities.get(end_city, {}).get("position")
        
        if start_pos and end_pos:
            # 计算道路长度
            length = ((end_pos[0] - start_pos[0]) ** 2 + 
                      (end_pos[1] - start_pos[1]) ** 2) ** 0.5
            
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
            # 同步更新道路网络连接关系，确保路径计算可用
            self.road_system.initialize(self.roads)
            # 更新可见性
            self.visibility_manager.update_visibility(self.cities, self.roads)
    
    def get_city(self, city_id: str):
        """获取城市信息
        
        Args:
            city_id: 城市ID
            
        Returns:
            城市信息字典
        """
        return self.cities.get(city_id)
    
    def get_road(self, road_id: str):
        """获取道路信息
        
        Args:
            road_id: 道路ID
            
        Returns:
            道路信息字典
        """
        return self.roads.get(road_id)
    
    def get_cities(self):
        """获取所有城市
        
        Returns:
            城市字典
        """
        return self.cities
    
    def get_roads(self):
        """获取所有道路
        
        Returns:
            道路字典
        """
        return self.roads
    
    def remove_city(self, city_id: str):
        """移除城市
        
        Args:
            city_id: 城市ID
        """
        if city_id in self.cities:
            del self.cities[city_id]
            # 删除与该城市关联的道路，并重建道路连接
            self.roads = {
                rid: road for rid, road in self.roads.items()
                if road.get("start_city") != city_id and road.get("end_city") != city_id
            }
            self.road_system.initialize(self.roads)
            self.visibility_manager.update_visibility(self.cities, self.roads)
    
    def remove_road(self, road_id: str):
        """移除道路
        
        Args:
            road_id: 道路ID
        """
        if road_id in self.roads:
            del self.roads[road_id]
            self.road_system.initialize(self.roads)
            self.visibility_manager.update_visibility(self.cities, self.roads)
    
    def calculate_movement_path(self, start_city: str, end_city: str) -> List[str]:
        """计算行军路线
        
        Args:
            start_city: 起点城市ID
            end_city: 终点城市ID
            
        Returns:
            行军路线（道路ID列表）
        """
        if self.road_system:
            return self.road_system.calculate_path(start_city, end_city)
        return []
    
    def calculate_supply_cost(self, path: List[str], army_size: int) -> int:
        """计算军粮消耗
        
        Args:
            path: 行军路线（道路ID列表）
            army_size: 军队规模
            
        Returns:
            军粮消耗
        """
        if self.road_system:
            return self.road_system.calculate_supply_cost(path, army_size)
        return 0
    
    def update_visibility(self):
        """更新地图可见性"""
        self.visibility_manager.update_visibility(self.cities, self.roads)
    
    def get_visible_cities(self, player_id: str = "player") -> List[str]:
        """获取可见城市
        
        Args:
            player_id: 玩家ID
            
        Returns:
            可见城市ID列表
        """
        return self.visibility_manager.get_visible_cities(player_id)
    
    def get_visible_roads(self, player_id: str = "player") -> List[str]:
        """获取可见道路
        
        Args:
            player_id: 玩家ID
            
        Returns:
            可见道路ID列表
        """
        return self.visibility_manager.get_visible_roads(player_id)
    
    def get_intelligence_points(self, player_id: str = "player") -> List[Dict]:
        """获取情报点
        
        Args:
            player_id: 玩家ID
            
        Returns:
            情报点列表
        """
        return self.intelligence_system.get_intelligence_points(player_id)
    
    def unlock_intelligence(self, intel_id: str, player_id: str = "player") -> bool:
        """解锁情报
        
        Args:
            intel_id: 情报ID
            player_id: 玩家ID
            
        Returns:
            是否解锁成功
        """
        return self.intelligence_system.unlock_intelligence(intel_id, player_id)
    
    def calculate_march_time(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int], 
                             road_type: str = "官道", speed: float = 1.0) -> float:
        """计算行军时间
        
        Args:
            start_pos: 起点位置
            end_pos: 终点位置
            road_type: 道路类型
            speed: 基础速度
            
        Returns:
            行军时间（天）
        """
        return self.road_system.calculate_march_time(start_pos, end_pos, road_type, speed)
    
    def calculate_path_cost(self, start_city: str, end_city: str, 
                           army_size: int) -> Dict:
        """计算路径成本
        
        Args:
            start_city: 起点城市ID
            end_city: 终点城市ID
            army_size: 军队规模
            
        Returns:
            路径成本字典，包含时间、粮食消耗等
        """
        path = self.calculate_movement_path(start_city, end_city)
        if not path:
            return {"time": 0, "supply": 0, "path": []}
        
        supply_cost = self.calculate_supply_cost(path, army_size)
        
        # 计算行军时间
        start_pos = self.cities[start_city]["position"]
        end_pos = self.cities[end_city]["position"]
        march_time = self.calculate_march_time(start_pos, end_pos)
        
        return {
            "time": march_time,
            "supply": supply_cost,
            "path": path
        }