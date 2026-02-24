#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
可见性管理器
管理地图的可见性规则和迷雾效果
"""

from typing import Dict, List, Optional, Tuple


class VisibilityManager:
    """可见性管理器"""
    
    def __init__(self):
        """初始化可见性管理器"""
        self.visibility_states = {
            "player_controlled": {
                "cities": [],
                "roads": []
            },
            "enemy_controlled": {
                "cities": [],
                "roads": []
            },
            "intelligence_unlocked": {
                "cities": [],
                "roads": []
            }
        }
        self.fog_areas = []
        self.road_connections = {}
    
    def initialize(self, cities: Dict, roads: Dict):
        """初始化可见性管理器
        
        Args:
            cities: 城市字典
            roads: 道路字典
        """
        # 初始化道路连接关系
        for road_id, road in roads.items():
            start_city = road.get("start_city")
            end_city = road.get("end_city")
            
            if start_city not in self.road_connections:
                self.road_connections[start_city] = []
            if end_city not in self.road_connections:
                self.road_connections[end_city] = []
            
            self.road_connections[start_city].append(road_id)
            self.road_connections[end_city].append(road_id)
    
    def get_visibility(self, city_id: str) -> bool:
        """获取城市可见性
        
        Args:
            city_id: 城市ID
            
        Returns:
            是否可见
        """
        # 检查是否是我方控制的城市
        if city_id in self.visibility_states["player_controlled"]["cities"]:
            return True
        
        # 检查是否是情报解锁的城市
        if city_id in self.visibility_states["intelligence_unlocked"]["cities"]:
            return True
        
        # 检查是否通过道路连接可见
        if self._is_visible_via_road(city_id):
            return True
        
        # 默认不可见
        return False
    
    def get_road_visibility(self, road_id: str) -> bool:
        """获取道路可见性
        
        Args:
            road_id: 道路ID
            
        Returns:
            是否可见
        """
        # 检查是否是我方控制的道路
        if road_id in self.visibility_states["player_controlled"]["roads"]:
            return True
        
        # 检查是否是情报解锁的道路
        if road_id in self.visibility_states["intelligence_unlocked"]["roads"]:
            return True
        
        # 检查是否连接到我方城市
        if self._is_road_connected_to_player(road_id):
            return True
        
        # 默认不可见
        return False
    
    def _is_visible_via_road(self, city_id: str) -> bool:
        """检查城市是否通过道路连接可见
        
        Args:
            city_id: 城市ID
            
        Returns:
            是否可见
        """
        # 检查是否有道路连接到我方城市
        if city_id in self.road_connections:
            for road_id in self.road_connections[city_id]:
                if self._is_road_connected_to_player(road_id):
                    return True
        return False
    
    def _is_road_connected_to_player(self, road_id: str) -> bool:
        """检查道路是否连接到我方城市
        
        Args:
            road_id: 道路ID
            
        Returns:
            是否可见
        """
        # 这里需要根据实际的道路数据结构实现
        # 暂时返回False
        return False
    
    def update_visibility(self, cities: Dict, roads: Dict):
        """更新可见性
        
        Args:
            cities: 城市字典
            roads: 道路字典
        """
        # 重置玩家控制的城市和道路
        self.visibility_states["player_controlled"]["cities"] = []
        self.visibility_states["player_controlled"]["roads"] = []
        self.visibility_states["enemy_controlled"]["cities"] = []
        
        # 更新道路连接关系
        self.road_connections = {}
        for road_id, road in roads.items():
            start_city = road.get("start_city")
            end_city = road.get("end_city")
            
            if start_city not in self.road_connections:
                self.road_connections[start_city] = []
            if end_city not in self.road_connections:
                self.road_connections[end_city] = []
            
            self.road_connections[start_city].append(road_id)
            self.road_connections[end_city].append(road_id)
        
        # 更新城市可见性
        for city_id, city in cities.items():
            if city.get("owner") == "player":
                self.add_player_city(city_id)
            elif city.get("owner") == "enemy":
                self.add_enemy_city(city_id)
        
        # 更新迷雾区域
        self._update_fog_areas()
    
    def _update_fog_areas(self):
        """更新迷雾区域"""
        # 计算迷雾区域
        self.fog_areas = []
        # 实现迷雾区域的计算逻辑
    
    def render_fog(self, surface):
        """渲染迷雾
        
        Args:
            surface: 渲染表面
        """
        # 渲染迷雾效果
        # 暂时空实现
        pass
    
    def get_visible_cities(self, player_id: str = "player") -> List[str]:
        """获取可见城市
        
        Args:
            player_id: 玩家ID
            
        Returns:
            可见城市ID列表
        """
        visible_cities = []
        # 我方控制的城市
        visible_cities.extend(self.visibility_states["player_controlled"]["cities"])
        # 情报解锁的城市
        visible_cities.extend(self.visibility_states["intelligence_unlocked"]["cities"])
        # 通过道路连接可见的城市
        for city_id in self.road_connections:
            if self._is_visible_via_road(city_id) and city_id not in visible_cities:
                visible_cities.append(city_id)
        return visible_cities
    
    def get_visible_roads(self, player_id: str = "player") -> List[str]:
        """获取可见道路
        
        Args:
            player_id: 玩家ID
            
        Returns:
            可见道路ID列表
        """
        visible_roads = []
        # 我方控制的道路
        visible_roads.extend(self.visibility_states["player_controlled"]["roads"])
        # 情报解锁的道路
        visible_roads.extend(self.visibility_states["intelligence_unlocked"]["roads"])
        # 连接到我方城市的道路
        for city_id in self.visibility_states["player_controlled"]["cities"]:
            if city_id in self.road_connections:
                for road_id in self.road_connections[city_id]:
                    if road_id not in visible_roads:
                        visible_roads.append(road_id)
        return visible_roads
    
    def add_player_city(self, city_id: str):
        """添加我方城市
        
        Args:
            city_id: 城市ID
        """
        if city_id not in self.visibility_states["player_controlled"]["cities"]:
            self.visibility_states["player_controlled"]["cities"].append(city_id)
            # 更新连接的道路可见性
            self._update_connected_roads(city_id)
    
    def add_enemy_city(self, city_id: str):
        """添加敌方城市
        
        Args:
            city_id: 城市ID
        """
        if city_id not in self.visibility_states["enemy_controlled"]["cities"]:
            self.visibility_states["enemy_controlled"]["cities"].append(city_id)
    
    def _update_connected_roads(self, city_id: str):
        """更新连接的道路可见性
        
        Args:
            city_id: 城市ID
        """
        if city_id in self.road_connections:
            for road_id in self.road_connections[city_id]:
                if road_id not in self.visibility_states["player_controlled"]["roads"]:
                    self.visibility_states["player_controlled"]["roads"].append(road_id)