# NetKit 测试架构 (重构版)

## 📋 概述

NetKit 测试架构已完全重构，采用**本机优先**的测试策略，专注于真实环境下的功能验证。

## 🏗️ 测试目录结构

```
tests/
├── netconfig/              # 网络配置功能测试
│   ├── test_netconfig_service.py      # 网络配置服务测试
│   ├── test_netconfig_integration.py  # 网络配置集成测试
│   └── test_netconfig_e2e.py         # 端到端测试
├── ping/                   # Ping功能测试
│   └── test_ping_service.py          # Ping服务测试
├── route/                  # 路由功能测试
│   └── test_route_service.py         # 路由服务测试
├── subnet/                 # 子网计算功能测试
│   └── test_subnet_service.py        # 子网计算服务测试
├── gui/                    # GUI功能测试
│   └── test_main_window.py           # 主窗口测试
├── utils/                  # 工具类测试
│   ├── test_admin_check.py           # 管理员权限检查
│   └── test_network_monitor.py       # 网络监控工具
├── fixtures/               # 测试数据和工具
├── scripts/                # 测试脚本
├── conftest.py            # pytest配置 (简化版)
└── README.md              # 本文档
```

## 🚀 运行测试

### **快速测试**
```bash
# 快速验证核心功能
scripts/test_quick.bat
```

### **完整测试**
```bash
# 运行所有功能测试
scripts/test_all.bat
```

### **分模块测试**
```bash
# 网络配置功能测试
scripts/test_netconfig.bat

# Ping功能测试
scripts/test_ping.bat

# 子网计算功能测试
python -m pytest tests/subnet/ -v

# 直接使用pytest
python -m pytest tests/netconfig/ -v
python -m pytest tests/ping/ -v
python -m pytest tests/subnet/ -v
```

## 🎯 测试策略

### **核心原则**
1. **本机真实环境测试** - 所有测试在开发者本机真实环境中运行
2. **功能导向** - 按功能模块组织测试，而非按测试类型
3. **简化配置** - 移除复杂的CI环境适配逻辑
4. **开发者友好** - 提供简单易用的测试脚本

### **CI/CD职责重新定义**
- ✅ **自动构建** - 编译和打包
- ✅ **代码质量检查** - Linting和格式化
- ✅ **自动发布** - 发布到GitHub Releases
- ❌ **功能测试** - 由开发者本机负责

## 🔧 测试环境要求

### **系统要求**
- Windows 10/11
- Python 3.12+
- 管理员权限 (网络配置测试需要)

### **网络要求**
- 能够访问公共DNS (8.8.8.8, 1.1.1.1)
- 至少一个活动的网络接口
- 能够执行ping命令

## 📝 编写测试

### **测试文件命名规范**
```
test_[模块名]_[测试类型].py

例如：
- test_netconfig_service.py      # 网络配置服务测试
- test_ping_service.py          # Ping服务测试
- test_netconfig_integration.py # 网络配置集成测试
- test_netconfig_e2e.py         # 端到端测试
```

### **测试标记**
```python
@pytest.mark.netconfig      # 网络配置功能
@pytest.mark.ping          # Ping功能
@pytest.mark.route         # 路由功能
@pytest.mark.subnet        # 子网计算功能
@pytest.mark.gui           # GUI功能
@pytest.mark.utils         # 工具类
@pytest.mark.integration   # 集成测试
@pytest.mark.e2e           # 端到端测试
@pytest.mark.performance   # 性能测试
```

### **示例测试**
```python
import pytest
from netkit.services.netconfig import get_network_interfaces
from netkit.services.subnet import SubnetCalculator

@pytest.mark.netconfig
def test_get_network_interfaces():
    """测试获取网络接口"""
    interfaces = get_network_interfaces()
    
    assert isinstance(interfaces, list)
    assert len(interfaces) > 0
    print(f"发现 {len(interfaces)} 个网络接口")

@pytest.mark.subnet
def test_subnet_calculation():
    """测试子网计算"""
    calculator = SubnetCalculator()
    result = calculator.calculate_subnet_info("192.168.1.0", "24")
    
    assert result['network_address'] == '192.168.1.0'
    assert result['broadcast_address'] == '192.168.1.255'
    assert result['host_count'] == '254'
    print(f"子网 {result['cidr_notation']} 计算成功")
```

## 🚨 故障排除

### **常见问题**

1. **权限不足**
   ```
   解决方案：以管理员身份运行测试脚本
   ```

2. **网络连接问题**
   ```
   解决方案：检查网络连接，确保能访问公共DNS
   ```

3. **依赖缺失**
   ```
   解决方案：运行 pip install -r requirements.txt
   ```

4. **测试失败**
   ```
   解决方案：查看详细错误信息，检查网络环境
   ```

## 💡 最佳实践

### **开发流程**
1. 编写功能代码
2. 运行 `scripts/test_quick.bat` 快速验证
3. 运行相关模块测试 (如 `scripts/test_netconfig.bat`)
4. 修复问题后运行 `scripts/test_all.bat`
5. 提交代码

### **测试编写**
- 专注于真实场景测试
- 避免过度Mock
- 提供清晰的错误信息
- 包含性能验证

### **维护建议**
- 定期运行完整测试套件
- 及时修复失败的测试
- 根据功能变更更新测试
- 保持测试代码简洁

---

**记住**：新的测试架构专注于**真实环境验证**，确保NetKit在用户实际使用环境中的稳定性和可靠性。