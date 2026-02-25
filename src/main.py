#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
三国志策略游戏主入口文件
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QTimer
from ui.weiyang_main_window import WeiyangMainWindow as MainWindow

def main():
    """游戏主函数"""
    # 设置高DPI支持
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # 创建QApplication实例
    app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setApplicationName("三国志策略游戏")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("SanGuoGame")
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    # 自动化测试：如果设置环境变量 AUTOFOCUS_TEST，则在短延迟后自动开始一次朝会（用于验证地图聚焦）
    if os.environ.get("AUTOFOCUS_TEST"):
        # 使用单次定时器在UI完全初始化后触发朝会
        QTimer.singleShot(500, lambda: window.game_controller.start_court_meeting())
    
    # 运行应用程序
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()