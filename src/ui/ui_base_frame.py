#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UI系统基础框架
实现UI系统的核心组件和基础功能
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QFrame, QGraphicsView,
                             QGraphicsScene, QGraphicsPixmapItem, QButtonGroup, QRadioButton)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QRectF, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor, QPixmap
from ui.court_map_widget import CourtTopDownMapWidget


class UIBaseFrame(QWidget):
    """UI系统基础框架类"""
    
    # 信号定义
    palace_clicked = pyqtSignal(str)  # 宫殿点击信号
    character_clicked = pyqtSignal(str)  # 人物点击信号
    court_decision = pyqtSignal(str)  # 朝会决策信号
    court_meeting_completed = pyqtSignal()  # 朝会完成信号
    
    def __init__(self, parent=None):
        """初始化UI基础框架"""
        super().__init__(parent)
        
        # 设置基本属性
        self.setMinimumSize(700, 450)
        
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
        self.intel_label = None
        self.faction_panel_label = None
        
        # 朝会状态
        self.court_meeting_active = False
        self.current_meeting_data = None
        self.option_buttons = None
        # 地图视图（在朝会区域下方嵌入）
        self.court_map_view = None
        
        # 初始化UI
        self._init_ui()
        
        # 应用基础样式
        self._apply_base_style()
        
        # 连接窗口大小改变事件
        self.resizeEvent = self._on_window_resize
    
    def _init_ui(self):
        """初始化用户界面"""
        # 创建主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(5)
        
        # 创建中央区域
        central_layout = QHBoxLayout()
        central_layout.setContentsMargins(5, 5, 5, 5)  # 添加内边距
        central_layout.setSpacing(10)  # 添加间距
        
        # 左侧主要信息区域（用于显示朝会议案信息及选项）
        self.main_content_area = self._create_main_content_area()
        central_layout.addWidget(self.main_content_area, 7)  # 占70%宽度
        
        # 右侧信息面板（显示各类信息提示）
        self.info_panel = self._create_info_panel()
        central_layout.addWidget(self.info_panel, 3)  # 占30%宽度
        
        self.main_layout.addLayout(central_layout, 1)  # 设置伸缩因子，占据大部分空间
        
        # 创建底部控制栏
        self.bottom_bar = self._create_bottom_bar()
        self.main_layout.addWidget(self.bottom_bar, 0)  # 不设置伸缩因子，固定高度
        

    
    def _create_top_bar(self):
        """创建顶部状态栏"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        frame.setMinimumHeight(50)  # 使用最小高度而不是最大高度
        frame.setMaximumHeight(80)  # 设置合理的最大高度
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(10, 5, 10, 5)  # 添加内边距
        
        # 设置字体
        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        
        # 时间信息
        self.year_label = QLabel("年份: 190")
        self.year_label.setFont(font)
        self.year_label.setMinimumWidth(100)  # 设置最小宽度
        layout.addWidget(self.year_label)
        
        self.season_label = QLabel("季节: 春")
        self.season_label.setFont(font)
        self.season_label.setMinimumWidth(100)  # 设置最小宽度
        layout.addWidget(self.season_label)
        
        layout.addStretch()
        
        # 资源信息
        self.gold_label = QLabel("金钱: 10000")
        self.gold_label.setFont(font)
        self.gold_label.setMinimumWidth(120)  # 设置最小宽度
        layout.addWidget(self.gold_label)
        
        self.food_label = QLabel("粮食: 50000")
        self.food_label.setFont(font)
        self.food_label.setMinimumWidth(120)  # 设置最小宽度
        layout.addWidget(self.food_label)
        
        return frame
    
    def setup_speed_controls(self, pause_callback, normal_callback, fast_x3_callback):
        """设置速度控制按钮的回调函数"""
        if hasattr(self, 'pause_btn'):
            self.pause_btn.clicked.connect(pause_callback)
        if hasattr(self, 'normal_speed_btn'):
            self.normal_speed_btn.clicked.connect(normal_callback)
        if hasattr(self, 'fast_x3_btn'):
            self.fast_x3_btn.clicked.connect(fast_x3_callback)
    
    def update_speed_buttons(self, current_speed):
        """更新速度按钮高亮状态（不改尺寸，仅改背景色）"""
        ACTIVE_COLORS = {
            "pause":  "background-color: #FF6B6B;",
            "normal": "background-color: #4ECDC4;",
            "fast":   "background-color: #FFD700;",
        }
        DEFAULT = ""  # 恢复默认样式，尺寸由 setFixedSize 控制
        
        if hasattr(self, 'pause_btn'):
            self.pause_btn.setStyleSheet(ACTIVE_COLORS["pause"] if current_speed == "pause" else DEFAULT)
        if hasattr(self, 'normal_speed_btn'):
            self.normal_speed_btn.setStyleSheet(ACTIVE_COLORS["normal"] if current_speed == "normal" else DEFAULT)
        if hasattr(self, 'fast_x3_btn'):
            self.fast_x3_btn.setStyleSheet(ACTIVE_COLORS["fast"] if current_speed in ("fast", "fastest", "ultra") else DEFAULT)
    
    def _create_bottom_bar(self):
        """创建底部控制栏"""
        frame = QFrame()
        frame.setObjectName("bottom_bar")  # 用于调色时排除其内按钮
        frame.setFrameStyle(QFrame.Box)
        frame.setFixedHeight(48)
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)
        
        BTN_W, BTN_H = 90, 32  # 统一按钮尺寸
        
        # 添加按钮
        save_game_btn = QPushButton("保存游戏")
        save_game_btn.clicked.connect(self._on_save_game)
        save_game_btn.setFixedSize(BTN_W, BTN_H)
        layout.addWidget(save_game_btn)
        
        load_game_btn = QPushButton("加载游戏")
        load_game_btn.clicked.connect(self._on_load_game)
        load_game_btn.setFixedSize(BTN_W, BTN_H)
        layout.addWidget(load_game_btn)
        
        layout.addStretch()
        
        # 速度控制按钮（仅保留：暂停 / 正常 / 快速×3）
        self.pause_btn = QPushButton("暂停")
        self.pause_btn.setFixedSize(BTN_W, BTN_H)
        layout.addWidget(self.pause_btn)
        
        self.normal_speed_btn = QPushButton("正常")
        self.normal_speed_btn.setFixedSize(BTN_W, BTN_H)
        layout.addWidget(self.normal_speed_btn)
        
        self.fast_x3_btn = QPushButton("快速X3")
        self.fast_x3_btn.setFixedSize(BTN_W, BTN_H)
        layout.addWidget(self.fast_x3_btn)
        
        layout.addStretch()
        
        help_btn = QPushButton("帮助")
        help_btn.clicked.connect(self._on_help)
        help_btn.setFixedSize(BTN_W, BTN_H)
        layout.addWidget(help_btn)
        
        return frame
    
    def _create_info_panel(self):
        """创建右侧信息面板"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        frame.setMinimumWidth(250)  # 减小最小宽度，更适应小窗口
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 10, 10, 10)  # 添加内边距
        layout.setSpacing(10)  # 添加间距
        
        # 标题
        title = QLabel("信息面板")
        title.setFont(QFont("", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setContentsMargins(0, 0, 0, 5)  # 添加底部边距
        layout.addWidget(title)
        
        # 添加状态信息区域
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.Box)
        status_layout = QVBoxLayout(status_frame)
        status_layout.setSpacing(5)  # 添加间距
        
        # 年份
        year_layout = QHBoxLayout()
        year_label = QLabel("年份:")
        self.year_label = QLabel("190")
        year_layout.addWidget(year_label)
        year_layout.addWidget(self.year_label)
        status_layout.addLayout(year_layout)
        
        # 月份
        month_layout = QHBoxLayout()
        month_label = QLabel("月份:")
        self.month_label = QLabel("1")
        month_layout.addWidget(month_label)
        month_layout.addWidget(self.month_label)
        status_layout.addLayout(month_layout)
        
        # 日期
        day_layout = QHBoxLayout()
        day_label = QLabel("日期:")
        self.day_label = QLabel("1")
        day_layout.addWidget(day_label)
        day_layout.addWidget(self.day_label)
        status_layout.addLayout(day_layout)
        
        # 天气 (暂时显示为默认值)
        weather_layout = QHBoxLayout()
        weather_label = QLabel("天气:")
        self.weather_label = QLabel("晴")
        weather_layout.addWidget(weather_label)
        weather_layout.addWidget(self.weather_label)
        status_layout.addLayout(weather_layout)
        
        # 国库钱粮
        resource_layout = QHBoxLayout()
        resource_label = QLabel("国库:")
        self.gold_label = QLabel("钱: 10000")
        self.food_label = QLabel("粮: 50000")
        self.intel_label = QLabel("情报: 20")
        resource_layout.addWidget(resource_label)
        resource_sub_layout = QVBoxLayout()
        resource_sub_layout.addWidget(self.gold_label)
        resource_sub_layout.addWidget(self.food_label)
        resource_sub_layout.addWidget(self.intel_label)
        resource_layout.addLayout(resource_sub_layout)
        status_layout.addLayout(resource_layout)

        # 势力态势
        faction_sep = QLabel("──────────")
        faction_sep.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(faction_sep)
        faction_title = QLabel("势力态势")
        faction_title.setAlignment(Qt.AlignCenter)
        faction_title.setFont(QFont("", 9, QFont.Bold))
        status_layout.addWidget(faction_title)
        self.faction_panel_label = QLabel("加载中...")
        self.faction_panel_label.setWordWrap(True)
        self.faction_panel_label.setAlignment(Qt.AlignLeft)
        status_layout.addWidget(self.faction_panel_label)

        layout.addWidget(status_frame)
        
        # 信息显示区域
        info_area = QLabel("点击宫殿或人物查看详细信息")
        info_area.setAlignment(Qt.AlignTop)
        info_area.setWordWrap(True)
        info_area.setMinimumHeight(100)  # 设置最小高度
        layout.addWidget(info_area, 1)  # 设置伸缩因子，占据剩余空间
        
        # 状态消息区域
        status_msg_frame = QFrame()
        status_msg_frame.setFrameStyle(QFrame.Box)
        status_msg_layout = QVBoxLayout(status_msg_frame)
        self.status_msg_label = QLabel("准备就绪")
        self.status_msg_label.setWordWrap(True)
        status_msg_layout.addWidget(self.status_msg_label)
        layout.addWidget(status_msg_frame)
        
        return frame
    
    
    def _create_main_content_area(self):
        """创建左侧主要信息区域"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        frame.setMinimumSize(500, 300)  # 设置最小尺寸
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 10, 10, 10)  # 添加边距
        layout.setSpacing(10)  # 添加间距
        
        # 默认显示宫殿地图
        self.palace_map = self._create_palace_map()
        layout.addWidget(self.palace_map)
        
        # 朝会区域（初始隐藏）
        self.court_meeting_area = self._create_court_meeting_area()
        self.court_meeting_area.setVisible(False)
        layout.addWidget(self.court_meeting_area)
        
        return frame
    
    def _create_court_meeting_area(self):
        """创建朝会区域"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 朝会标题
        self.court_title_label = QLabel("朝会")
        self.court_title_label.setFont(QFont("", 16, QFont.Bold))
        self.court_title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.court_title_label)
        
        # 朝会信息区域
        self.court_info_area = QLabel()
        self.court_info_area.setAlignment(Qt.AlignTop)
        self.court_info_area.setWordWrap(True)
        self.court_info_area.setMinimumHeight(80)
        layout.addWidget(self.court_info_area, 2)

        # 嵌入2D正视图地图（显示城市/关隘/道路，默认隐藏）
        try:
            self.court_map_view = CourtTopDownMapWidget()
            self.court_map_view.setVisible(False)
            self.court_map_view.setMinimumHeight(100)
            layout.addWidget(self.court_map_view, 5)
        except Exception:
            self.court_map_view = None
        
        # 朝会选项区域
        self.court_options_frame = QFrame()
        self.court_options_frame.setFrameStyle(QFrame.Box)
        self.court_options_layout = QVBoxLayout(self.court_options_frame)
        layout.addWidget(self.court_options_frame)
        
        # 朝会决策按钮
        self.court_decision_btn = QPushButton("做出决策")
        self.court_decision_btn.clicked.connect(self._on_court_decision)
        self.court_decision_btn.setFixedSize(90, 32)
        self.court_decision_btn.setEnabled(False)  # 初始禁用，直到选择选项
        layout.addWidget(self.court_decision_btn, 0, Qt.AlignLeft)

        # 退朝按钮（所有议题处理完后显示，点击返回主界面并恢复时间）
        self.dismiss_btn = QPushButton("退朝")
        self.dismiss_btn.clicked.connect(self._restore_main_content)
        self.dismiss_btn.setFixedSize(90, 32)
        self.dismiss_btn.setVisible(False)
        layout.addWidget(self.dismiss_btn, 0, Qt.AlignLeft)

        return frame
    
    def _create_palace_map(self):
        """创建宫殿地图"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        frame.setMinimumSize(500, 300)  # 减小最小尺寸，更适应小窗口
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 10, 10, 10)  # 添加边距
        layout.setSpacing(10)  # 添加间距
        
        # 添加标题
        title = QLabel("未央宫地图")
        title.setFont(QFont("", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setContentsMargins(0, 0, 0, 10)  # 添加底部边距
        layout.addWidget(title)
        
        # 创建宫殿按钮区域 - 使用水平布局放置宫殿按钮
        palace_layout = QHBoxLayout()
        palace_layout.setSpacing(20)  # 添加区域间距
        
        # 宣室殿按钮
        xuanshi_btn = QPushButton("宣室殿")
        xuanshi_btn.clicked.connect(self._on_xuanshi_palace_clicked)
        xuanshi_btn.setFixedSize(90, 32)
        xuanshi_btn.setToolTip("处理紧急朝会，应对突发事件")
        palace_layout.addWidget(xuanshi_btn)
        
        # 承明殿按钮
        chengming_btn = QPushButton("承明殿")
        chengming_btn.clicked.connect(self._on_chengming_palace_clicked)
        chengming_btn.setFixedSize(90, 32)
        chengming_btn.setToolTip("处理每月初一的大朝会")
        palace_layout.addWidget(chengming_btn)
        
        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #8B4513;")
        palace_layout.addWidget(separator)
        
        # 椒房殿按钮
        jiaofang_btn = QPushButton("椒房殿")
        jiaofang_btn.clicked.connect(lambda: self.palace_clicked.emit("椒房殿"))
        jiaofang_btn.setFixedSize(90, 32)
        jiaofang_btn.setToolTip("后宫管理")
        palace_layout.addWidget(jiaofang_btn)
        
        # 长乐宫按钮
        changle_btn = QPushButton("长乐宫")
        changle_btn.clicked.connect(lambda: self.palace_clicked.emit("长乐宫"))
        changle_btn.setFixedSize(90, 32)
        changle_btn.setToolTip("皇室事务")
        palace_layout.addWidget(changle_btn)
        
        layout.addLayout(palace_layout, 1)  # 设置伸缩因子，占据大部分空间
        
        return frame
    
    def _on_xuanshi_palace_clicked(self):
        """处理宣室殿点击事件"""
        # 发射宫殿点击信号
        self.palace_clicked.emit("宣室殿")
    
    def _on_chengming_palace_clicked(self):
        """处理承明殿点击事件"""
        # 只发射信号，由 WeiyangMainWindow 负责调用 get_monthly_court_data 并展示真实朝会数据
        self.palace_clicked.emit("承明殿")
    
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
    
    def update_time_info(self, year, month, day):
        """更新时间信息"""
        self.year_label.setText(str(year))
        self.month_label.setText(str(month))
        self.day_label.setText(str(day))
    
    def update_resource_info(self, gold, food, intel=0, soldiers=0):
        """更新资源信息。food < 2旬供给时橙色警告，= 0 时红色。"""
        self.gold_label.setText(f"钱: {gold}")
        self.food_label.setText(f"粮: {food}")
        if self.intel_label:
            self.intel_label.setText(f"情报: {intel}")
        xun_cost = soldiers if soldiers > 0 else 1
        if food == 0:
            self.food_label.setStyleSheet("color: #ff4444; font-weight: bold;")
        elif food < xun_cost * 20:
            self.food_label.setStyleSheet("color: #ffa500; font-weight: bold;")
        else:
            self.food_label.setStyleSheet("")

    def update_faction_panel(self, faction_dims: dict, factions: dict):
        """更新势力态势面板。faction_dims: {id: {military,economy,...}}，factions: {id: {name,...}}"""
        if not hasattr(self, "faction_panel_label") or not self.faction_panel_label:
            return
        FACTION_ORDER = ["wei", "shu", "wu"]
        DIM_ABBR = {"military": "军", "economy": "经", "diplomacy": "外"}
        lines = []
        for fid in FACTION_ORDER:
            dims = faction_dims.get(fid, {})
            name = factions.get(fid, {}).get("name", fid)
            vals = " ".join(f"{abbr}{dims.get(key, 50):.0f}"
                            for key, abbr in DIM_ABBR.items())
            lines.append(f"{name}: {vals}")
        self.faction_panel_label.setText("\n".join(lines))
    
    def show_info(self, title, content):
        """在信息面板显示信息"""
        # 找到信息面板中的标签并更新内容
        for i in range(self.info_panel.layout().count()):
            widget = self.info_panel.layout().itemAt(i).widget()
            if isinstance(widget, QLabel) and widget != self.info_panel.layout().itemAt(0).widget():
                widget.setText(f"<b>{title}</b><br>{content}")
                break
    
    def show_court_meeting(self, meeting_data):
        """在主要信息区域显示朝会信息"""
        self.court_meeting_active = True
        self.current_meeting_data = meeting_data
        
        # 隐藏宫殿地图，显示朝会区域
        self.palace_map.setVisible(False)
        self.court_meeting_area.setVisible(True)
        
        # 清空现有选项
        self._clear_court_options()
        
        # 显示朝会标题
        if meeting_data.get("type") == "monthly":
            title = "月度朝会"
            if "topics" in meeting_data:
                total_topics = len(meeting_data["topics"])
                current_index = meeting_data.get("current_topic_index", 0)
                topic = meeting_data["topics"][current_index]
                title += f" - 议题 {current_index + 1}/{total_topics}"
        else:
            title = "紧急朝会"
        
        self.court_title_label.setText(title)
        
        # 构建朝会信息文本
        info_text = ""
        
        # 添加时间信息
        year = meeting_data.get("year", 190)
        season = meeting_data.get("season", 1)
        season_names = {1: "春", 2: "夏", 3: "秋", 4: "冬"}
        season_name = season_names.get(season, "春")
        info_text += f"<p><b>时间:</b> {year}年 {season_name}</p>"
        
        # 添加议题信息
        if "topic" in meeting_data:
            topic = meeting_data["topic"]
            info_text += f"<h3>{topic.get('title', '未知议题')}</h3>"
            info_text += f"<p><b>描述:</b> {topic.get('description', '')}</p>"
            info_text += f"<p><b>背景:</b> {topic.get('background', '')}</p>"
            
            # 添加选项
            if "options" in topic:
                self._add_court_options(topic["options"])
        
        # 更新信息标签
        self.court_info_area.setText(info_text)
        
        # 在右侧信息面板显示朝会提示信息
        self._show_court_hints(meeting_data)

        # 显示规则：仅当议题存在 related_position（格子坐标）时才显示地图并居中；否则隐藏。
        topic = meeting_data.get("topic") if meeting_data else None
        related_pos = topic.get("related_position") if topic else None
        has_grid_pos = isinstance(related_pos, (list, tuple)) and len(related_pos) >= 2

        if self.court_map_view:
            if has_grid_pos:
                self.court_map_view.setVisible(True)
                self.court_map_view.center_on_grid(
                    int(related_pos[0]), int(related_pos[1]), view_range=250)
                self._refresh_map_fog()
            else:
                self.court_map_view.setVisible(False)
                self.court_map_view.reset()
        
        # 显示选项区域和决策按钮；确保退朝按钮隐藏
        self.court_options_frame.setVisible(True)
        self.court_decision_btn.setVisible(True)
        self.court_decision_btn.setEnabled(False)  # 初始禁用，直到选择选项
        self.dismiss_btn.setVisible(False)

    def _refresh_map_fog(self):
        """从 game_controller 读取当前可见性，刷新地图迷雾。"""
        if not self.court_map_view:
            return
        gc = getattr(self, "game_controller", None)
        if not gc:
            return
        player_faction = gc.game_model.game_data["game_info"].get("current_faction", "wei")
        cities = gc.game_model.get_cities_for_player(player_faction)
        # faction=None 表示迷雾（未解锁情报的敌方城市）
        fog_data = {city_id: city.get("faction") for city_id, city in cities.items()}
        self.court_map_view.set_fog_data(fog_data)
        """更新朝会信息"""
        self.current_meeting_data = meeting_data
        
        # 清空现有选项
        self._clear_court_options()
        
        # 显示朝会标题
        if meeting_data.get("type") == "monthly":
            title = "月度朝会"
            if "topics" in meeting_data:
                total_topics = len(meeting_data["topics"])
                current_index = meeting_data.get("current_topic_index", 0)
                topic = meeting_data["topics"][current_index]
                title += f" - 议题 {current_index + 1}/{total_topics}"
        else:
            title = "紧急朝会"
        
        self.court_title_label.setText(title)
        
        # 构建朝会信息文本
        info_text = ""
        
        # 添加时间信息
        year = meeting_data.get("year", 190)
        season = meeting_data.get("season", 1)
        season_names = {1: "春", 2: "夏", 3: "秋", 4: "冬"}
        season_name = season_names.get(season, "春")
        info_text += f"<p><b>时间:</b> {year}年 {season_name}</p>"
        
        # 添加议题信息
        if "topic" in meeting_data:
            topic = meeting_data["topic"]
            info_text += f"<h3>{topic.get('title', '未知议题')}</h3>"
            info_text += f"<p><b>描述:</b> {topic.get('description', '')}</p>"
            info_text += f"<p><b>背景:</b> {topic.get('background', '')}</p>"
            
            # 添加选项
            if "options" in topic:
                self._add_court_options(topic["options"])
        
        # 更新左侧主要信息区域
        self.court_info_area.setText(info_text)
        
        # 更新右侧信息面板的提示信息
        self._show_court_hints(meeting_data)
        
        # 同步更新：仅当议题存在 related_position（格子坐标）时才显示地图并居中；否则隐藏。
        topic = meeting_data.get("topic") if meeting_data else None
        related_pos = topic.get("related_position") if topic else None
        has_grid_pos = isinstance(related_pos, (list, tuple)) and len(related_pos) >= 2

        if self.court_map_view:
            if has_grid_pos:
                self.court_map_view.setVisible(True)
                self.court_map_view.center_on_grid(
                    int(related_pos[0]), int(related_pos[1]), view_range=250)
                self._refresh_map_fog()
            else:
                self.court_map_view.setVisible(False)
                self.court_map_view.reset()
        
        # 显示选项区域和决策按钮；确保退朝按钮隐藏
        self.court_options_frame.setVisible(True)
        self.court_decision_btn.setVisible(True)
        self.court_decision_btn.setEnabled(False)  # 初始禁用，直到选择选项
        self.dismiss_btn.setVisible(False)

    def _show_court_hints(self, meeting_data):
        """在右侧信息面板显示朝会提示信息"""
        # 找到信息面板中的标签并更新内容
        for i in range(self.info_panel.layout().count()):
            widget = self.info_panel.layout().itemAt(i).widget()
            if isinstance(widget, QLabel) and widget.text() == "点击宫殿或人物查看详细信息":
                hints_text = "<b>朝会提示</b><br><br>"
                
                # 添加基本提示
                hints_text += "• 请仔细阅读议题描述和背景<br>"
                hints_text += "• 考虑每个选项的利弊<br>"
                hints_text += "• 选择一个选项后点击\"做出决策\"<br><br>"
                
                # 添加当前议题提示
                if "topic" in meeting_data:
                    topic = meeting_data["topic"]
                    hints_text += f"<b>当前议题:</b> {topic.get('title', '未知议题')}<br><br>"
                    
                    # 添加选项简要说明
                    if "options" in topic:
                        hints_text += "<b>选项概要:</b><br>"
                        for i, option in enumerate(topic["options"]):
                            option_text = option.get("text", f"选项 {i+1}")
                            hints_text += f"• {option_text}<br>"
                
                widget.setText(hints_text)
                break
    
    def show_court_meeting_complete(self):
        """显示朝会完成信息"""
        self.court_meeting_active = False

        # 构建完成信息文本
        info_text = "<h3>朝会完成</h3>"
        info_text += "<p>所有议题已讨论完毕，朝会结束。</p>"
        info_text += "<p>请点击下方<b>退朝</b>按钮返回主界面，时间将自动恢复推进。</p>"

        # 更新左侧主要信息区域
        self.court_info_area.setText(info_text)

        # 隐藏地图、选项和决策按钮，显示退朝按钮
        if self.court_map_view:
            self.court_map_view.setVisible(False)
            self.court_map_view.reset()
        self.court_options_frame.setVisible(False)
        self.court_decision_btn.setVisible(False)
        self.dismiss_btn.setVisible(True)

        # 在右侧信息面板显示完成信息
        self._show_court_complete_hints()
    
    def _show_court_complete_hints(self):
        """在右侧信息面板显示朝会完成提示"""
        # 找到信息面板中的标签并更新内容
        for i in range(self.info_panel.layout().count()):
            widget = self.info_panel.layout().itemAt(i).widget()
            if isinstance(widget, QLabel) and widget.text().startswith("<b>朝会提示</b>"):
                hints_text = "<b>朝会已完成</b><br><br>"
                hints_text += "• 所有议题已处理完毕<br>"
                hints_text += "• 3秒后返回主界面<br>"
                hints_text += '• 点击"退朝"按钮返回主界面'

                widget.setText(hints_text)
                break

    def _restore_main_content(self):
        """恢复主界面内容"""
        # 隐藏退朝按钮
        self.dismiss_btn.setVisible(False)
        # 隐藏朝会区域，显示宫殿地图
        self.court_meeting_area.setVisible(False)
        self.palace_map.setVisible(True)
        
        # 恢复右侧信息面板的默认内容
        for i in range(self.info_panel.layout().count()):
            widget = self.info_panel.layout().itemAt(i).widget()
            if isinstance(widget, QLabel):
                text = widget.text()
                if text.startswith("<b>朝会已完成</b>"):
                    widget.setText("点击宫殿或人物查看详细信息")
                    break
        
        # 朝会结束后，发出信号通知主窗口恢复游戏时间
        self.court_meeting_completed.emit()
    
    def _add_court_options(self, options):
        """添加朝会选项"""
        # 确保option_buttons初始化为None
        self.option_buttons = None
        
        # 创建选项按钮组
        self.option_buttons = QButtonGroup(self)
        self.option_buttons.setExclusive(True)
        
        # 为每个选项创建单选按钮
        for i, option in enumerate(options):
            option_id = option.get("id", f"option_{i}")
            option_text = option.get("title", option.get("text", f"选项 {i+1}"))
            
            # 创建单选按钮
            radio_btn = QRadioButton(option_text)
            radio_btn.setProperty("option_id", option_id)
            radio_btn.toggled.connect(self._on_option_selected)
            
            # 添加到按钮组
            self.option_buttons.addButton(radio_btn, i)
            
            # 添加到选项布局
            self.court_options_layout.addWidget(radio_btn)
    
    def _on_option_selected(self, checked):
        """处理选项选择"""
        if checked:
            # 启用决策按钮
            self.court_decision_btn.setEnabled(True)
    
    def _clear_court_options(self):
        """清空朝会选项"""
        # 清空选项布局中的所有控件
        while self.court_options_layout.count():
            child = self.court_options_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # 重置选项按钮组
        self.option_buttons = None
    
    def _on_court_decision(self):
        """处理朝会决策"""
        if not self.court_meeting_active:
            return
        
        # 获取选中的选项
        selected_option_id = None
        if hasattr(self, 'option_buttons'):
            checked_button = self.option_buttons.checkedButton()
            if checked_button:
                selected_option_id = checked_button.property("option_id")
        
        # 发射决策信号
        if selected_option_id:
            self.court_decision.emit(selected_option_id)
        else:
            # 显示错误消息
            self.status_msg_label.setText("请先选择一个选项")
    

    
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
        if width < 1000:
            font_size = 9
        elif width < 1200:
            font_size = 10
        elif width < 1400:
            font_size = 11
        else:
            font_size = 12
        
        # 设置基础字体
        base_font = QFont("", font_size)
        self.setFont(base_font)
        
        # 调整宫殿按钮大小
        self._adjust_palace_buttons(width, height)
        
        # 调整信息面板大小
        self._adjust_info_panel(width, height)
    
    def _adjust_palace_buttons(self, width, height):
        """调整宫殿按钮大小"""
        # 根据窗口大小调整按钮
        if width < 1000:
            button_width = 80
            button_height = 40
            font_size = 9
        elif width < 1200:
            button_width = 100
            button_height = 50
            font_size = 10
        elif width < 1400:
            button_width = 120
            button_height = 60
            font_size = 11
        else:
            button_width = 140
            button_height = 70
            font_size = 12
        
        # 设置按钮样式
        button_style = f"""
            QPushButton {{
                min-width: {button_width}px;
                max-width: {button_width}px;
                min-height: {button_height}px;
                max-height: {button_height}px;
                font-size: {font_size}pt;
                font-weight: bold;
            }}
        """
        
        # 应用样式到所有按钮
        for button in self.findChildren(QPushButton):
            if "宫殿" in button.text() or "殿" in button.text():
                button.setStyleSheet(button_style)
    
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
        if hasattr(self, 'year_label') and self.year_label:
            self.year_label.setFont(info_font)
        if hasattr(self, 'month_label') and self.month_label:
            self.month_label.setFont(info_font)
        if hasattr(self, 'day_label') and self.day_label:
            self.day_label.setFont(info_font)
        if hasattr(self, 'gold_label') and self.gold_label:
            self.gold_label.setFont(info_font)
        if hasattr(self, 'food_label') and self.food_label:
            self.food_label.setFont(info_font)
        if hasattr(self, 'intel_label') and self.intel_label:
            self.intel_label.setFont(info_font)
    
    def _on_save_game(self):
        """处理保存游戏按钮点击事件"""
        from PyQt5.QtWidgets import QMessageBox, QFileDialog
        
        # 获取保存文件路径
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存游戏", "", "三国志存档文件 (*.sgs);;All Files (*)"
        )
        
        if file_path:
            QMessageBox.information(self, "保存游戏", f"游戏已保存到: {file_path}")
        else:
            QMessageBox.information(self, "保存游戏", "保存游戏功能待实现")
    
    def _on_load_game(self):
        """处理加载游戏按钮点击事件"""
        from PyQt5.QtWidgets import QMessageBox, QFileDialog
        
        # 获取加载文件路径
        file_path, _ = QFileDialog.getOpenFileName(
            self, "加载游戏", "", "三国志存档文件 (*.sgs);;All Files (*)"
        )
        
        if file_path:
            QMessageBox.information(self, "加载游戏", f"游戏已从以下路径加载: {file_path}")
        else:
            QMessageBox.information(self, "加载游戏", "加载游戏功能待实现")
    
    def _on_help(self):
        """处理帮助按钮点击事件"""
        from PyQt5.QtWidgets import QMessageBox
        help_text = """
        <h3>三国志策略游戏 - 帮助</h3>
        <p><b>游戏目标:</b> 作为君主，通过朝会决策管理国家，最终统一三国。</p>
        <p><b>基本操作:</b></p>
        <ul>
            <li>点击宫殿进入相应功能</li>
            <li>在朝会中选择提案并做出决策</li>
            <li>使用速度控制按钮调整游戏速度</li>
        </ul>
        <p><b>数值说明:</b></p>
        <ul>
            <li><b>军事:</b> 影响军队战斗力和防御能力</li>
            <li><b>经济:</b> 影响财政收入和资源生产</li>
            <li><b>科技:</b> 影响研究进度和技术应用</li>
            <li><b>民心:</b> 影响民众满意度和稳定性</li>
            <li><b>外交:</b> 影响与其他势力的关系</li>
        </ul>
        """
        QMessageBox.about(self, "帮助", help_text)