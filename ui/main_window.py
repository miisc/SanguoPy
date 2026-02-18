#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
主窗口
游戏的主界面
"""

import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QStatusBar, QMenuBar, QMenu,
                             QAction, QMessageBox, QTabWidget)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QFont
from game.game_controller import GameController
from ui.map_view import MapView
from ui.court_dialog import CourtMeetingDialog


class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        
        # 设置窗口属性
        self.setWindowTitle("三国志策略游戏")
        self.setGeometry(100, 100, 1200, 800)
        
        # 游戏控制器
        self.game_controller = GameController()
        
        # UI组件
        self.central_widget = None
        self.status_bar = None
        self.menu_bar = None
        self.map_view = None
        self.court_dialog = None
        
        # 信息标签
        self.year_label = None
        self.season_label = None
        self.gold_label = None
        self.food_label = None
        self.population_label = None
        self.soldiers_label = None
        
        # 初始化UI
        self._init_ui()
        
        # 连接信号
        self._connect_signals()
        
        # 开始新游戏
        self.game_controller.start_new_game()
        
        # 设置定时器，定期更新界面
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_ui)
        self.update_timer.start(1000)  # 每秒更新一次
    
    def _init_ui(self):
        """初始化用户界面"""
        # 创建菜单栏
        self._create_menu_bar()
        
        # 创建中央部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(self.central_widget)
        
        # 创建顶部信息栏
        info_layout = self._create_info_bar()
        main_layout.addLayout(info_layout)
        
        # 创建标签页
        tab_widget = QTabWidget()
        
        # 地图标签页
        self.map_view = MapView(self.game_controller)
        tab_widget.addTab(self.map_view, "地图")
        
        # 朝会标签页
        court_tab = QWidget()
        court_layout = QVBoxLayout(court_tab)
        court_layout.addWidget(QLabel("点击下方'召开朝会'按钮进入朝会"))
        tab_widget.addTab(court_tab, "朝会")
        
        main_layout.addWidget(tab_widget)
        
        # 创建底部控制栏
        control_layout = self._create_control_bar()
        main_layout.addLayout(control_layout)
        
        # 创建状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("准备就绪")
    
    def _create_menu_bar(self):
        """创建菜单栏"""
        self.menu_bar = self.menuBar()
        
        # 游戏菜单
        game_menu = self.menu_bar.addMenu("游戏")
        
        new_game_action = QAction("新游戏", self)
        new_game_action.triggered.connect(self._new_game)
        game_menu.addAction(new_game_action)
        
        save_game_action = QAction("保存游戏", self)
        save_game_action.triggered.connect(self._save_game)
        game_menu.addAction(save_game_action)
        
        load_game_action = QAction("加载游戏", self)
        load_game_action.triggered.connect(self._load_game)
        game_menu.addAction(load_game_action)
        
        game_menu.addSeparator()
        
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        game_menu.addAction(exit_action)
        
        # 帮助菜单
        help_menu = self.menu_bar.addMenu("帮助")
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _create_info_bar(self):
        """创建顶部信息栏"""
        layout = QHBoxLayout()
        
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
        
        self.population_label = QLabel("人口: 100000")
        self.population_label.setFont(font)
        layout.addWidget(self.population_label)
        
        self.soldiers_label = QLabel("士兵: 5000")
        self.soldiers_label.setFont(font)
        layout.addWidget(self.soldiers_label)
        
        return layout
    
    def _create_control_bar(self):
        """创建底部控制栏"""
        layout = QHBoxLayout()
        
        # 添加按钮
        advance_time_btn = QPushButton("下一回合")
        advance_time_btn.clicked.connect(self._advance_time)
        layout.addWidget(advance_time_btn)
        
        court_meeting_btn = QPushButton("召开朝会")
        court_meeting_btn.clicked.connect(self._open_court_meeting)
        layout.addWidget(court_meeting_btn)
        
        layout.addStretch()
        
        return layout
    
    def _connect_signals(self):
        """连接信号和槽"""
        # 游戏控制器信号
        self.game_controller.game_updated.connect(self._update_ui)
        self.game_controller.resources_updated.connect(self._update_resources)
        self.game_controller.time_advanced.connect(self._update_time)
    
    def _update_ui(self):
        """更新界面"""
        self._update_time(self.game_controller.get_game_info())
        self._update_resources(self.game_controller.get_resources())
    
    def _update_time(self, game_info):
        """更新时间信息"""
        year = game_info.get("year", 190)
        season = game_info.get("season", 1)
        
        season_names = {1: "春", 2: "夏", 3: "秋", 4: "冬"}
        season_name = season_names.get(season, "春")
        
        self.year_label.setText(f"年份: {year}")
        self.season_label.setText(f"季节: {season_name}")
    
    def _update_resources(self, resources):
        """更新资源信息"""
        gold = resources.get("gold", 0)
        food = resources.get("food", 0)
        population = resources.get("population", 0)
        soldiers = resources.get("soldiers", 0)
        
        self.gold_label.setText(f"金钱: {gold}")
        self.food_label.setText(f"粮食: {food}")
        self.population_label.setText(f"人口: {population}")
        self.soldiers_label.setText(f"士兵: {soldiers}")
    
    def _new_game(self):
        """开始新游戏"""
        reply = QMessageBox.question(self, "新游戏", "确定要开始新游戏吗？当前进度将丢失。",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.game_controller.start_new_game()
            self.status_bar.showMessage("新游戏已开始")
    
    def _save_game(self):
        """保存游戏"""
        # 简化实现，实际应该弹出文件对话框
        save_file = "savegame.json"
        self.game_controller.save_game(save_file)
        self.status_bar.showMessage(f"游戏已保存到 {save_file}")
    
    def _load_game(self):
        """加载游戏"""
        # 简化实现，实际应该弹出文件对话框
        save_file = "savegame.json"
        if os.path.exists(save_file):
            self.game_controller.load_game(save_file)
            self.status_bar.showMessage(f"游戏已从 {save_file} 加载")
        else:
            self.status_bar.showMessage("存档文件不存在")
    
    def _advance_time(self):
        """推进时间"""
        self.game_controller.advance_time()
        self.status_bar.showMessage("时间已推进")
    
    def _open_court_meeting(self):
        """打开朝会对话框"""
        # 检查是否可以召开朝会
        if not self.game_controller.court_meeting_system.can_hold_meeting():
            QMessageBox.information(self, "朝会", "当前不能召开朝会")
            return
        
        # 开始朝会
        meeting_data = self.game_controller.start_court_meeting()
        if meeting_data["success"]:
            # 创建朝会对话框
            self.court_dialog = CourtMeetingDialog(self.game_controller, self)
            self.court_dialog.show()
            self.status_bar.showMessage("朝会已开始")
        else:
            QMessageBox.warning(self, "朝会", meeting_data["message"])
    
    def _show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, "关于", "三国志策略游戏 v1.0\n\n一个基于PyQt的三国策略游戏。")