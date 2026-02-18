#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UI系统基础框架
实现UI系统的核心组件和基础功能
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QFrame, QGraphicsView,
                             QGraphicsScene, QGraphicsPixmapItem)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QRectF
from PyQt5.QtGui import QFont, QPalette, QColor, QPixmap


class UIBaseFrame(QWidget):
    """UI系统基础框架类"""
    
    # 信号定义
    palace_clicked = pyqtSignal(str)  # 宫殿点击信号
    character_clicked = pyqtSignal(str)  # 人物点击信号
    
    def __init__(self, parent=None):
        """初始化UI基础框架"""
        super().__init__(parent)
        
        # 设置基本属性
        self.setMinimumSize(1024, 768)
        
        # UI组件
        self.main_layout = None
        self.top_bar = None
        self.central_area = None
        self.info_panel = None
        self.bottom_bar = None
        
        # 信息标签
        self.year_label = None
        self.season_label = None
        self.gold_label = None
        self.food_label = None
        
        # 初始化UI
        self._init_ui()
        
        # 应用基础样式
        self._apply_base_style()
    
    def _init_ui(self):
        """初始化用户界面"""
        # 创建主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(5)
        
        # 创建顶部状态栏
        self.top_bar = self._create_top_bar()
        self.main_layout.addWidget(self.top_bar)
        
        # 创建中央区域
        central_layout = QHBoxLayout()
        
        # 中央区域将用于放置未央宫地图
        self.central_area = QWidget()
        self.central_area.setMinimumSize(700, 500)
        central_layout.addWidget(self.central_area, 7)  # 占70%宽度
        
        # 右侧信息面板
        self.info_panel = self._create_info_panel()
        central_layout.addWidget(self.info_panel, 3)  # 占30%宽度
        
        self.main_layout.addLayout(central_layout)
        
        # 创建底部控制栏
        self.bottom_bar = self._create_bottom_bar()
        self.main_layout.addWidget(self.bottom_bar)
    
    def _create_top_bar(self):
        """创建顶部状态栏"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        frame.setMaximumHeight(50)
        
        layout = QHBoxLayout(frame)
        
        # 设置字体
        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        
        # 时间信息
        self.year_label = QLabel("年份: 190")
        self.year_label.setFont(font)
        layout.addWidget(self.year_label)
        
        self.season_label = QLabel("季节: 春")
        self.season_label.setFont(font)
        layout.addWidget(self.season_label)
        
        layout.addStretch()
        
        # 资源信息
        self.gold_label = QLabel("金钱: 10000")
        self.gold_label.setFont(font)
        layout.addWidget(self.gold_label)
        
        self.food_label = QLabel("粮食: 50000")
        self.food_label.setFont(font)
        layout.addWidget(self.food_label)
        
        return frame
    
    def _create_info_panel(self):
        """创建右侧信息面板"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        frame.setMinimumWidth(300)
        
        layout = QVBoxLayout(frame)
        
        # 标题
        title = QLabel("信息面板")
        title.setFont(QFont("", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 信息显示区域
        info_area = QLabel("点击宫殿或人物查看详细信息")
        info_area.setAlignment(Qt.AlignTop)
        info_area.setWordWrap(True)
        layout.addWidget(info_area)
        
        return frame
    
    def _create_bottom_bar(self):
        """创建底部控制栏"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        frame.setMaximumHeight(50)
        
        layout = QHBoxLayout(frame)
        
        # 添加按钮
        system_settings_btn = QPushButton("系统设置")
        layout.addWidget(system_settings_btn)
        
        save_game_btn = QPushButton("保存游戏")
        layout.addWidget(save_game_btn)
        
        load_game_btn = QPushButton("加载游戏")
        layout.addWidget(load_game_btn)
        
        layout.addStretch()
        
        help_btn = QPushButton("帮助")
        layout.addWidget(help_btn)
        
        return frame
    
    def _apply_base_style(self):
        """应用基础样式"""
        # 设置基础颜色
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(245, 245, 220))  # 象牙白背景
        palette.setColor(QPalette.WindowText, QColor(26, 26, 26))  # 墨黑文字
        self.setPalette(palette)
        
        # 设置基础样式
        self.setStyleSheet("""
            QFrame {
                background-color: #F5F5DC;
                border: 1px solid #8B4513;
                border-radius: 3px;
            }
            
            QLabel {
                color: #1A1A1A;
                background-color: transparent;
            }
            
            QPushButton {
                background-color: #C73E1E;
                color: white;
                border: 1px solid #8B2500;
                border-radius: 3px;
                padding: 5px;
                min-width: 80px;
            }
            
            QPushButton:hover {
                background-color: #E64A2A;
            }
            
            QPushButton:pressed {
                background-color: #A7320E;
            }
        """)
    
    def update_time_info(self, year, season):
        """更新时间信息"""
        season_names = {1: "春", 2: "夏", 3: "秋", 4: "冬"}
        season_name = season_names.get(season, "春")
        
        self.year_label.setText(f"年份: {year}")
        self.season_label.setText(f"季节: {season_name}")
    
    def update_resource_info(self, gold, food):
        """更新资源信息"""
        self.gold_label.setText(f"金钱: {gold}")
        self.food_label.setText(f"粮食: {food}")
    
    def show_info(self, title, content):
        """在信息面板显示信息"""
        # 找到信息面板中的标签并更新内容
        for i in range(self.info_panel.layout().count()):
            widget = self.info_panel.layout().itemAt(i).widget()
            if isinstance(widget, QLabel) and widget != self.info_panel.layout().itemAt(0).widget():
                widget.setText(f"<b>{title}</b><br>{content}")
                break