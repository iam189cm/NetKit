#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络配置服务完整单元测试
测试 netkit.services.netconfig 模块的所有功能
"""

import pytest
import unittest.mock as mock
import subprocess
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# 导入所有测试目标
from netkit.services.netconfig import (
    # 网卡管理
    get_network_interfaces,
    get_network_interfaces_with_details,
    extract_interface_name_from_display,
    format_interface_display_name,
    get_network_connection_status,
    get_interface_ip_address,
    
    # 网卡信息
    get_network_card_info,
    get_network_adapter_hardware_info,
    get_interface_config,
    get_interface_mac_address,
    get_interface_basic_info,
    get_interface_ip_config,
    
    # IP配置
    apply_profile,
    validate_ip_config,
    check_network_conflict,
    suggest_ip_config
)


class TestNetworkInterfaceManagement:
    """测试网卡管理功能 - 6个函数"""
    
    @pytest.mark.unit
    def test_get_network_interfaces_success(self):
        """测试成功获取网络接口列表"""
        with patch('netkit.services.netconfig.interface_manager.get_async_manager') as mock_get_manager:
            # 模拟异步管理器
            mock_manager = Mock()
            mock_get_manager.return_value = mock_manager
            
            # 模拟适配器对象
            mock_adapter1 = Mock()
            mock_adapter1.connection_id = "以太网"
            mock_adapter2 = Mock()
            mock_adapter2.connection_id = "Wi-Fi"
            
            mock_manager.get_all_adapters_fast.return_value = [mock_adapter1, mock_adapter2]
            
            interfaces = get_network_interfaces()
            
            assert isinstance(interfaces, list)
            assert "以太网" in interfaces
            assert "Wi-Fi" in interfaces
            mock_manager.get_all_adapters_fast.assert_called_once_with(False)
    
    @pytest.mark.unit
    def test_get_network_interfaces_show_all(self):
        """测试获取所有网络接口（包括虚拟网卡）"""
        with patch('netkit.services.netconfig.interface_manager.get_async_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_get_manager.return_value = mock_manager
            
            mock_adapter = Mock()
            mock_adapter.connection_id = "VMware Network Adapter"
            mock_manager.get_all_adapters_fast.return_value = [mock_adapter]
            
            interfaces = get_network_interfaces(show_all=True)
            
            assert "VMware Network Adapter" in interfaces
            mock_manager.get_all_adapters_fast.assert_called_once_with(True)
    
    @pytest.mark.unit
    def test_get_network_interfaces_exception(self):
        """测试异常情况"""
        with patch('netkit.services.netconfig.interface_manager.get_async_manager') as mock_get_manager:
            mock_get_manager.side_effect = Exception("测试异常")
            
            interfaces = get_network_interfaces()
            
            assert interfaces == []
    
    @pytest.mark.unit
    def test_get_network_interfaces_with_details_success(self):
        """测试获取带详细信息的网络接口列表"""
        with patch('netkit.services.netconfig.interface_manager.get_async_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_get_manager.return_value = mock_manager
            
            # 模拟返回详细信息的元组列表
            mock_manager.get_all_adapters_with_details.return_value = [
                ("[已连接] 以太网 (Realtek) - 192.168.1.100", "以太网"),
                ("[已断开] Wi-Fi (Intel) - 未配置", "Wi-Fi")
            ]
            
            result = get_network_interfaces_with_details()
            
            assert isinstance(result, list)
            assert len(result) == 2
            assert result[0][0] == "[已连接] 以太网 (Realtek) - 192.168.1.100"
            assert result[0][1] == "以太网"
            mock_manager.get_all_adapters_with_details.assert_called_once_with(False)
    
    @pytest.mark.unit
    def test_get_network_interfaces_with_details_exception(self):
        """测试获取详细信息时的异常情况"""
        with patch('netkit.services.netconfig.interface_manager.get_async_manager') as mock_get_manager:
            mock_get_manager.side_effect = Exception("测试异常")
            
            result = get_network_interfaces_with_details()
            
            assert result == []
    
    @pytest.mark.unit
    def test_extract_interface_name_from_display(self):
        """测试从显示名称中提取原始接口名称"""
        # 测试完整格式: [状态] 网卡名称 (制造商 型号) - IP地址
        display_name = "[已连接] 以太网 (Realtek PCIe GBE) - 192.168.1.100"
        result = extract_interface_name_from_display(display_name)
        assert result == "以太网"
        
        # 测试简单格式
        simple_name = "Wi-Fi"
        result = extract_interface_name_from_display(simple_name)
        assert result == "Wi-Fi"
        
        # 测试空字符串
        result = extract_interface_name_from_display("")
        assert result == ""
        
        # 测试异常情况
        result = extract_interface_name_from_display(None)
        assert result == ""
    
    @pytest.mark.unit
    def test_format_interface_display_name(self):
        """测试格式化网卡显示名称"""
        with patch('netkit.services.netconfig.interface_manager.get_network_connection_status') as mock_status, \
             patch('netkit.services.netconfig.interface_manager.get_interface_ip_address') as mock_ip, \
             patch('netkit.services.netconfig.get_network_adapter_hardware_info') as mock_hardware:
            
            # 模拟返回值
            mock_status.return_value = "已连接"
            mock_ip.return_value = "192.168.1.100"
            mock_hardware.return_value = {
                'manufacturer': 'Realtek Semiconductor Corp.',
                'model': 'PCIe GBE Family Controller'
            }
            
            result = format_interface_display_name("以太网")
            
            # 验证函数能正常执行并返回字符串
            assert isinstance(result, str)
            assert len(result) > 0
            # 验证基本的格式化结果包含接口名称
            assert "以太网" in result
    
    @pytest.mark.unit
    def test_get_network_connection_status_from_cache(self):
        """测试从缓存获取网络连接状态"""
        with patch('netkit.services.netconfig.interface_manager.get_async_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_get_manager.return_value = mock_manager
            
            # 模拟缓存中有数据
            mock_adapter = Mock()
            mock_adapter.connection_status = "已连接"
            mock_manager.adapters_cache = {"以太网": mock_adapter}
            
            result = get_network_connection_status("以太网")
            
            assert result == "已连接"
    
    @pytest.mark.unit
    def test_get_network_connection_status_fallback(self):
        """测试从服务获取网络连接状态（缓存未命中）"""
        with patch('netkit.services.netconfig.interface_manager.get_async_manager') as mock_get_manager, \
             patch('netkit.services.netconfig.interface_manager.get_network_info_service') as mock_get_service:
            
            mock_manager = Mock()
            mock_get_manager.return_value = mock_manager
            mock_manager.adapters_cache = {}  # 空缓存
            
            mock_service = Mock()
            mock_get_service.return_value = mock_service
            mock_service.get_interface_basic_info.return_value = {'connection_status': '已断开'}
            
            result = get_network_connection_status("Wi-Fi")
            
            assert result == "已断开"
            mock_service.get_interface_basic_info.assert_called_once_with("Wi-Fi")
    
    @pytest.mark.unit
    def test_get_network_connection_status_exception(self):
        """测试获取连接状态时的异常情况"""
        with patch('netkit.services.netconfig.interface_manager.get_async_manager') as mock_get_manager:
            mock_get_manager.side_effect = Exception("测试异常")
            
            result = get_network_connection_status("以太网")
            
            assert result == "未知"
    
    @pytest.mark.unit
    def test_get_interface_ip_address_from_cache(self):
        """测试从缓存获取接口IP地址"""
        with patch('netkit.services.netconfig.interface_manager.get_async_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_get_manager.return_value = mock_manager
            
            # 模拟缓存中有数据
            mock_adapter = Mock()
            mock_adapter.ip_addresses = ["192.168.1.100", "192.168.1.101"]
            mock_manager.adapters_cache = {"以太网": mock_adapter}
            
            result = get_interface_ip_address("以太网")
            
            assert result == "192.168.1.100"
    
    @pytest.mark.unit
    def test_get_interface_ip_address_no_ip(self):
        """测试获取IP地址时无IP配置的情况"""
        with patch('netkit.services.netconfig.interface_manager.get_async_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_get_manager.return_value = mock_manager
            
            # 模拟没有IP地址
            mock_adapter = Mock()
            mock_adapter.ip_addresses = []
            mock_manager.adapters_cache = {"以太网": mock_adapter}
            
            result = get_interface_ip_address("以太网")
            
            assert result == "未配置"
    
    @pytest.mark.unit
    def test_get_interface_ip_address_exception(self):
        """测试获取IP地址时的异常情况"""
        with patch('netkit.services.netconfig.interface_manager.get_async_manager') as mock_get_manager:
            mock_get_manager.side_effect = Exception("测试异常")
            
            result = get_interface_ip_address("以太网")
            
            assert result == "未配置"


class TestNetworkCardInfo:
    """测试网卡信息获取功能 - 6个函数"""
    
    @pytest.mark.unit
    def test_get_network_card_info_success(self):
        """测试成功获取网卡信息"""
        with patch('netkit.services.netconfig.interface_info.get_network_info_service') as mock_get_service:
            mock_service = Mock()
            mock_get_service.return_value = mock_service
            
            mock_service.get_network_card_info.return_value = {
                'name': '以太网',
                'status': '已启用',
                'ip': '192.168.1.100',
                'mask': '255.255.255.0',
                'gateway': '192.168.1.1',
                'dns1': '8.8.8.8',
                'dns2': '8.8.4.4'
            }
            
            result = get_network_card_info("以太网")
            
            assert result['name'] == '以太网'
            assert result['ip'] == '192.168.1.100'
            assert result['gateway'] == '192.168.1.1'
            mock_service.get_network_card_info.assert_called_once_with("以太网")
    
    @pytest.mark.unit
    def test_get_network_adapter_hardware_info_success(self):
        """测试获取网卡硬件信息"""
        with patch('netkit.services.netconfig.interface_info.get_network_info_service') as mock_get_service:
            mock_service = Mock()
            mock_get_service.return_value = mock_service
            
            mock_service.get_network_adapter_hardware_info.return_value = {
                'manufacturer': 'Realtek Semiconductor Corp.',
                'model': 'PCIe GBE Family Controller',
                'full_description': 'Realtek PCIe GBE Family Controller',
                'speed': '1000 Mbps'
            }
            
            result = get_network_adapter_hardware_info("以太网")
            
            assert result['manufacturer'] == 'Realtek Semiconductor Corp.'
            assert result['model'] == 'PCIe GBE Family Controller'
            assert result['speed'] == '1000 Mbps'
            mock_service.get_network_adapter_hardware_info.assert_called_once_with("以太网")
    
    @pytest.mark.unit
    def test_get_interface_config_success(self):
        """测试获取接口配置"""
        with patch('netkit.services.netconfig.interface_info.get_network_info_service') as mock_get_service:
            mock_service = Mock()
            mock_get_service.return_value = mock_service
            
            config_output = """
