#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
历史未央宫地图视图
实现基于历史资料的未央宫2D平面地图
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QScrollArea, QFrame, QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsObject)
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QRect, QPointF, QRectF
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush, QPixmap, QPolygonF


class HistoricalPalaceItem(QGraphicsObject, QGraphicsItem):
    """历史宫殿图形项"""
    
    # 信号定义
    clicked = pyqtSignal(str)  # 点击信号
    
    def __init__(self, name, display_name, palace_type, x, y, width, height, description=""):
        """初始化历史宫殿图形项"""
        super().__init__()
        
        # 宫殿属性
        self.name = name
        self.display_name = display_name
        self.palace_type = palace_type  # 'front', 'back', 'culture', 'office', 'garden'
        self.description = description
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # 设置图形项属性
        self.setPos(x, y)
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        
        # 边界矩形
        self.bounding_rect = QRectF(0, 0, width, height)
    
    def boundingRect(self):
        """返回边界矩形"""
        return self.bounding_rect
    
    def paint(self, painter, option, widget):
        """绘制宫殿"""
        # 设置抗锯齿
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 根据宫殿类型设置颜色
        if self.palace_type == 'front':
            # 前朝宫殿 - 朱红色
            color = QColor(199, 62, 30, 180)
            border_color = QColor(139, 37, 0)
        elif self.palace_type == 'back':
            # 后宫宫殿 - 金黄色
            color = QColor(212, 175, 55, 180)
            border_color = QColor(139, 105, 20)
        elif self.palace_type == 'culture':
            # 文化建筑 - 青色
            color = QColor(70, 130, 180, 180)
            border_color = QColor(25, 25, 112)
        elif self.palace_type == 'office':
            # 官署建筑 - 灰色
            color = QColor(128, 128, 128, 180)
            border_color = QColor(64, 64, 64)
        else:  # garden
            # 园林水体 - 蓝色
            color = QColor(100, 149, 237, 180)
            border_color = QColor(0, 0, 139)
        
        # 绘制宫殿主体
        painter.fillRect(self.bounding_rect, color)
        painter.setPen(QPen(border_color, 2))
        painter.drawRect(self.bounding_rect)
        
        # 绘制宫殿名称
        painter.setPen(QPen(Qt.white, 1))
        painter.setFont(QFont("", 10, QFont.Bold))
        painter.drawText(self.bounding_rect, Qt.AlignCenter, self.display_name)
        
        # 如果被选中，绘制选中效果
        if self.isSelected():
            painter.setPen(QPen(Qt.yellow, 3))
            painter.drawRect(self.bounding_rect.adjusted(-2, -2, 2, 2))
    
    def mousePressEvent(self, event):
        """处理鼠标点击事件"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.name)
        super().mousePressEvent(event)
    
    def hoverEnterEvent(self, event):
        """处理鼠标悬停进入事件"""
        self.setToolTip(f"{self.display_name}\n{self.description}")
        super().hoverEnterEvent(event)


class HistoricalWeiyangMap(QGraphicsView):
    """历史未央宫地图视图"""
    
    # 信号定义
    palace_clicked = pyqtSignal(str)  # 宫殿点击信号
    
    def __init__(self, parent=None):
        """初始化历史未央宫地图视图"""
        super().__init__(parent)
        
        # 地图属性
        self.map_width = 900
        self.map_height = 700
        self.scale_factor = 1.0
        
        # 场景
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        # 宫殿字典
        self.palaces = {}
        
        # 初始化UI
        self._init_ui()
        
        # 创建未央宫地图
        self._create_weiyang_palace()
    
    def _init_ui(self):
        """初始化用户界面"""
        # 设置基本属性
        self.setMinimumSize(700, 500)
        self.setRenderHint(QPainter.Antialiasing)
        
        # 设置场景范围
        self.scene.setSceneRect(0, 0, self.map_width, self.map_height)
        
        # 设置拖拽模式
        self.setDragMode(QGraphicsView.RubberBandDrag)
    
    def _create_weiyang_palace(self):
        """创建未央宫地图"""
        # 绘制背景
        background_rect = self.scene.addRect(0, 0, self.map_width, self.map_height, 
                                           QPen(Qt.NoPen), QBrush(QColor(245, 245, 220)))
        
        # 绘制宫墙
        wall_pen = QPen(QColor(139, 69, 19), 3)
        self.scene.addRect(50, 50, self.map_width-100, self.map_height-100, wall_pen)
        
        # 绘制中轴线
        axis_pen = QPen(QColor(205, 133, 63), 1, Qt.DashLine)
        self.scene.addLine(self.map_width/2, 50, self.map_width/2, self.map_height-50, axis_pen)
        self.scene.addLine(50, self.map_height/2, self.map_width-50, self.map_height/2, axis_pen)
        
        # 创建主要宫殿
        
        # 前殿 - 位于中央，是未央宫的主体建筑
        self._add_palace("前殿", "前殿", "front", 400, 200, 100, 80, 
                        "未央宫的主体建筑，仅处理州郡内政（直接统治区）")
        
        # 椒房殿 - 位于前殿以北，皇后居所
        self._add_palace("椒房殿", "椒房殿", "back", 400, 100, 100, 80, 
                        "皇后居所，仅处理后宫事务和继承人培养")
        
        # 承明殿 - 位于前殿东南
        self._add_palace("承明殿", "承明殿", "front", 550, 250, 80, 60, 
                        "接见大臣、处理外交事务的场所")
        
        # 宣室殿 - 位于前殿西南
        self._add_palace("宣室殿", "宣室殿", "front", 270, 250, 80, 60, 
                        "皇帝处理紧急军情和重大危机的场所")
        
        # 麒麟阁 - 位于前殿东北
        self._add_palace("麒麟阁", "麒麟阁", "front", 550, 150, 80, 60, 
                        "表彰功臣、展示功绩的场所")
        
        # 金銮殿 - 位于前殿西北
        self._add_palace("金銮殿", "金銮殿", "front", 270, 150, 80, 60, 
                        "举行一般典礼的场所")
        
        # 太庙 - 位于北部，重大祭祀场所
        self._add_palace("太庙", "太庙", "front", 400, 50, 100, 80, 
                        "仅处理祭祀和重大典礼的皇家宗庙")
        
        # 石渠阁 - 位于北部，文化建筑
        self._add_palace("石渠阁", "石渠阁", "culture", 550, 100, 80, 60, 
                        "皇室文化建筑，收藏图书典籍")
        
        # 天禄阁 - 位于北部，文化建筑
        self._add_palace("天禄阁", "天禄阁", "culture", 270, 100, 80, 60, 
                        "皇室文化建筑，收藏图书典籍")
        
        # 少府 - 位于西部，官署建筑
        self._add_palace("少府", "少府", "office", 150, 200, 80, 60, 
                        "管理皇室财政的官署")
        
        # 中央官署 - 位于西部，官署建筑
        self._add_palace("中央官署", "中央官署", "office", 150, 300, 80, 60, 
                        "处理国家政务的中央官署")
        
        # 太官署 - 位于西南，管理宫廷饮食
        self._add_palace("太官署", "太官署", "office", 150, 400, 80, 60, 
                        "管理宫廷饮食的机构")
        
        # 长秋宫 - 位于东部，太后居所
        self._add_palace("长秋宫", "长秋宫", "back", 670, 200, 80, 60, 
                        "太后居所")
        
        # 增成宫 - 位于东部，妃嫔居所
        self._add_palace("增成宫", "增成宫", "back", 670, 300, 80, 60, 
                        "妃嫔居所")
        
        # 永巷 - 位于东部，宫女居所
        self._add_palace("永巷", "永巷", "back", 670, 400, 80, 60, 
                        "宫女居所")
        
        # 掖庭 - 位于东部，宫中服务人员居所
        self._add_palace("掖庭", "掖庭", "back", 670, 500, 80, 60, 
                        "宫中服务人员居所")
        
        # 沧池 - 位于西南部，园林水体
        self._add_palace("沧池", "沧池", "garden", 200, 500, 120, 80, 
                        "皇宫池苑区，园林水体")
        
        # 添加地图标题
        title_item = self.scene.addText("东汉未央宫平面图", QFont("", 16, QFont.Bold))
        title_item.setPos(self.map_width/2 - 80, 10)
        
        # 添加方向指示
        self._add_compass(800, 100)
        
        # 添加比例尺
        self._add_scale(100, 620)
    
    def _add_palace(self, name, display_name, palace_type, x, y, width, height, description=""):
        """添加宫殿"""
        palace = HistoricalPalaceItem(name, display_name, palace_type, x, y, width, height, description)
        palace.clicked.connect(self._on_palace_clicked)
        self.scene.addItem(palace)
        self.palaces[name] = palace
    
    def _add_compass(self, x, y):
        """添加方向指示"""
        # 绘制圆形背景
        compass_bg = self.scene.addEllipse(x, y, 50, 50, QPen(Qt.black, 1), QBrush(Qt.white))
        
        # 绘制方向标记
        font = QFont("", 10, QFont.Bold)
        self.scene.addText("N", font).setPos(x+20, y-5)
        self.scene.addText("S", font).setPos(x+20, y+35)
        self.scene.addText("E", font).setPos(x+40, y+15)
        self.scene.addText("W", font).setPos(x, y+15)
    
    def _add_scale(self, x, y):
        """添加比例尺"""
        # 绘制比例尺线条
        scale_line = self.scene.addLine(x, y, x+100, y, QPen(Qt.black, 2))
        
        # 绘制刻度
        for i in range(5):
            xi = x + i * 25
            self.scene.addLine(xi, y-5, xi, y+5, QPen(Qt.black, 1))
        
        # 添加比例尺文字
        scale_text = self.scene.addText("100米", QFont("", 8))
        scale_text.setPos(x+30, y+10)
    
    def _on_palace_clicked(self, palace_name):
        """处理宫殿点击事件"""
        self.palace_clicked.emit(palace_name)
    
    def wheelEvent(self, event):
        """处理鼠标滚轮事件，用于缩放"""
        # 获取滚轮滚动的角度
        angle_delta = event.angleDelta().y()
        
        # 根据滚动方向进行缩放
        if angle_delta > 0:
            # 放大
            if self.scale_factor < 2.0:
                self.scale_factor *= 1.1
                self.scale(1.1, 1.1)
        else:
            # 缩小
            if self.scale_factor > 0.5:
                self.scale_factor /= 1.1
                self.scale(1/1.1, 1/1.1)
        
        super().wheelEvent(event)
    
    def reset_zoom(self):
        """重置缩放"""
        self.resetTransform()
        self.scale_factor = 1.0
        self.centerOn(self.map_width/2, self.map_height/2)