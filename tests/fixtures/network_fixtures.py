#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络测试数据工厂和Fixture
提供统一的测试数据管理
"""

import pytest
from unittest.mock import Mock
from typing import List, Dict, Any


class NetworkTestDataFactory:
    """网络测试数据工厂"""
    
    @staticmethod
    def create_mock_network_adapters(count: int = 3) -> List[Mock]:
        """创建Mock网络适配器"""
        adapters = []
        adapter_names = ['以太网', 'Wi-Fi', 'VPN连接', '蓝牙网络', '虚拟网卡']
        
        for i in range(min(count, len(adapter_names))):
            adapter = Mock()
            adapter.connection_id = adapter_names[i]
            adapter.description = f"Mock Network Adapter {i+1}"
            adapter.connection_status = "Connected" if i < 2 else "Disconnected"
            adapter.mac_address = f"00:11:22:33:44:{i:02d}"
            adapter.speed = 1000000000  # 1Gbps
            adapters.append(adapter)
        
        return adapters
    
    @staticmethod
    def create_ip_configs() -> List[Dict[str, str]]:
        """创建IP配置测试数据"""
        return [
            {
                'ip': '192.168.1.100',
                'mask': '255.255.255.0',
                'gateway': '192.168.1.1',
                'dns': '8.8.8.8,8.8.4.4',
                'description': '家庭网络配置'
            },
            {
                'ip': '10.0.0.100',
                'mask': '255.255.255.0', 
                'gateway': '10.0.0.1',
                'dns': '1.1.1.1,1.0.0.1',
                'description': '办公网络配置'
            },
            {
                'ip': '172.16.0.100',
                'mask': '255.255.0.0',
                'gateway': '172.16.0.1',
                'dns': '8.8.8.8,1.1.1.1',
                'description': '企业网络配置'
            },
            {
                'ip': '192.168.0.50',
                'mask': '255.255.255.0',
                'gateway': '192.168.0.1',
                'dns': '223.5.5.5,223.6.6.6',
                'description': '备用网络配置'
            }
        ]
    
    @staticmethod
    def create_invalid_ip_configs() -> List[Dict[str, str]]:
        """创建无效IP配置测试数据"""
        return [
            {
                'ip': '999.999.999.999',
                'mask': '255.255.255.0',
                'gateway': '192.168.1.1',
                'dns': '8.8.8.8',
                'error_type': 'invalid_ip'
            },
            {
                'ip': '192.168.1.100',
                'mask': '999.999.999.999',
                'gateway': '192.168.1.1',
                'dns': '8.8.8.8',
                'error_type': 'invalid_mask'
            },
            {
                'ip': '192.168.1.100',
                'mask': '255.255.255.0',
                'gateway': '192.168.2.1',  # 不在同一网段
                'dns': '8.8.8.8',
                'error_type': 'gateway_not_in_subnet'
            },
            {
                'ip': '192.168.1.100',
                'mask': '255.255.255.0',
                'gateway': '192.168.1.1',
                'dns': 'invalid.dns',
                'error_type': 'invalid_dns'
            }
        ]
    
    @staticmethod
    def create_ping_targets() -> List[Dict[str, Any]]:
        """创建Ping目标测试数据"""
        return [
            {'host': '8.8.8.8', 'expected_reachable': True, 'description': 'Google DNS'},
            {'host': '1.1.1.1', 'expected_reachable': True, 'description': 'Cloudflare DNS'},
            {'host': '192.168.1.1', 'expected_reachable': True, 'description': '默认网关'},
            {'host': '127.0.0.1', 'expected_reachable': True, 'description': '本机回环'},
            {'host': '192.168.255.254', 'expected_reachable': False, 'description': '不存在的内网地址'},
            {'host': 'invalid.host.name', 'expected_reachable': False, 'description': '无效主机名'}
        ]


@pytest.fixture(scope="session")
def network_data_factory():
    """网络测试数据工厂Fixture"""
    return NetworkTestDataFactory()


@pytest.fixture
def mock_network_adapters(network_data_factory):
    """Mock网络适配器Fixture"""
    return network_data_factory.create_mock_network_adapters()


@pytest.fixture
def valid_ip_configs(network_data_factory):
    """有效IP配置Fixture"""
    return network_data_factory.create_ip_configs()


@pytest.fixture
def invalid_ip_configs(network_data_factory):
    """无效IP配置Fixture"""
    return network_data_factory.create_invalid_ip_configs()


@pytest.fixture
def ping_targets(network_data_factory):
    """Ping目标Fixture"""
    return network_data_factory.create_ping_targets()


@pytest.fixture
def performance_test_data():
    """性能测试数据Fixture"""
    return {
        'concurrent_users': [1, 5, 10, 20],
        'test_duration': 30,  # 秒
        'acceptable_response_time': 2.0,  # 秒
        'acceptable_success_rate': 0.95  # 95%
    }


@pytest.fixture
def ci_environment_data():
    """CI环境测试数据Fixture"""
    return {
        'mock_adapters': NetworkTestDataFactory.create_mock_network_adapters(5),
        'skip_real_network_tests': True,
        'use_mock_wmi': True,
        'timeout_multiplier': 2.0  # CI环境超时时间翻倍
    }