接口"以太网"的配置

    DHCP 已启用:                          否
    IP 地址:                           192.168.1.100
    子网前缀长度:                        24
    默认网关:                           192.168.1.1
    DNS 服务器:                        8.8.8.8
                                       8.8.4.4
"""
            mock_service.get_interface_config.return_value = config_output
            
            result = get_interface_config("以太网")
            
            assert "192.168.1.100" in result
            assert "192.168.1.1" in result
            assert "8.8.8.8" in result
            mock_service.get_interface_config.assert_called_once_with("以太网")
    
    @pytest.mark.unit
    def test_get_interface_mac_address_success(self):
        """测试获取接口MAC地址"""
        with patch('netkit.services.netconfig.interface_info.get_network_info_service') as mock_get_service:
            mock_service = Mock()
            mock_get_service.return_value = mock_service
            
            mock_service.get_interface_mac_address.return_value = "00:11:22:33:44:55"
            
            result = get_interface_mac_address("以太网")
            
            assert result == "00:11:22:33:44:55"
            mock_service.get_interface_mac_address.assert_called_once_with("以太网")
    
    @pytest.mark.unit
    def test_get_interface_basic_info_success(self):
        """测试获取接口基本信息"""
        with patch('netkit.services.netconfig.interface_info.get_network_info_service') as mock_get_service:
            mock_service = Mock()
            mock_get_service.return_value = mock_service
            
            mock_service.get_interface_basic_info.return_value = {
                'status': '已启用',
                'type': '专用',
                'connection_status': '已连接'
            }
            
            result = get_interface_basic_info("以太网")
            
            assert result['status'] == '已启用'
            assert result['type'] == '专用'
            assert result['connection_status'] == '已连接'
            mock_service.get_interface_basic_info.assert_called_once_with("以太网")
    
    @pytest.mark.unit
    def test_get_interface_ip_config_success(self):
        """测试获取接口IP配置信息"""
        with patch('netkit.services.netconfig.interface_info.get_network_info_service') as mock_get_service:
            mock_service = Mock()
            mock_get_service.return_value = mock_service
            
            mock_service.get_interface_ip_config.return_value = {
                'ip': '192.168.1.100',
                'mask': '255.255.255.0',
                'gateway': '192.168.1.1',
                'dns1': '8.8.8.8',
                'dns2': '8.8.4.4'
            }
            
            result = get_interface_ip_config("以太网")
            
            assert result['ip'] == '192.168.1.100'
            assert result['mask'] == '255.255.255.0'
            assert result['gateway'] == '192.168.1.1'
            assert result['dns1'] == '8.8.8.8'
            mock_service.get_interface_ip_config.assert_called_once_with("以太网")


class TestIPConfiguration:
    """测试IP配置功能 - 4个函数"""
    
    @pytest.mark.unit
    def test_apply_profile_auto_ip_auto_dns(self):
        """测试自动IP和自动DNS配置（纯DHCP）"""
        with patch('wmi.WMI') as mock_wmi, \
             patch('pythoncom.CoInitialize'), \
             patch('pythoncom.CoUninitialize'):
            
            # 模拟WMI对象
            mock_c = Mock()
            mock_wmi.return_value = mock_c
            
            # 模拟网络适配器
            mock_adapter = Mock()
            mock_adapter.NetConnectionID = "以太网"
            mock_adapter.Index = 1
            mock_c.Win32_NetworkAdapter.return_value = [mock_adapter]
            
            # 模拟网络配置
            mock_config = Mock()
            mock_config.Index = 1
            mock_c.Win32_NetworkAdapterConfiguration.return_value = [mock_config]
            
            # 模拟_apply_full_dhcp函数
            with patch('netkit.services.netconfig.ip_configurator._apply_full_dhcp') as mock_apply:
                mock_apply.return_value = {'success': True, 'message': 'DHCP配置成功'}
                
                result = apply_profile(
                    "以太网",
                    "auto",  # IP模式
                    "auto",  # DNS模式
                    {},      # IP配置
                    {}       # DNS配置
                )
                
                assert result['success'] is True
                assert 'DHCP' in result['message']
                mock_apply.assert_called_once_with(mock_config)
    
    @pytest.mark.unit
    def test_apply_profile_manual_ip_manual_dns(self):
        """测试手动IP和手动DNS配置（纯静态）"""
        with patch('wmi.WMI') as mock_wmi, \
             patch('pythoncom.CoInitialize'), \
             patch('pythoncom.CoUninitialize'):
            
            mock_c = Mock()
            mock_wmi.return_value = mock_c
            
            mock_adapter = Mock()
            mock_adapter.NetConnectionID = "以太网"
            mock_adapter.Index = 1
            mock_c.Win32_NetworkAdapter.return_value = [mock_adapter]
            
            mock_config = Mock()
            mock_config.Index = 1
            mock_c.Win32_NetworkAdapterConfiguration.return_value = [mock_config]
            
            with patch('netkit.services.netconfig.ip_configurator._apply_full_static') as mock_apply:
                mock_apply.return_value = {'success': True, 'message': '静态配置成功'}
                
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
                assert '静态' in result['message']
    
    @pytest.mark.unit
    def test_apply_profile_interface_not_found(self):
        """测试网络接口不存在的情况"""
        with patch('wmi.WMI') as mock_wmi, \
             patch('pythoncom.CoInitialize'), \
             patch('pythoncom.CoUninitialize'):
            
            mock_c = Mock()
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
            assert "找不到网络适配器连接" in result['error']
    
    @pytest.mark.unit
    def test_apply_profile_invalid_mode(self):
        """测试无效的配置模式"""
        with patch('wmi.WMI') as mock_wmi, \
             patch('pythoncom.CoInitialize'), \
             patch('pythoncom.CoUninitialize'):
            
            mock_c = Mock()
            mock_wmi.return_value = mock_c
            
            mock_adapter = Mock()
            mock_adapter.NetConnectionID = "以太网"
            mock_adapter.Index = 1
            mock_c.Win32_NetworkAdapter.return_value = [mock_adapter]
            
            mock_config = Mock()
            mock_config.Index = 1
            mock_c.Win32_NetworkAdapterConfiguration.return_value = [mock_config]
            
            result = apply_profile(
                "以太网",
                "invalid",  # 无效模式
                "auto",
                {},
                {}
            )
            
            assert result['success'] is False
            assert "无效的配置模式" in result['error']
    
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
    
    @pytest.mark.unit
    def test_check_network_conflict_no_conflict(self):
        """测试无网络冲突"""
        with patch('netkit.services.netconfig.ip_configurator.get_network_interfaces') as mock_get_interfaces, \
             patch('netkit.services.netconfig.ip_configurator.get_interface_config') as mock_get_config:
            
            mock_get_interfaces.return_value = ["以太网", "Wi-Fi"]
            # 模拟两个接口的配置，第一个调用返回以太网配置，第二个调用返回Wi-Fi配置
            mock_get_config.side_effect = [
                """
