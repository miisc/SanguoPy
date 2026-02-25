#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
朝会2D地图小部件
以正视图渲染城市、关隘和道路，支持以指定位置为中心显示小范围地图。

坐标系说明：
  - 逻辑坐标：与 cities.json 中 x/y 相同，范围约 0-800 × 0-600
  - 网格坐标：50×50 格，转换公式 lx = gx/50*800，ly = gy/50*600
  - 视口：显示逻辑坐标中以 focal 为中心、大小为 view_range×view_range 的矩形，
           并将其缩放到 widget 像素尺寸
"""

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import (QPainter, QColor, QPen, QBrush,
                         QFont, QFontMetrics, QPainterPath)

# ─────────────────────────────────────────────
# 静态地图数据
# ─────────────────────────────────────────────

# 逻辑地图尺寸（与 cities.json 坐标对应）
MAP_W = 800
MAP_H = 600

# 城市数据（与 cities.json 保持一致，这里内嵌以避免文件 IO 依赖）
CITIES = {
    "luoyang":  {"name": "洛阳",  "x": 400, "y": 300, "faction": "wei"},
    "chengdu":  {"name": "成都",  "x": 200, "y": 420, "faction": "shu"},
    "jianye":   {"name": "建业",  "x": 610, "y": 410, "faction": "wu"},
    "chang'an": {"name": "长安",  "x": 290, "y": 240, "faction": "wei"},
    "xuchang":  {"name": "许昌",  "x": 460, "y": 330, "faction": "wei"},
}

# 关隘数据（逻辑坐标）
PASSES = [
    {"name": "虎牢关", "x": 430, "y": 310},   # 洛阳→许昌之间
    {"name": "函谷关", "x": 345, "y": 270},   # 长安→洛阳要道
    {"name": "潼关",   "x": 310, "y": 255},   # 长安以东
    {"name": "街亭",   "x": 245, "y": 320},   # 成都→长安途中
]

# 道路（城市 ID 两端点，以及道路名称）
ROADS = [
    ("luoyang",  "xuchang",  "官道"),
    ("luoyang",  "chang'an", "官道"),
    ("luoyang",  "jianye",   "官道"),
    ("xuchang",  "jianye",   "官道"),
    ("chang'an", "chengdu",  "蜀道"),
    ("chengdu",  "jianye",   "水路"),
]

# 势力颜色
FACTION_COLORS = {
    "wei": QColor(70, 130, 180),    # 钢蓝
    "shu": QColor(60, 160, 80),     # 草绿
    "wu":  QColor(200, 100, 40),    # 橙红
}

# 网格坐标 → 逻辑坐标
def grid_to_logical(gx: float, gy: float):
    return gx / 50.0 * MAP_W, gy / 50.0 * MAP_H


class CourtTopDownMapWidget(QWidget):
    """2D 正视图地图小部件，用于朝会界面嵌入展示。"""

    # 默认视口半径（逻辑坐标单位）；越小则越放大
    DEFAULT_VIEW_RANGE = 260

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(100)
        # focal 为逻辑坐标中心点
        self._focal_x = MAP_W / 2
        self._focal_y = MAP_H / 2
        self._view_range = self.DEFAULT_VIEW_RANGE
        # 可选高亮点（逻辑坐标）
        self._highlight_x = None
        self._highlight_y = None

    # ── 公共接口 ──────────────────────────────

    def center_on_grid(self, gx: float, gy: float, view_range: int = DEFAULT_VIEW_RANGE):
        """以网格坐标 [gx, gy] 为中心，view_range 为视口半径（逻辑单位）。"""
        lx, ly = grid_to_logical(gx, gy)
        self._focal_x = lx
        self._focal_y = ly
        self._highlight_x = lx
        self._highlight_y = ly
        self._view_range = view_range
        self.update()

    def center_on_city(self, city_id: str, view_range: int = DEFAULT_VIEW_RANGE):
        """以城市 ID 为中心。"""
        city = CITIES.get(city_id)
        if city:
            self._focal_x = city["x"]
            self._focal_y = city["y"]
            self._highlight_x = city["x"]
            self._highlight_y = city["y"]
            self._view_range = view_range
            self.update()

    def reset(self):
        """重置到全图视图。"""
        self._focal_x = MAP_W / 2
        self._focal_y = MAP_H / 2
        self._view_range = max(MAP_W, MAP_H) // 2 + 50
        self._highlight_x = None
        self._highlight_y = None
        self.update()

    # ── 内部绘制 ──────────────────────────────

    def _logical_to_widget(self, lx: float, ly: float):
        """将逻辑坐标映射到 widget 像素坐标，保持宽高比不失真。
        view_range 为 Y 轴半径，X 轴半径按控件宽高比自动缩放。"""
        vr = self._view_range
        ww = max(self.width(), 1)
        wh = max(self.height(), 1)
        aspect = ww / wh
        vx_half = vr * aspect   # X 方向视口随控件宽高比拉伸，避免地图横向压缩
        vy_half = vr
        vx0 = self._focal_x - vx_half
        vy0 = self._focal_y - vy_half
        vx1 = self._focal_x + vx_half
        vy1 = self._focal_y + vy_half
        px = (lx - vx0) / (vx1 - vx0) * ww
        py = (ly - vy0) / (vy1 - vy0) * wh
        return px, py

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        self._draw_background(painter)
        self._draw_roads(painter)
        self._draw_passes(painter)
        self._draw_cities(painter)
        if self._highlight_x is not None:
            self._draw_highlight(painter)
        self._draw_border(painter)
        painter.end()

    def _draw_background(self, painter: QPainter):
        """绘制地形底色（简单渐变）。"""
        painter.fillRect(self.rect(), QColor(210, 230, 185))  # 浅黄绿草地

    def _draw_roads(self, painter: QPainter):
        """绘制道路。"""
        road_pen = {
            "官道": QPen(QColor(160, 120, 60), 2.5, Qt.SolidLine),
            "蜀道": QPen(QColor(130, 90,  50), 1.8, Qt.DashLine),
            "水路": QPen(QColor(80,  140, 200), 2.0, Qt.DotLine),
        }
        for (c1_id, c2_id, road_type) in ROADS:
            c1 = CITIES.get(c1_id)
            c2 = CITIES.get(c2_id)
            if not c1 or not c2:
                continue
            x1, y1 = self._logical_to_widget(c1["x"], c1["y"])
            x2, y2 = self._logical_to_widget(c2["x"], c2["y"])
            pen = road_pen.get(road_type, road_pen["官道"])
            painter.setPen(pen)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

    def _draw_passes(self, painter: QPainter):
        """绘制关隘（▲ 三角标记 + 名称）。"""
        sz = 8
        for p in PASSES:
            px, py = self._logical_to_widget(p["x"], p["y"])
            # 只绘制视口内的关隘
            if not (-40 < px < self.width() + 40 and -40 < py < self.height() + 40):
                continue
            # 绘制三角形
            path = QPainterPath()
            path.moveTo(px, py - sz)
            path.lineTo(px + sz, py + sz)
            path.lineTo(px - sz, py + sz)
            path.closeSubpath()
            painter.setBrush(QBrush(QColor(180, 50, 30)))
            painter.setPen(QPen(QColor(100, 20, 10), 1))
            painter.drawPath(path)
            # 名称
            font = QFont("", 8, QFont.Bold)
            painter.setFont(font)
            painter.setPen(QColor(80, 10, 10))
            painter.drawText(int(px) - 18, int(py) + sz + 13, p["name"])

    def _draw_cities(self, painter: QPainter):
        """绘制城市（方块 + 名称）。"""
        sz = 10
        font = QFont("", 9, QFont.Bold)
        painter.setFont(font)
        for city_id, city in CITIES.items():
            cx, cy = self._logical_to_widget(city["x"], city["y"])
            if not (-40 < cx < self.width() + 40 and -40 < cy < self.height() + 40):
                continue
            color = FACTION_COLORS.get(city["faction"], QColor(150, 150, 150))
            # 城市方块
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(Qt.black, 1.5))
            painter.drawRect(int(cx) - sz // 2, int(cy) - sz // 2, sz, sz)
            # 城墙轮廓（小凸出）
            inset = 3
            for dx, dy in [(-sz, 0), (sz, 0), (0, -sz), (0, sz)]:
                painter.drawRect(int(cx + dx) - inset, int(cy + dy) - inset,
                                 inset * 2, inset * 2)
            # 城市名称（白底黑字）
            fm = QFontMetrics(font)
            text_w = fm.horizontalAdvance(city["name"])
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(255, 255, 255, 180)))
            painter.drawRect(int(cx) - text_w // 2 - 2, int(cy) + sz + 2,
                             text_w + 4, fm.height())
            painter.setPen(QColor(20, 20, 20))
            painter.drawText(int(cx) - text_w // 2, int(cy) + sz + 2 + fm.ascent(), city["name"])

    def _draw_highlight(self, painter: QPainter):
        """绘制焦点位置的高亮标记（红色脉冲环 + 十字）。"""
        hx, hy = self._logical_to_widget(self._highlight_x, self._highlight_y)
        r = 18
        # 外环
        painter.setPen(QPen(QColor(220, 40, 40, 180), 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(QPointF(hx, hy), r, r)
        # 内点
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(220, 40, 40, 200)))
        painter.drawEllipse(QPointF(hx, hy), 4, 4)
        # 十字线
        pen = QPen(QColor(220, 40, 40, 160), 1, Qt.DashLine)
        painter.setPen(pen)
        painter.drawLine(int(hx) - r - 8, int(hy), int(hx) + r + 8, int(hy))
        painter.drawLine(int(hx), int(hy) - r - 8, int(hx), int(hy) + r + 8)

    def _draw_border(self, painter: QPainter):
        """绘制地图边框。"""
        painter.setPen(QPen(QColor(100, 70, 30), 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(1, 1, self.width() - 2, self.height() - 2)
