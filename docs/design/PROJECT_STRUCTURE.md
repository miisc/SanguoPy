# 三国志策略游戏项目结构

## 1. 项目根目录

```
SanGuoHtmlDemo/
├── main.py                 # 主入口文件
├── README.md              # 项目简要说明
├── requirements.txt       # Python依赖声明
├── .gitignore            # Git忽略文件
├── PROJECT_STRUCTURE.md   # 本文件 - 项目结构说明
├── game/                 # 游戏核心模块
├── ui/                   # 用户界面组件
├── data/                 # 游戏数据文件
├── resources/            # 资源文件
└── docs/                 # 文档目录
```

## 2. 游戏核心模块 (game/)

### 2.1 核心文件
- `__init__.py` - 包初始化文件
- `game_controller.py` - 游戏控制器 (Controller)
- `game_model.py` - 游戏数据模型 (Model)
- `game_timer.py` - 游戏时间控制器

### 2.2 系统模块
- `court_meeting.py` - 朝会系统
- `military.py` - 军事系统
- `road_system.py` - 道路系统
- `ai_system.py` - AI决策系统
- `event_system.py` - 事件系统

### 2.3 数据模型
- `city.py` - 城池数据模型
- `general.py` - 武将数据模型
- `army.py` - 军队数据模型
- `technology.py` - 科技数据模型

## 3. 用户界面组件 (ui/)

### 3.1 主要组件
- `__init__.py` - 包初始化文件
- `main_window.py` - 主窗口
- `map_view.py` - 地图视图
- `map_items.py` - 地图图形项

### 3.2 对话框组件
- `court_dialog.py` - 朝会对话框
- `city_info_dialog.py` - 城池信息对话框
- `general_info_dialog.py` - 武将信息对话框
- `army_movement_dialog.py` - 军队移动对话框

### 3.3 渲染器
- `map_renderer.py` - 地图渲染器
- `road_renderer.py` - 道路渲染器
- `army_renderer.py` - 军队渲染器

## 4. 游戏数据 (data/)

### 4.1 数据文件
- `cities.json` - 城池数据
- `generals.json` - 武将数据
- `roads.json` - 道路数据
- `events.json` - 事件数据
- `technologies.json` - 科技数据

### 4.2 数据格式
所有数据文件采用JSON格式，便于维护和扩展。

## 5. 资源文件 (resources/)

### 5.1 图片资源
- `images/` - 游戏图片、图标、背景等

### 5.2 样式表
- `styles/` - PyQt样式表 (QSS文件)
  - `main_style.qss` - 主界面样式
  - `court_style.qss` - 朝会界面样式
  - `map_style.qss` - 地图界面样式

### 5.3 音频资源 (可选)
- `sounds/` - 游戏音效和背景音乐

## 6. 文档目录 (docs/)

### 6.1 设计文档
- `design/`
  - `需求文档.md` - 完整功能需求
  - `技术实现规范.md` - 技术架构说明

### 6.2 功能说明
- `features/`
  - `ARMY_ROAD_MOVEMENT.md` - 军队道路移动
  - `COURT_MEETING_SYSTEM.md` - 朝会系统
  - `REALTIME_UPDATE.md` - 实时更新系统
  - `ROAD_SYSTEM.md` - 道路系统
  - `COURT_MEETING_QUICKSTART.md` - 朝会快速开始

### 6.3 开发阶段
- `phases/` - 项目实施阶段文档

### 6.4 测试结果
- `tests/` - 测试结果和报告

## 7. 架构说明

### 7.1 MVC架构
- **Model**: `game/` 目录下的所有数据和逻辑
- **View**: `ui/` 目录下的所有界面组件
- **Controller**: `game_controller.py` 协调Model和View

### 7.2 依赖关系
- `main.py` → `game_controller.py`
- `game_controller.py` → `game_model.py` + 所有系统模块
- `ui/` 组件 → `game_controller.py` (通过信号槽通信)

### 7.3 信号槽机制
- 游戏状态变化 → UI更新
- 用户操作 → 游戏逻辑处理
- 时间流逝 → 游戏状态更新

## 8. 开发流程

### 8.1 环境搭建
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# 安装依赖
pip install -r requirements.txt

# 运行游戏
python main.py
```

### 8.2 代码规范
- 使用Python 3.8+语法
- 遵循PEP 8代码风格
- 类名使用大驼峰命名法
- 方法名使用小驼峰命名法
- 变量名使用下划线命名法

### 8.3 测试策略
- 单元测试: `test/` 目录 (待创建)
- 集成测试: 手动测试游戏流程
- UI测试: 验证界面交互正常

## 9. 扩展性设计

### 9.1 插件系统
- 数据文件可独立修改
- 系统模块可插拔
- 支持Mod扩展

### 9.2 多平台支持
- Windows: 原生支持
- macOS: 需要PyQt6适配
- Linux: 需要依赖库安装

### 9.3 网络功能
- 预留网络通信接口
- 支持多人对战扩展
- 云存档功能预留

## 10. 版本管理

### 10.1 Git分支策略
- `main`: 稳定版本
- `develop`: 开发版本
- `feature/*`: 功能分支
- `hotfix/*`: 紧急修复分支

### 10.2 发布流程
1. 功能开发完成
2. 代码审查
3. 测试验证
4. 合并到develop
5. 发布候选版本
6. 最终测试
7. 合并到main
8. 打包发布

## 更新日志

### 2026-02-15
- ✅ 创建完整的PyQt桌面应用项目结构
- ✅ 定义MVC架构和模块划分
- ✅ 规范文件组织和命名约定
- 🔄 **技术栈统一**: 全面从Web技术栈迁移至PyQt桌面应用