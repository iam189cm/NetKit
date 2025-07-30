# CI/CD 修复说明

## 问题描述

GitHub Actions CI/CD 流程中出现模块导入错误：
```
ModuleNotFoundError: No module named 'netkit'
```

测试无法找到项目的核心模块，导致所有单元测试失败。

## 问题原因

1. **Python路径配置不正确**：CI环境中Python无法找到项目模块
2. **包未正确安装**：缺少setup.py文件和包安装配置
3. **测试环境配置缺失**：缺少conftest.py配置文件

## 解决方案

### 1. 更新pytest配置 (pytest.ini)

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
pythonpath = 
    .
    netkit
    gui
```

**改动说明**：
- 将`pythonpath = .`改为多行配置
- 明确添加`netkit`和`gui`目录到Python路径

### 2. 创建包安装配置 (setup.py)

创建标准的Python包配置文件，支持：
- 包依赖管理
- 可编辑模式安装 (`pip install -e .`)
- 控制台脚本入口点
- 开发依赖配置

### 3. 更新CI工作流 (.github/workflows/ci.yml)

在依赖安装步骤中添加：
```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    pip install -e .  # 新增：以可编辑模式安装项目
```

### 4. 添加测试配置 (tests/conftest.py)

创建pytest配置文件，包含：
- 自动Python路径设置
- 测试环境初始化
- 通用fixtures定义
- 临时目录管理

## 修复效果

### 修复前
```
ERROR collecting tests/unit/test_netconfig_service.py
ModuleNotFoundError: No module named 'netkit'
```

### 修复后
```
======================================= test session starts ========================================
collected 36 items / 2 deselected / 34 selected

tests/unit/test_netconfig_service.py::TestNetworkInterfaceManagement::test_get_network_interfaces_success PASSED
...
========================== 34 passed, 2 deselected, 35 warnings in 0.15s ===========================
```

## 技术细节

### 1. Python包导入机制

在Python中，模块导入需要满足以下条件之一：
- 模块在`sys.path`中的目录里
- 模块已通过pip安装
- 设置了正确的`PYTHONPATH`环境变量

### 2. pytest pythonpath配置

pytest的`pythonpath`配置会自动添加指定目录到`sys.path`，确保测试可以导入项目模块。

### 3. 可编辑模式安装

`pip install -e .`会：
- 在site-packages中创建.pth文件
- 将项目目录添加到Python路径
- 允许代码更改立即生效，无需重新安装

## 验证步骤

1. **本地验证**：
   ```bash
   python -c "import netkit.services.netconfig; print('Import successful')"
   python -m pytest tests/unit/ -v --tb=short -m "unit"
   ```

2. **CI环境验证**：
   推送代码后检查GitHub Actions执行结果

## 相关文件

- `pytest.ini` - pytest配置
- `setup.py` - 包安装配置
- `tests/conftest.py` - 测试环境配置
- `.github/workflows/ci.yml` - CI工作流配置

## 注意事项

1. **编码问题**：所有文件使用UTF-8编码
2. **路径分隔符**：在Windows CI环境中使用正确的路径分隔符
3. **依赖版本**：确保所有依赖版本兼容
4. **测试标记**：pytest标记配置需要与测试文件中的标记一致

## 后续优化

1. 考虑使用pyproject.toml替代setup.py
2. 添加更多的测试环境配置
3. 优化CI缓存策略
4. 添加代码覆盖率报告上传

---

**修复日期**：2024年12月
**修复版本**：v1.0.0
**测试状态**：✅ 通过