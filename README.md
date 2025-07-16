
# NETKit-Py

一款面向网络工程师的Windows图形化工具箱，提供常用网络诊断与配置操作。

## 🚀 功能特性

- **IP地址快速切换**: 保存和切换多套网络配置
- **Ping测试**: 单/多线程网络连通性测试
- **子网计算器**: IP地址和子网掩码计算
- **路由追踪**: 可视化网络路径追踪
- **静态路由管理**: 路由表的增删查改

## 📁 项目结构

```
netkit_py/
├── netkit/                    # 核心逻辑模块（无GUI依赖）
│   ├── services/             # 网络服务实现
│   │   ├── ip_switcher.py    # IP切换服务
│   │   ├── ping.py           # Ping测试服务
│   │   ├── subnet.py         # 子网计算服务
│   │   ├── traceroute.py     # 路由追踪服务
│   │   └── route.py          # 路由管理服务
│   └── utils/                # 工具模块
│       └── admin_check.py    # 管理员权限检测
├── gui/                      # 图形用户界面
│   ├── main.py              # 应用程序入口
│   ├── views/               # 各功能界面
│   │   ├── ip_switcher_view.py
│   │   ├── ping_view.py
│   │   ├── subnet_view.py
│   │   ├── traceroute_view.py
│   │   └── route_view.py
│   └── assets/              # 资源文件
│       ├── icons/           # 图标文件
│       └── style.tcl        # 自定义样式
├── tests/                   # 测试文件
├── scripts/                 # 构建和部署脚本
│   ├── build.bat           # 原始构建脚本
│   ├── build.ps1           # PowerShell构建脚本
│   ├── build_onefile.bat   # 单文件构建脚本
│   ├── netkit.spec         # PyInstaller配置
│   └── netkit_onefile.spec # 单文件PyInstaller配置
├── docs/                    # 文档目录
│   ├── project_1.md        # 项目需求文档
│   └── 使用说明_单文件版本.md # 使用说明
├── releases/                # 发布文件
│   └── NETKit-Py.exe       # 单文件可执行程序
├── start_netkit.py         # 启动脚本
├── start_netkit.bat        # Windows启动脚本
├── pyproject.toml          # 项目配置
├── requirements.txt        # 依赖列表
└── README.md              # 项目说明
```

## 🛠️ 开发环境

- **Python**: 3.12+
- **GUI框架**: Tkinter + ttkbootstrap
- **核心依赖**: psutil, subprocess, ipaddress
- **打包工具**: PyInstaller

## 📦 构建说明

### 单文件构建
```bash
# 运行构建脚本
scripts/build_onefile.bat

# 或手动构建
pyinstaller scripts/netkit_onefile.spec
```

### 多文件构建
```bash
# 运行构建脚本
scripts/build.bat

# 或手动构建
pyinstaller scripts/netkit.spec
```

## 🚀 快速开始

### 开发模式
```bash
# 安装依赖
pip install -r requirements.txt

# 运行程序
python start_netkit.py
```

### 生产模式
直接运行 `releases/NETKit-Py.exe`

## ⚠️ 注意事项

- 程序需要管理员权限才能正常使用所有功能
- 支持Windows 10及以上版本
- 建议右键选择"以管理员身份运行"

## 📖 文档

- [项目需求文档](docs/project_1.md)
- [使用说明](docs/使用说明_单文件版本.md)

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

GPL-3.0 License
