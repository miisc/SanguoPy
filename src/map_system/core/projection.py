"""
等距投影转换

实现网格坐标与屏幕坐标之间的转换，用于伪3D地图渲染
"""

import math
from typing import Tuple


class IsometricProjection:
    """等距投影转换类
    
    负责将网格坐标转换为屏幕坐标，实现伪3D效果
    """
    
    def __init__(self, tile_width: int = 64, tile_height: int = 32):
        """初始化等距投影转换
        
        Args:
            tile_width: 地形块的宽度（像素）
            tile_height: 地形块的高度（像素）
        """
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.angle = 45  # 俯视角度（度）
        
        # 计算转换系数
        self.x_factor = tile_width / 2
        self.y_factor = tile_height / 2
    
    def grid_to_screen(self, grid_x: int, grid_y: int) -> Tuple[float, float]:
        """将网格坐标转换为屏幕坐标
        
        Args:
            grid_x: 网格X坐标
            grid_y: 网格Y坐标
            
        Returns:
            屏幕坐标(x, y)
        """
        screen_x = (grid_x - grid_y) * self.x_factor
        screen_y = (grid_x + grid_y) * self.y_factor
        return screen_x, screen_y
    
    def screen_to_grid(self, screen_x: float, screen_y: float) -> Tuple[int, int]:
        """将屏幕坐标转换为网格坐标
        
        Args:
            screen_x: 屏幕X坐标
            screen_y: 屏幕Y坐标
            
        Returns:
            网格坐标(x, y)
        """
        grid_x = (screen_x / self.x_factor + screen_y / self.y_factor) / 2
        grid_y = (screen_y / self.y_factor - screen_x / self.x_factor) / 2
        return int(round(grid_x)), int(round(grid_y))
    
    def get_tile_bounds(self, grid_x: int, grid_y: int) -> Tuple[float, float, float, float]:
        """获取地形块在屏幕上的边界
        
        Args:
            grid_x: 网格X坐标
            grid_y: 网格Y坐标
            
        Returns:
            地形块的边界(left, top, right, bottom)
        """
        center_x, center_y = self.grid_to_screen(grid_x, grid_y)
        return (
            center_x - self.x_factor,  # left
            center_y - self.y_factor,  # top
            center_x + self.x_factor,  # right
            center_y + self.y_factor   # bottom
        )
    
    def get_tile_center(self, grid_x: int, grid_y: int) -> Tuple[float, float]:
        """获取地形块在屏幕上的中心点
        
        Args:
            grid_x: 网格X坐标
            grid_y: 网格Y坐标
            
        Returns:
            地形块的中心点坐标(x, y)
        """
        return self.grid_to_screen(grid_x, grid_y)
    
    def is_point_in_tile(self, screen_x: float, screen_y: float, grid_x: int, grid_y: int) -> bool:
        """判断屏幕点是否在指定地形块内
        
        Args:
            screen_x: 屏幕X坐标
            screen_y: 屏幕Y坐标
            grid_x: 网格X坐标
            grid_y: 网格Y坐标
            
        Returns:
            如果点在地形块内返回True，否则返回False
        """
        # 将屏幕坐标转换为相对于地形块中心的坐标
        center_x, center_y = self.grid_to_screen(grid_x, grid_y)
        rel_x = screen_x - center_x
        rel_y = screen_y - center_y
        
        # 检查点是否在菱形内
        # 菱形的边界条件：|x/a| + |y/b| <= 1
        # 其中a是菱形的半宽，b是菱形的半高
        a = self.x_factor
        b = self.y_factor
        
        return (abs(rel_x) / a + abs(rel_y) / b) <= 1