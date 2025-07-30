#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络配置集成测试
测试网络配置服务与GUI的完整交互流程
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# 导入测试目标
from netkit.services.netconfig import (
    get_network_interfaces,
    apply_profile,
    validate_ip_config,
    get_interface_config
)
# GUI相关导入在实际GUI测试中再使用
# from gui.views.netconfig.netconfig_view import NetConfigView


@pytest.mark.integration
class TestNetworkConfigurationIntegration:
    """网络配置集成测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.test_interface = "Test Ethernet"
        self.valid_config = {
            'ip': '192.168.1.100',
            'mask': '255.255.255.0',
            'gateway': '192.168.1.1',
            'dns1': '8.8.8.8',
            'dns2': '8.8.4.4'
        }
    
    @patch('subprocess.run')
    @patch('netkit.services.netconfig.async_manager.get_async_manager')
    def test_complete_ip_configuration_workflow(self, mock_async_manager, mock_subprocess):
        """测试完整的IP配置工作流程"""
        # 模拟网卡信息
        mock_wmi.return_value = [
            {
                'Name': self.test_interface,
                'Description': 'Test Network Adapter',
                'DeviceID': 'TEST_DEVICE_01',
                'MACAddress': '00:11:22:33:44:55',
                'NetConnectionStatus': 2,  # Connected
                'ConfigManagerErrorCode': 0
            }
        ]
        
        # 模拟netsh命令成功
        mock_subprocess.return_value = Mock(
            returncode=0,
            stdout="配置成功",
            stderr=""
        )
        
        # 1. 获取网络接口
        interfaces = get_network_interfaces()
        assert len(interfaces) > 0
        assert self.test_interface in [iface['name'] for iface in interfaces]
        
        # 2. 验证配置
        is_valid, errors = validate_ip_config(self.valid_config)
        assert is_valid
        assert len(errors) == 0
        
        # 3. 应用配置
        success = apply_profile(self.test_interface, self.valid_config)
        assert success
        
        # 验证netsh命令被正确调用
        assert mock_subprocess.call_count >= 2  # IP和DNS配置
    
    @patch('subprocess.run')
    @patch('netkit.services.netconfig.wmi_engine.get_network_adapters')
    def test_error_handling_integration(self, mock_wmi, mock_subprocess):
        """测试错误处理集成"""
        # 模拟网卡信息
        mock_wmi.return_value = [
            {
                'Name': self.test_interface,
                'Description': 'Test Network Adapter',
                'DeviceID': 'TEST_DEVICE_01',
                'MACAddress': '00:11:22:33:44:55',
                'NetConnectionStatus': 2,
                'ConfigManagerErrorCode': 0
            }
        ]
        
        # 模拟netsh命令失败
        mock_subprocess.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="配置失败"
        )
        
        # 尝试应用无效配置
        invalid_config = {
            'ip': '999.999.999.999',  # 无效IP
            'mask': '255.255.255.0',
            'gateway': '192.168.1.1',
            'dns1': '8.8.8.8',
            'dns2': '8.8.4.4'
        }
        
        # 验证配置应该失败
        is_valid, errors = validate_ip_config(invalid_config)
        assert not is_valid
        assert len(errors) > 0
        assert "IP地址格式无效" in str(errors)
    
    @patch('subprocess.run')
    @patch('netkit.services.netconfig.wmi_engine.get_network_adapters')
    def test_dhcp_configuration_integration(self, mock_wmi, mock_subprocess):
        """测试DHCP配置集成"""
        # 模拟网卡信息
        mock_wmi.return_value = [
            {
                'Name': self.test_interface,
                'Description': 'Test Network Adapter',
                'DeviceID': 'TEST_DEVICE_01',
                'MACAddress': '00:11:22:33:44:55',
                'NetConnectionStatus': 2,
                'ConfigManagerErrorCode': 0
            }
        ]
        
        # 模拟netsh命令成功
        mock_subprocess.return_value = Mock(
            returncode=0,
            stdout="DHCP配置成功",
            stderr=""
        )
        
        # DHCP配置
        dhcp_config = {
            'mode': 'dhcp',
            'dns_mode': 'auto'
        }
        
        # 应用DHCP配置
        success = apply_profile(self.test_interface, dhcp_config)
        assert success
        
        # 验证正确的netsh命令被调用
        mock_subprocess.assert_called()


@pytest.mark.integration
class TestNetworkInterfaceIntegration:
    """网络接口集成测试"""
    
    @patch('netkit.services.netconfig.wmi_engine.get_network_adapters')
    @patch('subprocess.run')
    def test_interface_detection_and_status(self, mock_subprocess, mock_wmi):
        """测试网络接口检测和状态获取"""
        # 模拟多个网卡
        mock_wmi.return_value = [
            {
                'Name': 'Ethernet',
                'Description': 'Intel Network Adapter',
                'DeviceID': 'DEVICE_01',
                'MACAddress': '00:11:22:33:44:55',
                'NetConnectionStatus': 2,  # Connected
                'ConfigManagerErrorCode': 0
            },
            {
                'Name': 'Wi-Fi',
                'Description': 'Wireless Network Adapter',
                'DeviceID': 'DEVICE_02',
                'MACAddress': '66:77:88:99:AA:BB',
                'NetConnectionStatus': 7,  # Disconnected
                'ConfigManagerErrorCode': 0
            }
        ]
        
        # 模拟ipconfig命令输出
        mock_subprocess.return_value = Mock(
            returncode=0,
            stdout="""
