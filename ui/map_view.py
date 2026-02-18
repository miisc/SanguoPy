#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
地图视图
显示游戏地图和相关信息
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsView, QGraphicsScene, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QBrush, QColor, QPainter
from game.game_controller import GameController


class MapView(QWidget):
    """地图视图类"""
    
    def __init__(self, game_controller):
        """初始化地图视图"""
        super().__init__()
        self.game_controller = game_controller
        
        # 创建UI
        self._init_ui()
        
        # 连接信号
        self._connect_signals()
        
        # 初始化地图
        self._init_map()
    
    def _init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        
        # 标题
        title = QLabel("地图视图")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 创建图形视图和场景
        self.graphics_view = QGraphicsView()
        self.graphics_scene = QGraphicsScene()
        self.graphics_view.setScene(self.graphics_scene)
        
        # 设置视图属性
        self.graphics_view.setRenderHint(QPainter.Antialiasing)
        self.graphics_view.setMinimumSize(800, 600)
        
        layout.addWidget(self.graphics_view)
    
    def _connect_signals(self):
        """连接信号和槽"""
        self.game_controller.game_updated.connect(self.update_map)
    
    def _init_map(self):
        """初始化地图"""
        # 设置场景大小
        self.graphics_scene.setSceneRect(0, 0, 800, 600)
        
        # 绘制简单的地图背景
        self.graphics_scene.addRect(0, 0, 800, 600, QPen(Qt.NoPen), QBrush(QColor(240, 240, 200)))
        
        # 添加一些示例城市
        self._draw_cities()
    
    def _draw_cities(self):
        """绘制城市"""
        cities = self.game_controller.get_cities()
        
        if not cities:
            # 如果没有城市数据，添加一些示例城市
            example_cities = [
                {"id": "luoyang", "name": "洛阳", "x": 400, "y": 300, "faction": "wei"},
                {"id": "chengdu", "name": "成都", "x": 200, "y": 400, "faction": "shu"},
                {"id": "jianye", "name": "建业", "x": 600, "y": 400, "faction": "wu"},
                {"id": "chang'an", "name": "长安", "x": 350, "y": 250, "faction": "wei"},
                {"id": "xuchang", "name": "许昌", "x": 450, "y": 320, "faction": "wei"}
            ]
            
            for city in example_cities:
                self._draw_city(city)
        else:
            # 使用实际城市数据
            for city_id, city_data in cities.items():
                self._draw_city(city_data)
    
    def _draw_city(self, city):
        """绘制单个城市"""
        x = city.get("x", 400)
        y = city.get("y", 300)
        name = city.get("name", "未知")
        faction = city.get("faction", "none")
        
        # 根据势力设置颜色
        faction_colors = {
            "wei": QColor(0, 0, 255),      # 蓝色
            "shu": QColor(0, 128, 0),     # 绿色
            "wu": QColor(255, 0, 0),      # 红色
            "none": QColor(128, 128, 128)  # 灰色
        }
        
        color = faction_colors.get(faction, QColor(128, 128, 128))
        
        # 绘制城市圆圈
        circle = self.graphics_scene.addEllipse(x-10, y-10, 20, 20, QPen(Qt.black), QBrush(color))
        
        # 添加城市名称
        text = self.graphics_scene.addText(name)
        text.setPos(x-15, y+15)
    
    def update_map(self):
        """更新地图"""
        # 清除当前地图
        self.graphics_scene.clear()
        
        # 重新绘制地图
        self._init_map()