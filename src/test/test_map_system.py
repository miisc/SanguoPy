"""
地图系统测试应用程序

用于测试基础地图框架与伪3D渲染功能
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from src.map_system import MapView, TerrainType


class MapTestWindow(QMainWindow):
    """地图测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("三国策略游戏 - 地图系统测试")
        self.setGeometry(100, 100, 1000, 800)
        
        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # 创建信息面板
        info_panel = self._create_info_panel()
        layout.addWidget(info_panel)
        
        # 创建地图视图
        self.map_view = MapView(50, 50)
        layout.addWidget(self.map_view)
        
        # 连接信号
        self.map_view.tile_clicked.connect(self.on_tile_clicked)
        self.map_view.tile_hovered.connect(self.on_tile_hovered)
    
    def _create_info_panel(self):
        """创建信息面板"""
        panel = QWidget()
        panel.setMaximumHeight(100)
        layout = QHBoxLayout()
        panel.setLayout(layout)
        
        # 标题
        title = QLabel("基础地图框架与伪3D渲染测试")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # 地形信息标签
        self.terrain_info = QLabel("点击或悬停在地形块上查看信息")
        self.terrain_info.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.terrain_info)
        
        return panel
    
    def on_tile_clicked(self, grid_x: int, grid_y: int, terrain_type: TerrainType):
        """处理地形块点击事件
        
        Args:
            grid_x: 网格X坐标
            grid_y: 网格Y坐标
            terrain_type: 地形类型
        """
        self.terrain_info.setText(
            f"点击: ({grid_x}, {grid_y}) - {terrain_type.name_cn} "
            f"(移动成本: {terrain_type.move_cost}, 防御加成: {terrain_type.defense_bonus})"
        )
    
    def on_tile_hovered(self, grid_x: int, grid_y: int, terrain_type: TerrainType):
        """处理地形块悬停事件
        
        Args:
            grid_x: 网格X坐标
            grid_y: 网格Y坐标
            terrain_type: 地形类型
        """
        self.terrain_info.setText(
            f"悬停: ({grid_x}, {grid_y}) - {terrain_type.name_cn}"
        )


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    window = MapTestWindow()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()