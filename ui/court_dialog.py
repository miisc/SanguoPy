#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
朝会对话框
朝会系统的用户界面
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QScrollArea, QWidget, QFrame,
                             QGroupBox, QTextEdit, QButtonGroup, QRadioButton)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap
from game.game_controller import GameController


class CourtMeetingDialog(QDialog):
    """朝会对话框类"""
    
    def __init__(self, game_controller, parent=None):
        """初始化朝会对话框"""
        super().__init__(parent)
        self.game_controller = game_controller
        self.meeting_data = None
        self.selected_option_id = None
        
        # 设置对话框属性
        self.setWindowTitle("朝会")
        self.setModal(True)
        self.resize(900, 700)
        
        # 初始化UI
        self._init_ui()
        
        # 加载朝会数据
        self._load_meeting_data()
    
    def _init_ui(self):
        """初始化用户界面"""
        main_layout = QVBoxLayout(self)
        
        # 创建顶部区域 - 朝会标题和日期
        header_layout = self._create_header()
        main_layout.addLayout(header_layout)
        
        # 创建中央区域 - 议题和意见
        content_layout = QHBoxLayout()
        
        # 左侧 - 议题信息
        topic_layout = self._create_topic_section()
        content_layout.addLayout(topic_layout, 1)
        
        # 右侧 - 朝臣意见
        opinion_layout = self._create_opinion_section()
        content_layout.addLayout(opinion_layout, 1)
        
        main_layout.addLayout(content_layout)
        
        # 创建底部区域 - 决策选项
        decision_layout = self._create_decision_section()
        main_layout.addLayout(decision_layout)
        
        # 创建按钮区域
        button_layout = self._create_button_section()
        main_layout.addLayout(button_layout)
    
    def _create_header(self):
        """创建顶部区域"""
        layout = QHBoxLayout()
        
        # 朝会标题
        title_label = QLabel("朝会")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # 日期信息
        self.date_label = QLabel("190年 春")
        date_font = QFont()
        date_font.setPointSize(12)
        self.date_label.setFont(date_font)
        layout.addWidget(self.date_label)
        
        return layout
    
    def _create_topic_section(self):
        """创建议题区域"""
        layout = QVBoxLayout()
        
        # 议题标题
        self.topic_title_label = QLabel("议题标题")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self.topic_title_label.setFont(title_font)
        layout.addWidget(self.topic_title_label)
        
        # 议题描述
        self.topic_desc_label = QLabel("议题描述")
        self.topic_desc_label.setWordWrap(True)
        layout.addWidget(self.topic_desc_label)
        
        # 议题背景
        topic_bg_group = QGroupBox("背景信息")
        topic_bg_layout = QVBoxLayout(topic_bg_group)
        
        self.topic_bg_text = QTextEdit()
        self.topic_bg_text.setReadOnly(True)
        self.topic_bg_text.setMaximumHeight(120)
        topic_bg_layout.addWidget(self.topic_bg_text)
        
        layout.addWidget(topic_bg_group)
        
        return layout
    
    def _create_opinion_section(self):
        """创建朝臣意见区域"""
        layout = QVBoxLayout()
        
        # 标题
        opinion_title = QLabel("朝臣意见")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        opinion_title.setFont(title_font)
        layout.addWidget(opinion_title)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 朝臣意见容器
        self.opinions_container = QWidget()
        self.opinions_layout = QVBoxLayout(self.opinions_container)
        scroll_area.setWidget(self.opinions_container)
        
        layout.addWidget(scroll_area)
        
        return layout
    
    def _create_decision_section(self):
        """创建决策区域"""
        layout = QVBoxLayout()
        
        # 标题
        decision_title = QLabel("决策选项")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        decision_title.setFont(title_font)
        layout.addWidget(decision_title)
        
        # 选项按钮组
        self.decision_group = QButtonGroup(self)
        self.decision_buttons = []
        
        # 创建选项
        for i in range(3):  # 假设有3个选项
            option_frame = QFrame()
            option_frame.setFrameStyle(QFrame.Box)
            option_layout = QVBoxLayout(option_frame)
            
            # 单选按钮
            radio_btn = QRadioButton(f"选项 {i+1}")
            radio_btn.setProperty("option_index", i)
            self.decision_group.addButton(radio_btn, i)
            self.decision_buttons.append(radio_btn)
            option_layout.addWidget(radio_btn)
            
            # 选项描述
            option_desc = QLabel("选项描述")
            option_desc.setWordWrap(True)
            option_desc.setProperty("option_desc_index", i)
            option_layout.addWidget(option_desc)
            
            layout.addWidget(option_frame)
        
        # 连接按钮组信号
        self.decision_group.buttonClicked.connect(self._on_option_selected)
        
        return layout
    
    def _create_button_section(self):
        """创建按钮区域"""
        layout = QHBoxLayout()
        
        layout.addStretch()
        
        # 确认按钮
        self.confirm_btn = QPushButton("确认决策")
        self.confirm_btn.clicked.connect(self._confirm_decision)
        self.confirm_btn.setEnabled(False)  # 初始禁用
        layout.addWidget(self.confirm_btn)
        
        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)
        
        return layout
    
    def _load_meeting_data(self):
        """加载朝会数据"""
        self.meeting_data = self.game_controller.get_court_meeting_data()
        
        if not self.meeting_data:
            return
        
        # 更新日期
        year = self.meeting_data.get("year", 190)
        season = self.meeting_data.get("season", 1)
        season_names = {1: "春", 2: "夏", 3: "秋", 4: "冬"}
        season_name = season_names.get(season, "春")
        self.date_label.setText(f"{year}年 {season_name}")
        
        # 更新议题信息
        topic = self.meeting_data.get("topic", {})
        self.topic_title_label.setText(topic.get("title", "未知议题"))
        self.topic_desc_label.setText(topic.get("description", ""))
        self.topic_bg_text.setText(topic.get("background", ""))
        
        # 更新朝臣意见
        self._update_opinions()
        
        # 更新决策选项
        self._update_decision_options(topic.get("options", []))
    
    def _update_opinions(self):
        """更新朝臣意见"""
        # 清除现有意见
        for i in reversed(range(self.opinions_layout.count())):
            child = self.opinions_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # 添加新意见
        opinions = self.meeting_data.get("opinions", [])
        for opinion in opinions:
            opinion_frame = QFrame()
            opinion_frame.setFrameStyle(QFrame.Box)
            opinion_layout = QVBoxLayout(opinion_frame)
            
            # 朝臣信息
            participant_name = opinion.get("participant_name", "未知朝臣")
            name_label = QLabel(f"【{participant_name}】")
            name_font = QFont()
            name_font.setBold(True)
            name_label.setFont(name_font)
            opinion_layout.addWidget(name_label)
            
            # 意见内容
            opinion_text = opinion.get("opinion", "")
            opinion_label = QLabel(opinion_text)
            opinion_label.setWordWrap(True)
            opinion_layout.addWidget(opinion_label)
            
            # 支持度
            support_level = opinion.get("support_level", 50)
            support_label = QLabel(f"支持度: {support_level}%")
            opinion_layout.addWidget(support_label)
            
            self.opinions_layout.addWidget(opinion_frame)
        
        # 添加弹性空间
        self.opinions_layout.addStretch()
    
    def _update_decision_options(self, options):
        """更新决策选项"""
        for i, option in enumerate(options):
            if i < len(self.decision_buttons):
                # 更新按钮文本
                self.decision_buttons[i].setText(option.get("title", f"选项 {i+1}"))
                
                # 更新选项描述
                option_desc = None
                for child in self.decision_buttons[i].parent().findChildren(QLabel):
                    if child.property("option_desc_index") == i:
                        option_desc = child
                        break
                
                if option_desc:
                    option_desc.setText(option.get("description", ""))
    
    def _on_option_selected(self, button):
        """选项被选择时的处理"""
        option_index = button.property("option_index")
        self.selected_option_id = self.meeting_data["topic"]["options"][option_index]["id"]
        
        # 启用确认按钮
        self.confirm_btn.setEnabled(True)
    
    def _confirm_decision(self):
        """确认决策"""
        if not self.selected_option_id:
            return
        
        # 执行决策
        result = self.game_controller.make_court_decision(self.selected_option_id)
        
        if result.get("success"):
            # 显示决策结果
            decision = result.get("decision", {})
            resource_changes = result.get("resource_changes", {})
            
            message = f"决策已执行: {decision.get('title', '')}\n\n"
            
            if resource_changes:
                message += "资源变化:\n"
                for resource, change in resource_changes.items():
                    if change > 0:
                        message += f"  {resource}: +{change}\n"
                    else:
                        message += f"  {resource}: {change}\n"
            
            # 显示结果对话框
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "朝会结果", message)
            
            # 关闭对话框
            self.accept()
        else:
            # 显示错误信息
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "错误", result.get("message", "决策执行失败"))