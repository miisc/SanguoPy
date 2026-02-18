"""
地图网格数据结构

定义地图网格的基础数据结构和操作
"""

from typing import List, Optional, Tuple
from .terrain import TerrainType


class MapGrid:
    """地图网格基础类
    
    负责存储和管理地图的网格数据和地形信息
    """
    
    def __init__(self, width: int, height: int):
        """初始化地图网格
        
        Args:
            width: 地图宽度（网格数）
            height: 地图高度（网格数）
        """
        self.width = width
        self.height = height
        # 初始化网格数据，默认为None
        self.grid_data = [[None for _ in range(width)] for _ in range(height)]
    
    def is_valid_position(self, x: int, y: int) -> bool:
        """检查坐标是否在有效范围内
        
        Args:
            x: 网格X坐标
            y: 网格Y坐标
            
        Returns:
            如果坐标有效返回True，否则返回False
        """
        return 0 <= x < self.width and 0 <= y < self.height
    
    def get_terrain(self, x: int, y: int) -> Optional[TerrainType]:
        """获取指定位置的地形类型
        
        Args:
            x: 网格X坐标
            y: 网格Y坐标
            
        Returns:
            地形类型，如果位置无效或未设置地形则返回None
        """
        if not self.is_valid_position(x, y):
            return None
        return self.grid_data[y][x]
    
    def set_terrain(self, x: int, y: int, terrain_type: TerrainType) -> bool:
        """设置指定位置的地形类型
        
        Args:
            x: 网格X坐标
            y: 网格Y坐标
            terrain_type: 地形类型
            
        Returns:
            如果设置成功返回True，否则返回False
        """
        if not self.is_valid_position(x, y):
            return False
        
        self.grid_data[y][x] = terrain_type
        return True
    
    def fill_terrain(self, terrain_type: TerrainType):
        """用指定地形填充整个地图
        
        Args:
            terrain_type: 地形类型
        """
        for y in range(self.height):
            for x in range(self.width):
                self.grid_data[y][x] = terrain_type
    
    def get_terrain_rect(self, x: int, y: int, width: int, height: int) -> List[List[Optional[TerrainType]]]:
        """获取指定矩形区域的地形数据
        
        Args:
            x: 起始X坐标
            y: 起始Y坐标
            width: 矩形宽度
            height: 矩形高度
            
        Returns:
            地形数据的二维列表
        """
        result = []
        for dy in range(height):
            row = []
            for dx in range(width):
                row.append(self.get_terrain(x + dx, y + dy))
            result.append(row)
        return result
    
    def set_terrain_rect(self, x: int, y: int, terrain_data: List[List[TerrainType]]) -> bool:
        """设置指定矩形区域的地形数据
        
        Args:
            x: 起始X坐标
            y: 起始Y坐标
            terrain_data: 地形数据的二维列表
            
        Returns:
            如果设置成功返回True，否则返回False
        """
        height = len(terrain_data)
        if height == 0:
            return False
        
        width = len(terrain_data[0])
        
        # 检查区域是否有效
        if x < 0 or y < 0 or x + width > self.width or y + height > self.height:
            return False
        
        # 设置地形数据
        for dy in range(height):
            for dx in range(width):
                self.set_terrain(x + dx, y + dy, terrain_data[dy][dx])
        
        return True
    
    def get_terrain_count(self, terrain_type: TerrainType) -> int:
        """获取指定地形类型的数量
        
        Args:
            terrain_type: 地形类型
            
        Returns:
            地形类型的数量
        """
        count = 0
        for row in self.grid_data:
            for terrain in row:
                if terrain == terrain_type:
                    count += 1
        return count
    
    def get_random_position(self, terrain_type: Optional[TerrainType] = None) -> Optional[Tuple[int, int]]:
        """获取随机位置
        
        Args:
            terrain_type: 如果指定，只返回该地形类型的位置
            
        Returns:
            随机位置坐标(x, y)，如果没有找到合适位置则返回None
        """
        import random
        
        if terrain_type is None:
            # 返回任意随机位置
            return random.randint(0, self.width - 1), random.randint(0, self.height - 1)
        
        # 收集所有指定地形类型的位置
        positions = []
        for y in range(self.height):
            for x in range(self.width):
                if self.grid_data[y][x] == terrain_type:
                    positions.append((x, y))
        
        if not positions:
            return None
        
        return random.choice(positions)
    
    def clear(self):
        """清空地图数据"""
        for y in range(self.height):
            for x in range(self.width):
                self.grid_data[y][x] = None