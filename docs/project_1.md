# NetKit - 需求与技术规格（v0.1 草案）
---

## 1 项目愿景

一款面向网络工程师的 **Windows** 图形化工具箱，提供常用网络诊断与配置操作，界面采用 **Tkinter + ttkbootstrap Darkly 主题**，支持一键打包为单文件 .exe。

## 2 MVP 功能清单

| 序号 | 功能                | 说明                                                           |                  |
| -- | ----------------- | ------------------------------------------------------------ | ---------------- |
| 1  | **IP 地址快速切换**     | 读取/保存多套 IP、网关、DNS，快速应用；基于 `netsh interface ip set address …` |                  |
| 2  | **Ping 测试**       | 单/多线程 ping（并发不阻塞 GUI），显示 RTT/丢包统计                            |                  |
| 3  | **子网 / VLSM 计算器** | 输入网络地址与需求主机数，输出最优划分；支持 IPv4，预留 IPv6 Backlog                  |                  |
| 4  | **Traceroute**    | 可视化 TTL 路由节点；调用系统 `tracert`                                  |                  |
| 5  | **静态路由管理**        | 列表增删查，调用 \`netsh interface ipv4 add                          | delete route …\` |

> **Backlog**：端口扫描、软路由管理、IPv6 支持、CLI 模式。

## 3 非功能需求

- 默认深色主题，可切换亮色（未来）
- **程序需以管理员权限启动**；若检测到权限不足，将提示用户右键“以管理员身份运行”后退出
- 国际化：v0.1 仅中文，v0.2 增加英文（gettext）
- 单文件安装包（PyInstaller），≥ Python 3.12 运行时已封装
- 许可：主项目 GPL-3.0；商业增值模块单独授权

## 4 技术栈

- **语言**：Python 3.12
- **GUI**：Tkinter + ttkbootstrap（`darkly` 主题）
- **核心库**：`subprocess`, `ipaddress`, `psutil`, `concurrent.futures`
- **打包**：PyInstaller `--onefile --noconsole`
- **更新**：PyUpdater（签名证书保存在私有仓库）
- **CI/CD**：GitHub Actions（Windows runner）
  - Lint ➜ Test ➜ Build ➜ Upload Release

## 5 项目目录结构

```
netkit_py/
├─ netkit/                # 核心逻辑无 GUI 依赖
│  ├─ services/
│  │   ├─ ip_switcher.py
│  │   ├─ ping.py
│  │   ├─ subnet.py
│  │   ├─ traceroute.py
│  │   └─ route.py
│  └─ utils/
│      └─ admin_check.py   # 检测管理员权限
├─ gui/
│  ├─ main.py             # app 入口
│  ├─ views/              # 每个功能一个 ttk.Frame
│  └─ assets/
│      ├─ icons/
│      └─ style.tcl       # ttkbootstrap 自定义样式
├─ tests/                 # pytest 用例
├─ scripts/               # 打包 / 发布脚本
├─ pyproject.toml
└─ README.md
```

## 6 管理员权限方案

程序启动时调用 `ctypes.windll.shell32.IsUserAnAdmin()` 检测权限。

- **若已是管理员** → 继续正常加载 GUI。
- **若非管理员** → 使用 `tkinter.messagebox.showwarning()` 弹窗提示：
  > “检测到当前未以管理员身份运行。请右键本程序图标，选择『以管理员身份运行』后重新启动。” 然后安全退出。

> 注：所有核心操作均基于 `netsh` 命令执行，不再做延迟提权或后台服务方案。

## 7 国际化（i18n）

- 使用 `gettext`；所有字符串放在 `locales/zh_CN/LC_MESSAGES/netkit.po`。
- GUI 通过 `tkinter.StringVar` 结合翻译函数 `_()` 实现动态切换。

## 8 测试 & CI/CD

- **pytest**：为每个 service 编写单元测试，Mock `subprocess` 输出
- **GitHub Actions**：
  ```yaml
  name: CI
  on: [push, pull_request]
  jobs:
    build:
      runs-on: windows-latest
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-python@v5
          with: {python-version: '3.12'}
        - run: pip install -r requirements.txt
        - run: pytest -v
        - run: pyinstaller netkit.spec
        - uses: actions/upload-artifact@v4
          with: {path: dist/*.exe}
  ```

## 9 里程碑

| 日期    | 目标                                         |
| ----- | ------------------------------------------ |
| 07-20 | 初始化仓库 Skeleton + README + GitHub Action 雏形 |
| 07-27 | 完成核心 service（Ping/Subnet/IP 切换）单元测试通过      |
| 08-05 | 完成 GUI MVP v0.1-alpha 发布，同事试用反馈            |
| 08-12 | 集成 PyUpdater，发布 v0.1-beta                  |
| 08-30 | i18n 英文版 + 文档完善，发布 v1.0                    |

---





