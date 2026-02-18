#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
历史未央宫主窗口
实现基于历史资料的未央宫全景地图主界面
"""

import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QStatusBar, QMenuBar, QMenu,
                             QAction, QMessageBox, QDialog, QFormLayout, QLineEdit, QTextEdit, QFrame)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QFont
from game.game_controller import GameController
from ui.ui_base_frame import UIBaseFrame
from ui.historical_weiyang_map import HistoricalWeiyangMap
from ui.court_dialog import CourtMeetingDialog


class HistoricalPalaceDialog(QDialog):
    """历史宫殿交互对话框"""
    
    def __init__(self, palace_name, game_controller, parent=None):
        """初始化历史宫殿对话框"""
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
        if self.palace_name == "前殿":
            info_layout.addRow(QLabel("功能:"), QLabel("未央宫的主体建筑，仅处理州郡内政（直接统治区）"))
            info_layout.addRow(QLabel("历史:"), QLabel("建于高祖七年，由萧何主持建造"))
            info_layout.addRow(QLabel("当前状态:"), QLabel("皇帝正在处理州郡政务"))
            info_layout.addRow(QLabel("管辖范围:"), QLabel("直接统治的州郡政务"))
            info_layout.addRow(QLabel("可用人员:"), QLabel("10名大臣、5名文书"))
            
            # 添加处理内政按钮
            handle_admin_btn = QPushButton("处理内政")
            handle_admin_btn.clicked.connect(self._handle_administration)
            info_layout.addRow("", handle_admin_btn)
            
        elif self.palace_name == "椒房殿":
            info_layout.addRow(QLabel("功能:"), QLabel("皇后居所，仅处理后宫事务和继承人培养"))
            info_layout.addRow(QLabel("历史:"), QLabel("位于前殿以北330米，由正殿、配殿和附属建筑组成"))
            info_layout.addRow(QLabel("当前状态:"), QLabel("皇后正在处理后宫事务"))
            info_layout.addRow(QLabel("后宫管理:"), QLabel("妃嫔、宫女、太监管理"))
            info_layout.addRow(QLabel("继承人培养:"), QLabel("太子、公主教育培养"))
            
            # 添加后宫管理按钮
            manage_harem_btn = QPushButton("管理后宫")
            manage_harem_btn.clicked.connect(self._manage_harem)
            info_layout.addRow("", manage_harem_btn)
            
            # 添加继承人培养按钮
            educate_heir_btn = QPushButton("培养继承人")
            educate_heir_btn.clicked.connect(self._educate_heir)
            info_layout.addRow("", educate_heir_btn)
            
        elif self.palace_name == "宣室殿":
            info_layout.addRow(QLabel("功能:"), QLabel("皇帝处理紧急军情和重大危机的场所"))
            info_layout.addRow(QLabel("历史:"), QLabel("位于前殿西南，是皇帝决策和处理紧急事务的地方"))
            info_layout.addRow(QLabel("当前状态:"), QLabel("空闲，等待紧急军情"))
            info_layout.addRow(QLabel("处理范围:"), QLabel("紧急军情、重大危机、突发事件"))
            info_layout.addRow(QLabel("决策机制:"), QLabel("皇帝快速决策，无需朝议"))
            
            # 添加紧急处理按钮
            emergency_btn = QPushButton("处理紧急事务")
            emergency_btn.clicked.connect(self._handle_emergency)
            info_layout.addRow("", emergency_btn)
            
        elif self.palace_name == "太庙":
            info_layout.addRow(QLabel("功能:"), QLabel("仅处理祭祀和重大典礼的皇家宗庙"))
            info_layout.addRow(QLabel("历史:"), QLabel("汉代皇家宗庙，祭祀祖先和举行重大典礼的场所"))
            info_layout.addRow(QLabel("当前状态:"), QLabel("空闲，等待祭祀日期"))
            info_layout.addRow(QLabel("祭祀对象:"), QLabel("汉朝历代先帝先祖"))
            info_layout.addRow(QLabel("典礼类型:"), QLabel("登基大典、封禅大典、宗庙大典"))
            
            # 添加祭祀按钮
            hold_ceremony_btn = QPushButton("举行祭祀")
            hold_ceremony_btn.clicked.connect(self._hold_ceremony)
            info_layout.addRow("", hold_ceremony_btn)
            
        elif self.palace_name == "石渠阁" or self.palace_name == "天禄阁":
            info_layout.addRow(QLabel("功能:"), QLabel("皇室文化建筑，收藏图书典籍"))
            info_layout.addRow(QLabel("历史:"), QLabel("汉代国家图书馆和档案馆，收藏大量珍贵典籍"))
            info_layout.addRow(QLabel("当前状态:"), QLabel("学士正在整理典籍"))
            info_layout.addRow(QLabel("藏书数量:"), QLabel("经史子集万余卷"))
            
        elif self.palace_name == "沧池":
            info_layout.addRow(QLabel("功能:"), QLabel("皇宫池苑区，园林水体"))
            info_layout.addRow(QLabel("历史:"), QLabel("未央宫西南部的重要园林景观"))
            info_layout.addRow(QLabel("当前状态:"), QLabel("池水清澈，荷花盛开"))
            info_layout.addRow(QLabel("景观:"), QLabel("亭台楼阁，景色优美"))
            
        else:
            # 其他宫殿的通用信息
            palace_info = self._get_palace_info(self.palace_name)
            info_layout.addRow(QLabel("功能:"), QLabel(palace_info["function"]))
            info_layout.addRow(QLabel("历史:"), QLabel(palace_info["history"]))
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
        people_list = QLabel(self._get_palace_people(self.palace_name))
        people_list.setWordWrap(True)
        people_layout.addWidget(people_list)
        
        layout.addWidget(people_frame)
        
        # 创建按钮区域
        button_layout = QHBoxLayout()
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def _get_palace_info(self, palace_name):
        """获取宫殿信息"""
        palace_info_map = {
            "承明殿": {
                "function": "接见大臣、处理外交事务的场所",
                "history": "位于前殿东南，是皇帝接见使臣和大臣的重要场所"
            },
            "宣室殿": {
                "function": "皇帝处理政务、朝会的重要场所",
                "history": "位于前殿西南，是皇帝决策和处理日常政务的地方"
            },
            "麒麟阁": {
                "function": "表彰功臣、展示功绩的场所",
                "history": "位于前殿东北，汉代表彰功臣的重要场所"
            },
            "金銮殿": {
                "function": "举行重大典礼的场所",
                "history": "位于前殿西北，皇帝举行册封、祭祀等重大典礼的地方"
            },
            "少府": {
                "function": "管理皇室财政的官署",
                "history": "位于西部，负责管理皇室财务和物资"
            },
            "中央官署": {
                "function": "处理国家政务的中央官署",
                "history": "位于西部，是中央政府处理日常政务的场所"
            },
            "太官署": {
                "function": "管理宫廷饮食的机构",
                "history": "位于西南，负责管理宫廷饮食和宴会"
            },
            "长秋宫": {
                "function": "太后居所",
                "history": "位于东部，是太后居住和处理事务的宫殿"
            },
            "增成宫": {
                "function": "妃嫔居所",
                "history": "位于东部，是皇帝妃嫔居住的宫殿"
            },
            "永巷": {
                "function": "宫女居所",
                "history": "位于东部，是宫女居住和工作的场所"
            },
            "掖庭": {
                "function": "宫中服务人员居所",
                "history": "位于东部，是宫中服务人员居住的地方"
            }
        }
        
        return palace_info_map.get(palace_name, {
            "function": "宫殿功能",
            "history": "宫殿历史"
        })
    
    def _get_palace_people(self, palace_name):
        """获取宫殿内人物"""
        palace_people_map = {
            "前殿": "皇帝 - 刘备\n诸葛亮 - 丞相\n关羽 - 将军\n张飞 - 将军\n赵云 - 将军",
            "椒房殿": "皇后 - 甘夫人\n妃嫔 - 糜夫人\n宫女 - 10人\n太监 - 5人",
            "承明殿": "使臣 - 魏国使者\n使臣 - 吴国使者\n大臣 - 3人\n侍从 - 5人",
            "宣室殿": "大臣 - 5人\n文书 - 10人\n侍从 - 5人",
            "麒麟阁": "功臣画像 - 10幅\n守卫 - 5人\n文书 - 3人",
            "金銮殿": "礼官 - 3人\n乐师 - 10人\n侍从 - 10人",
            "石渠阁": "学士 - 20人\n书吏 - 30人\n守卫 - 5人",
            "天禄阁": "学士 - 15人\n书吏 - 20人\n守卫 - 5人",
            "少府": "官员 - 10人\n会计 - 5人\n库吏 - 10人",
            "中央官署": "官员 - 20人\n文书 - 30人\n侍从 - 10人",
            "太官署": "御厨 - 20人\n帮厨 - 30人\n采买 - 10人",
            "长秋宫": "太后 - 吴夫人\n侍女 - 10人\n太监 - 5人",
            "增成宫": "妃嫔 - 5人\n侍女 - 15人\n太监 - 5人",
            "永巷": "宫女 - 30人\n主管 - 2人\n太监 - 3人",
            "掖庭": "服务人员 - 20人\n主管 - 2人\n太监 - 5人",
            "沧池": "园丁 - 10人\n渔夫 - 5人\n守卫 - 5人"
        }
        
        return palace_people_map.get(palace_name, "张三 - 大臣\n李四 - 将军\n王五 - 文官")
    
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
    
    def _handle_administration(self):
        """处理内政"""
        QMessageBox.information(self, "处理内政", "进入州郡内政处理界面\n可处理：税收、建设、法律、人事等事务")
    
    def _manage_harem(self):
        """管理后宫"""
        QMessageBox.information(self, "后宫管理", "进入后宫管理界面\n可管理：妃嫔册封、宫女安排、太监管理等事务")
    
    def _educate_heir(self):
        """培养继承人"""
        QMessageBox.information(self, "继承人培养", "进入继承人培养界面\n可培养：太子教育、公主婚配、皇子分封等事务")
    
    def _handle_emergency(self):
        """处理紧急事务"""
        QMessageBox.information(self, "紧急事务处理", "进入紧急事务处理界面\n可处理：军情报告、危机应对、突发事件等事务")
    
    def _hold_ceremony(self):
        """举行祭祀"""
        QMessageBox.information(self, "举行祭祀", "进入祭祀典礼界面\n可举行：宗庙祭祀、封禅大典、登基典礼等重大仪式")


class HistoricalWeiyangMainWindow(QMainWindow):
    """历史未央宫主窗口类，实现基于历史资料的主界面"""
    
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        
        # 设置窗口属性
        self.setWindowTitle("三国志策略游戏 - 历史未央宫")
        self.setGeometry(100, 100, 1200, 800)
        
        # 游戏控制器
        self.game_controller = GameController()
        
        # UI组件
        self.ui_base_frame = None
        self.weiyang_map = None
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
        
        # 创建历史未央宫地图
        self.weiyang_map = HistoricalWeiyangMap(self.ui_base_frame.central_area)
        palace_layout = QVBoxLayout(self.ui_base_frame.central_area)
        palace_layout.addWidget(self.weiyang_map)
        
        # 创建地图控制按钮
        control_layout = QHBoxLayout()
        
        zoom_in_btn = QPushButton("放大")
        zoom_in_btn.clicked.connect(self._zoom_in)
        control_layout.addWidget(zoom_in_btn)
        
        zoom_out_btn = QPushButton("缩小")
        zoom_out_btn.clicked.connect(self._zoom_out)
        control_layout.addWidget(zoom_out_btn)
        
        reset_btn = QPushButton("重置视图")
        reset_btn.clicked.connect(self._reset_view)
        control_layout.addWidget(reset_btn)
        
        control_layout.addStretch()
        
        palace_layout.addLayout(control_layout)
        
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
        help_menu = self.menuBar().addMenu("帮助")
        
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
        self.weiyang_map.palace_clicked.connect(self._on_palace_clicked)
    
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
        self.palace_dialog = HistoricalPalaceDialog(palace_name, self.game_controller, self)
        self.palace_dialog.show()
        
        self.status_bar.showMessage(f"进入{palace_name}")
    
    def _get_palace_info(self, palace_name):
        """获取宫殿信息"""
        palace_info_map = {
            "前殿": "未央宫的主体建筑，仅处理州郡内政（直接统治区）。建于高祖七年，由萧何主持建造。",
            "椒房殿": "皇后居所，仅处理后宫事务和继承人培养。位于前殿以北330米，由正殿、配殿和附属建筑组成。",
            "宣室殿": "皇帝处理紧急军情和重大危机的场所。位于前殿西南，是皇帝决策和处理紧急事务的地方。",
            "太庙": "仅处理祭祀和重大典礼的皇家宗庙。汉代皇家宗庙，祭祀祖先和举行重大典礼的场所。",
            "承明殿": "接见大臣、处理外交事务的场所。位于前殿东南，是皇帝接见使臣和大臣的重要场所。",
            "麒麟阁": "表彰功臣、展示功绩的场所。位于前殿东北，汉代表彰功臣的重要场所。",
            "金銮殿": "举行一般典礼的场所。位于前殿西北，皇帝举行册封等一般典礼的地方。",
            "石渠阁": "皇室文化建筑，收藏图书典籍。汉代国家图书馆和档案馆，收藏大量珍贵典籍。",
            "天禄阁": "皇室文化建筑，收藏图书典籍。与石渠阁并称为汉代最重要的文化建筑。",
            "少府": "管理皇室财政的官署。位于西部，负责管理皇室财务和物资。",
            "中央官署": "处理国家政务的中央官署。位于西部，是中央政府处理日常政务的场所。",
            "太官署": "管理宫廷饮食的机构。位于西南，负责管理宫廷饮食和宴会。",
            "长秋宫": "太后居所。位于东部，是太后居住和处理事务的宫殿。",
            "增成宫": "妃嫔居所。位于东部，是皇帝妃嫔居住的宫殿。",
            "永巷": "宫女居所。位于东部，是宫女居住和工作的场所。",
            "掖庭": "宫中服务人员居所。位于东部，是宫中服务人员居住的地方。",
            "沧池": "皇宫池苑区，园林水体。未央宫西南部的重要园林景观，池水清澈，景色优美。"
        }
        
        return palace_info_map.get(palace_name, "宫殿信息暂未更新。")
    
    def _zoom_in(self):
        """放大地图"""
        self.weiyang_map.scale(1.2, 1.2)
    
    def _zoom_out(self):
        """缩小地图"""
        self.weiyang_map.scale(0.8, 0.8)
    
    def _reset_view(self):
        """重置视图"""
        self.weiyang_map.reset_zoom()
    
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
            self.weiyang_map.show()
        else:
            self.weiyang_map.hide()
    
    def _show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, "关于", "三国志策略游戏 v1.0\n\n一个基于历史资料的三国策略游戏。")