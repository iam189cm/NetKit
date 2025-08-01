#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NetKit端到端测试
完整的网络配置和测试工作流程
"""

import pytest
import time
from unittest.mock import Mock, patch

# 导入实际的服务模块
from netkit.services.netconfig import (
    get_network_interfaces,
    validate_ip_config,
    apply_profile,
    get_interface_config
)
from netkit.services.ping import PingService


class TestNetKitE2E:
    """NetKit端到端测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.test_interface = "以太网"
        self.ping_service = PingService()
        self.test_network = "192.168.1"
    
    @patch('wmi.WMI')
    @patch('pythoncom.CoInitialize')
    @patch('netkit.services.netconfig.async_manager.get_async_manager')
    @patch('subprocess.run')
    def test_complete_network_setup_and_test_workflow(self, mock_subprocess, mock_async_manager, mock_coinit, mock_wmi):
        """测试完整的网络设置和测试工作流程"""
        # 1. 模拟网络接口发现
        mock_adapter_info = Mock()
        mock_adapter_info.connection_id = self.test_interface
        mock_adapter_info.description = "Realtek PCIe GbE Family Controller"
        mock_adapter_info.connection_status = "Connected"
        mock_adapter_info.mac_address = "00:11:22:33:44:55"
        
        mock_manager = Mock()
        mock_manager.get_all_adapters_fast.return_value = [mock_adapter_info]
        mock_async_manager.return_value = mock_manager
        
        # 2. 模拟WMI网络配置
        mock_adapter = Mock()
        mock_adapter.NetConnectionID = self.test_interface
        mock_adapter.Index = 12
        
        mock_config = Mock()
        mock_config.Index = 12
        mock_config.EnableStatic.return_value = (0,)  # 成功
        mock_config.SetGateways.return_value = (0,)
        mock_config.SetDNSServerSearchOrder.return_value = (0,)
        
        mock_wmi_instance = Mock()
        mock_wmi_instance.Win32_NetworkAdapter.return_value = [mock_adapter]
        mock_wmi_instance.Win32_NetworkAdapterConfiguration.return_value = [mock_config]
        mock_wmi.return_value = mock_wmi_instance
        
        # 3. 模拟ping命令成功
        mock_ping_result = Mock()
        mock_ping_result.returncode = 0
        mock_ping_result.stdout = b"Pinging 8.8.8.8 with 32 bytes of data:\nReply from 8.8.8.8: bytes=32 time=15ms TTL=117\n\nPing statistics for 8.8.8.8:\n    Packets: Sent = 1, Received = 1, Lost = 0 (0% loss)"
        mock_ping_result.stderr = b""
        mock_subprocess.return_value = mock_ping_result
        
        # === 执行完整工作流程 ===
        
        # === 步骤1: 发现网络接口 ===
        print("步骤1: 发现网络接口...")
        interfaces = get_network_interfaces()
        assert len(interfaces) > 0, "未发现任何网络接口"
        assert self.test_interface in interfaces, f"未找到测试接口 {self.test_interface}"
        print(f"✓ 发现 {len(interfaces)} 个网络接口")
        
        # === 步骤2: 验证IP配置 ===
        print("步骤2: 验证IP配置...")
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
        assert validation_result['valid'] == True, f"IP配置验证失败: {validation_result.get('error', '')}"
        print("✓ IP配置验证通过")
        
        # === 步骤3: 应用网络配置 ===
        print("步骤3: 应用网络配置...")
        apply_result = apply_profile(
            interface_name=self.test_interface,
            ip_mode='manual',
            dns_mode='manual',
            ip_config=ip_config,
            dns_config=dns_config
        )
        assert apply_result['success'] == True, f"网络配置应用失败: {apply_result.get('error', '')}"
        print("✓ 网络配置应用成功")
        
        # === 步骤4: 测试网络连通性 ===
        print("步骤4: 测试网络连通性...")
        
        # 4.1 测试网关连通性
        gateway_result = self.ping_service.ping_single('8.8.8.8', count=2, timeout=2000)
        assert gateway_result['success'] == True, "网关ping测试失败"
        print("✓ 网关连通正常")
        
        # 4.2 测试DNS服务器
        dns_result = self.ping_service.ping_single(dns_config['dns1'], count=2, timeout=3000)
        assert dns_result['success'] == True, "DNS服务器ping测试失败"
        print("✓ DNS服务器连通正常")
        
        print("✅ 完整工作流程测试通过！")
    
    @patch('netkit.services.netconfig.async_manager.get_async_manager')
    def test_network_interface_discovery_workflow(self, mock_async_manager):
        """测试网络接口发现工作流程"""
        # 模拟多个网络接口
        mock_adapters = []
        interface_names = ["以太网", "WLAN", "蓝牙网络连接"]
        
        for i, name in enumerate(interface_names):
            mock_adapter = Mock()
            mock_adapter.connection_id = name
            mock_adapter.description = f"Network Adapter {i+1}"
            mock_adapter.connection_status = "Connected" if i < 2 else "Disconnected"
            mock_adapters.append(mock_adapter)
        
        mock_manager = Mock()
        mock_manager.get_all_adapters_fast.return_value = mock_adapters
        mock_async_manager.return_value = mock_manager
        
        # 执行接口发现
        interfaces = get_network_interfaces()
        
        # 验证结果
        assert len(interfaces) >= 2, "应该发现至少2个接口"
        assert "以太网" in interfaces
        assert "WLAN" in interfaces
        
        print(f"✓ 发现接口: {', '.join(interfaces)}")
    
    def test_ip_validation_workflow(self):
        """测试IP配置验证工作流程"""
        # 测试各种IP配置场景
        test_cases = [
            # (ip, mask, gateway, dns, expected_valid, description)
            ('192.168.1.100', '255.255.255.0', '192.168.1.1', '8.8.8.8', True, '标准家庭网络'),
            ('10.0.0.100', '255.255.255.0', '10.0.0.1', '1.1.1.1', True, '企业网络'),
            ('172.16.0.100', '255.255.0.0', '172.16.0.1', '8.8.8.8,8.8.4.4', True, '大型网络'),
            ('999.999.999.999', '255.255.255.0', '192.168.1.1', '8.8.8.8', False, '无效IP地址'),
            ('192.168.1.100', '999.999.999.999', '192.168.1.1', '8.8.8.8', False, '无效子网掩码'),
        ]
        
        for ip, mask, gateway, dns, expected_valid, description in test_cases:
            print(f"测试: {description}")
            
            result = validate_ip_config(ip=ip, mask=mask, gateway=gateway, dns=dns)
            
            if expected_valid:
                assert result['valid'] == True, f"{description} 应该验证通过"
                print(f"✓ {description} 验证通过")
            else:
                assert result['valid'] == False, f"{description} 应该验证失败"
                print(f"✓ {description} 正确识别为无效配置")
    
    @patch('netkit.services.ping.ping_executor.subprocess.run')
    def test_network_connectivity_workflow(self, mock_subprocess):
        """测试网络连通性测试工作流程"""
        # 模拟不同的ping结果
        def mock_ping_response(args, **kwargs):
            host = args[-1]  # 最后一个参数是主机地址
            
            mock_result = Mock()
            if host in ['8.8.8.8', '1.1.1.1', '8.8.4.4']:
                # 模拟成功的ping
                mock_result.returncode = 0
                mock_result.stdout = f"Pinging {host} with 32 bytes of data:\nReply from {host}: bytes=32 time=15ms TTL=117\n\nPing statistics for {host}:\n    Packets: Sent = 1, Received = 1, Lost = 0 (0% loss)".encode()
                mock_result.stderr = b""
            else:
                # 模拟失败的ping
                mock_result.returncode = 1
                mock_result.stdout = f"Pinging {host} with 32 bytes of data:\nRequest timed out.\n\nPing statistics for {host}:\n    Packets: Sent = 1, Received = 0, Lost = 1 (100% loss)".encode()
                mock_result.stderr = b""
            
            return mock_result
        
        mock_subprocess.side_effect = mock_ping_response
        
        # 测试连通性检查工作流程
        test_hosts = [
            ('8.8.8.8', True, 'Google DNS'),
            ('1.1.1.1', True, 'Cloudflare DNS'),
            ('192.168.1.999', False, '无效私有地址'),
        ]
        
        connectivity_results = {}
        
        for host, expected_success, description in test_hosts:
            print(f"测试连通性: {description} ({host})")
            
            result = self.ping_service.ping_single(host, count=1, timeout=2000)
            connectivity_results[host] = result
            
            if expected_success:
                assert result['success'] == True, f"{description} 应该连通"
                print(f"✓ {description} 连通正常")
            else:
                assert result['success'] == False, f"{description} 应该不连通"
                print(f"✓ {description} 正确识别为不连通")
        
        # 验证批量连通性测试
        batch_hosts = ['8.8.8.8', '1.1.1.1']
        batch_results = self.ping_service.batch_ping(batch_hosts, count=1, timeout=2000, max_workers=2)
        
        assert len(batch_results) == 2, "批量ping应该返回所有主机的结果"
        for host in batch_hosts:
            assert host in batch_results, f"批量ping结果中应该包含 {host}"
            assert batch_results[host]['result']['success'] == True, f"批量ping中 {host} 应该成功"
        
        print("✓ 批量连通性测试通过")


if __name__ == "__main__":
    # 运行端到端测试
    pytest.main([__file__, "-v"])