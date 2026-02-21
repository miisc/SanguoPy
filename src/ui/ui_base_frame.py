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
        self.setMinimumSize(800, 600)
        
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
        
        # 中央区域将用于放置未央宫地图
        self.central_area = self._create_palace_map()
        central_layout.addWidget(self.central_area, 7)  # 占70%宽度
        
        # 右侧信息面板
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
    
    def setup_speed_controls(self, pause_callback, normal_callback, fast_callback, fastest_callback, ultra_callback=None):
        """设置速度控制按钮的回调函数"""
        if hasattr(self, 'pause_btn'):
            self.pause_btn.clicked.connect(pause_callback)
        if hasattr(self, 'normal_speed_btn'):
            self.normal_speed_btn.clicked.connect(normal_callback)
        if hasattr(self, 'fast_speed_btn'):
            self.fast_speed_btn.clicked.connect(fast_callback)
        if hasattr(self, 'fastest_speed_btn'):
            self.fastest_speed_btn.clicked.connect(fastest_callback)
        if hasattr(self, 'ultra_speed_btn') and ultra_callback:
            self.ultra_speed_btn.clicked.connect(ultra_callback)
    
    def update_speed_buttons(self, current_speed):
        """更新速度按钮状态"""
        # 重置所有按钮样式
        if hasattr(self, 'pause_btn'):
            self.pause_btn.setStyleSheet("")
        if hasattr(self, 'normal_speed_btn'):
            self.normal_speed_btn.setStyleSheet("")
        if hasattr(self, 'fast_speed_btn'):
            self.fast_speed_btn.setStyleSheet("")
        if hasattr(self, 'fastest_speed_btn'):
            self.fastest_speed_btn.setStyleSheet("")
        if hasattr(self, 'ultra_speed_btn'):
            self.ultra_speed_btn.setStyleSheet("")
        
        # 高亮当前速度按钮
        if current_speed == "pause" and hasattr(self, 'pause_btn'):
            self.pause_btn.setStyleSheet("background-color: #FF6B6B;")
        elif current_speed == "normal" and hasattr(self, 'normal_speed_btn'):
            self.normal_speed_btn.setStyleSheet("background-color: #4ECDC4;")
        elif current_speed == "fast" and hasattr(self, 'fast_speed_btn'):
            self.fast_speed_btn.setStyleSheet("background-color: #45B7D1;")
        elif current_speed == "fastest" and hasattr(self, 'fastest_speed_btn'):
            self.fastest_speed_btn.setStyleSheet("background-color: #96CEB4;")
        elif current_speed == "ultra" and hasattr(self, 'ultra_speed_btn'):
            self.ultra_speed_btn.setStyleSheet("background-color: #FFD700;")  # 金色背景表示超快速度
    
    def _create_bottom_bar(self):
        """创建底部控制栏"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        frame.setFixedHeight(60)  # 使用固定高度，确保在窗口缩放时保持一致
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(10, 5, 10, 5)  # 添加边距
        
        # 添加按钮
        save_game_btn = QPushButton("保存游戏")
        save_game_btn.clicked.connect(self._on_save_game)
        save_game_btn.setMinimumSize(100, 40)  # 设置最小尺寸
        layout.addWidget(save_game_btn)
        
        load_game_btn = QPushButton("加载游戏")
        load_game_btn.clicked.connect(self._on_load_game)
        load_game_btn.setMinimumSize(100, 40)  # 设置最小尺寸
        layout.addWidget(load_game_btn)
        
        layout.addStretch()
        
        # 添加游戏速度控制按钮
        speed_layout = QHBoxLayout()
        speed_layout.setSpacing(5)  # 添加按钮间距
        
        # 暂停按钮
        self.pause_btn = QPushButton("暂停")
        self.pause_btn.setMinimumSize(60, 30)  # 设置最小尺寸
        speed_layout.addWidget(self.pause_btn)
        
        # 正常速度按钮
        self.normal_speed_btn = QPushButton("正常")
        self.normal_speed_btn.setMinimumSize(60, 30)  # 设置最小尺寸
        speed_layout.addWidget(self.normal_speed_btn)
        
        # 加速按钮
        self.fast_speed_btn = QPushButton("加速")
        self.fast_speed_btn.setMinimumSize(60, 30)  # 设置最小尺寸
        speed_layout.addWidget(self.fast_speed_btn)
        
        # 最快速度按钮
        self.fastest_speed_btn = QPushButton("最快")
        self.fastest_speed_btn.setMinimumSize(60, 30)  # 设置最小尺寸
        speed_layout.addWidget(self.fastest_speed_btn)
        
        # 超快速度按钮
        self.ultra_speed_btn = QPushButton("超快")
        self.ultra_speed_btn.setMinimumSize(60, 30)  # 设置最小尺寸
        speed_layout.addWidget(self.ultra_speed_btn)
        
        layout.addLayout(speed_layout)
        
        help_btn = QPushButton("帮助")
        help_btn.clicked.connect(self._on_help)
        help_btn.setMinimumSize(100, 40)  # 设置最小尺寸
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
        resource_layout.addWidget(resource_label)
        resource_sub_layout = QVBoxLayout()
        resource_sub_layout.addWidget(self.gold_label)
        resource_sub_layout.addWidget(self.food_label)
        resource_layout.addLayout(resource_sub_layout)
        status_layout.addLayout(resource_layout)
        
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
    
    
    def _create_palace_map(self):
        """创建宫殿地图"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        frame.setMinimumSize(600, 400)  # 减小最小尺寸，更适应小窗口
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 10, 10, 10)  # 添加边距
        layout.setSpacing(10)  # 添加间距
        
        # 添加标题
        title = QLabel("未央宫地图")
        title.setFont(QFont("", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setContentsMargins(0, 0, 0, 10)  # 添加底部边距
        layout.addWidget(title)
        
        # 创建宫殿按钮区域 - 使用水平布局放置前朝和后宫两个区域
        palace_layout = QHBoxLayout()
        palace_layout.setSpacing(20)  # 添加区域间距
        
        # 前朝区域
        front_palace_frame = QFrame()
        front_palace_frame.setFrameStyle(QFrame.Box)
        # 设置前朝区域的样式，体现其庄重的特性
        front_palace_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #8B4513;  /* 深棕色边框 */
                border-radius: 5px;
                background-color: #FFF8DC;  /* 米色背景 */
            }
        """)
        front_palace_layout = QVBoxLayout(front_palace_frame)
        front_palace_layout.setContentsMargins(15, 15, 15, 15)  # 增加内边距
        front_palace_layout.setSpacing(10)  # 添加按钮间距
        
        front_title = QLabel("前朝")
        front_title.setFont(QFont("", 14, QFont.Bold))
        front_title.setAlignment(Qt.AlignCenter)
        front_title.setStyleSheet("color: #8B0000;")  # 深红色标题
        front_title.setContentsMargins(0, 0, 0, 10)  # 添加底部边距
        front_palace_layout.addWidget(front_title)
        
        # 宣室殿按钮
        xuanshi_btn = QPushButton("宣室殿")
        xuanshi_btn.clicked.connect(lambda: self.palace_clicked.emit("宣室殿"))
        xuanshi_btn.setMinimumSize(120, 60)  # 增加按钮尺寸
        xuanshi_btn.setToolTip("处理紧急朝会，应对突发事件")  # 添加工具提示
        front_palace_layout.addWidget(xuanshi_btn)
        
        # 承明殿按钮
        chengming_btn = QPushButton("承明殿")
        chengming_btn.clicked.connect(lambda: self.palace_clicked.emit("承明殿"))
        chengming_btn.setMinimumSize(120, 60)  # 增加按钮尺寸
        chengming_btn.setToolTip("处理每月初一的大朝会")  # 添加工具提示
        front_palace_layout.addWidget(chengming_btn)
        
        # 添加弹性空间使宫殿按钮居中
        front_palace_layout.addStretch()
        
        palace_layout.addWidget(front_palace_frame, 1)  # 分配相同的空间
        
        # 添加分隔线，强调前朝后宫的分离
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #8B4513;")  # 深棕色分隔线
        palace_layout.addWidget(separator)
        
        # 后宫区域
        rear_palace_frame = QFrame()
        rear_palace_frame.setFrameStyle(QFrame.Box)
        # 设置后宫区域的样式，体现其柔和的特性
        rear_palace_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #DA70D6;  /* 紫罗兰色边框 */
                border-radius: 5px;
                background-color: #FFF0F5;  /* 淡粉色背景 */
            }
        """)
        rear_palace_layout = QVBoxLayout(rear_palace_frame)
        rear_palace_layout.setContentsMargins(15, 15, 15, 15)  # 增加内边距
        rear_palace_layout.setSpacing(10)  # 添加按钮间距
        
        rear_title = QLabel("后宫")
        rear_title.setFont(QFont("", 14, QFont.Bold))
        rear_title.setAlignment(Qt.AlignCenter)
        rear_title.setStyleSheet("color: #DA70D6;")  # 紫罗兰色标题
        rear_title.setContentsMargins(0, 0, 0, 10)  # 添加底部边距
        rear_palace_layout.addWidget(rear_title)
        
        # 椒房殿按钮
        jiaofang_btn = QPushButton("椒房殿")
        jiaofang_btn.clicked.connect(lambda: self.palace_clicked.emit("椒房殿"))
        jiaofang_btn.setMinimumSize(120, 60)  # 增加按钮尺寸
        jiaofang_btn.setToolTip("后宫管理")  # 添加工具提示
        rear_palace_layout.addWidget(jiaofang_btn)
        
        # 长乐宫按钮
        changle_btn = QPushButton("长乐宫")
        changle_btn.clicked.connect(lambda: self.palace_clicked.emit("长乐宫"))
        changle_btn.setMinimumSize(120, 60)  # 增加按钮尺寸
        changle_btn.setToolTip("皇室事务")  # 添加工具提示
        rear_palace_layout.addWidget(changle_btn)
        
        # 添加弹性空间使宫殿按钮居中
        rear_palace_layout.addStretch()
        
        palace_layout.addWidget(rear_palace_frame, 1)  # 分配相同的空间
        
        layout.addLayout(palace_layout, 1)  # 设置伸缩因子，占据大部分空间
        
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
    
    def update_time_info(self, year, month, day):
        """更新时间信息"""
        self.year_label.setText(str(year))
        self.month_label.setText(str(month))
        self.day_label.setText(str(day))
    
    def update_resource_info(self, gold, food):
        """更新资源信息"""
        self.gold_label.setText(f"钱: {gold}")
        self.food_label.setText(f"粮: {food}")
    
    def show_info(self, title, content):
        """在信息面板显示信息"""
        # 找到信息面板中的标签并更新内容
        for i in range(self.info_panel.layout().count()):
            widget = self.info_panel.layout().itemAt(i).widget()
            if isinstance(widget, QLabel) and widget != self.info_panel.layout().itemAt(0).widget():
                widget.setText(f"<b>{title}</b><br>{content}")
                break
    
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