#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pytest配置文件
本机测试环境配置
"""

import os
import sys
import platform
import pytest

# 导入测试Fixture
from tests.fixtures import *

# 设置测试模式
os.environ['NETKIT_TEST_MODE'] = '1'
os.environ['NETKIT_LOCAL_TEST'] = '1'


@pytest.fixture(scope="session")
def test_environment():
    """测试环境信息fixture"""
    return {
        'is_local': True,
        'platform': platform.system(),
        'python_version': sys.version_info[:2],
        'test_mode': 'local'
    }


# 配置pytest标记
def pytest_configure(config):
    """配置pytest标记"""
    config.addinivalue_line("markers", "netconfig: 网络配置功能测试")
    config.addinivalue_line("markers", "ping: Ping功能测试")
    config.addinivalue_line("markers", "route: 路由功能测试")
    config.addinivalue_line("markers", "gui: GUI功能测试")
    config.addinivalue_line("markers", "utils: 工具类测试")
    config.addinivalue_line("markers", "integration: 集成测试")
    config.addinivalue_line("markers", "e2e: 端到端测试")
    config.addinivalue_line("markers", "performance: 性能测试")
    config.addinivalue_line("markers", "slow: 运行时间较长的测试")
    
    # 输出本机测试环境信息
    print(f"\n🏠 NetKit 本机测试环境")
    print(f"平台: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print(f"测试模式: 本机真实环境测试")
    print("="*50)