Windows IP 配置

以太网适配器 Ethernet:
   连接特定的 DNS 后缀 . . . . . . . :
   IPv4 地址 . . . . . . . . . . . . : 192.168.1.100
   子网掩码  . . . . . . . . . . . . : 255.255.255.0
   默认网关. . . . . . . . . . . . . : 192.168.1.1

无线局域网适配器 Wi-Fi:
   媒体状态  . . . . . . . . . . . . : 媒体已断开连接
            """,
            stderr=""
        )
        
        # 获取网络接口
        interfaces = get_network_interfaces()
        
        # 验证结果
        assert len(interfaces) == 2
        
        # 验证以太网接口
        ethernet = next((iface for iface in interfaces if iface['name'] == 'Ethernet'), None)
        assert ethernet is not None
        assert ethernet['status'] == 'Connected'
        
        # 验证Wi-Fi接口
        wifi = next((iface for iface in interfaces if iface['name'] == 'Wi-Fi'), None)
        assert wifi is not None
        assert wifi['status'] == 'Disconnected'
    
    @patch('netkit.services.netconfig.wmi_engine.get_network_adapters')
    def test_interface_configuration_retrieval(self, mock_wmi):
        """测试网络接口配置获取"""
        mock_wmi.return_value = [
            {
                'Name': 'Ethernet',
                'Description': 'Test Network Adapter',
                'DeviceID': 'TEST_DEVICE',
                'MACAddress': '00:11:22:33:44:55',
                'NetConnectionStatus': 2,
                'ConfigManagerErrorCode': 0
            }
        ]
        
        # 获取接口配置
        config = get_interface_config('Ethernet')
        
        # 验证配置结构
        assert isinstance(config, dict)
        assert 'name' in config
        assert 'mac_address' in config
        assert 'status' in config


@pytest.mark.integration
@pytest.mark.slow
class TestNetworkConfigurationStress:
    """网络配置压力测试"""
    
    @patch('subprocess.run')
    @patch('netkit.services.netconfig.wmi_engine.get_network_adapters')
    def test_rapid_configuration_changes(self, mock_wmi, mock_subprocess):
        """测试快速配置更改"""
        # 模拟网卡
        mock_wmi.return_value = [
            {
                'Name': 'Test Ethernet',
                'Description': 'Test Network Adapter',
                'DeviceID': 'TEST_DEVICE',
                'MACAddress': '00:11:22:33:44:55',
                'NetConnectionStatus': 2,
                'ConfigManagerErrorCode': 0
            }
        ]
        
        # 模拟成功的netsh命令
        mock_subprocess.return_value = Mock(
            returncode=0,
            stdout="配置成功",
            stderr=""
        )
        
        # 快速切换多个配置
        configs = [
            {
                'ip': '192.168.1.100',
                'mask': '255.255.255.0',
                'gateway': '192.168.1.1',
                'dns1': '8.8.8.8',
                'dns2': '8.8.4.4'
            },
            {
                'ip': '192.168.1.101',
                'mask': '255.255.255.0',
                'gateway': '192.168.1.1',
                'dns1': '1.1.1.1',
                'dns2': '1.0.0.1'
            },
            {
                'mode': 'dhcp',
                'dns_mode': 'auto'
            }
        ]
        
        # 快速应用多个配置
        for i, config in enumerate(configs):
            start_time = time.time()
            success = apply_profile('Test Ethernet', config)
            end_time = time.time()
            
            assert success, f"配置 {i+1} 应用失败"
            assert end_time - start_time < 5.0, f"配置 {i+1} 应用时间过长"
    
    @patch('subprocess.run')
    @patch('netkit.services.netconfig.wmi_engine.get_network_adapters')
    def test_concurrent_interface_operations(self, mock_wmi, mock_subprocess):
        """测试并发接口操作"""
        # 模拟多个网卡
        mock_wmi.return_value = [
            {
                'Name': f'Test Ethernet {i}',
                'Description': f'Test Network Adapter {i}',
                'DeviceID': f'TEST_DEVICE_{i:02d}',
                'MACAddress': f'00:11:22:33:44:{i:02x}',
                'NetConnectionStatus': 2,
                'ConfigManagerErrorCode': 0
            }
            for i in range(5)
        ]
        
        # 模拟成功的netsh命令
        mock_subprocess.return_value = Mock(
            returncode=0,
            stdout="配置成功",
            stderr=""
        )
        
        # 并发获取接口信息
        import concurrent.futures
        
        def get_interface_info(interface_name):
            return get_interface_config(interface_name)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(get_interface_info, f'Test Ethernet {i}')
                for i in range(5)
            ]
            
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # 验证所有操作都成功
        assert len(results) == 5
        for result in results:
            assert isinstance(result, dict)
            assert 'name' in result


# UI集成测试暂时移到GUI测试模块中
# 这里专注于服务层的集成测试


if __name__ == "__main__":
    # 运行集成测试
    pytest.main([__file__, "-v", "-m", "integration"])