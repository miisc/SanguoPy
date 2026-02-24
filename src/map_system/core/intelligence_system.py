#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
情报系统
管理迷雾区域的情报解锁和交互
"""

from typing import Dict, List, Optional, Tuple


class IntelligenceSystem:
    """情报系统"""
    
    def __init__(self):
        """初始化情报系统"""
        self.intelligence_points = 100
        self.max_intelligence_points = 200
        self.daily_intelligence_gain = 10
        self.unlocks = []
        self.visibility_manager = None
        self.unlock_costs = {
            "city": {
                "base_cost": 20,
                "distance_factor": 0.1,
                "importance_factor": 1.5
            },
            "road": {
                "base_cost": 15,
                "length_factor": 0.05,
                "type_factor": {
                    "官道": 1.0,
                    "山间小径": 1.2,
                    "水路": 1.5
                }
            },
            "area": {
                "base_cost": 100,
                "size_factor": 1.0,
                "density_factor": 0.1
            }
        }
    
    def initialize(self, visibility_manager):
        """初始化情报系统
        
        Args:
            visibility_manager: 可见性管理器
        """
        self.visibility_manager = visibility_manager
    
    def get_intelligence_points(self, player_id: str = "player") -> List[Dict]:
        """获取情报点
        
        Args:
            player_id: 玩家ID
            
        Returns:
            情报点列表
        """
        # 返回当前情报点数作为一个列表项
        return [{"points": self.intelligence_points, "max_points": self.max_intelligence_points}]
    
    def consume_intelligence_points(self, amount: int) -> bool:
        """消耗情报点
        
        Args:
            amount: 消耗数量
            
        Returns:
            是否消耗成功
        """
        if self.intelligence_points >= amount:
            self.intelligence_points -= amount
            return True
        return False
    
    def generate_intelligence(self):
        """生成情报点"""
        self.intelligence_points = min(
            self.intelligence_points + self.daily_intelligence_gain,
            self.max_intelligence_points
        )
    
    def unlock_area(self, area_id: str, unlock_type: str) -> bool:
        """解锁区域
        
        Args:
            area_id: 区域ID
            unlock_type: 解锁类型 (city, road, area)
            
        Returns:
            是否解锁成功
        """
        # 计算解锁成本
        cost = self.calculate_unlock_cost(area_id, unlock_type)
        
        # 检查情报点是否足够
        if not self.consume_intelligence_points(cost):
            return False
        
        # 执行解锁
        if unlock_type == "city":
            # 解锁城市
            if self.visibility_manager:
                self.visibility_manager.visibility_states["intelligence_unlocked"]["cities"].append(area_id)
                self.visibility_manager.update_visibility({})
        elif unlock_type == "road":
            # 解锁道路
            if self.visibility_manager:
                self.visibility_manager.visibility_states["intelligence_unlocked"]["roads"].append(area_id)
                self.visibility_manager.update_visibility({})
        elif unlock_type == "area":
            # 解锁区域（需要实现区域解锁逻辑）
            pass
        
        # 记录解锁
        self.unlocks.append({
            "id": area_id,
            "type": unlock_type,
            "cost": cost,
            "timestamp": "current_time"  # 需要替换为实际时间
        })
        
        return True
    
    def calculate_unlock_cost(self, area_id: str, unlock_type: str) -> int:
        """计算解锁成本
        
        Args:
            area_id: 区域ID
            unlock_type: 解锁类型
            
        Returns:
            解锁成本
        """
        if unlock_type not in self.unlock_costs:
            return 0
        
        cost_config = self.unlock_costs[unlock_type]
        base_cost = cost_config.get("base_cost", 0)
        
        # 根据类型计算额外成本
        if unlock_type == "city":
            # 城市解锁成本
            distance_factor = cost_config.get("distance_factor", 0)
            importance_factor = cost_config.get("importance_factor", 1.0)
            # 这里需要根据实际情况计算距离和重要性
            cost = base_cost * importance_factor
        elif unlock_type == "road":
            # 道路解锁成本
            length_factor = cost_config.get("length_factor", 0)
            type_factor = cost_config.get("type_factor", {"官道": 1.0})
            # 这里需要根据实际道路计算长度和类型
            cost = base_cost
        elif unlock_type == "area":
            # 区域解锁成本
            size_factor = cost_config.get("size_factor", 1.0)
            density_factor = cost_config.get("density_factor", 0)
            # 这里需要根据实际区域计算大小和密度
            cost = base_cost * size_factor
        else:
            cost = base_cost
        
        return int(cost)
    
    def handle_click(self, position: Tuple[int, int]) -> Optional[Dict]:
        """处理迷雾区域点击
        
        Args:
            position: 点击位置
            
        Returns:
            点击结果
        """
        # 检查是否点击了迷雾区域
        # 这里需要实现迷雾区域的检测逻辑
        
        # 假设点击了迷雾区域，计算解锁成本
        cost = 20  # 示例成本
        
        return {
            "type": "fog",
            "cost": cost,
            "message": f"需消耗{cost}情报点解锁"
        }
    
    def update_intelligence_status(self):
        """更新情报状态"""
        # 更新情报时效性
        # 移除过期的解锁
        current_time = "current_time"  # 需要替换为实际时间
        self.unlocks = [unlock for unlock in self.unlocks 
                       if not self._is_expired(unlock, current_time)]
    
    def _is_expired(self, unlock: Dict, current_time) -> bool:
        """检查解锁是否过期
        
        Args:
            unlock: 解锁记录
            current_time: 当前时间
            
        Returns:
            是否过期
        """
        # 实现过期检查逻辑
        return False
    
    def unlock_intelligence(self, intel_id: str, player_id: str = "player") -> bool:
        """解锁情报
        
        Args:
            intel_id: 情报ID
            player_id: 玩家ID
            
        Returns:
            是否解锁成功
        """
        # 简化实现，假设解锁成功
        return True
    
    def get_unlocked_areas(self, player_id: str = "player") -> List[str]:
        """获取已解锁区域
        
        Args:
            player_id: 玩家ID
            
        Returns:
            已解锁区域列表
        """
        # 返回已解锁的区域
        unlocked_areas = []
        for unlock in self.unlocks:
            if unlock["type"] == "area":
                unlocked_areas.append(unlock["id"])
        return unlocked_areas