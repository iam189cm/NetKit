#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络配置服务单元测试
测试 netkit.services.netconfig 模块的主要功能
"""

import pytest
import unittest.mock as mock
import subprocess
import json
import os
from pathlib import Path

# 导入测试目标
from netkit.services.netconfig import (
    get_network_interfaces,
    get_network_card_info,
    apply_profile,
    validate_ip_config
)


class TestNetworkInterfaceOperations:
    """测试网络接口相关操作"""
    
    @pytest.mark.unit
    def test_get_network_interfaces_success(self):
        """测试成功获取网络接口列表"""
        with mock.patch('netkit.services.netconfig.interface_manager.get_async_manager') as mock_get_manager:
            # 模拟异步管理器
            mock_manager = mock.Mock()
            mock_get_manager.return_value = mock_manager
            
            # 模拟适配器对象
            mock_adapter1 = mock.Mock()
            mock_adapter1.connection_id = "以太网"
            mock_adapter2 = mock.Mock()
            mock_adapter2.connection_id = "Wi-Fi"
            
            mock_manager.get_all_adapters_fast.return_value = [mock_adapter1, mock_adapter2]
            
            interfaces = get_network_interfaces()
            
            assert isinstance(interfaces, list)
            assert "以太网" in interfaces
            assert "Wi-Fi" in interfaces
    
    @pytest.mark.unit
    def test_get_network_interfaces_empty(self):
        """测试空接口列表"""
        with mock.patch('netkit.services.netconfig.interface_manager.get_async_manager') as mock_get_manager:
            mock_manager = mock.Mock()
            mock_get_manager.return_value = mock_manager
            mock_manager.get_all_adapters_fast.return_value = []
            
            interfaces = get_network_interfaces()
            
            assert interfaces == []
    
    @pytest.mark.unit
    def test_get_network_interfaces_command_failure(self):
        """测试命令执行失败的情况"""
        with mock.patch('netkit.services.netconfig.interface_manager.get_async_manager') as mock_get_manager:
            mock_get_manager.side_effect = Exception("获取失败")
            
            interfaces = get_network_interfaces()
            
            assert interfaces == []


class TestNetworkCardInfo:
    """测试网卡详细信息获取"""
    
    @pytest.mark.unit
    def test_get_network_card_info_success(self):
        """测试成功获取网卡信息"""
        interface_name = "以太网"
        
        with mock.patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = """
接口"以太网"的配置

    DHCP 已启用:                          否
    IP 地址:                           192.168.1.100
    子网前缀长度:                        24
    默认网关:                           192.168.1.1
    DNS 服务器:                        8.8.8.8
                                       8.8.4.4
