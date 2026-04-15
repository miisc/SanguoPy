#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
未央宫主窗口
实现基于MVP需求的未央宫全景地图主界面
"""

import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QMenuBar, QMenu,
                             QAction, QMessageBox, QDialog, QFormLayout, QFrame)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QFont
from game.game_controller import GameController
from ui.ui_base_frame import UIBaseFrame
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
            info_layout.addRow(QLabel("功能:"), QLabel("处理紧急朝会，应对突发事件"))
            info_layout.addRow(QLabel("当前状态:"), QLabel("空闲，等待紧急事件"))
            
            # 添加紧急朝会按钮
            emergency_btn = QPushButton("召开紧急朝会")
            emergency_btn.clicked.connect(self._handle_emergency_court)
            info_layout.addRow("", emergency_btn)
            
        elif self.palace_name == "承明殿":
            info_layout.addRow(QLabel("功能:"), QLabel("处理每月初一的大朝会"))
            info_layout.addRow(QLabel("当前状态:"), QLabel("等待下月初一"))
            
            # 添加大朝会按钮（仅在月初可用）
            self.court_btn = QPushButton("召开大朝会")
            self.court_btn.clicked.connect(self._handle_monthly_court)
            self.court_btn.setEnabled(False)  # 默认禁用，非月初不可用
            info_layout.addRow("", self.court_btn)
            
        elif self.palace_name == "椒房殿":
            info_layout.addRow(QLabel("功能:"), QLabel("后宫管理"))
            info_layout.addRow(QLabel("当前状态:"), QLabel("正常运行"))
            
            # 添加后宫管理按钮
            manage_btn = QPushButton("管理后宫")
            manage_btn.clicked.connect(self._manage_harem)
            info_layout.addRow("", manage_btn)
            
        elif self.palace_name == "长乐宫":
            info_layout.addRow(QLabel("功能:"), QLabel("皇室事务"))
            info_layout.addRow(QLabel("当前状态:"), QLabel("正常运行"))
            
            # 添加皇室事务按钮
            manage_btn = QPushButton("处理皇室事务")
            manage_btn.clicked.connect(self._manage_royal_affairs)
            info_layout.addRow("", manage_btn)
        
        layout.addWidget(info_frame)
        
        # 添加关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
    
    def _handle_emergency_court(self):
        """处理紧急朝会"""
        # 通知父窗口开始紧急朝会
        if self.parent() and hasattr(self.parent(), '_start_emergency_court_in_panel'):
            self.parent()._start_emergency_court_in_panel()
        self.close()
    
    def _handle_monthly_court(self):
        """处理每月大朝会"""
        # 通知父窗口开始月度朝会
        if self.parent() and hasattr(self.parent(), '_start_monthly_court_in_panel'):
            self.parent()._start_monthly_court_in_panel()
        self.close()
    
    def _manage_harem(self):
        """管理后宫"""
        QMessageBox.information(self, "后宫管理", "后宫管理功能待实现")
    
    def _manage_royal_affairs(self):
        """处理皇室事务"""
        QMessageBox.information(self, "皇室事务", "皇室事务功能待实现")
    
    def enable_monthly_court(self):
        """启用月度朝会按钮"""
        if hasattr(self, 'court_btn') and self.palace_name == "承明殿":
            self.court_btn.setEnabled(True)


class WeiyangMainWindow(QMainWindow):
    """未央宫主窗口"""
    
    def __init__(self, parent=None):
        """初始化主窗口"""
        super().__init__(parent)
        
        # 游戏控制器
        self.game_controller = GameController()
        
        # 设置窗口属性
        self.setWindowTitle("三国志策略游戏 - 未央宫")
        self.setMinimumSize(800, 600)
        
        # 初始化UI
        self._init_ui()
        
        # 初始化菜单
        self._init_menu()
        
        # 初始化状态栏
        self._init_status_bar()
        
        # 初始化游戏时间
        self._init_game_timer()
        
        # 将 game_controller 注入到 UI 框架，以便 UI 可以访问城池等数据并控制地图
        self.map_frame.game_controller = self.game_controller

        # 连接游戏控制器信号
        self.game_controller.time_advanced.connect(self._on_time_advanced)
        self.game_controller.resources_updated.connect(self._on_resources_updated)
        self.game_controller.game_updated.connect(self._on_game_updated)
        self.game_controller.monthly_court_due.connect(self._on_monthly_court_due)
        self.game_controller.court_meeting_system.meeting_completed.connect(self._on_court_meeting_completed)
        # 监听朝会开始信号以便触发地图聚焦等联动
        try:
            self.game_controller.court_meeting_system.meeting_started.connect(self._on_court_meeting_started)
        except Exception:
            pass
        
        # 连接UI框架信号
        self.map_frame.court_decision.connect(self._on_court_decision)
        self.map_frame.court_meeting_completed.connect(self._on_court_meeting_completed)
        
        # 连接窗口大小改变事件
        self.resizeEvent = self._on_window_resize
        
        # 设置默认速度按钮状态（延后执行以确保UI已初始化）
        QTimer.singleShot(0, self._update_speed_buttons)
    
    def _init_ui(self):
        """初始化用户界面"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 5, 10, 5)  # 减小边距，避免底部按钮被遮挡
        main_layout.setSpacing(0)
        
        # 创建未央宫地图框架
        self.map_frame = UIBaseFrame()
        self.map_frame.palace_clicked.connect(self._on_palace_clicked)
        
        # 设置速度控制按钮的回调函数
        self.map_frame.setup_speed_controls(
            self._pause_game,
            self._set_normal_speed,
            self._set_ultra_speed
        )
        
        main_layout.addWidget(self.map_frame, 1)  # 设置伸缩因子，占据大部分空间
    
    def _init_menu(self):
        """初始化菜单栏"""
        menubar = self.menuBar()
        
        # 游戏菜单
        game_menu = menubar.addMenu("游戏")
        
        # 新游戏
        new_game_action = QAction("新游戏", self)
        new_game_action.triggered.connect(self._new_game)
        game_menu.addAction(new_game_action)
        
        # 保存游戏
        save_action = QAction("保存", self)
        save_action.triggered.connect(self._save_game)
        game_menu.addAction(save_action)
        
        # 加载游戏
        load_action = QAction("加载", self)
        load_action.triggered.connect(self._load_game)
        game_menu.addAction(load_action)
        
        game_menu.addSeparator()
        
        # 退出
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        game_menu.addAction(exit_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        
        # 关于
        about_action = QAction("关于", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _init_status_bar(self):
        """不再使用 QStatusBar（占用窗口高度且会递挡底部按钮），消息直接写入信息面板。"""
        pass

    def _show_status(self, msg: str):
        """将状态消息显示到左侧信息面板的 status_msg_label。"""
        try:
            if hasattr(self, 'map_frame') and hasattr(self.map_frame, 'status_msg_label'):
                self.map_frame.status_msg_label.setText(msg)
        except Exception:
            pass
    
    def _init_game_timer(self):
        """初始化游戏定时器"""
        # 游戏速度设置（毫秒）
        self.game_speeds = {
            "pause": 0,      # 暂停
            "normal": 500,   
            "fast": 250,     # 加速：(x2速度)
            "fastest": 100,  # 最快：(x5速度)
            "ultra": 50      # 超级快：(x10速度)
        }
        
        # 当前游戏速度
        self.current_speed = "normal"
        
        # 创建游戏定时器
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self._update_game_time)
        self.game_timer.start(self.game_speeds[self.current_speed])
    
    def _on_palace_clicked(self, palace_name):
        """处理宫殿点击事件"""
        # 如果是承明殿，直接在信息面板显示大朝会
        if palace_name == "承明殿":
            # 暂停游戏时间
            self._pause_game()
            # 开始月度朝会
            self._start_monthly_court_in_panel()
            return
        # 如果是宣室殿，直接在信息面板显示紧急朝会
        elif palace_name == "宣室殿":
            # 暂停游戏时间
            self._pause_game()
            # 开始紧急朝会
            self._start_emergency_court_in_panel()
            return
        
        # 否则打开宫殿对话框
        palace_dialog = PalaceDialog(palace_name, self.game_controller, self)
        palace_dialog.exec_()
    
    def _on_monthly_court_due(self, game_info):
        """处理月度朝会到期"""
        # 直接开始月度朝会，不弹出提示框
        self._start_monthly_court_in_panel()
    
    def _start_monthly_court_in_panel(self):
        """在信息面板中开始月度朝会"""
        # 暂停游戏时间
        self._pause_game()
        
        # 获取月度朝会数据
        meeting_data = self.game_controller.get_monthly_court_data()
        if meeting_data:
            # 在信息面板显示朝会
            self.map_frame.show_court_meeting(meeting_data)
            # 若会议包含相关位置，确保地图聚焦（map_frame 会处理）
            # 更新状态消息
            self._show_status("月度朝会开始")
    
    def _start_emergency_court_in_panel(self):
        """在信息面板中开始紧急朝会"""
        # 暂停游戏时间
        self._pause_game()
        
        # 获取紧急朝会数据
        meeting_data = self.game_controller.get_emergency_court_data()
        if meeting_data:
            # 在信息面板显示朝会
            self.map_frame.show_court_meeting(meeting_data)
            # 若会议包含相关位置，确保地图聚焦（map_frame 会处理）
            # 更新状态消息
            self._show_status("紧急朝会开始")

    def _on_court_meeting_started(self, meeting_data):
        """当朝会开始时的处理（用于地图联动等）"""
        # 将meeting_data传给frame以便其聚焦地图（如果包含相关位置信息）
        try:
            if hasattr(self, 'map_frame') and self.map_frame:
                # 如果面板正在显示朝会，则直接使用现有方法
                self.map_frame.show_court_meeting(meeting_data)
        except Exception:
            pass
    
    def _on_court_decision(self, option_id):
        """处理朝会决策"""
        # 验证选项ID
        if option_id is None:
            QMessageBox.warning(self, "决策错误", "无效的决策选项")
            return
        
        # 优先查询当前活动中的朝会（可能是单议题/多议题/紧急），以决定调用哪个决策方法
        meeting = self.game_controller.get_court_meeting_data()
        if not meeting:
            # 如果没有活动中的朝会，尝试获取月度或紧急朝会数据（会在内部创建）
            meeting = self.game_controller.get_monthly_court_data() or self.game_controller.get_emergency_court_data()

        # 根据会议结构选择合适的决策接口：多议题 -> 月度，多数紧急/单议题 -> 对应接口
        if meeting and "topics" in meeting:
            result = self.game_controller.make_monthly_decision(option_id)
        elif meeting and meeting.get("type") == "emergency":
            result = self.game_controller.make_emergency_decision(option_id)
        else:
            result = self.game_controller.make_court_decision(option_id)
        
        if result.get("success", False):
            # 更新状态消息
            decision_message = result.get('message', '决策已执行')
            self._show_status(f"已做出决策: {decision_message}")
            
            # 检查是否还有更多议题
            if result.get("has_more_topics", False):
                # 必须使用 get_monthly/emergency_court_data，它们会将当前 topic 填入 meeting_data["topic"]
                # get_court_meeting_data() 仅返回原始 dict，不包含当前议题字段
                if meeting and meeting.get("type") == "emergency":
                    update_data = self.game_controller.get_emergency_court_data()
                else:
                    update_data = self.game_controller.get_monthly_court_data()
                if update_data:
                    self.map_frame.update_court_meeting(update_data)
            else:
                # 朝会完成
                self.map_frame.show_court_meeting_complete()
                self._show_status("朝会完成")
                
                # 更新游戏状态显示
                game_info = self.game_controller.get_game_info()
                self._on_time_advanced(game_info)
        else:
            # 决策失败
            error_message = result.get("message", "未知错误")
            QMessageBox.warning(self, "决策失败", error_message)
            self._show_status(f"决策失败: {error_message}")
    
    def _update_game_time(self):
        """更新游戏时间"""
        # 通知游戏控制器推进时间
        self.game_controller.advance_time()
        
        # 获取更新后的游戏信息
        game_info = self.game_controller.get_game_info()
        current_year = game_info["year"]
        current_month = game_info["month"]
        current_day = game_info["day"]
        
        # 更新UI框架中的时间信息
        self.map_frame.update_time_info(current_year, current_month, current_day)
    
    def _new_game(self):
        """开始新游戏"""
        reply = QMessageBox.question(self, "新游戏", "确定要开始新游戏吗？当前进度将丢失。",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            # 重置游戏状态
            self.game_controller.reset_game()
            self._show_status("新游戏已开始")
    
    def _save_game(self):
        """保存游戏"""
        # 这里应该实现保存游戏逻辑
        QMessageBox.information(self, "保存游戏", "游戏保存功能待实现")
    
    def _load_game(self):
        """加载游戏"""
        # 这里应该实现加载游戏逻辑
        QMessageBox.information(self, "加载游戏", "游戏加载功能待实现")
    
    def _pause_game(self):
        """暂停游戏"""
        self.current_speed = "pause"
        self.game_timer.stop()
        self._show_status("游戏已暂停")
        self._update_speed_buttons()
    
    def _set_normal_speed(self):
        """设置正常速度"""
        self.current_speed = "normal"
        self.game_timer.start(self.game_speeds[self.current_speed])
        self._show_status("游戏速度：正常")
        self._update_speed_buttons()
    
    def _set_fast_speed(self):
        """设置加速"""
        self.current_speed = "fast"
        self.game_timer.start(self.game_speeds[self.current_speed])
        self._show_status("游戏速度：加速")
        self._update_speed_buttons()
    
    def _set_fastest_speed(self):
        """设置最快速度"""
        self.current_speed = "fastest"
        self.game_timer.start(self.game_speeds[self.current_speed])
        self._show_status("游戏速度：最快")
        self._update_speed_buttons()
    
    def _set_ultra_speed(self):
        """设置超快速度"""
        self.current_speed = "ultra"
        self.game_timer.start(self.game_speeds[self.current_speed])
        self._show_status("游戏速度：快速x3")
        self._update_speed_buttons()
    
    def _update_speed_buttons(self):
        """更新速度按钮状态"""
        # 通过UI框架更新速度按钮状态
        if hasattr(self, 'map_frame'):
            self.map_frame.update_speed_buttons(self.current_speed)
    
    def _show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, "关于", "三国志策略游戏\n版本 1.0.0\n\n一个基于PyQt5的三国志题材策略游戏")
    
    def _on_window_resize(self, event):
        """处理窗口大小改变事件"""
        # 获取新的窗口大小
        new_size = event.size()
        width = new_size.width()
        height = new_size.height()
        
        # 调整UI组件大小
        self._adjust_ui_layout(width, height)
        
        # 调用父类的resizeEvent
        super().resizeEvent(event)
    
    def _adjust_ui_layout(self, width, height):
        """根据窗口大小调整UI布局"""
        # 仅调整字体
        if width < 1000:
            font_size = 10
        elif width < 1200:
            font_size = 11
        elif width < 1400:
            font_size = 12
        else:
            font_size = 13
        self.setFont(QFont("", font_size))
    
    def _adjust_palace_buttons(self, width, height):
        pass  # 按钮统一使用 setFixedSize，不再动态变更
    
    def _adjust_info_panel(self, width, height):
        """调整信息面板大小"""
        # 根据窗口大小调整信息面板字体
        if width < 1000:
            font_size = 9
        elif width < 1200:
            font_size = 10
        elif width < 1400:
            font_size = 11
        else:
            font_size = 12
        
        # 设置信息面板字体
        info_font = QFont("", font_size)
        
        # 应用到信息面板中的标签
        if hasattr(self, 'time_label'):
            self.time_label.setFont(info_font)
        if hasattr(self, 'faction_label'):
            self.faction_label.setFont(info_font)
    
    def _on_time_advanced(self, game_info):
        """处理时间推进"""
        # 更新UI框架中的时间信息
        year = game_info.get("year", 190)
        month = game_info.get("month", 1)
        day = game_info.get("day", 1)
        self.map_frame.update_time_info(year, month, day)
    
    def _on_resources_updated(self, resources):
        """处理资源更新"""
        gold = resources.get("gold", 0)
        food = resources.get("food", 0)
        court_res = self.game_controller.game_model.get_court_resources()
        intel = court_res.get("intel_points", 0)
        self.map_frame.update_resource_info(gold, food, intel)
    
    def _on_game_updated(self):
        """处理游戏状态更新"""
        # 可以在这里添加游戏状态更新的UI响应
        pass
    
    def _on_court_meeting_completed(self, meeting_result=None):
        """处理朝会完成"""
        # 更新UI状态，显示朝会结果
        if meeting_result:
            self._show_status(f"朝会完成: {meeting_result.get('topic', {}).get('title', '未知议题')}")
        else:
            self._show_status("朝会完成")
        
        # 恢复游戏时间
        self._set_normal_speed()