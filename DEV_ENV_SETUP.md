# 三国策略游戏 - 开发环境设置指南

## 虚拟环境设置

本项目已配置Python虚拟环境，所有开发和测试都应在此环境中进行。

### 激活虚拟环境

在Windows PowerShell中运行：
```powershell
.\venv\Scripts\activate
```

激活后，命令行提示符前会显示 `(venv)`。

### 安装依赖

依赖已经安装完成，如果需要重新安装：
```bash
pip install -r requirements.txt
```

### 运行项目

#### 运行地图系统测试
```bash
python test_map_system.py
```

#### 运行环境测试
```bash
python test_env.py
```

### 项目结构

```
SanGuoHtmlDemo/
├── venv/                    # Python虚拟环境
├── src/                     # 源代码
│   └── map_system/          # 地图系统模块
├── docs/                    # 文档
│   ├── design/              # 设计文档
│   └── features/            # 功能文档
├── test_map_system.py       # 地图系统测试程序
├── test_env.py              # 环境测试程序
└── requirements.txt         # 项目依赖
```

### 注意事项

1. 始终在虚拟环境中进行开发和测试
2. 不要提交 `venv/` 目录到版本控制系统
3. 如果添加新的依赖，请更新 `requirements.txt` 文件