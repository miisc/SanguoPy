#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
新主窗口
实现以未央宫全景地图为核心的主界面
"""

import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QStatusBar, QMenuBar, QMenu,
                             QAction, QMessageBox, QDialog, QFormLayout, QLineEdit, QTextEdit, QFrame)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QFont
from game.game_controller import GameController
from ui.ui_base_frame import UIBaseFrame
from ui.weiyang_palace_map import WeiyangPalaceMap
from ui.court_dialog import CourtMeetingDialog


class PalaceDialog(QDialog):
    """宫殿交互对话框"""
    
    def __init__(self, palace_name, game_controller, parent=None):
        """初始化宫殿对话框"""
        super().__init__(parent)
        
        # 对话框属性
        self.palace_name = palace_name
        self.game_controller = game_controller
        
        # 设置对话框属性
        self.setWindowTitle(f"{palace_name} - 宫殿事务")
        self.setMinimumSize(600, 400)
        
        # 初始化UI
        self._init_ui()
    
    def _init_ui(self):
        """初始化用户界面"""
        # 创建主布局
        layout = QVBoxLayout(self)
        
        # 创建标题
        title = QLabel(f"{self.palace_name}")
        title.setFont(QFont("", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 创建宫殿信息
        info_frame = QFrame()
        info_frame.setFrameStyle(QFrame.Box)
        info_layout = QFormLayout(info_frame)
        
        # 根据宫殿名称添加不同的信息
        if self.palace_name == "宣室殿":
            info_layout.addRow(QLabel("功能:"), QLabel("处理政务、朝会的主要场所"))
            info_layout.addRow(QLabel("当前状态:"), QLabel("空闲"))
            info_layout.addRow(QLabel("可用人员:"), QLabel("5名大臣"))
            
            # 添加朝会按钮
            hold_court_btn = QPushButton("召开朝会")
            hold_court_btn.clicked.connect(self._hold_court_meeting)
            info_layout.addRow("", hold_court_btn)
            
        elif self.palace_name == "承明殿":
            info_layout.addRow(QLabel("功能:"), QLabel("接见大臣、处理外交事务"))
            info_layout.addRow(QLabel("当前状态:"), QLabel("空闲"))
            info_layout.addRow(QLabel("外交关系:"), QLabel("魏国: 中立, 蜀国: 友好, 吴国: 敌对"))
            
        elif self.palace_name == "椒房殿":
            info_layout.addRow(QLabel("功能:"), QLabel("皇后居所，处理后宫事务"))
            info_layout.addRow(QLabel("当前状态:"), QLabel("皇后正在休息"))
            info_layout.addRow(QLabel("后宫人员:"), QLabel("皇后、妃嫔、宫女共50人"))
            
        else:
            # 其他宫殿的通用信息
            info_layout.addRow(QLabel("功能:"), QLabel("宫殿功能"))
            info_layout.addRow(QLabel("当前状态:"), QLabel("空闲"))
            info_layout.addRow(QLabel("人员数量:"), QLabel("10人"))
        
        layout.addWidget(info_frame)
        
        # 创建人物列表
        people_frame = QFrame()
        people_frame.setFrameStyle(QFrame.Box)
        people_layout = QVBoxLayout(people_frame)
        
        people_title = QLabel("宫殿内人物")
        people_title.setFont(QFont("", 12, QFont.Bold))
        people_layout.addWidget(people_title)
        
        # 添加示例人物
        people_list = QLabel("张三 - 大臣\n李四 - 将军\n王五 - 文官")
        people_list.setWordWrap(True)
        people_layout.addWidget(people_list)
        
        layout.addWidget(people_frame)
        
        # 创建按钮区域
        button_layout = QHBoxLayout()
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def _hold_court_meeting(self):
        """召开朝会"""
        # 检查是否可以召开朝会
        if not self.game_controller.court_meeting_system.can_hold_meeting():
            QMessageBox.information(self, "朝会", "当前不能召开朝会")
            return
        
        # 开始朝会
        meeting_data = self.game_controller.start_court_meeting()
        if meeting_data["success"]:
            # 创建朝会对话框
            court_dialog = CourtMeetingDialog(self.game_controller, self)
            court_dialog.show()
            self.accept()  # 关闭宫殿对话框
        else:
            QMessageBox.warning(self, "朝会", meeting_data["message"])


class NewMainWindow(QMainWindow):
    """新主窗口类，实现以未央宫为核心的主界面"""
    
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        
        # 设置窗口属性
        self.setWindowTitle("三国志策略游戏 - 未央宫")
        self.setGeometry(100, 100, 1200, 800)
        
        # 游戏控制器
        self.game_controller = GameController()
        
        # UI组件
        self.ui_base_frame = None
        self.palace_map = None
        self.status_bar = None
        self.menu_bar = None
        self.palace_dialog = None
        
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
        
        # 创建UI基础框架
        self.ui_base_frame = UIBaseFrame(self)
        self.setCentralWidget(self.ui_base_frame)
        
        # 创建未央宫地图
        self.palace_map = WeiyangPalaceMap(self.ui_base_frame.central_area)
        palace_layout = QVBoxLayout(self.ui_base_frame.central_area)
        palace_layout.addWidget(self.palace_map)
        
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
        
        # 视图菜单
        view_menu = self.menu_bar.addMenu("视图")
        
        toggle_map_action = QAction("显示地图", self)
        toggle_map_action.setCheckable(True)
        toggle_map_action.setChecked(True)
        toggle_map_action.triggered.connect(self._toggle_map)
        view_menu.addAction(toggle_map_action)
        
        # 帮助菜单
        help_menu = self.menu_bar.addMenu("帮助")
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _connect_signals(self):
        """连接信号和槽"""
        # 游戏控制器信号
        self.game_controller.game_updated.connect(self._update_ui)
        self.game_controller.resources_updated.connect(self._update_resources)
        self.game_controller.time_advanced.connect(self._update_time)
        
        # UI基础框架信号
        self.ui_base_frame.palace_clicked.connect(self._on_palace_clicked)
        
        # 地图信号
        self.palace_map.palace_clicked.connect(self._on_palace_clicked)
    
    def _update_ui(self):
        """更新界面"""
        self._update_time(self.game_controller.get_game_info())
        self._update_resources(self.game_controller.get_resources())
    
    def _update_time(self, game_info):
        """更新时间信息"""
        year = game_info.get("year", 190)
        season = game_info.get("season", 1)
        
        # 更新UI基础框架的时间信息
        self.ui_base_frame.update_time_info(year, season)
    
    def _update_resources(self, resources):
        """更新资源信息"""
        gold = resources.get("gold", 0)
        food = resources.get("food", 0)
        
        # 更新UI基础框架的资源信息
        self.ui_base_frame.update_resource_info(gold, food)
    
    def _on_palace_clicked(self, palace_name):
        """处理宫殿点击事件"""
        # 在信息面板显示宫殿信息
        palace_info = self._get_palace_info(palace_name)
        self.ui_base_frame.show_info(palace_name, palace_info)
        
        # 显示宫殿对话框
        self.palace_dialog = PalaceDialog(palace_name, self.game_controller, self)
        self.palace_dialog.show()
        
        self.status_bar.showMessage(f"进入{palace_name}")
    
    def _get_palace_info(self, palace_name):
        """获取宫殿信息"""
        palace_info_map = {
            "宣室殿": "处理政务、朝会的主要场所。当前有5名大臣在此等候。",
            "承明殿": "接见大臣、处理外交事务的场所。当前有3名使臣等候接见。",
            "麒麟阁": "表彰功臣、展示功绩的场所。当前展示着10位功臣的事迹。",
            "金銮殿": "举行重大典礼的场所。当前空闲，可用于举行典礼。",
            "尚书台": "处理文书、诏令的场所。当前有15份文书待处理。",
            "太官署": "管理宫廷饮食的场所。今日已准备宫廷宴席。",
            "椒房殿": "皇后居所，处理后宫事务。皇后正在处理后宫事务。",
            "长秋宫": "太后居所。太后正在休息。",
            "增成宫": "妃嫔居所。当前有8位妃嫔在此。",
            "永巷": "宫女居所。当前有30名宫女在此。",
            "掖庭": "宫中服务人员居所。当前有20名服务人员在此。"
        }
        
        return palace_info_map.get(palace_name, "宫殿信息暂未更新。")
    
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
    
    def _toggle_map(self, checked):
        """切换地图显示"""
        if checked:
            self.palace_map.show()
        else:
            self.palace_map.hide()
    
    def _show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, "关于", "三国志策略游戏 v1.0\n\n一个基于PyQt的三国策略游戏。")