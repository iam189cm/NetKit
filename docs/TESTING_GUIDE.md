# NetKit 测试指南

## 📋 目录
- [测试架构概述](#测试架构概述)
- [测试类型说明](#测试类型说明)
- [运行测试](#运行测试)
- [编写测试](#编写测试)
- [CI/CD集成](#cicd集成)
- [测试最佳实践](#测试最佳实践)

## 🏗️ 测试架构概述

NetKit项目采用分层测试架构，确保代码质量和功能稳定性：

```
tests/
├── unit/                   # 单元测试
├── integration/           # 集成测试  
├── gui/                   # GUI测试
├── performance/           # 性能测试
├── fixtures/              # 测试数据和Fixture
├── conftest.py           # pytest配置
└── run_tests.py          # 测试运行脚本
```

### 测试覆盖率要求
- **目标覆盖率**: 85%
- **最低覆盖率**: 70%
- **核心模块覆盖率**: 90%+

## 🧪 测试类型说明

### 1. 单元测试 (Unit Tests)
- **目标**: 测试单个函数或类的功能
- **位置**: `tests/unit/`
- **标记**: `@pytest.mark.unit`
- **运行时间**: < 1秒/测试

**示例**:
```python
@pytest.mark.unit
def test_validate_ip_config_valid():
    """测试有效IP配置验证"""
    result = validate_ip_config(
        ip='192.168.1.100',
        mask='255.255.255.0',
        gateway='192.168.1.1',
        dns='8.8.8.8'
    )
    assert result['valid'] is True
```

### 2. 集成测试 (Integration Tests)
- **目标**: 测试模块间的交互
- **位置**: `tests/integration/`
- **标记**: `@pytest.mark.integration`
- **运行时间**: < 10秒/测试

### 3. GUI测试 (GUI Tests)
- **目标**: 测试用户界面组件
- **位置**: `tests/gui/`
- **标记**: `@pytest.mark.gui`
- **特点**: 使用Mock避免真实GUI操作

### 4. 性能测试 (Performance Tests)
- **目标**: 验证系统性能指标
- **位置**: `tests/performance/`
- **标记**: `@pytest.mark.performance`
- **指标**: 响应时间、并发处理能力

## 🚀 运行测试

### 本地开发环境

```bash
# 运行所有测试
python tests/run_tests.py --type all --verbose

# 运行特定类型测试
python tests/run_tests.py --type unit --verbose
python tests/run_tests.py --type integration --verbose
python tests/run_tests.py --type gui --verbose
python tests/run_tests.py --type performance --verbose

# 并行运行测试（推荐）
pytest -n auto --dist=worksteal

# 生成覆盖率报告
python tests/run_tests.py --type unit --coverage-only
```

### CI环境
测试在GitHub Actions中自动运行，支持：
- Windows 2022 和 Windows Latest
- Python 3.12
- 并行执行
- 自动覆盖率检查

## ✍️ 编写测试

### 使用测试数据工厂

```python
from tests.fixtures import network_data_factory, valid_ip_configs

def test_with_factory_data(valid_ip_configs):
    """使用测试数据工厂"""
    for config in valid_ip_configs:
        result = validate_ip_config(**config)
        assert result['valid'], f"配置验证失败: {config['description']}"
```

### Mock网络接口

```python
@patch('netkit.services.netconfig.interface_manager.get_async_manager')
def test_network_interface_mock(mock_async_manager, mock_network_adapters):
    """使用Mock网络接口"""
    mock_manager = Mock()
    mock_manager.get_all_adapters_fast.return_value = mock_network_adapters
    mock_async_manager.return_value = mock_manager
    
    interfaces = get_network_interfaces()
    assert len(interfaces) > 0
```

### CI环境适配

```python
@pytest.mark.ci_skip  # CI环境跳过
def test_real_network_operation():
    """需要真实网络环境的测试"""
    pass

def test_ci_compatible(test_environment):
    """CI兼容的测试"""
    if test_environment['is_ci']:
        # 使用Mock数据
        pass
    else:
        # 使用真实数据
        pass
```

## 🔄 CI/CD集成

### 质量门禁
项目设置了严格的质量门禁：

1. **测试通过率**: 100%
2. **代码覆盖率**: ≥85%
3. **代码质量检查**: 通过Flake8、Black、isort
4. **安全扫描**: 通过Bandit和Safety检查

### 自动化流程
```yaml
测试阶段 → 代码质量检查 → 质量门禁 → 构建 → 发布
```

只有通过所有质量检查的代码才能进入构建阶段。

### 测试报告
- **HTML报告**: `reports/`目录
- **覆盖率报告**: `htmlcov/`目录  
- **质量报告**: `reports/quality_report.json`

## 🎯 测试最佳实践

### 1. 测试命名规范
```python
def test_[功能]_[场景]_[期望结果]():
    """测试描述"""
    pass

# 好的例子
def test_validate_ip_config_invalid_ip_returns_error():
    """测试IP配置验证在无效IP时返回错误"""
    pass
```

### 2. 使用描述性断言
```python
# 推荐
assert result['valid'], f"IP配置验证失败: {result.get('error', '')}"

# 不推荐  
assert result['valid']
```

### 3. 测试数据管理
- 使用测试数据工厂创建测试数据
- 避免硬编码测试数据
- 为不同场景准备专门的测试数据集

### 4. Mock使用原则
- Mock外部依赖（网络、文件系统、WMI等）
- 保持Mock的简单性
- 验证Mock的调用

### 5. 性能测试注意事项
- 设置合理的性能基准
- 使用`@pytest.mark.slow`标记耗时测试
- 在CI中跳过长时间运行的性能测试

### 6. 错误处理测试
```python
def test_function_handles_network_error():
    """测试网络错误处理"""
    with patch('requests.get', side_effect=ConnectionError):
        result = network_function()
        assert 'error' in result
        assert 'network' in result['error'].lower()
```

## 🔧 测试工具配置

### pytest配置 (pytest.ini)
```ini
[tool:pytest]
testpaths = tests
addopts = 
    -v --strict-markers --tb=short
    --cov=netkit --cov=gui
    --cov-fail-under=85
    -n auto --dist=worksteal
```

### 覆盖率配置 (.coveragerc)
```ini
[run]
source = netkit, gui
omit = 
    */tests/*
    */venv/*
    setup.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
```

## 🚨 故障排除

### 常见问题

1. **CI环境测试失败**
   - 检查是否使用了真实网络操作
   - 确认Mock配置正确
   - 查看CI环境特定的错误日志

2. **覆盖率不足**
   - 运行 `coverage report --show-missing` 查看未覆盖代码
   - 添加针对性的单元测试
   - 检查是否有死代码

3. **测试运行缓慢**
   - 使用并行执行 `-n auto`
   - 检查是否有不必要的网络请求
   - 优化测试数据准备

4. **GUI测试问题**
   - 确保在CI环境中使用Mock
   - 检查tkinter相关的依赖
   - 使用虚拟显示器

## 📊 测试质量监控

使用 `scripts/test_quality_check.py` 脚本监控测试质量：

```bash
python scripts/test_quality_check.py
```

该脚本会检查：
- 代码覆盖率
- 测试成功率  
- 测试性能
- 生成质量得分

## 🎯 持续改进

### 定期审查
- 每月审查测试覆盖率趋势
- 识别测试薄弱环节
- 更新测试数据和场景

### 测试重构
- 定期重构重复的测试代码
- 提取公共的测试工具函数
- 保持测试代码的可维护性

---

**记住**: 好的测试是代码质量的保障，也是重构和功能迭代的信心来源。投入时间编写高质量的测试，会在长期开发中获得巨大回报。