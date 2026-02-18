"""
地形渲染器

负责渲染地图上的地形，实现伪3D效果
"""

import os
from typing import Dict, Optional
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtCore import Qt

from ..core.map_grid import MapGrid
from ..core.terrain import TerrainType
from ..core.projection import IsometricProjection


class TerrainRenderer:
    """地形渲染器
    
    负责加载地形资源并渲染地形到场景中
    """
    
    def __init__(self, scene: QGraphicsScene):
        """初始化地形渲染器
        
        Args:
            scene: 用于渲染的图形场景
        """
        self.scene = scene
        self.terrain_images: Dict[TerrainType, QPixmap] = {}
        self.projection = IsometricProjection(64, 32)
        self.load_terrain_images()
    
    def load_terrain_images(self):
        """加载地形图像资源
        
        如果找不到图像资源，则生成简单的占位图像
        """
        # 尝试从资源目录加载图像
        resources_dir = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "terrain")
        
        for terrain_type in TerrainType:
            image_path = os.path.join(resources_dir, f"{terrain_type.name.lower()}.png")
            
            if os.path.exists(image_path):
                # 从文件加载图像
                pixmap = QPixmap(image_path)
                self.terrain_images[terrain_type] = pixmap
            else:
                # 生成简单的占位图像
                self.terrain_images[terrain_type] = self._generate_placeholder_image(terrain_type)
    
    def _generate_placeholder_image(self, terrain_type: TerrainType) -> QPixmap:
        """生成地形类型的占位图像
        
        Args:
            terrain_type: 地形类型
            
        Returns:
            生成的图像
        """
        # 创建一个64x32的菱形图像
        width, height = 64, 32
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.transparent)
        
        # 根据地形类型选择颜色
        colors = {
            TerrainType.PLAIN: QColor(139, 195, 74),      # 浅绿色
            TerrainType.MOUNTAIN: QColor(158, 158, 158),  # 灰色
            TerrainType.HILL: QColor(189, 154, 122),      # 棕色
            TerrainType.RIVER: QColor(33, 150, 243),       # 蓝色
            TerrainType.FOREST: QColor(76, 175, 80),      # 深绿色
            TerrainType.DESERT: QColor(255, 235, 59)      # 黄色
        }
        
        color = colors.get(terrain_type, QColor(128, 128, 128))
        
        # 绘制菱形
        from PyQt5.QtGui import QPainter, QPolygonF
        from PyQt5.QtCore import QPointF
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 创建菱形路径
        polygon = QPolygonF([
            QPointF(width / 2, 0),            # 顶点
            QPointF(width - 1, height / 2),  # 右点
            QPointF(width / 2, height - 1),  # 底点
            QPointF(0, height / 2)            # 左点
        ])
        
        # 填充菱形
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawPolygon(polygon)
        
        # 添加边框
        painter.setPen(QColor(0, 0, 0, 100))
        painter.drawPolygon(polygon)
        
        painter.end()
        return pixmap
    
    def render_terrain(self, map_grid: MapGrid):
        """渲染地形
        
        Args:
            map_grid: 地图网格数据
        """
        # 清除现有的地形项
        self._clear_terrain_items()
        
        # 渲染所有地形块
        for y in range(map_grid.height):
            for x in range(map_grid.width):
                terrain_type = map_grid.get_terrain(x, y)
                if terrain_type is not None:
                    self.render_tile(x, y, terrain_type)
    
    def render_tile(self, grid_x: int, grid_y: int, terrain_type: TerrainType) -> Optional[QGraphicsPixmapItem]:
        """渲染单个地形块
        
        Args:
            grid_x: 网格X坐标
            grid_y: 网格Y坐标
            terrain_type: 地形类型
            
        Returns:
            创建的地形项
        """
        # 计算屏幕坐标
        screen_x, screen_y = self.projection.grid_to_screen(grid_x, grid_y)
        
        # 获取地形图像
        pixmap = self.terrain_images.get(terrain_type)
        if pixmap is None:
            return None
        
        # 创建地形项
        item = QGraphicsPixmapItem(pixmap)
        item.setPos(screen_x, screen_y)
        
        # 存储网格坐标，用于后续交互
        item.setData(0, (grid_x, grid_y))
        item.setData(1, terrain_type)
        
        # 设置Z值，确保正确的渲染顺序
        # Y坐标越大，Z值越大，确保后面的地形块不会被前面的遮挡
        item.setZValue(grid_y + grid_x * 0.01)
        
        # 添加到场景
        self.scene.addItem(item)
        
        return item
    
    def _clear_terrain_items(self):
        """清除场景中的所有地形项"""
        # 获取场景中的所有项
        items = self.scene.items()
        
        # 移除所有地形项
        for item in items:
            # 检查是否是地形项（通过数据判断）
            if item.data(0) is not None and isinstance(item.data(0), tuple) and len(item.data(0)) == 2:
                self.scene.removeItem(item)
    
    def get_terrain_item_at(self, screen_x: float, screen_y: float) -> Optional[QGraphicsPixmapItem]:
        """获取指定屏幕位置的地形项
        
        Args:
            screen_x: 屏幕X坐标
            screen_y: 屏幕Y坐标
            
        Returns:
            地形项，如果没有找到则返回None
        """
        # 获取指定位置的所有项
        items = self.scene.items(screen_x, screen_y)
        
        # 查找地形项
        for item in items:
            if isinstance(item, QGraphicsPixmapItem) and item.data(0) is not None:
                return item
        
        return None
    
    def update_tile(self, grid_x: int, grid_y: int, terrain_type: TerrainType):
        """更新指定位置的地形
        
        Args:
            grid_x: 网格X坐标
            grid_y: 网格Y坐标
            terrain_type: 新的地形类型
        """
        # 查找并移除旧的地形项
        screen_x, screen_y = self.projection.grid_to_screen(grid_x, grid_y)
        item = self.get_terrain_item_at(screen_x, screen_y)
        
        if item:
            self.scene.removeItem(item)
        
        # 渲染新的地形项
        self.render_tile(grid_x, grid_y, terrain_type)