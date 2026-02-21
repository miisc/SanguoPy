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
    
    def __init__(self, game_controller, parent=None, meeting_type="monthly"):
        """初始化朝会对话框
        
        Args:
            game_controller: 游戏控制器
            parent: 父窗口
            meeting_type: 朝会类型，"monthly"为月度朝会，"emergency"为紧急朝会
        """
        super().__init__(parent)
        self.game_controller = game_controller
        self.meeting_type = meeting_type
        self.meeting_data = None
        self.selected_option_id = None
        
        # 设置对话框属性
        if meeting_type == "emergency":
            self.setWindowTitle("紧急朝会")
        else:
            self.setWindowTitle("月度朝会")
        self.setModal(True)
        self.setMinimumSize(800, 600)
        self.resize(900, 700)
        
        # 初始化UI
        self._init_ui()
        
        # 加载朝会数据
        self._load_meeting_data()
        
        # 连接窗口大小改变事件
        self.resizeEvent = self._on_window_resize
    
    def _init_ui(self):
        """初始化用户界面"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)  # 添加边距
        main_layout.setSpacing(10)  # 添加间距
        
        # 创建顶部区域 - 朝会标题和日期
        header_layout = self._create_header()
        main_layout.addLayout(header_layout)
        
        # 创建中央区域 - 议题和意见
        content_layout = QHBoxLayout()
        content_layout.setSpacing(10)  # 添加间距
        
        # 左侧 - 议题信息
        topic_layout = self._create_topic_section()
        content_layout.addLayout(topic_layout, 1)
        
        # 右侧 - 朝臣意见
        opinion_layout = self._create_opinion_section()
        content_layout.addLayout(opinion_layout, 1)
        
        main_layout.addLayout(content_layout, 1)  # 设置伸缩因子，占据大部分空间
        
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
        if self.meeting_type == "emergency":
            title_label = QLabel("紧急朝会")
        else:
            title_label = QLabel("月度朝会")
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
        layout.setSpacing(5)  # 添加间距
        
        # 议题标题
        self.topic_title_label = QLabel("议题标题")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self.topic_title_label.setFont(title_font)
        self.topic_title_label.setWordWrap(True)  # 允许文本换行
        layout.addWidget(self.topic_title_label)
        
        # 议题描述
        self.topic_desc_label = QLabel("议题描述")
        self.topic_desc_label.setWordWrap(True)
        self.topic_desc_label.setMinimumHeight(50)  # 设置最小高度
        layout.addWidget(self.topic_desc_label, 1)  # 设置伸缩因子
        
        # 议题背景
        topic_bg_group = QGroupBox("背景信息")
        topic_bg_layout = QVBoxLayout(topic_bg_group)
        
        self.topic_bg_text = QTextEdit()
        self.topic_bg_text.setReadOnly(True)
        self.topic_bg_text.setMinimumHeight(80)  # 设置最小高度而不是最大高度
        topic_bg_layout.addWidget(self.topic_bg_text)
        
        layout.addWidget(topic_bg_group)
        
        return layout
    
    def _create_opinion_section(self):
        """创建朝臣意见区域"""
        layout = QVBoxLayout()
        layout.setSpacing(5)  # 添加间距
        
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
        scroll_area.setMinimumHeight(150)  # 设置最小高度
        
        # 朝臣意见容器
        self.opinions_container = QWidget()
        self.opinions_layout = QVBoxLayout(self.opinions_container)
        self.opinions_layout.setSpacing(5)  # 添加间距
        scroll_area.setWidget(self.opinions_container)
        
        layout.addWidget(scroll_area, 1)  # 设置伸缩因子，占据剩余空间
        
        # 添加与官员互动的按钮
        interaction_layout = QHBoxLayout()
        
        # 询问情况按钮
        self.ask_status_btn = QPushButton("询问情况")
        self.ask_status_btn.clicked.connect(self._ask_official_status)
        interaction_layout.addWidget(self.ask_status_btn)
        
        # 下达指令按钮
        self.give_order_btn = QPushButton("下达指令")
        self.give_order_btn.clicked.connect(self._give_official_order)
        interaction_layout.addWidget(self.give_order_btn)
        
        layout.addLayout(interaction_layout)
        
        return layout
    
    def _create_decision_section(self):
        """创建决策区域"""
        layout = QVBoxLayout()
        layout.setSpacing(5)  # 添加间距
        
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
            option_layout.setSpacing(3)  # 添加间距
            
            # 单选按钮
            radio_btn = QRadioButton(f"选项 {i+1}")
            radio_btn.setProperty("option_index", i)
            self.decision_group.addButton(radio_btn, i)
            self.decision_buttons.append(radio_btn)
            radio_btn.setMinimumHeight(30)  # 设置最小高度
            option_layout.addWidget(radio_btn)
            
            # 选项描述
            option_desc = QLabel("选项描述")
            option_desc.setWordWrap(True)
            option_desc.setProperty("option_desc_index", i)
            option_desc.setMinimumHeight(40)  # 设置最小高度
            option_layout.addWidget(option_desc)
            
            # 预期效果
            effect_label = QLabel("预期效果: 待定")
            effect_label.setWordWrap(True)
            effect_label.setProperty("option_effect_index", i)
            effect_label.setMinimumHeight(40)  # 设置最小高度
            option_layout.addWidget(effect_label)
            
            layout.addWidget(option_frame)
        
        # 连接按钮组信号
        self.decision_group.buttonClicked.connect(self._on_option_selected)
        
        return layout
    
    def _create_button_section(self):
        """创建按钮区域"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 10, 0, 0)  # 添加顶部边距
        layout.setSpacing(10)  # 添加按钮间距
        
        layout.addStretch()
        
        # 确认按钮
        self.confirm_btn = QPushButton("确认决策")
        self.confirm_btn.clicked.connect(self._confirm_decision)
        self.confirm_btn.setEnabled(False)  # 初始禁用
        self.confirm_btn.setMinimumSize(100, 40)  # 设置最小尺寸
        layout.addWidget(self.confirm_btn)
        
        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setMinimumSize(100, 40)  # 设置最小尺寸
        layout.addWidget(cancel_btn)
        
        return layout
    
    def _load_meeting_data(self):
        """加载朝会数据"""
        if self.meeting_type == "emergency":
            self.meeting_data = self.game_controller.get_emergency_court_data()
        else:
            self.meeting_data = self.game_controller.get_monthly_court_data()
        
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
        
        # 如果是月度朝会，显示议题进度
        if self.meeting_type == "monthly" and "topics" in self.meeting_data:
            total_topics = len(self.meeting_data["topics"])
            current_index = self.meeting_data.get("current_topic_index", 0)
            progress_text = f"议题 {current_index + 1}/{total_topics}"
            self.topic_title_label.setText(f"{topic.get('title', '未知议题')} - {progress_text}")
        
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
            
            # 朝臣专业领域
            expertise = opinion.get("expertise", "综合")
            expertise_label = QLabel(f"专长: {expertise}")
            expertise_label.setStyleSheet("color: #555555; font-size: 9pt;")
            opinion_layout.addWidget(expertise_label)
            
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
                
                # 更新预期效果
                option_effect = None
                for child in self.decision_buttons[i].parent().findChildren(QLabel):
                    if child.property("option_effect_index") == i:
                        option_effect = child
                        break
                
                if option_effect:
                    effects = option.get("effects", {})
                    effect_text = "预期效果: "
                    
                    # 显示主要数值变化
                    if "military" in effects:
                        effect_text += f"军事 {effects['military']:+d} "
                    if "economy" in effects:
                        effect_text += f"经济 {effects['economy']:+d} "
                    if "tech" in effects:
                        effect_text += f"科技 {effects['tech']:+d} "
                    if "people" in effects:
                        effect_text += f"民心 {effects['people']:+d} "
                    if "diplomacy" in effects:
                        effect_text += f"外交 {effects['diplomacy']:+d} "
                    
                    option_effect.setText(effect_text)
    
    def _on_option_selected(self, button):
        """选项被选择时的处理"""
        option_index = button.property("option_index")
        
        # 获取当前议题
        current_topic = self.meeting_data.get("topic", {}) if self.meeting_data else {}
        options = current_topic.get("options", [])
        
        if 0 <= option_index < len(options):
            self.selected_option_id = options[option_index]["id"]
        else:
            self.selected_option_id = None
        
        # 启用确认按钮
        self.confirm_btn.setEnabled(True)
    
    def _confirm_decision(self):
        """确认决策"""
        if not self.selected_option_id:
            return
        
        # 执行决策
        if self.meeting_type == "emergency":
            result = self.game_controller.make_emergency_decision(self.selected_option_id)
        else:
            result = self.game_controller.make_monthly_decision(self.selected_option_id)
        
        if result.get("success"):
            # 显示决策结果
            decision = result.get("decision", {})
            resource_changes = result.get("resource_changes", {})
            
            # 构建消息
            message = f"决策已执行: {decision.get('option_title', '')}\n\n"
            
            if resource_changes:
                message += "数值变化:\n"
                for resource, change in resource_changes.items():
                    if change > 0:
                        message += f"  {resource}: +{change}\n"
                    else:
                        message += f"  {resource}: {change}\n"
            
            # 检查是否还有更多议题要处理
            if result.get("has_more_topics", False):
                message += f"\n{result.get('message', '')}"
                
                # 显示结果对话框，但不关闭对话框
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(self, "议题处理", message)
                
                # 重新加载朝会数据以显示下一个议题
                self._load_meeting_data()
                
                # 重置选择状态
                self.selected_option_id = None
                self.confirm_btn.setEnabled(False)
                
                # 重新设置单选按钮状态
                for btn in self.decision_buttons:
                    btn.setChecked(False)
            else:
                # 所有议题都已处理完毕
                message += f"\n{result.get('message', '')}"
                
                # 显示最终结果对话框
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(self, "朝会结束", message)
                
                # 关闭对话框
                self.accept()
        else:
            # 显示错误信息
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "错误", result.get("message", "决策执行失败"))
    
    def _ask_official_status(self):
        """询问官员情况"""
        # 弹出对话框让用户选择要询问的官员
        from PyQt5.QtWidgets import QListWidget, QDialog, QVBoxLayout, QPushButton, QMessageBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("选择官员")
        dialog.resize(300, 400)
        
        layout = QVBoxLayout(dialog)
        
        # 创建官员列表
        official_list = QListWidget()
        
        # 获取当前朝会的参与者
        participants = self.game_controller.get_participants_for_meeting()
        
        for participant in participants:
            item_text = f"{participant['name']} ({participant.get('title', '官员')})"
            official_list.addItem(item_text)
        
        layout.addWidget(official_list)
        
        # 确认按钮
        confirm_btn = QPushButton("询问")
        def on_confirm():
            selected_items = official_list.selectedItems()
            if not selected_items:
                QMessageBox.warning(dialog, "警告", "请选择一位官员")
                return
            
            selected_index = official_list.row(selected_items[0])
            if selected_index < len(participants):
                selected_participant = participants[selected_index]
                self._show_official_details(selected_participant)
        
        confirm_btn.clicked.connect(on_confirm)
        layout.addWidget(confirm_btn)
        
        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(dialog.close)
        layout.addWidget(cancel_btn)
        
        dialog.exec_()
    
    def _show_official_details(self, participant):
        """显示官员详细信息"""
        # 获取官员详细信息
        official_info = self.game_controller.get_participant_info(participant['id'])
        
        if official_info:
            details = (
                f"姓名: {official_info['name']}\n"
                f"职位: {official_info['title']}\n"
                f"性格: {official_info['personality']}\n"
                f"智力: {official_info['intelligence']}\n"
                f"政治: {official_info['politics']}\n"
                f"忠诚: {official_info['loyalty']}\n"
                f"军事: {official_info['military']}\n"
                f"描述: {official_info['description']}"
            )
            
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, f"{official_info['name']} 的详情", details)
        else:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "错误", "无法获取官员信息")
    
    def _give_official_order(self):
        """下达指令给官员"""
        from PyQt5.QtWidgets import QListWidget, QDialog, QVBoxLayout, QPushButton, QMessageBox, QTextEdit
        
        dialog = QDialog(self)
        dialog.setWindowTitle("下达指令")
        dialog.resize(400, 500)
        
        layout = QVBoxLayout(dialog)
        
        # 创建官员列表
        official_list = QListWidget()
        
        # 获取当前朝会的参与者
        participants = self.game_controller.get_participants_for_meeting()
        
        for participant in participants:
            item_text = f"{participant['name']} ({participant.get('title', '官员')})"
            official_list.addItem(item_text)
        
        layout.addWidget(official_list)
        layout.addWidget(QLabel("指令内容:"))
        
        # 指令输入框
        instruction_input = QTextEdit()
        instruction_input.setPlaceholderText("请输入要下达的指令...")
        layout.addWidget(instruction_input)
        
        # 确认按钮
        confirm_btn = QPushButton("下达指令")
        def on_confirm():
            selected_items = official_list.selectedItems()
            if not selected_items:
                QMessageBox.warning(dialog, "警告", "请选择一位官员")
                return
            
            instruction = instruction_input.toPlainText().strip()
            if not instruction:
                QMessageBox.warning(dialog, "警告", "请输入指令内容")
                return
            
            selected_index = official_list.row(selected_items[0])
            if selected_index < len(participants):
                selected_participant = participants[selected_index]
                
                # 模拟下达指令的效果
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(
                    dialog, 
                    "指令下达", 
                    f"已向 {selected_participant['name']} 下达指令:\n\n{instruction}\n\n"
                    f"该官员表示会认真执行您的命令。"
                )
                dialog.close()
        
        confirm_btn.clicked.connect(on_confirm)
        layout.addWidget(confirm_btn)
        
        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(dialog.close)
        layout.addWidget(cancel_btn)
        
        dialog.exec_()
    
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
        # 根据窗口宽度调整字体大小
        if width < 900:
            font_size = 9
        elif width < 1100:
            font_size = 10
        elif width < 1300:
            font_size = 11
        else:
            font_size = 12
        
        # 设置基础字体
        base_font = QFont("", font_size)
        self.setFont(base_font)
        
        # 调整标题字体
        if hasattr(self, 'topic_title_label'):
            title_font = QFont("", font_size + 2, QFont.Bold)
            self.topic_title_label.setFont(title_font)
        
        # 调整选项按钮大小
        self._adjust_option_buttons(width, height)
        
        # 调整意见区域字体
        self._adjust_opinion_area(width, height)
    
    def _adjust_option_buttons(self, width, height):
        """调整选项按钮大小"""
        # 根据窗口大小调整按钮
        if width < 900:
            button_height = 30
            font_size = 9
        elif width < 1100:
            button_height = 40
            font_size = 10
        elif width < 1300:
            button_height = 50
            font_size = 11
        else:
            button_height = 60
            font_size = 12
        
        # 设置按钮样式
        button_style = f"""
            QRadioButton {{
                min-height: {button_height}px;
                font-size: {font_size}pt;
                spacing: 10px;
            }}
        """
        
        # 应用样式到所有单选按钮
        if hasattr(self, 'decision_group'):
            for button in self.decision_group.buttons():
                button.setStyleSheet(button_style)
    
    def _adjust_opinion_area(self, width, height):
        """调整意见区域字体"""
        # 根据窗口大小调整意见区域字体
        if width < 900:
            font_size = 8
        elif width < 1100:
            font_size = 9
        elif width < 1300:
            font_size = 10
        else:
            font_size = 11
        
        # 设置意见区域字体
        opinion_font = QFont("", font_size)
        
        # 应用到意见区域中的标签
        if hasattr(self, 'opinions_container'):
            for label in self.opinions_container.findChildren(QLabel):
                label.setFont(opinion_font)
                label.setWordWrap(True)  # 确保文本自动换行
    
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
        # 根据窗口宽度调整字体大小
        if width < 900:
            font_size = 9
        elif width < 1100:
            font_size = 10
        elif width < 1300:
            font_size = 11
        else:
            font_size = 12
        
        # 设置基础字体
        base_font = QFont("", font_size)
        self.setFont(base_font)
        
        # 调整标题字体
        if hasattr(self, 'topic_title_label'):
            title_font = QFont("", font_size + 2, QFont.Bold)
            self.topic_title_label.setFont(title_font)
        
        # 调整选项按钮大小
        self._adjust_option_buttons(width, height)
        
        # 调整意见区域字体
        self._adjust_opinion_area(width, height)
    
    def _adjust_option_buttons(self, width, height):
        """调整选项按钮大小"""
        # 根据窗口大小调整按钮
        if width < 900:
            button_height = 30
            font_size = 9
        elif width < 1100:
            button_height = 40
            font_size = 10
        elif width < 1300:
            button_height = 50
            font_size = 11
        else:
            button_height = 60
            font_size = 12
        
        # 设置按钮样式
        button_style = f"""
            QRadioButton {{
                min-height: {button_height}px;
                font-size: {font_size}pt;
                spacing: 10px;
            }}
        """
        
        # 应用样式到所有单选按钮
        if hasattr(self, 'decision_group'):
            for button in self.decision_group.buttons():
                button.setStyleSheet(button_style)
    
    def _adjust_opinion_area(self, width, height):
        """调整意见区域字体"""
        # 根据窗口大小调整意见区域字体
        if width < 900:
            font_size = 8
        elif width < 1100:
            font_size = 9
        elif width < 1300:
            font_size = 10
        else:
            font_size = 11
        
        # 设置意见区域字体
        opinion_font = QFont("", font_size)
        
        # 应用到意见区域中的标签
        if hasattr(self, 'opinions_container'):
            for label in self.opinions_container.findChildren(QLabel):
                label.setFont(opinion_font)
                label.setWordWrap(True)  # 确保文本自动换行