"""
            
            info = get_network_card_info(interface_name)
            
            assert info['name'] == interface_name
            assert 'ip' in info
            assert 'gateway' in info
    
    @pytest.mark.unit
    def test_get_network_card_info_command_failure(self):
        """测试命令执行失败"""
        interface_name = "不存在的网卡"
        
        with mock.patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stdout = ""
            
            info = get_network_card_info(interface_name)
            
            assert info['name'] == interface_name


class TestIPConfigValidation:
    """测试IP配置验证"""
    
    @pytest.mark.unit
    def test_validate_ip_config_valid(self):
        """测试有效IP配置验证"""
        result = validate_ip_config(
            "192.168.1.100",
            "255.255.255.0",
            "192.168.1.1",
            "8.8.8.8"
        )
        
        assert result['valid'] is True
    
    @pytest.mark.unit
    def test_validate_ip_config_invalid_ip(self):
        """测试无效IP地址"""
        result = validate_ip_config(
            "256.256.256.256",  # 无效IP
            "255.255.255.0",
            "192.168.1.1",
            "8.8.8.8"
        )
        
        assert result['valid'] is False
        assert 'error' in result
    
    @pytest.mark.unit
    def test_validate_ip_config_invalid_mask(self):
        """测试无效子网掩码"""
        result = validate_ip_config(
            "192.168.1.100",
            "255.255.255.1",  # 无效掩码
            "192.168.1.1",
            "8.8.8.8"
        )
        
        assert result['valid'] is False
        assert 'error' in result
    
    @pytest.mark.unit
    def test_validate_ip_config_empty_dns(self):
        """测试空DNS配置"""
        result = validate_ip_config(
            "192.168.1.100",
            "255.255.255.0",
            "192.168.1.1",
            ""
        )
        
        assert result['valid'] is True


class TestApplyProfile:
    """测试应用配置"""
    
    @pytest.mark.unit
    def test_apply_profile_auto_ip_auto_dns(self):
        """测试自动IP和自动DNS配置"""
        with mock.patch('wmi.WMI') as mock_wmi:
            # 模拟WMI对象
            mock_c = mock.Mock()
            mock_wmi.return_value = mock_c
            
            # 模拟网络适配器
            mock_adapter = mock.Mock()
            mock_adapter.NetConnectionID = "以太网"
            mock_adapter.Index = 1
            mock_c.Win32_NetworkAdapter.return_value = [mock_adapter]
            
            # 模拟网络配置
            mock_config = mock.Mock()
            mock_config.Index = 1
            mock_config.EnableDHCP.return_value = (0,)
            mock_config.SetDNSServerSearchOrder.return_value = (0,)
            mock_c.Win32_NetworkAdapterConfiguration.return_value = [mock_config]
            
            result = apply_profile(
                "以太网",
                "auto",  # IP模式
                "auto",  # DNS模式
                {},      # IP配置
                {}       # DNS配置
            )
            
            assert result['success'] is True
    
    @pytest.mark.unit
    def test_apply_profile_manual_ip_manual_dns(self):
        """测试手动IP和手动DNS配置"""
        with mock.patch('wmi.WMI') as mock_wmi:
            # 模拟WMI对象
            mock_c = mock.Mock()
            mock_wmi.return_value = mock_c
            
            # 模拟网络适配器
            mock_adapter = mock.Mock()
            mock_adapter.NetConnectionID = "以太网"
            mock_adapter.Index = 1
            mock_c.Win32_NetworkAdapter.return_value = [mock_adapter]
            
            # 模拟网络配置
            mock_config = mock.Mock()
            mock_config.Index = 1
            mock_config.EnableStatic.return_value = (0,)
            mock_config.SetGateways.return_value = (0,)
            mock_config.SetDNSServerSearchOrder.return_value = (0,)
            mock_c.Win32_NetworkAdapterConfiguration.return_value = [mock_config]
            
            result = apply_profile(
                "以太网",
                "manual",  # IP模式
                "manual",  # DNS模式
                {
                    "ip": "192.168.1.100",
                    "mask": "255.255.255.0",
                    "gateway": "192.168.1.1"
                },
                {
                    "dns1": "8.8.8.8",
                    "dns2": "8.8.4.4"
                }
            )
            
            assert result['success'] is True
    
    @pytest.mark.unit
    def test_apply_profile_interface_not_found(self):
        """测试网络接口不存在的情况"""
        with mock.patch('wmi.WMI') as mock_wmi:
            mock_c = mock.Mock()
            mock_wmi.return_value = mock_c
            mock_c.Win32_NetworkAdapter.return_value = []  # 没有找到适配器
            
            result = apply_profile(
                "不存在的网卡",
                "auto",
                "auto",
                {},
                {}
            )
            
            assert result['success'] is False
            assert "找不到" in result['error']


@pytest.mark.performance
class TestPerformance:
    """性能测试"""
    
    @pytest.mark.benchmark
    def test_validate_ip_config_performance(self, benchmark):
        """测试IP配置验证性能"""
        def validate_config():
            return validate_ip_config("192.168.1.100", "255.255.255.0", "192.168.1.1", "8.8.8.8")
        
        result = benchmark(validate_config)
        assert result['valid'] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 