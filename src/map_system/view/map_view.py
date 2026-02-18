"""
地图视图

提供地图的显示和交互功能
"""

from typing import Optional, Tuple
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5.QtCore import Qt, QPoint, pyqtSignal
from PyQt5.QtGui import QPainter, QWheelEvent, QMouseEvent

from ..core.map_grid import MapGrid
from ..core.terrain import TerrainType
from ..core.projection import IsometricProjection
from ..renderer.terrain_renderer import TerrainRenderer


class MapView(QGraphicsView):
    """地图视图类
    
    提供地图的显示和交互功能，包括缩放、拖动等
    """
    
    # 信号定义
    tile_clicked = pyqtSignal(int, int, TerrainType)  # 地形块被点击
    tile_hovered = pyqtSignal(int, int, TerrainType)  # 地形块被悬停
    
    def __init__(self, width: int = 50, height: int = 50, parent=None):
        """初始化地图视图
        
        Args:
            width: 地图宽度（网格数）
            height: 地图高度（网格数）
            parent: 父窗口
        """
        super().__init__(parent)
        
        # 创建场景
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        # 初始化地图
        self.map_grid = MapGrid(width, height)
        self.terrain_renderer = TerrainRenderer(self.scene)
        self.projection = IsometricProjection(64, 32)
        
        # 设置视图属性
        self.setRenderHint(QPainter.Antialiasing)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 初始化地图数据
        self.initialize_map()
        
        # 渲染地图
        self.terrain_renderer.render_terrain(self.map_grid)
        
        # 缩放级别
        self.zoom_level = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 3.0
        
        # 拖动相关
        self.last_pan_point = QPoint()
        self.is_panning = False
        
        # 调整视图大小以适应地图
        self.adjust_view_size()
    
    def initialize_map(self):
        """初始化地图数据
        
        生成一个简单的测试地图，包含各种地形类型
        """
        # 填充基础地形
        self.map_grid.fill_terrain(TerrainType.PLAIN)
        
        # 添加一些山地
        mountain_positions = [
            (10, 10), (11, 10), (10, 11), (11, 11),
            (30, 20), (31, 20), (30, 21), (31, 21),
            (15, 35), (16, 35), (15, 36), (16, 36)
        ]
        
        for x, y in mountain_positions:
            if self.map_grid.is_valid_position(x, y):
                self.map_grid.set_terrain(x, y, TerrainType.MOUNTAIN)
        
        # 添加一些丘陵
        hill_positions = [
            (5, 5), (6, 5), (5, 6), (6, 6),
            (25, 15), (26, 15), (25, 16), (26, 16),
            (35, 30), (36, 30), (35, 31), (36, 31)
        ]
        
        for x, y in hill_positions:
            if self.map_grid.is_valid_position(x, y):
                self.map_grid.set_terrain(x, y, TerrainType.HILL)
        
        # 添加一条河流
        river_path = [
            (20, 0), (20, 1), (20, 2), (21, 3), (21, 4), 
            (22, 5), (22, 6), (23, 7), (23, 8), (24, 9),
            (24, 10), (25, 11), (25, 12), (26, 13), (26, 14)
        ]
        
        for x, y in river_path:
            if self.map_grid.is_valid_position(x, y):
                self.map_grid.set_terrain(x, y, TerrainType.RIVER)
        
        # 添加一些森林
        forest_positions = [
            (8, 8), (9, 8), (8, 9), (9, 9), (10, 8), (8, 10),
            (28, 18), (29, 18), (28, 19), (29, 19), (30, 18), (28, 20),
            (18, 28), (19, 28), (18, 29), (19, 29), (20, 28), (18, 30)
        ]
        
        for x, y in forest_positions:
            if self.map_grid.is_valid_position(x, y):
                self.map_grid.set_terrain(x, y, TerrainType.FOREST)
        
        # 添加一些沙漠
        desert_positions = [
            (40, 40), (41, 40), (40, 41), (41, 41), (42, 40), (40, 42),
            (38, 38), (39, 38), (38, 39), (39, 39), (40, 38), (38, 40)
        ]
        
        for x, y in desert_positions:
            if self.map_grid.is_valid_position(x, y):
                self.map_grid.set_terrain(x, y, TerrainType.DESERT)
    
    def adjust_view_size(self):
        """调整视图大小以适应地图"""
        # 计算地图的屏幕边界
        left, top, right, bottom = self.projection.get_tile_bounds(0, 0)
        map_left, map_top, map_right, map_bottom = self.projection.get_tile_bounds(
            self.map_grid.width - 1, self.map_grid.height - 1
        )
        
        # 计算地图的屏幕尺寸
        map_width = map_right - map_left
        map_height = map_bottom - map_top
        
        # 设置场景矩形
        self.scene.setSceneRect(map_left, map_top, map_width, map_height)
        
        # 居中显示地图
        self.centerOn(map_width / 2, map_height / 2)
    
    def wheelEvent(self, event: QWheelEvent):
        """鼠标滚轮缩放
        
        Args:
            event: 滚轮事件
        """
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor
        
        # 保存原始场景位置
        old_pos = self.mapToScene(event.pos())
        
        # 缩放
        if event.angleDelta().y() > 0:
            # 放大
            if self.zoom_level < self.max_zoom:
                zoom_factor = zoom_in_factor
                self.zoom_level *= zoom_in_factor
            else:
                return
        else:
            # 缩小
            if self.zoom_level > self.min_zoom:
                zoom_factor = zoom_out_factor
                self.zoom_level *= zoom_out_factor
            else:
                return
        
        # 应用缩放
        self.scale(zoom_factor, zoom_factor)
        
        # 获取新位置
        new_pos = self.mapToScene(event.pos())
        
        # 调整场景位置，保持鼠标下的点不变
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())
    
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件
        
        Args:
            event: 鼠标事件
        """
        if event.button() == Qt.LeftButton:
            # 检查是否点击了地形块
            scene_pos = self.mapToScene(event.pos())
            grid_pos = self.projection.screen_to_grid(scene_pos.x(), scene_pos.y())
            
            if self.map_grid.is_valid_position(grid_pos[0], grid_pos[1]):
                terrain_type = self.map_grid.get_terrain(grid_pos[0], grid_pos[1])
                if terrain_type is not None:
                    self.tile_clicked.emit(grid_pos[0], grid_pos[1], terrain_type)
        
        elif event.button() == Qt.MiddleButton:
            # 开始拖动
            self.is_panning = True
            self.last_pan_point = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
        
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放事件
        
        Args:
            event: 鼠标事件
        """
        if event.button() == Qt.MiddleButton and self.is_panning:
            # 结束拖动
            self.is_panning = False
            self.setCursor(Qt.ArrowCursor)
        
        super().mouseReleaseEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动事件
        
        Args:
            event: 鼠标事件
        """
        if self.is_panning:
            # 拖动视图
            delta = event.pos() - self.last_pan_point
            self.last_pan_point = event.pos()
            
            # 获取当前场景位置
            h_value = self.horizontalScrollBar().value()
            v_value = self.verticalScrollBar().value()
            
            # 更新滚动条位置
            self.horizontalScrollBar().setValue(h_value - delta.x())
            self.verticalScrollBar().setValue(v_value - delta.y())
        else:
            # 检查是否悬停在地形块上
            scene_pos = self.mapToScene(event.pos())
            grid_pos = self.projection.screen_to_grid(scene_pos.x(), scene_pos.y())
            
            if self.map_grid.is_valid_position(grid_pos[0], grid_pos[1]):
                terrain_type = self.map_grid.get_terrain(grid_pos[0], grid_pos[1])
                if terrain_type is not None:
                    self.tile_hovered.emit(grid_pos[0], grid_pos[1], terrain_type)
        
        super().mouseMoveEvent(event)
    
    def get_tile_at(self, screen_x: int, screen_y: int) -> Optional[Tuple[int, int, TerrainType]]:
        """获取指定屏幕位置的地形块信息
        
        Args:
            screen_x: 屏幕X坐标
            screen_y: 屏幕Y坐标
            
        Returns:
            地形块信息(x, y, terrain_type)，如果没有找到则返回None
        """
        scene_pos = self.mapToScene(screen_x, screen_y)
        grid_pos = self.projection.screen_to_grid(scene_pos.x(), scene_pos.y())
        
        if not self.map_grid.is_valid_position(grid_pos[0], grid_pos[1]):
            return None
        
        terrain_type = self.map_grid.get_terrain(grid_pos[0], grid_pos[1])
        if terrain_type is None:
            return None
        
        return grid_pos[0], grid_pos[1], terrain_type
    
    def center_on_tile(self, grid_x: int, grid_y: int):
        """将视图中心移动到指定地形块
        
        Args:
            grid_x: 网格X坐标
            grid_y: 网格Y坐标
        """
        screen_x, screen_y = self.projection.grid_to_screen(grid_x, grid_y)
        self.centerOn(screen_x, screen_y)
    
    def reset_zoom(self):
        """重置缩放级别"""
        self.resetTransform()
        self.zoom_level = 1.0
    
    def set_zoom(self, zoom_level: float):
        """设置缩放级别
        
        Args:
            zoom_level: 缩放级别
        """
        # 限制缩放级别
        zoom_level = max(self.min_zoom, min(self.max_zoom, zoom_level))
        
        # 计算缩放因子
        zoom_factor = zoom_level / self.zoom_level
        
        # 应用缩放
        self.scale(zoom_factor, zoom_factor)
        
        # 更新缩放级别
        self.zoom_level = zoom_level