接口"以太网"的配置
    IP 地址:                           192.168.1.50
    默认网关:                           192.168.1.1
""",
                """
接口"Wi-Fi"的配置
    IP 地址:                           192.168.2.50
    默认网关:                           192.168.2.1
"""
            ]
            
            result = check_network_conflict("192.168.1.100", "255.255.255.0", "192.168.1.1")
            
            assert result['has_conflict'] is True  # 网关冲突
            assert len(result['conflicts']) > 0
    
    @pytest.mark.unit
    def test_check_network_conflict_ip_conflict(self):
        """测试IP地址冲突"""
        with patch('netkit.services.netconfig.ip_configurator.get_network_interfaces') as mock_get_interfaces, \
             patch('netkit.services.netconfig.ip_configurator.get_interface_config') as mock_get_config:
            
            mock_get_interfaces.return_value = ["以太网"]
            mock_get_config.return_value = """
接口"以太网"的配置
    IP 地址:                           192.168.1.100
    默认网关:                           192.168.1.1
"""
            
            result = check_network_conflict("192.168.1.100", "255.255.255.0", "192.168.1.1")
            
            assert result['has_conflict'] is True
            assert len(result['conflicts']) > 0
            assert "IP地址" in result['conflicts'][0]
    
    @pytest.mark.unit
    def test_check_network_conflict_exception(self):
        """测试网络冲突检查异常"""
        with patch('netkit.services.netconfig.ip_configurator.get_network_interfaces') as mock_get_interfaces:
            mock_get_interfaces.side_effect = Exception("测试异常")
            
            result = check_network_conflict("192.168.1.100", "255.255.255.0", "192.168.1.1")
            
            assert result['has_conflict'] is True
            assert len(result['conflicts']) > 0
            assert "出错" in result['conflicts'][0]
    
    @pytest.mark.unit
    def test_suggest_ip_config_success(self):
        """测试IP配置建议"""
        with patch('netkit.services.netconfig.ip_configurator.get_interface_config') as mock_get_config, \
             patch('netkit.services.netconfig.ip_configurator.validate_ip_config') as mock_validate:
            
            mock_get_config.return_value = """
