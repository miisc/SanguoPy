#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
未央宫地图视图
实现未央宫全景2D平面地图的显示和交互
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QScrollArea, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QRect
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush, QPixmap


class PalaceWidget(QFrame):
    """宫殿组件类"""
    
    # 信号定义
    clicked = pyqtSignal(str)  # 点击信号
    
    def __init__(self, name, display_name, palace_type, x, y, width, height, parent=None):
        """初始化宫殿组件"""
        super().__init__(parent)
        
        # 宫殿属性
        self.name = name
        self.display_name = display_name
        self.palace_type = palace_type  # 'front' 或 'back'
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # 设置组件属性
        self.move(x, y)
        self.setFixedSize(width, height)
        self.setFrameStyle(QFrame.Box)
        self.setCursor(Qt.PointingHandCursor)
        
        # 设置样式
        self._set_style()
    
    def _set_style(self):
        """设置宫殿样式"""
        if self.palace_type == 'front':
            # 前朝宫殿使用暖色调
            self.setStyleSheet("""
                QFrame {
                    background-color: rgba(199, 62, 30, 150);
                    border: 2px solid #8B2500;
                    border-radius: 5px;
                }
            """)
        else:
            # 后宫宫殿使用柔和色调
            self.setStyleSheet("""
                QFrame {
                    background-color: rgba(212, 175, 55, 150);
                    border: 2px solid #8B6914;
                    border-radius: 5px;
                }
            """)
    
    def paintEvent(self, event):
        """绘制宫殿"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制宫殿名称
        painter.setPen(QPen(Qt.white, 1))
        painter.setFont(QFont("", 10, QFont.Bold))
        painter.drawText(self.rect(), Qt.AlignCenter, self.display_name)
        
        super().paintEvent(event)
    
    def mousePressEvent(self, event):
        """处理鼠标点击事件"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.name)
        super().mousePressEvent(event)


class WeiyangPalaceMap(QWidget):
    """未央宫地图视图类"""
    
    # 信号定义
    palace_clicked = pyqtSignal(str)  # 宫殿点击信号
    
    def __init__(self, parent=None):
        """初始化未央宫地图视图"""
        super().__init__(parent)
        
        # 地图属性
        self.map_width = 800
        self.map_height = 600
        self.scale_factor = 1.0
        
        # 宫殿字典
        self.palaces = {}
        
        # 初始化UI
        self._init_ui()
        
        # 创建宫殿
        self._create_palaces()
    
    def _init_ui(self):
        """初始化用户界面"""
        # 设置基本属性
        self.setMinimumSize(700, 500)
        self.setStyleSheet("background-color: #F5F5DC;")
        
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # 创建地图容器
        self.map_container = QWidget()
        self.map_container.setFixedSize(self.map_width, self.map_height)
        
        # 创建地图布局
        self.map_layout = QVBoxLayout(self.map_container)
        
        # 添加地图标题
        title = QLabel("东汉未央宫平面图")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("", 16, QFont.Bold))
        self.map_layout.addWidget(title)
        
        # 创建宫殿区域
        self.palace_area = QWidget(self.map_container)
        self.palace_area.setGeometry(50, 50, self.map_width - 100, self.map_height - 100)
        
        # 添加到滚动区域
        scroll_area.setWidget(self.map_container)
        layout.addWidget(scroll_area)
        
        # 创建缩放控制
        zoom_layout = QHBoxLayout()
        
        zoom_in_btn = QPushButton("放大")
        zoom_in_btn.clicked.connect(self._zoom_in)
        zoom_layout.addWidget(zoom_in_btn)
        
        zoom_out_btn = QPushButton("缩小")
        zoom_out_btn.clicked.connect(self._zoom_out)
        zoom_layout.addWidget(zoom_out_btn)
        
        reset_btn = QPushButton("重置")
        reset_btn.clicked.connect(self._reset_zoom)
        zoom_layout.addWidget(reset_btn)
        
        zoom_layout.addStretch()
        
        layout.addLayout(zoom_layout)
    
    def _create_palaces(self):
        """创建宫殿"""
        # 前朝宫殿
        self._add_palace("宣室殿", "宣室殿", "front", 100, 100, 120, 80)
        self._add_palace("承明殿", "承明殿", "front", 250, 100, 120, 80)
        self._add_palace("麒麟阁", "麒麟阁", "front", 400, 100, 120, 80)
        self._add_palace("金銮殿", "金銮殿", "front", 550, 100, 120, 80)
        self._add_palace("尚书台", "尚书台", "front", 100, 220, 120, 80)
        self._add_palace("太官署", "太官署", "front", 250, 220, 120, 80)
        
        # 后宫宫殿
        self._add_palace("椒房殿", "椒房殿", "back", 400, 220, 120, 80)
        self._add_palace("长秋宫", "长秋宫", "back", 550, 220, 120, 80)
        self._add_palace("增成宫", "增成宫", "back", 100, 340, 120, 80)
        self._add_palace("永巷", "永巷", "back", 250, 340, 120, 80)
        self._add_palace("掖庭", "掖庭", "back", 400, 340, 120, 80)
    
    def _add_palace(self, name, display_name, palace_type, x, y, width, height):
        """添加宫殿"""
        palace = PalaceWidget(name, display_name, palace_type, x, y, width, height, self.palace_area)
        palace.clicked.connect(self._on_palace_clicked)
        self.palaces[name] = palace
    
    def _on_palace_clicked(self, palace_name):
        """处理宫殿点击事件"""
        self.palace_clicked.emit(palace_name)
    
    def _zoom_in(self):
        """放大地图"""
        if self.scale_factor < 2.0:
            self.scale_factor += 0.1
            self._update_scale()
    
    def _zoom_out(self):
        """缩小地图"""
        if self.scale_factor > 0.5:
            self.scale_factor -= 0.1
            self._update_scale()
    
    def _reset_zoom(self):
        """重置缩放"""
        self.scale_factor = 1.0
        self._update_scale()
    
    def _update_scale(self):
        """更新缩放"""
        # 更新地图容器大小
        new_width = int(self.map_width * self.scale_factor)
        new_height = int(self.map_height * self.scale_factor)
        self.map_container.setFixedSize(new_width, new_height)
        
        # 更新宫殿区域大小
        palace_area_width = int((self.map_width - 100) * self.scale_factor)
        palace_area_height = int((self.map_height - 100) * self.scale_factor)
        self.palace_area.setGeometry(50, 50, palace_area_width, palace_area_height)
        
        # 更新宫殿位置和大小
        for palace in self.palaces.values():
            new_x = int(palace.x * self.scale_factor)
            new_y = int(palace.y * self.scale_factor)
            new_width = int(palace.width * self.scale_factor)
            new_height = int(palace.height * self.scale_factor)
            
            palace.move(new_x, new_y)
            palace.setFixedSize(new_width, new_height)
    
    def paintEvent(self, event):
        """绘制地图背景"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制背景
        painter.fillRect(self.rect(), QColor(245, 245, 220))  # 象牙白背景
        
        # 如果有缩放，绘制缩放比例
        if self.scale_factor != 1.0:
            painter.setPen(QPen(Qt.black, 1))
            painter.setFont(QFont("", 10))
            painter.drawText(10, 20, f"缩放: {int(self.scale_factor * 100)}%")
        
        super().paintEvent(event)