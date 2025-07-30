#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
端到端集成测试
测试整个NetKit应用的完整工作流程
"""

import pytest
import time
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# 导入测试目标
from netkit.services.netconfig import (
    get_network_interfaces,
    apply_profile,
    validate_ip_config
)
from netkit.services.ping.ping_service import PingService
from netkit.services.subnet import SubnetCalculator
from netkit.services.traceroute import TracerouteService
from netkit.services.route import RouteService


@pytest.mark.integration
class TestCompleteWorkflow:
    """完整工作流程测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.test_interface = "Test Ethernet"
        self.ping_service = PingService()
        self.subnet_calc = SubnetCalculator()
        self.traceroute_service = TracerouteService()
        self.route_service = RouteService()
    
    @patch('subprocess.run')
    @patch('netkit.services.netconfig.wmi_engine.get_network_adapters')
    def test_complete_network_setup_workflow(self, mock_wmi, mock_subprocess):
        """测试完整的网络设置工作流程"""
        # 1. 模拟网卡信息
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
        
        # 2. 模拟各种命令的成功输出
        def mock_command_response(cmd, **kwargs):
            cmd_str = ' '.join(cmd) if isinstance(cmd, list) else str(cmd)
            
            if 'netsh interface ip set address' in cmd_str:
                return Mock(returncode=0, stdout="IP配置成功", stderr="")
            elif 'netsh interface ip set dns' in cmd_str:
                return Mock(returncode=0, stdout="DNS配置成功", stderr="")
            elif 'ping' in cmd_str:
                return Mock(
                    returncode=0,
                    stdout="来自 8.8.8.8 的回复: 字节=32 时间=15ms TTL=117\n平均 = 15ms",
                    stderr=""
                )
            elif 'tracert' in cmd_str:
                return Mock(
                    returncode=0,
                    stdout="""
通过最多 30 个跃点跟踪到 8.8.8.8 的路由
  1     2 ms     1 ms     1 ms  192.168.1.1
  2    15 ms    14 ms    16 ms  8.8.8.8
跟踪完成。
                    """,
                    stderr=""
                )
            elif 'route' in cmd_str:
                return Mock(
                    returncode=0,
                    stdout="路由操作成功",
                    stderr=""
                )
            else:
                return Mock(returncode=0, stdout="命令成功", stderr="")
        
        mock_subprocess.side_effect = mock_command_response
        
        # 3. 执行完整工作流程
        
        # 步骤1: 获取网络接口
        interfaces = get_network_interfaces()
        assert len(interfaces) > 0
        test_interface = next((iface for iface in interfaces 
                             if iface['name'] == self.test_interface), None)
        assert test_interface is not None
        
        # 步骤2: 配置IP地址
        ip_config = {
            'ip': '192.168.1.100',
            'mask': '255.255.255.0',
            'gateway': '192.168.1.1',
            'dns1': '8.8.8.8',
            'dns2': '8.8.4.4'
        }
        
        # 验证配置
        is_valid, errors = validate_ip_config(ip_config)
        assert is_valid, f"IP配置验证失败: {errors}"
        
        # 应用配置
        config_success = apply_profile(self.test_interface, ip_config)
        assert config_success, "IP配置应用失败"
        
        # 步骤3: 测试网络连通性
        ping_result = self.ping_service.ping_host('8.8.8.8')
        assert ping_result is not None
        assert ping_result['success'] == True
        
        # 步骤4: 计算子网信息
        subnet_info = self.subnet_calc.calculate_subnet(
            ip_config['ip'], 
            ip_config['mask']
        )
        assert subnet_info is not None
        assert 'network' in subnet_info
        assert 'broadcast' in subnet_info
        
        # 步骤5: 执行路由追踪
        traceroute_result = self.traceroute_service.traceroute('8.8.8.8')
        assert traceroute_result is not None
        assert len(traceroute_result) > 0
        
        # 验证整个流程的调用次数
        assert mock_subprocess.call_count >= 5  # 至少5次命令调用
    
    @patch('subprocess.run')
    @patch('netkit.services.netconfig.wmi_engine.get_network_adapters')
    def test_network_troubleshooting_workflow(self, mock_wmi, mock_subprocess):
        """测试网络故障排除工作流程"""
        # 1. 模拟网络问题场景
        mock_wmi.return_value = [
            {
                'Name': self.test_interface,
                'Description': 'Test Network Adapter',
                'DeviceID': 'TEST_DEVICE_01',
                'MACAddress': '00:11:22:33:44:55',
                'NetConnectionStatus': 7,  # 断开连接
                'ConfigManagerErrorCode': 0
            }
        ]
        
        # 2. 模拟命令响应
        def mock_troubleshoot_response(cmd, **kwargs):
            cmd_str = ' '.join(cmd) if isinstance(cmd, list) else str(cmd)
            
            if 'ping 127.0.0.1' in cmd_str:  # 本地回环测试
                return Mock(
                    returncode=0,
                    stdout="来自 127.0.0.1 的回复: 字节=32 时间<1ms TTL=128",
                    stderr=""
                )
            elif 'ping 192.168.1.1' in cmd_str:  # 网关测试
                return Mock(
                    returncode=1,
                    stdout="",
                    stderr="请求超时"
                )
            elif 'ping 8.8.8.8' in cmd_str:  # 外网测试
                return Mock(
                    returncode=1,
                    stdout="",
                    stderr="请求超时"
                )
            elif 'tracert' in cmd_str:
                return Mock(
                    returncode=1,
                    stdout="无法解析目标系统名",
                    stderr=""
                )
            else:
                return Mock(returncode=0, stdout="", stderr="")
        
        mock_subprocess.side_effect = mock_troubleshoot_response
        
        # 3. 执行故障排除流程
        
        # 步骤1: 检查网络接口状态
        interfaces = get_network_interfaces()
        problem_interface = next((iface for iface in interfaces 
                                if iface['name'] == self.test_interface), None)
        assert problem_interface is not None
        assert problem_interface['status'] == 'Disconnected'
        
        # 步骤2: 本地回环测试
        loopback_result = self.ping_service.ping_host('127.0.0.1')
        assert loopback_result['success'] == True  # 本地回环应该成功
        
        # 步骤3: 网关连通性测试
        gateway_result = self.ping_service.ping_host('192.168.1.1')
        assert gateway_result['success'] == False  # 网关不通
        
        # 步骤4: 外网连通性测试
        internet_result = self.ping_service.ping_host('8.8.8.8')
        assert internet_result['success'] == False  # 外网不通
        
        # 步骤5: 路由追踪测试
        traceroute_result = self.traceroute_service.traceroute('8.8.8.8')
        assert traceroute_result is None or len(traceroute_result) == 0
        
        # 根据测试结果，可以判断是网络接口问题
    
    @patch('subprocess.run')
    @patch('netkit.services.netconfig.wmi_engine.get_network_adapters')
    def test_configuration_backup_restore_workflow(self, mock_wmi, mock_subprocess):
        """测试配置备份和恢复工作流程"""
        # 1. 模拟网卡信息
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
        
        # 2. 模拟成功的命令响应
        mock_subprocess.return_value = Mock(
            returncode=0,
            stdout="配置成功",
            stderr=""
        )
        
        # 3. 创建临时配置文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            backup_file = Path(f.name)
            
            # 原始配置
            original_config = {
                'interface': self.test_interface,
                'config': {
                    'ip': '192.168.1.100',
                    'mask': '255.255.255.0',
                    'gateway': '192.168.1.1',
                    'dns1': '8.8.8.8',
                    'dns2': '8.8.4.4'
                }
            }
            
            # 保存配置到文件
            json.dump(original_config, f, indent=2)
        
        try:
            # 4. 执行配置备份恢复流程
            
            # 步骤1: 应用原始配置
            success = apply_profile(
                original_config['interface'], 
                original_config['config']
            )
            assert success
            
            # 步骤2: 更改配置
            new_config = {
                'ip': '192.168.1.200',
                'mask': '255.255.255.0',
                'gateway': '192.168.1.1',
                'dns1': '1.1.1.1',
                'dns2': '1.0.0.1'
            }
            
            success = apply_profile(self.test_interface, new_config)
            assert success
            
            # 步骤3: 从备份文件恢复配置
            with open(backup_file, 'r') as f:
                backup_data = json.load(f)
            
            success = apply_profile(
                backup_data['interface'],
                backup_data['config']
            )
            assert success
            
            # 验证配置应用次数
            assert mock_subprocess.call_count >= 6  # 至少6次配置操作
            
        finally:
            # 清理临时文件
            backup_file.unlink(missing_ok=True)


