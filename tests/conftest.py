#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pytest配置文件
包含测试夹具和全局配置
"""

import os
import sys
import platform
import pytest

# 设置测试模式
os.environ['NETKIT_TEST_MODE'] = '1'

def is_ci_environment():
    """检测是否在CI环境中运行"""
    ci_indicators = [
        'GITHUB_ACTIONS',
        'CI',
        'CONTINUOUS_INTEGRATION',
        'BUILD_NUMBER'
    ]
    return any(os.environ.get(indicator) for indicator in ci_indicators)

def is_windows_server():
    """检测是否在Windows Server环境中运行"""
    try:
        return "Server" in platform.version() or "Server" in platform.release()
    except:
        return False

def has_network_interfaces():
    """检测是否能够获取到网络接口"""
    try:
        from netkit.services.netconfig.interface_manager import get_network_interfaces
        interfaces = get_network_interfaces(show_all=True)
        return len(interfaces) > 0
    except:
        return False

@pytest.fixture(scope="session")
def test_environment():
    """测试环境信息夹具"""
    return {
        'is_ci': is_ci_environment(),
        'is_server': is_windows_server(),
        'has_interfaces': has_network_interfaces(),
        'platform': platform.system(),
        'version': platform.version()
    }

@pytest.fixture
def skip_if_no_interfaces(test_environment):
    """在没有网络接口时跳过测试"""
    if not test_environment['has_interfaces']:
        pytest.skip(f"跳过测试: 在{test_environment['platform']}环境中未检测到网络接口")

@pytest.fixture  
def skip_if_ci_server(test_environment):
    """在CI Server环境中跳过真实网络测试"""
    if test_environment['is_ci'] and test_environment['is_server']:
        pytest.skip("跳过测试: CI Server环境可能不支持真实网络操作")

@pytest.fixture
def mock_network_environment(test_environment):
    """为CI环境提供mock网络环境"""
    if test_environment['is_ci'] and not test_environment['has_interfaces']:
        # 在CI环境中且没有真实接口时，提供mock数据
        return {
            'interfaces': ['以太网', 'Wi-Fi'],
            'mock_mode': True,
            'reason': 'CI环境兼容性'
        }
    else:
        return {
            'mock_mode': False
        }

# 配置pytest标记
def pytest_configure(config):
    """配置pytest标记"""
    config.addinivalue_line("markers", "real_network: 需要真实网络环境的测试")
    config.addinivalue_line("markers", "integration: 集成测试")
    config.addinivalue_line("markers", "ci_skip: 在CI环境中跳过的测试")
    
    # 输出环境信息
    env_info = {
        'is_ci': is_ci_environment(),
        'is_server': is_windows_server(),
        'has_interfaces': has_network_interfaces()
    }
    
    print(f"\n测试环境信息: {env_info}")
    
    if env_info['is_ci'] and env_info['is_server'] and not env_info['has_interfaces']:
        print("⚠️ 检测到CI Server环境且无网络接口，某些测试将被跳过或使用mock数据")

def pytest_runtest_setup(item):
    """测试前置检查"""
    # 检查CI跳过标记
    if item.get_closest_marker("ci_skip") and is_ci_environment():
        pytest.skip("在CI环境中跳过此测试")
        
    # 检查真实网络标记
    if item.get_closest_marker("real_network"):
        if is_ci_environment() and is_windows_server() and not has_network_interfaces():
            pytest.skip("CI Server环境不支持真实网络测试")