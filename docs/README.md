
# NetKit v2.0.0

[![Release Build](https://github.com/iam189cm/NetKit/actions/workflows/release.yml/badge.svg)](https://github.com/iam189cm/NetKit/actions/workflows/release.yml)
[![GitHub release](https://img.shields.io/github/release/iam189cm/NetKit.svg)](https://github.com/iam189cm/NetKit/releases)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](#-许可证)

一款面向网络工程师的Windows图形化工具箱，提供网络配置管理、连通性测试和路由管理等功能。

## 🚀 功能特性

- **网络配置管理**: 完整的网卡管理、信息显示、IP/DNS配置，支持DHCP和静态配置
- **可视化Ping测试**: 智能动态方格网络状态显示，支持批量IP范围扫描和连续监控
- **静态路由管理**: 路由表查看、添加、删除和修改功能
- **子网计算** (预留): 子网地址计算功能 - 开发中
- **路由跟踪** (预留): 网络路径跟踪功能 - 开发中

## 📁 项目结构

```
NetKit/
├── netkit/                    # 核心业务逻辑模块
│   ├── services/             # 网络服务实现
│   │   ├── netconfig/        # 网络配置服务
│   │   │   ├── interface_manager.py    # 网卡管理
│   │   │   ├── interface_info.py       # 网卡信息获取
│   │   │   ├── ip_configurator.py      # IP配置管理
│   │   │   ├── wmi_engine.py          # WMI查询引擎
│   │   │   └── async_manager.py       # 异步任务管理
│   │   ├── ping/             # Ping测试服务
│   │   │   ├── ping_service.py         # Ping服务核心
│   │   │   ├── ping_executor.py        # Ping执行器
│   │   │   ├── result_parser.py        # 结果解析器
│   │   │   └── ip_parser.py           # IP范围解析
│   │   ├── route/            # 静态路由管理服务
│   │   │   └── route.py      # 路由管理核心服务
│   │   ├── subnet/           # 子网计算服务（预留）
│   │   └── tracert/          # 路由跟踪服务（预留）
│   └── utils/                # 工具模块
│       ├── admin_check.py    # 管理员权限检测
│       ├── network_monitor.py # 网络状态监控
│       └── ui_helper.py      # UI辅助工具
├── gui/                      # 图形用户界面
│   ├── main.py              # 主应用程序窗口
│   ├── views/               # 功能视图模块
│   │   ├── netconfig/       # 网络配置UI组件
│   │   │   ├── netconfig_view.py       # 主配置视图
│   │   │   ├── interface_selector.py   # 网卡选择器
│   │   │   ├── info_display.py         # 信息显示组件
│   │   │   ├── config_form.py          # 配置表单
│   │   │   └── status_display.py       # 状态显示
│   │   ├── ping/            # Ping测试UI组件
│   │   │   ├── visual_ping_view.py     # 可视化Ping界面
│   │   │   ├── grid_cell.py           # 网格单元格组件
│   │   │   ├── scan_controller.py      # 扫描控制器
│   │   │   └── ui_components.py        # UI辅助组件
│   │   ├── route/            # 路由管理UI组件
│   │   │   └── route_view.py      # 路由管理界面
│   │   ├── subnet/           # 子网计算UI组件（预留）
│   │   └── tracert/          # 路由跟踪UI组件（预留）
│   └── assets/              # 资源文件
│       └── style.tcl        # ttkbootstrap样式配置
├── scripts/                 # 构建和工具脚本
│   ├── build.py            # Python构建脚本
│   ├── build.bat           # Windows构建脚本
│   ├── start.py            # 程序启动脚本
│   ├── start.bat           # Windows启动脚本
│   ├── netkit_onefile.spec # 单文件PyInstaller配置
│   ├── netkit_debug.spec   # 调试版PyInstaller配置
│   ├── performance_benchmark.py    # 性能测试脚本
│   ├── test_quick.bat      # 快速测试脚本
│   ├── test_all.bat        # 完整测试脚本
│   ├── test_netconfig.bat  # 网络配置测试脚本
│   ├── test_ping.bat       # Ping功能测试脚本
│   └── test_compatibility.py # 兼容性测试脚本
├── tests/                   # 测试文件
│   ├── netconfig/          # 网络配置功能测试
│   ├── ping/               # Ping功能测试
│   ├── route/              # 路由功能测试
│   ├── gui/                # GUI功能测试
│   ├── utils/              # 工具类测试
│   ├── fixtures/           # 测试数据和工具
│   ├── scripts/            # 测试脚本
│   └── conftest.py         # pytest配置
├── docs/                    # 文档目录
│   ├── README.md           # 项目说明文档
│   └── RELEASE_NOTES.md    # 版本发布说明
├── setup.py                # 项目安装配置
├── requirements.txt        # Python依赖列表
└── pytest.ini             # 测试配置文件
```

## 🛠️ 开发环境

- **Python**: 3.12+
- **GUI框架**: ttkbootstrap (基于tkinter)
- **核心依赖**: 
  - `ttkbootstrap>=1.10.1` - 现代化的tkinter主题框架
  - `psutil>=5.9.8` - 系统和进程监控
  - `WMI>=1.5.1` - Windows管理接口查询
  - `pywin32>=306` - Windows API访问
- **打包工具**: PyInstaller
- **测试框架**: pytest 及相关插件

## 📦 构建说明

### 单文件构建（推荐）
```bash
# 运行构建脚本（Windows）
scripts\build.bat

# 或使用Python构建脚本
python scripts/build.py

# 或手动构建
pyinstaller scripts/netkit_onefile.spec
```

构建成功后，可执行文件将生成在 `dist/NetKit.exe`，发布时会重命名为 `NetKit-v2.0.0.exe`。

### 调试版本构建
```bash
# 构建调试版本（包含控制台输出）
pyinstaller scripts/netkit_debug.spec
```

## 🚀 快速开始

### 开发模式
```bash
# 安装依赖
pip install -r requirements.txt

# 启动程序（Python脚本）
python scripts/start.py

# 或使用Windows批处理脚本
scripts\start.bat
```

### 生产模式
```bash
# 首先构建程序
scripts\build.bat

# 运行构建后的可执行文件
dist\NetKit.exe
```

### 测试运行
```bash
# 快速测试（Windows）
scripts\test_quick.bat

# 完整测试套件
scripts\test_all.bat

# 分模块测试
scripts\test_netconfig.bat  # 网络配置测试
scripts\test_ping.bat       # Ping功能测试

# 或使用pytest直接运行
python -m pytest
```

## ⚠️ 注意事项

- **管理员权限**: 程序需要管理员权限才能正常使用网络配置功能
- **系统要求**: 支持Windows 10及以上版本
- **运行建议**: 右键选择"以管理员身份运行"获得完整功能
- **DPI支持**: 自动适配高分屏显示，支持DPI缩放

## 🔧 主要特性说明

### 网络配置管理
- 支持有线和无线网卡的完整管理
- 自动检测网卡状态和配置信息
- 支持DHCP自动获取和静态IP配置
- 实时网络状态监控和异步操作

### 可视化Ping测试
- 智能IP范围解析（支持CIDR、区间等格式）
- 动态网格状态显示，直观展示网络连通性
- 支持连续监控和批量扫描
- 详细的响应时间统计和历史记录

### 静态路由管理
- 完整的路由表查看功能
- 支持路由的添加、删除和修改
- 自动路由冲突检测和验证
- 支持各种路由类型（默认、静态、直连等）

### 预留功能模块
- **子网计算器**: 子网地址计算和VLSM支持（开发中）
- **路由跟踪**: 网络路径跟踪和可视化分析（开发中）

## 📖 文档

- [版本发布说明](docs/RELEASE_NOTES.md)
- [测试说明](tests/README.md)

## 🤝 贡献

欢迎提交Issue和Pull Request！请确保：
- 代码符合项目规范
- 包含必要的测试用例
- 更新相关文档

## 📄 许可证

MIT License
