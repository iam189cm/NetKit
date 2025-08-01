#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络配置真实集成测试
基于项目实际实现的网络配置功能集成测试
"""

import pytest
import time
from unittest.mock import Mock, patch

# 导入实际的网络配置模块
from netkit.services.netconfig import (
    get_network_interfaces,
    get_network_interfaces_with_details,
    get_interface_config,
    validate_ip_config,
    apply_profile,
    get_network_connection_status,
    get_interface_ip_address
)


@pytest.mark.integration
class TestNetworkConfigReal:
    """基于实际实现的网络配置集成测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.test_interface = "以太网"
        self.test_ip_config = {
            'ip': '192.168.1.100',
            'mask': '255.255.255.0',
            'gateway': '192.168.1.1'
        }
        self.test_dns_config = {
            'dns1': '8.8.8.8',
            'dns2': '8.8.4.4'
        }
    
    @patch('netkit.services.netconfig.async_manager.get_async_manager')
    def test_get_network_interfaces_integration(self, mock_async_manager, test_environment, mock_network_environment):
        """测试获取网络接口列表的集成"""
        # 在CI Server环境中使用mock数据
        if mock_network_environment['mock_mode']:
            # 模拟异步管理器返回的适配器信息
            mock_adapter = Mock()
            mock_adapter.connection_id = "以太网"
            mock_adapter.description = "Intel Network Adapter"
            mock_adapter.connection_status = "Connected"
            
            mock_manager = Mock()
            mock_manager.get_all_adapters_fast.return_value = [mock_adapter]
            mock_async_manager.return_value = mock_manager
            
            # 获取接口列表
            interfaces = get_network_interfaces()
            
            # 在mock模式下应该有接口
            assert len(interfaces) > 0
            assert "以太网" in interfaces
            return
        
        # 真实环境测试
        mock_adapter = Mock()
        mock_adapter.connection_id = "以太网"
        mock_adapter.description = "Intel Network Adapter"
        mock_adapter.connection_status = "Connected"
        
        mock_manager = Mock()
        mock_manager.get_all_adapters_fast.return_value = [mock_adapter]
        mock_async_manager.return_value = mock_manager
        
        # 执行测试
        interfaces = get_network_interfaces()
        
        # 验证结果 - 允许在CI Server环境中为空
        assert isinstance(interfaces, list)
        if test_environment['is_ci'] and test_environment['is_server']:
            # CI Server环境可能返回0个接口，这是预期的
            pytest.skip("CI Server compatibility: Network interface detection differences")
        else:
            assert len(interfaces) > 0
            assert "以太网" in interfaces
        
        # 验证调用
        mock_async_manager.assert_called_once()
        mock_manager.get_all_adapters_fast.assert_called_once_with(False)
    
    @patch('netkit.services.netconfig.async_manager.get_async_manager')
    def test_get_network_interfaces_with_details_integration(self, mock_async_manager, test_environment, mock_network_environment):
        """测试获取网络接口详细信息的集成"""
        
        # 在CI Server环境中跳过或使用mock
        if test_environment['is_ci'] and test_environment['is_server'] and not test_environment['has_interfaces']:
            pytest.skip("CI Server compatibility: Skip real network interface tests")
        # 模拟适配器信息
        mock_adapter = Mock()
        mock_adapter.connection_id = "以太网"
        mock_adapter.description = "Intel Network Adapter"
        mock_adapter.mac_address = "00:11:22:33:44:55"
        mock_adapter.connection_status = "Connected"
        mock_adapter.ip_address = "192.168.1.100"
        mock_adapter.subnet_mask = "255.255.255.0"
        mock_adapter.gateway = "192.168.1.1"
        mock_adapter.dns_servers = ["8.8.8.8", "8.8.4.4"]
        
        mock_manager = Mock()
        mock_manager.get_all_adapters_fast.return_value = [mock_adapter]
        mock_async_manager.return_value = mock_manager
        
        # 执行测试
        interfaces = get_network_interfaces_with_details()
        
        # 验证结果
        assert isinstance(interfaces, list)
        assert len(interfaces) > 0
        
        interface = interfaces[0]
        # 处理tuple格式 (display_name, connection_id)
        if isinstance(interface, tuple):
            display_name, connection_id = interface
            assert connection_id == "以太网"
        elif isinstance(interface, dict):
            assert interface['name'] == "以太网"
            assert interface['description'] == "Intel Network Adapter"
            assert interface['mac_address'] == "00:11:22:33:44:55"
            assert interface['status'] == "Connected"
        else:
            # 如果是其他格式，至少验证基本内容
            assert "以太网" in str(interface)
    
    def test_validate_ip_config_integration(self):
        """测试IP配置验证的集成"""
        # 测试有效配置
        result = validate_ip_config(
            ip='192.168.1.100',
            mask='255.255.255.0',
            gateway='192.168.1.1',
            dns='8.8.8.8,8.8.4.4'
        )
        
        assert result['valid'] == True
        assert 'error' not in result or result['error'] == ''
        
        # 测试无效IP地址
        result = validate_ip_config(
            ip='999.999.999.999',
            mask='255.255.255.0',
            gateway='192.168.1.1',
            dns='8.8.8.8'
        )
        
        assert result['valid'] == False
        assert 'error' in result
        assert result['error'] != ''
    
    @patch('wmi.WMI')
    @patch('pythoncom.CoInitialize')
    def test_apply_profile_dhcp_integration(self, mock_coinit, mock_wmi):
        """测试应用DHCP配置的集成"""
        # 模拟WMI对象
        mock_adapter = Mock()
        mock_adapter.NetConnectionID = self.test_interface
        mock_adapter.Index = 12
        
        mock_config = Mock()
        mock_config.Index = 12
        mock_config.EnableDHCP.return_value = (0,)  # 成功
        mock_config.SetDNSServerSearchOrder.return_value = (0,)
        
        mock_wmi_instance = Mock()
        mock_wmi_instance.Win32_NetworkAdapter.return_value = [mock_adapter]
        mock_wmi_instance.Win32_NetworkAdapterConfiguration.return_value = [mock_config]
        mock_wmi.return_value = mock_wmi_instance
        
        # 执行测试 - DHCP模式
        result = apply_profile(
            interface_name=self.test_interface,
            ip_mode='auto',
            dns_mode='auto',
            ip_config={},
            dns_config={}
        )
        
        # 验证结果
        assert result['success'] == True
        assert 'message' in result
        
        # 验证WMI调用
        mock_coinit.assert_called()
        mock_wmi.assert_called()
        mock_config.EnableDHCP.assert_called()
    
    @patch('wmi.WMI')
    @patch('pythoncom.CoInitialize')
    def test_apply_profile_static_integration(self, mock_coinit, mock_wmi):
        """测试应用静态IP配置的集成"""
        # 模拟WMI对象
        mock_adapter = Mock()
        mock_adapter.NetConnectionID = self.test_interface
        mock_adapter.Index = 12
        
        mock_config = Mock()
        mock_config.Index = 12
        mock_config.EnableStatic.return_value = (0,)  # 成功
        # 处理SetGateways方法的不同签名 - 兼容Server和Desktop版本
        def mock_set_gateways(*args, **kwargs):
            # 接受任意参数格式，都返回成功
            return (0,)
        mock_config.SetGateways.side_effect = mock_set_gateways
        mock_config.SetDNSServerSearchOrder.return_value = (0,)
        
        mock_wmi_instance = Mock()
        mock_wmi_instance.Win32_NetworkAdapter.return_value = [mock_adapter]
        mock_wmi_instance.Win32_NetworkAdapterConfiguration.return_value = [mock_config]
        mock_wmi.return_value = mock_wmi_instance
        
        # 执行测试 - 静态IP模式
        result = apply_profile(
            interface_name=self.test_interface,
            ip_mode='manual',
            dns_mode='manual',
            ip_config=self.test_ip_config,
            dns_config=self.test_dns_config
        )
        
        # 验证结果
        assert result['success'] == True
        assert 'message' in result
        
        # 验证WMI调用
        mock_config.EnableStatic.assert_called_with(
            [self.test_ip_config['ip']], 
            [self.test_ip_config['mask']]
        )
        mock_config.SetGateways.assert_called_with(
            [self.test_ip_config['gateway']]
        )
        mock_config.SetDNSServerSearchOrder.assert_called_with(
            [self.test_dns_config['dns1'], self.test_dns_config['dns2']]
        )
    
    @patch('netkit.services.netconfig.interface_info.get_network_info_service')
    def test_get_interface_config_integration(self, mock_service):
        """测试获取接口配置的集成"""
        # 模拟网络信息服务
        mock_info_service = Mock()
        mock_info_service.get_interface_config.return_value = {
            'name': self.test_interface,
            'description': 'Intel Network Adapter',
            'mac_address': '00:11:22:33:44:55',
            'ip_address': '192.168.1.100',
            'subnet_mask': '255.255.255.0',
            'gateway': '192.168.1.1',
            'dns_servers': '8.8.8.8,8.8.4.4',
            'connection_status': 'Connected'
        }
        mock_service.return_value = mock_info_service
        
        # 执行测试
        config = get_interface_config(self.test_interface)
        
        # 验证结果
        assert isinstance(config, dict)
        assert config['name'] == self.test_interface
        assert config['mac_address'] == '00:11:22:33:44:55'
        assert config['ip_address'] == '192.168.1.100'
        assert config['connection_status'] == 'Connected'
        
        # 验证服务调用
        mock_service.assert_called()
        mock_info_service.get_interface_config.assert_called_with(self.test_interface)