@pytest.mark.integration
@pytest.mark.slow
class TestPerformanceWorkflow:
    """性能工作流程测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.ping_service = PingService()
        self.subnet_calc = SubnetCalculator()
    
    @patch('subprocess.run')
    def test_batch_operations_performance(self, mock_subprocess):
        """测试批量操作性能"""
        # 模拟快速响应的ping命令
        mock_subprocess.return_value = Mock(
            returncode=0,
            stdout="来自 主机 的回复: 字节=32 时间=1ms TTL=64\n平均 = 1ms",
            stderr=""
        )
        
        # 测试批量ping性能
        hosts = [f'192.168.1.{i}' for i in range(1, 51)]  # 50个主机
        
        start_time = time.time()
        results = self.ping_service.ping_multiple_hosts(hosts, max_workers=10)
        end_time = time.time()
        
        # 验证性能要求
        assert len(results) == 50
        assert end_time - start_time < 10  # 应该在10秒内完成
        
        # 验证结果质量
        successful_pings = [r for r in results if r['success']]
        assert len(successful_pings) == 50  # 所有ping都应该成功
    
    def test_subnet_calculation_performance(self):
        """测试子网计算性能"""
        # 测试大量子网计算
        test_cases = [
            ('192.168.1.0', '255.255.255.0'),
            ('10.0.0.0', '255.0.0.0'),
            ('172.16.0.0', '255.255.0.0'),
            ('192.168.0.0', '255.255.252.0'),
            ('10.10.10.0', '255.255.255.128')
        ] * 20  # 重复20次，总共100个计算
        
        start_time = time.time()
        results = []
        
        for ip, mask in test_cases:
            result = self.subnet_calc.calculate_subnet(ip, mask)
            results.append(result)
        
        end_time = time.time()
        
        # 验证性能要求
        assert len(results) == 100
        assert end_time - start_time < 1  # 应该在1秒内完成
        
        # 验证结果正确性
        for result in results:
            assert result is not None
            assert 'network' in result
            assert 'broadcast' in result
            assert 'host_count' in result


@pytest.mark.integration
class TestErrorRecoveryWorkflow:
    """错误恢复工作流程测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.ping_service = PingService()
    
    @patch('subprocess.run')
    @patch('netkit.services.netconfig.wmi_engine.get_network_adapters')
    def test_network_failure_recovery(self, mock_wmi, mock_subprocess):
        """测试网络故障恢复"""
        # 1. 模拟网卡信息
        mock_wmi.return_value = [
            {
                'Name': 'Test Ethernet',
                'Description': 'Test Network Adapter',
                'DeviceID': 'TEST_DEVICE_01',
                'MACAddress': '00:11:22:33:44:55',
                'NetConnectionStatus': 2,
                'ConfigManagerErrorCode': 0
            }
        ]
        
        # 2. 模拟命令失败然后成功的场景
        call_count = 0
        
        def mock_recovery_response(cmd, **kwargs):
            nonlocal call_count
            call_count += 1
            
            # 前几次调用失败，后面成功
            if call_count <= 2:
                return Mock(
                    returncode=1,
                    stdout="",
                    stderr="网络配置失败"
                )
            else:
                return Mock(
                    returncode=0,
                    stdout="配置成功",
                    stderr=""
                )
        
        mock_subprocess.side_effect = mock_recovery_response
        
        # 3. 执行带重试的配置操作
        max_retries = 3
        success = False
        
        for attempt in range(max_retries):
            try:
                result = apply_profile('Test Ethernet', {
                    'ip': '192.168.1.100',
                    'mask': '255.255.255.0',
                    'gateway': '192.168.1.1',
                    'dns1': '8.8.8.8',
                    'dns2': '8.8.4.4'
                })
                
                if result:
                    success = True
                    break
                    
            except Exception:
                if attempt == max_retries - 1:
                    raise
                time.sleep(1)  # 重试前等待
        
        # 验证最终成功
        assert success, "配置应该在重试后成功"
        assert call_count >= 2, "应该有重试操作"


if __name__ == "__main__":
    # 运行端到端集成测试
    pytest.main([__file__, "-v", "-m", "integration"])