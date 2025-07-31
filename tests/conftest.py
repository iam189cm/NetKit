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
        pytest.skip(f"Skip test: No network interfaces detected in {test_environment['platform']} environment")

@pytest.fixture  
def skip_if_ci_server(test_environment):
    """在CI Server环境中跳过真实网络测试"""
    if test_environment['is_ci'] and test_environment['is_server']:
        pytest.skip("Skip test: CI Server environment may not support real network operations")

@pytest.fixture
def mock_network_environment(test_environment):
    """为CI环境提供mock网络环境"""
    if test_environment['is_ci'] and not test_environment['has_interfaces']:
        # 在CI环境中且没有真实接口时，提供mock数据
        return {
            'interfaces': ['Ethernet', 'Wi-Fi'],
            'mock_mode': True,
            'reason': 'CI environment compatibility'
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
    
    # 输出环境信息 (使用ASCII安全的格式)
    env_info = {
        'is_ci': is_ci_environment(),
        'is_server': is_windows_server(),
        'has_interfaces': has_network_interfaces()
    }
    
    try:
        print(f"\nTest Environment Info: {env_info}")
        
        if env_info['is_ci'] and env_info['is_server'] and not env_info['has_interfaces']:
            print("WARNING: CI Server environment detected with no network interfaces")
            print("Some tests will be skipped or use mock data")
    except UnicodeEncodeError:
        # 在编码受限的环境中，使用纯ASCII输出
        print(f"\nTest Environment: CI={env_info['is_ci']}, "
              f"Server={env_info['is_server']}, "
              f"HasInterfaces={env_info['has_interfaces']}")
        
        if env_info['is_ci'] and env_info['is_server'] and not env_info['has_interfaces']:
            print("WARNING: CI Server environment - some tests will use mock data")

def pytest_runtest_setup(item):
    """测试前置检查"""
    # 检查CI跳过标记
    if item.get_closest_marker("ci_skip") and is_ci_environment():
        pytest.skip("Skip test in CI environment")
        
    # 检查真实网络标记
    if item.get_closest_marker("real_network"):
        if is_ci_environment() and is_windows_server() and not has_network_interfaces():
            pytest.skip("CI Server environment does not support real network tests")