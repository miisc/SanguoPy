"""
地形类型定义

定义游戏中各种地形类型及其属性
"""

from enum import Enum


class TerrainType(Enum):
    """地形类型枚举"""
    PLAIN = 0      # 平原
    MOUNTAIN = 1   # 山地
    HILL = 2       # 丘陵
    RIVER = 3      # 河流
    FOREST = 4     # 森林
    DESERT = 5     # 沙漠
    
    @property
    def name_cn(self):
        """中文名称"""
        names = {
            TerrainType.PLAIN: "平原",
            TerrainType.MOUNTAIN: "山地",
            TerrainType.HILL: "丘陵",
            TerrainType.RIVER: "河流",
            TerrainType.FOREST: "森林",
            TerrainType.DESERT: "沙漠"
        }
        return names[self]
    
    @property
    def move_cost(self):
        """移动成本（用于后续军队移动系统）"""
        costs = {
            TerrainType.PLAIN: 1.0,
            TerrainType.MOUNTAIN: 2.0,
            TerrainType.HILL: 1.5,
            TerrainType.RIVER: 3.0,
            TerrainType.FOREST: 1.5,
            TerrainType.DESERT: 1.8
        }
        return costs[self]
    
    @property
    def defense_bonus(self):
        """防御加成（用于后续战斗系统）"""
        bonuses = {
            TerrainType.PLAIN: 0,
            TerrainType.MOUNTAIN: 0.3,
            TerrainType.HILL: 0.15,
            TerrainType.RIVER: 0.1,
            TerrainType.FOREST: 0.2,
            TerrainType.DESERT: 0.05
        }
        return bonuses[self]