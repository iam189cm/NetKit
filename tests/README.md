# NetKit 测试指南

本文档介绍如何运行NetKit项目的各种测试。

## 🎯 测试覆盖范围

本项目包含以下类型的测试：

### 1. 单元测试 (Unit Tests)
- **位置**: `tests/unit/`
- **覆盖**: 服务层函数和类的独立测试
- **目标覆盖率**: 85%以上
- **测试内容**:
  - 网络接口获取和解析
  - IP配置验证
  - 配置文件管理
  - 网络冲突检查
  - 错误处理

### 2. GUI测试 (GUI Tests)
- **位置**: `tests/gui/`
- **覆盖**: 用户界面组件和交互测试
- **测试内容**:
  - 界面组件初始化
  - 用户输入验证
  - 按钮点击响应
  - 状态显示更新
  - 完整工作流程

### 3. 集成测试 (Integration Tests)
- **位置**: `tests/integration/`
- **覆盖**: 服务层与界面层的完整交互
- **测试内容**:
  - 端到端配置流程
  - 错误处理集成
  - 并发操作测试
  - 配置保存和加载

### 4. 性能测试 (Performance Tests)
- **位置**: `tests/performance/`
- **覆盖**: 系统性能和响应时间测试
- **测试内容**:
  - 基准性能测试
  - 大量数据处理
  - 内存使用监控
  - 响应时间验证

### 5. 压力测试 (Stress Tests)
- **位置**: `tests/performance/`
- **覆盖**: 极限条件下的系统稳定性
- **测试内容**:
  - 高并发操作
  - 内存泄漏检测
  - 长时间运行测试
  - 错误恢复能力

## 🚀 运行测试

### 方法1: 使用批处理文件 (推荐)

```bash
# Windows
run_tests.bat
```

选择相应的测试类型：
1. 单元测试
2. 集成测试  
3. GUI测试
4. 性能测试
5. 压力测试
6. 所有测试
7. 快速测试（不包含慢速测试）
8. 仅生成覆盖率报告

### 方法2: 使用Python脚本

```bash
# 运行所有测试
python scripts/run_tests.py --type all --verbose

# 运行单元测试
python scripts/run_tests.py --type unit --verbose

# 运行性能测试（包含慢速测试）
python scripts/run_tests.py --type performance --verbose --include-slow

# 仅生成覆盖率报告
python scripts/run_tests.py --coverage-only
```

### 方法3: 直接使用pytest

```bash
# 运行单元测试
pytest tests/unit/ -v -m "unit" --cov=netkit --cov=gui

# 运行GUI测试
pytest tests/gui/ -v -m "gui"

# 运行性能测试
pytest tests/performance/ -v -m "performance"

# 运行特定测试文件
pytest tests/unit/test_ip_switcher_service.py -v
```

## 📊 测试报告

运行测试后，会生成以下报告：

### HTML测试报告
- **位置**: `reports/`
- **内容**: 详细的测试结果、失败原因、执行时间
- **文件**:
  - `unit_report.html` - 单元测试报告
  - `integration_report.html` - 集成测试报告
  - `gui_report.html` - GUI测试报告
  - `performance_report.html` - 性能测试报告

### 覆盖率报告
- **位置**: `htmlcov/`
- **入口**: `htmlcov/index.html`
- **内容**: 代码覆盖率统计、未覆盖代码行
- **目标**: 85%以上覆盖率

### XML报告
- **位置**: `coverage.xml`
- **用途**: CI/CD集成、代码质量工具

## 🔧 测试配置

### pytest配置
测试配置在 `pytest.ini` 文件中：

```ini
[tool:pytest]
testpaths = tests
addopts = 
    -v
    --cov=netkit
    --cov=gui
    --cov-report=html
    --cov-fail-under=85
markers =
    unit: 单元测试
    integration: 集成测试
    gui: GUI测试
    performance: 性能测试
    slow: 慢速测试
    windows: Windows特定测试
```

### 测试标记 (Markers)
使用pytest标记来分类测试：

```python
@pytest.mark.unit          # 单元测试
@pytest.mark.integration   # 集成测试
@pytest.mark.gui           # GUI测试
@pytest.mark.performance   # 性能测试
@pytest.mark.slow          # 慢速测试
@pytest.mark.windows       # Windows特定测试
```

## 🛠️ 开发测试

### 添加新测试
1. 选择合适的测试类型目录
2. 创建以 `test_` 开头的文件
3. 编写测试函数（以 `test_` 开头）
4. 添加适当的pytest标记
5. 使用测试数据（`tests/test_data.py`）

### 测试数据
测试数据统一管理在 `tests/test_data.py`：

```python
from tests.test_data import (
    VALID_IP_CONFIGS,      # 有效IP配置
    INVALID_IP_CONFIGS,    # 无效IP配置
    MOCK_NETWORK_INTERFACES,  # 模拟网络接口
    PERFORMANCE_TEST_DATA,    # 性能测试数据
    STRESS_TEST_DATA         # 压力测试数据
)
```

### Mock和模拟
使用 `unittest.mock` 模拟系统调用：

```python
from unittest.mock import patch, MagicMock

@patch('subprocess.run')
def test_network_operation(mock_run):
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "mock output"
    # 测试代码
```

## 🔍 调试测试

### 运行特定测试
```bash
# 运行特定测试类
pytest tests/unit/test_ip_switcher_service.py::TestIPConfigValidation -v

# 运行特定测试方法
pytest tests/unit/test_ip_switcher_service.py::TestIPConfigValidation::test_validate_ip_config_valid -v
```

### 调试失败的测试
```bash
# 详细输出
pytest tests/unit/ -v --tb=long

# 在第一个失败处停止
pytest tests/unit/ -x

# 显示本地变量
pytest tests/unit/ --tb=short -l
```

### 性能分析
```bash
# 运行性能测试
pytest tests/performance/ -v --benchmark-only

# 生成性能报告
pytest tests/performance/ --benchmark-histogram
```

## 🚦 CI/CD集成

### GitHub Actions
项目配置了自动化测试，在以下情况触发：
- 推送到 `main` 分支
- 创建Pull Request
- 发布新版本

### 测试矩阵
- **操作系统**: Windows 2019 (Win10), Windows 2022 (Win11)
- **Python版本**: 3.12
- **测试类型**: 单元测试、集成测试、GUI测试、性能测试

### 覆盖率要求
- **最低覆盖率**: 85%
- **失败处理**: 覆盖率不足时构建失败
- **报告上传**: 自动上传到Codecov

## 📝 测试最佳实践

1. **测试命名**: 使用描述性的测试名称
2. **测试隔离**: 每个测试独立运行，不依赖其他测试
3. **Mock使用**: 模拟外部依赖，确保测试可重复
4. **边界测试**: 测试边界条件和异常情况
5. **性能测试**: 关注关键路径的性能表现
6. **文档更新**: 添加新功能时同步更新测试

## 🆘 常见问题

### Q: 测试运行缓慢
A: 使用 `--include-slow` 参数控制是否运行慢速测试

### Q: GUI测试失败
A: 确保在支持图形界面的环境中运行，或使用虚拟显示

### Q: 覆盖率不足
A: 查看 `htmlcov/index.html` 找到未覆盖的代码行

### Q: 模拟命令失败
A: 检查mock配置，确保返回值格式正确

### Q: 权限错误
A: 某些测试需要管理员权限，请以管理员身份运行

## 📞 支持

如有测试相关问题，请：
1. 查看测试报告了解详细错误信息
2. 检查测试数据和mock配置
3. 参考现有测试用例
4. 提交Issue描述问题 