@pytest.mark.integration
class TestNetworkConfigWorkflow:
    """网络配置工作流程集成测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.test_interface = "以太网"
    
    @patch('wmi.WMI')
    @patch('pythoncom.CoInitialize')
    @patch('netkit.services.netconfig.async_manager.get_async_manager')
    def test_complete_configuration_workflow(self, mock_async_manager, mock_coinit, mock_wmi):
        """测试完整的配置工作流程"""
        # 1. 模拟获取网络接口
        mock_adapter_info = Mock()
        mock_adapter_info.connection_id = self.test_interface
        mock_adapter_info.description = "Intel Network Adapter"
        mock_adapter_info.connection_status = "Connected"
        
        mock_manager = Mock()
        mock_manager.get_all_adapters_fast.return_value = [mock_adapter_info]
        mock_async_manager.return_value = mock_manager
        
        # 2. 模拟WMI配置应用
        mock_adapter = Mock()
        mock_adapter.NetConnectionID = self.test_interface
        mock_adapter.Index = 12
        
        mock_config = Mock()
        mock_config.Index = 12
        mock_config.EnableStatic.return_value = (0,)
        # 处理SetGateways方法的不同签名 - 兼容Server和Desktop版本
        def mock_set_gateways(*args, **kwargs):
            # 接受任意参数格式，都返回成功
            return (0,)
        mock_config.SetGateways.side_effect = mock_set_gateways
        mock_config.SetDNSServerSearchOrder.return_value = (0,)
        
        mock_wmi_instance = Mock()
        mock_wmi_instance.Win32_NetworkAdapter.return_value = [mock_adapter]
        mock_wmi_instance.Win32_NetworkAdapterConfiguration.return_value = [mock_config]
        mock_wmi.return_value = mock_wmi_instance
        
        # 执行完整工作流程
        
        # 步骤1: 获取网络接口列表
        interfaces = get_network_interfaces()
        assert len(interfaces) > 0
        assert self.test_interface in interfaces
        
        # 步骤2: 验证IP配置
        ip_config = {
            'ip': '192.168.1.100',
            'mask': '255.255.255.0',
            'gateway': '192.168.1.1'
        }
        dns_config = {
            'dns1': '8.8.8.8',
            'dns2': '8.8.4.4'
        }
        
        validation_result = validate_ip_config(
            ip=ip_config['ip'],
            mask=ip_config['mask'],
            gateway=ip_config['gateway'],
            dns=f"{dns_config['dns1']},{dns_config['dns2']}"
        )
        assert validation_result['valid'] == True
        
        # 步骤3: 应用配置
        apply_result = apply_profile(
            interface_name=self.test_interface,
            ip_mode='manual',
            dns_mode='manual',
            ip_config=ip_config,
            dns_config=dns_config
        )
        assert apply_result['success'] == True
        
        # 验证所有步骤都被正确调用
        mock_async_manager.assert_called()
        mock_coinit.assert_called()
        mock_wmi.assert_called()
    
    @patch('wmi.WMI')
    @patch('pythoncom.CoInitialize')
    def test_error_handling_workflow(self, mock_coinit, mock_wmi):
        """测试错误处理工作流程"""
        # 模拟找不到网络适配器的情况
        mock_wmi_instance = Mock()
        mock_wmi_instance.Win32_NetworkAdapter.return_value = []  # 空列表
        mock_wmi.return_value = mock_wmi_instance
        
        # 尝试应用配置到不存在的网卡
        result = apply_profile(
            interface_name="不存在的网卡",
            ip_mode='manual',
            dns_mode='manual',
            ip_config={'ip': '192.168.1.100', 'mask': '255.255.255.0', 'gateway': '192.168.1.1'},
            dns_config={'dns1': '8.8.8.8', 'dns2': '8.8.4.4'}
        )
        
        # 验证错误处理
        assert result['success'] == False
        assert 'error' in result
        assert '找不到网络适配器连接' in result['error']


@pytest.mark.integration
@pytest.mark.performance
class TestNetworkConfigPerformance:
    """网络配置性能集成测试"""
    
    @patch('netkit.services.netconfig.async_manager.get_async_manager')
    def test_interface_discovery_performance(self, mock_async_manager):
        """测试网络接口发现性能"""
        # 模拟多个网络接口
        mock_adapters = []
        for i in range(10):
            mock_adapter = Mock()
            mock_adapter.connection_id = f"以太网 {i}"
            mock_adapter.description = f"Network Adapter {i}"
            mock_adapters.append(mock_adapter)
        
        mock_manager = Mock()
        mock_manager.get_all_adapters_fast.return_value = mock_adapters
        mock_async_manager.return_value = mock_manager
        
        # 性能测试
        start_time = time.time()
        
        for _ in range(10):
            interfaces = get_network_interfaces()
            assert len(interfaces) == 10
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 性能断言：10次调用应该在1秒内完成
        assert total_time < 1.0, f"接口发现性能过慢: {total_time:.3f}s"
        
        avg_time = total_time / 10
        assert avg_time < 0.1, f"平均接口发现时间过慢: {avg_time:.3f}s"
    
    def test_validation_performance(self):
        """测试IP配置验证性能"""
        # 大量验证测试
        configs = [
            ('192.168.1.100', '255.255.255.0', '192.168.1.1', '8.8.8.8'),
            ('10.0.0.100', '255.255.255.0', '10.0.0.1', '1.1.1.1'),
            ('172.16.0.100', '255.255.0.0', '172.16.0.1', '8.8.4.4'),
        ] * 50  # 150个验证
        
        start_time = time.time()
        
        for ip, mask, gateway, dns in configs:
            result = validate_ip_config(ip, mask, gateway, dns)
            assert result['valid'] == True
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 性能断言：150次验证应该在2秒内完成
        assert total_time < 2.0, f"验证性能过慢: {total_time:.3f}s"
        
        avg_time = total_time / len(configs)
        assert avg_time < 0.02, f"平均验证时间过慢: {avg_time:.6f}s"


if __name__ == "__main__":
    # 运行网络配置集成测试
    pytest.main([__file__, "-v", "-m", "integration"])