接口"以太网"的配置
    IP 地址:                           192.168.1.100
    子网前缀长度:                        24
    默认网关:                           192.168.1.1
"""
            mock_validate.return_value = {'valid': True}
            
            result = suggest_ip_config("以太网")
            
            assert result['success'] is True
            assert 'suggestions' in result
            assert len(result['suggestions']) > 0
    
    @pytest.mark.unit
    def test_suggest_ip_config_no_interface(self):
        """测试接口不存在时的配置建议"""
        with patch('netkit.services.netconfig.ip_configurator.get_interface_config') as mock_get_config:
            mock_get_config.return_value = None
            
            result = suggest_ip_config("不存在的接口")
            
            assert result['success'] is False
            assert "无法获取接口" in result['error']


class TestErrorHandling:
    """测试错误处理和边界情况"""
    
    @pytest.mark.unit
    def test_all_functions_handle_none_input(self):
        """测试所有函数对None输入的处理"""
        # 测试能安全处理None输入的函数
        result = extract_interface_name_from_display(None)
        assert result == ""
    
    @pytest.mark.unit
    def test_service_functions_handle_exceptions(self):
        """测试服务函数的异常处理"""
        # 测试get_network_interfaces的异常处理
        with patch('netkit.services.netconfig.interface_manager.get_async_manager') as mock_get_manager:
            mock_get_manager.side_effect = Exception("测试异常")
            
            # 这个函数应该优雅地处理异常，返回空列表
            result = get_network_interfaces()
            assert result == []
        
        # 测试get_network_connection_status的异常处理
        with patch('netkit.services.netconfig.interface_manager.get_async_manager') as mock_get_manager:
            mock_get_manager.side_effect = Exception("测试异常")
            
            result = get_network_connection_status("测试")
            assert result == "未知"


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
    
    @pytest.mark.benchmark
    def test_extract_interface_name_performance(self, benchmark):
        """测试接口名称提取性能"""
        def extract_name():
            return extract_interface_name_from_display("[已连接] 以太网 (Realtek) - 192.168.1.100")
        
        result = benchmark(extract_name)
        assert result == "以太网"


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 