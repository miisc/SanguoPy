#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试虚拟环境是否正常工作
"""

import sys

def main():
    print(f"Python版本: {sys.version}")
    print("虚拟环境测试成功!")
    
    # 测试PyQt5是否正确安装
    try:
        from PyQt5.QtWidgets import QApplication
        print("PyQt5导入成功!")
        
        # 创建一个简单的应用程序实例
        app = QApplication([])
        print("QApplication创建成功!")
        
        # 不显示窗口，直接退出
        print("测试完成，退出程序。")
    except ImportError as e:
        print(f"PyQt5导入失败: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())