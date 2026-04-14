#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
道路系统
管理道路网络和行军规则
"""

from typing import Dict, List, Optional, Tuple
import math


class RoadSystem:
    """道路系统"""
    
    def __init__(self):
        """初始化道路系统"""
        self.roads = {}
        self.city_connections = {}
        self.road_types = {
            "官道": {
                "speed_factor": 1.0,
                "supply_factor": 1.0
            },
            "山间小径": {
                "speed_factor": 0.6,
                "supply_factor": 1.2
            },
            "水路": {
                "speed_factor": 0.8,
                "supply_factor": 0.6
            }
        }
    
    def initialize(self, roads: Dict):
        """初始化道路系统
        
        Args:
            roads: 道路字典
        """
        self.roads = roads
        self.city_connections = {}
        # 初始化城市连接关系
        for road_id, road in roads.items():
            start_city = road.get("start_city")
            end_city = road.get("end_city")
            
            if start_city not in self.city_connections:
                self.city_connections[start_city] = []
            if end_city not in self.city_connections:
                self.city_connections[end_city] = []
            
            self.city_connections[start_city].append((end_city, road_id))
            self.city_connections[end_city].append((start_city, road_id))
    
    def calculate_path(self, start_city: str, end_city: str) -> List[str]:
        """计算行军路线
        
        Args:
            start_city: 起点城市ID
            end_city: 终点城市ID
            
        Returns:
            行军路线（道路ID列表）
        """
        # 使用Dijkstra算法计算最短路径
        if start_city not in self.city_connections or \
           end_city not in self.city_connections:
            return []
        
        # 初始化距离字典
        distances = {}
        previous = {}
        for city in self.city_connections:
            distances[city] = float('inf')
        distances[start_city] = 0
        
        # 未访问的城市集合
        unvisited = set(self.city_connections.keys())
        
        while unvisited:
            # 选择距离最小的城市
            current = min(unvisited, key=lambda city: distances[city])
            unvisited.remove(current)
            
            # 如果到达终点
            if current == end_city:
                break
            
            # 遍历相邻城市
            for neighbor, road_id in self.city_connections.get(current, []):
                if neighbor in unvisited:
                    road = self.roads.get(road_id)
                    if road:
                        # 计算距离（考虑道路长度和速度因子）
                        distance = distances[current] + \
                                   road.get("length", 0) / road.get("speed_factor", 1.0)
                        
                        if distance < distances[neighbor]:
                            distances[neighbor] = distance
                            previous[neighbor] = (current, road_id)
        
        # 构建路径
        path = []
        current = end_city
        while current in previous:
            prev_city, road_id = previous[current]
            path.insert(0, road_id)
            current = prev_city
        
        return path
    
    def calculate_supply_cost(self, path: List[str], army_size: int) -> int:
        """计算军粮消耗
        
        Args:
            path: 行军路线（道路ID列表）
            army_size: 军队规模
            
        Returns:
            军粮消耗
        """
        total_cost = 0
        
        for road_id in path:
            road = self.roads.get(road_id)
            if road:
                # 计算行军天数（假设每天行军10单位距离）
                days = math.ceil(road.get("length", 0) / 10)
                # 计算军粮消耗
                supply_factor = road.get("supply_factor", 1.0)
                cost = army_size * days * supply_factor
                total_cost += int(cost)
        
        return total_cost
    
    def validate_path(self, path: List[str]) -> bool:
        """验证行军路径
        
        Args:
            path: 行军路线（道路ID列表）
            
        Returns:
            路径是否有效
        """
        if not path:
            return False
        
        # 验证路径中的道路是否存在
        for road_id in path:
            if road_id not in self.roads:
                return False
        
        # 验证路径是否连续
        for i in range(len(path) - 1):
            current_road = self.roads[path[i]]
            next_road = self.roads[path[i + 1]]
            
            # 检查两条道路是否相连
            if current_road["end_city"] != next_road["start_city"] and \
               current_road["end_city"] != next_road["end_city"] and \
               current_road["start_city"] != next_road["start_city"] and \
               current_road["start_city"] != next_road["end_city"]:
                return False
        
        return True
    
    def get_road_info(self, road_id: str) -> Optional[Dict]:
        """获取道路信息
        
        Args:
            road_id: 道路ID
            
        Returns:
            道路信息
        """
        return self.roads.get(road_id)
    
    def get_connected_cities(self, city_id: str) -> List[str]:
        """获取与城市相连的城市列表
        
        Args:
            city_id: 城市ID
            
        Returns:
            相连的城市列表
        """
        connected = []
        for neighbor, road_id in self.city_connections.get(city_id, []):
            connected.append(neighbor)
        return connected
    
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
        # 计算直线距离
        distance = math.sqrt((end_pos[0] - start_pos[0]) ** 2 + 
                           (end_pos[1] - start_pos[1]) ** 2)
        
        # 获取道路类型的速度因子
        speed_factor = self.road_types.get(road_type, {}).get("speed_factor", 1.0)
        
        # 计算行军时间（假设每天行军10单位距离）
        march_time = distance / (10 * speed_factor * speed)
        
        return max(1, march_time)  # 最少需要1天