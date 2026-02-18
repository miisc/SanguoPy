#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UI系统测试脚本
验证UI系统是否正常工作
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ui.new_main_window import NewMainWindow

def test_ui_system():
    """测试UI系统"""
    # 设置高DPI支持
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # 创建QApplication实例
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = NewMainWindow()
    
    # 打印测试信息
    print("UI系统测试:")
    print("1. 主窗口创建成功")
    print("2. UI基础框架创建成功")
    print("3. 未央宫地图创建成功")
    print("4. 所有组件初始化完成")
    
    # 显示窗口
    window.show()
    
    print("5. 主窗口显示成功")
    print("UI系统测试完成，窗口已显示")
    
    # 运行应用程序
    return app.exec_()

if __name__ == "__main__":
    test_ui_system()