#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NetKit真实性能测试
基于项目实际实现的网络配置和Ping功能性能测试
"""

import pytest
import time
import statistics
from unittest.mock import Mock, patch
from concurrent.futures import ThreadPoolExecutor, as_completed

# 导入实际的服务模块
from netkit.services.netconfig import (
    get_network_interfaces,
    validate_ip_config,
    apply_profile
)
from netkit.services.ping import PingService


@pytest.mark.performance
class TestNetworkConfigRealPerformance:
    """网络配置真实性能测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.test_configs = [
            ('192.168.1.100', '255.255.255.0', '192.168.1.1', '8.8.8.8,8.8.4.4'),
            ('10.0.0.100', '255.255.255.0', '10.0.0.1', '1.1.1.1,1.0.0.1'),
            ('172.16.0.100', '255.255.0.0', '172.16.0.1', '8.8.8.8,1.1.1.1'),
        ] * 20  # 60个配置测试
    
    @patch('netkit.services.netconfig.async_manager.get_async_manager')
    def test_interface_discovery_performance(self, mock_async_manager):
        """测试网络接口发现性能"""
        # 模拟多个网络接口
        mock_adapters = []
        for i in range(20):  # 模拟20个网络接口
            mock_adapter = Mock()
            mock_adapter.connection_id = f"以太网 {i}"
            mock_adapter.description = f"Network Adapter {i}"
            mock_adapter.connection_status = "Connected"
            mock_adapters.append(mock_adapter)
        
        mock_manager = Mock()
        mock_manager.get_all_adapters_fast.return_value = mock_adapters
        mock_async_manager.return_value = mock_manager
        
        # 执行性能测试
        times = []
        for _ in range(20):
            start_time = time.time()
            interfaces = get_network_interfaces()
            end_time = time.time()
            times.append(end_time - start_time)
            
            assert len(interfaces) == 20
        
        # 性能分析
        avg_time = statistics.mean(times)
        max_time = max(times)
        min_time = min(times)
        
        # 性能断言
        assert avg_time < 0.5, f"平均接口发现时间过长: {avg_time:.3f}s"
        assert max_time < 1.0, f"最大接口发现时间过长: {max_time:.3f}s"
        
        print(f"接口发现性能: 平均 {avg_time:.3f}s, 最大 {max_time:.3f}s, 最小 {min_time:.3f}s")
    
    def test_ip_validation_performance(self):
        """测试IP配置验证性能"""
        # 执行大量验证操作
        times = []
        
        for ip, mask, gateway, dns in self.test_configs:
            start_time = time.time()
            result = validate_ip_config(ip, mask, gateway, dns)
            end_time = time.time()
            times.append(end_time - start_time)
            
            assert result['valid'] == True, f"配置验证失败: {ip}, {mask}, {gateway}, {dns}"
        
        # 性能分析
        avg_time = statistics.mean(times)
        max_time = max(times)
        total_time = sum(times)
        
        # 性能断言
        assert avg_time < 0.01, f"平均验证时间过长: {avg_time:.6f}s"
        assert max_time < 0.05, f"最大验证时间过长: {max_time:.6f}s"
        assert total_time < 1.0, f"总验证时间过长: {total_time:.3f}s"
        
        print(f"IP验证性能: 平均 {avg_time:.6f}s, 最大 {max_time:.6f}s, 总计 {total_time:.3f}s")
    
    @patch('wmi.WMI')
    @patch('pythoncom.CoInitialize')
    def test_configuration_application_performance(self, mock_coinit, mock_wmi):
        """测试配置应用性能"""
        # 模拟WMI快速响应
        mock_adapter = Mock()
        mock_adapter.NetConnectionID = "以太网"
        mock_adapter.Index = 12
        
        mock_config = Mock()
        mock_config.Index = 12
        mock_config.EnableStatic.return_value = (0,)
        mock_config.SetGateways.return_value = (0,)
        mock_config.SetDNSServerSearchOrder.return_value = (0,)
        
        mock_wmi_instance = Mock()
        mock_wmi_instance.Win32_NetworkAdapter.return_value = [mock_adapter]
        mock_wmi_instance.Win32_NetworkAdapterConfiguration.return_value = [mock_config]
        mock_wmi.return_value = mock_wmi_instance
        
        # 性能测试配置
        test_configs = [
            {
                'ip_config': {'ip': '192.168.1.100', 'mask': '255.255.255.0', 'gateway': '192.168.1.1'},
                'dns_config': {'dns1': '8.8.8.8', 'dns2': '8.8.4.4'}
            },
            {
                'ip_config': {'ip': '192.168.1.101', 'mask': '255.255.255.0', 'gateway': '192.168.1.1'},
                'dns_config': {'dns1': '1.1.1.1', 'dns2': '1.0.0.1'}
            },
            {
                'ip_config': {'ip': '192.168.1.102', 'mask': '255.255.255.0', 'gateway': '192.168.1.1'},
                'dns_config': {'dns1': '8.8.8.8', 'dns2': '1.1.1.1'}
            }
        ]
        
        times = []
        for config in test_configs:
            start_time = time.time()
            result = apply_profile(
                interface_name="以太网",
                ip_mode='manual',
                dns_mode='manual',
                ip_config=config['ip_config'],
                dns_config=config['dns_config']
            )
            end_time = time.time()
            times.append(end_time - start_time)
            
            assert result['success'] == True, f"配置应用失败: {config}"
        
        # 性能分析
        avg_time = statistics.mean(times)
        max_time = max(times)
        
        # 性能断言
        assert avg_time < 1.0, f"平均配置应用时间过长: {avg_time:.3f}s"
        assert max_time < 2.0, f"最大配置应用时间过长: {max_time:.3f}s"
        
        print(f"配置应用性能: 平均 {avg_time:.3f}s, 最大 {max_time:.3f}s")


@pytest.mark.performance
class TestPingServiceRealPerformance:
    """Ping服务真实性能测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.ping_service = PingService()
    
    @patch('subprocess.run')
    def test_single_ping_performance(self, mock_subprocess):
        """测试单次ping性能"""
        # 模拟快速ping响应
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "来自 8.8.8.8 的回复: 字节=32 时间=15ms TTL=117"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        # 性能测试
        times = []
        hosts = ['8.8.8.8', '1.1.1.1', '8.8.4.4', '1.0.0.1'] * 5  # 20次ping
        
        for host in hosts:
            start_time = time.time()
            result = self.ping_service.ping_single(host, count=1, timeout=1000)
            end_time = time.time()
            times.append(end_time - start_time)
            
            assert result['success'] == True
        
        # 性能分析
        avg_time = statistics.mean(times)
        max_time = max(times)
        total_time = sum(times)
        
        # 性能断言
        assert avg_time < 0.5, f"平均单次ping时间过长: {avg_time:.3f}s"
        assert max_time < 1.0, f"最大单次ping时间过长: {max_time:.3f}s"
        assert total_time < 10.0, f"总ping时间过长: {total_time:.3f}s"
        
        print(f"单次ping性能: 平均 {avg_time:.3f}s, 最大 {max_time:.3f}s, 总计 {total_time:.3f}s")
    
    @patch('subprocess.run')
    def test_batch_ping_performance(self, mock_subprocess):
        """测试批量ping性能"""
        # 模拟ping响应
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "来自 主机 的回复: 字节=32 时间=10ms TTL=64"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        # 批量ping测试
        hosts = [f'192.168.1.{i}' for i in range(1, 26)]  # 25个主机
        
        start_time = time.time()
        results = self.ping_service.batch_ping(hosts, count=1, timeout=1000, max_workers=10)
        end_time = time.time()
        
        total_time = end_time - start_time
        
        # 验证结果
        assert len(results) == 25
        for host in hosts:
            assert host in results
            assert results[host]['result']['success'] == True
        
        # 性能断言
        assert total_time < 5.0, f"批量ping时间过长: {total_time:.3f}s"
        
        avg_time_per_host = total_time / len(hosts)
        assert avg_time_per_host < 0.2, f"平均每主机ping时间过长: {avg_time_per_host:.3f}s"
        
        print(f"批量ping性能: 总时间 {total_time:.3f}s, 平均每主机 {avg_time_per_host:.3f}s")
    
    @patch('subprocess.run')
    def test_concurrent_vs_sequential_ping_performance(self, mock_subprocess):
        """测试并发vs顺序ping性能对比"""
        # 模拟ping响应
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "来自 主机 的回复: 字节=32 时间=50ms TTL=64"  # 模拟较慢的响应
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        hosts = ['8.8.8.8', '1.1.1.1', '8.8.4.4', '1.0.0.1', '9.9.9.9']
        
        # 顺序执行测试
        start_time = time.time()
        sequential_results = []
        for host in hosts:
            result = self.ping_service.ping_single(host, count=1, timeout=1000)
            sequential_results.append(result)
        sequential_time = time.time() - start_time
        
        # 并发执行测试
        start_time = time.time()
        concurrent_results = self.ping_service.batch_ping(hosts, count=1, timeout=1000, max_workers=5)
        concurrent_time = time.time() - start_time
        
        # 验证结果
        assert len(sequential_results) == 5
        assert len(concurrent_results) == 5
        
        # 性能对比
        speedup = sequential_time / concurrent_time if concurrent_time > 0 else 1
        
        # 并发应该有性能优势
        assert concurrent_time <= sequential_time, f"并发执行应该不慢于顺序执行: 顺序{sequential_time:.3f}s vs 并发{concurrent_time:.3f}s"
        
        print(f"性能对比: 顺序 {sequential_time:.3f}s, 并发 {concurrent_time:.3f}s, 加速比 {speedup:.2f}x")


@pytest.mark.performance
@pytest.mark.slow
class TestNetKitRealStressPerformance:
    """NetKit真实压力性能测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.ping_service = PingService()
    
    @patch('subprocess.run')
    def test_high_volume_ping_stress(self, mock_subprocess):
        """测试大量ping的压力性能"""
        # 模拟ping响应
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "来自 主机 的回复: 字节=32 时间=5ms TTL=64"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        # 大量主机ping测试
        hosts = [f'192.168.1.{i}' for i in range(1, 101)]  # 100个主机
        
        start_time = time.time()
        results = self.ping_service.batch_ping(hosts, count=1, timeout=1000, max_workers=25)
        end_time = time.time()
        
        total_time = end_time - start_time
        
        # 验证结果
        assert len(results) == 100
        
        successful_pings = sum(1 for result in results.values() if result['result']['success'])
        success_rate = successful_pings / len(results)
        
        # 压力测试断言
        assert success_rate >= 0.95, f"成功率过低: {success_rate:.2%}"
        assert total_time < 15.0, f"压力测试时间过长: {total_time:.3f}s"
        
        avg_time_per_host = total_time / len(hosts)
        assert avg_time_per_host < 0.15, f"平均每主机时间过长: {avg_time_per_host:.3f}s"
        
        print(f"压力测试: {successful_pings}/{len(results)} 成功 ({success_rate:.1%}), 总时间 {total_time:.3f}s")
    
    def test_validation_stress_performance(self):
        """测试IP验证压力性能"""
        # 生成大量测试配置
        configs = []
        for i in range(1, 255):
            for j in range(1, 5):  # 每个网段4个IP
                configs.append((
                    f'192.168.{j}.{i}',
                    '255.255.255.0',
                    f'192.168.{j}.1',
                    '8.8.8.8,8.8.4.4'
                ))
        
        # 只取前500个配置进行测试
        configs = configs[:500]
        
        start_time = time.time()
        valid_count = 0
        
        for ip, mask, gateway, dns in configs:
            result = validate_ip_config(ip, mask, gateway, dns)
            if result['valid']:
                valid_count += 1
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 验证结果
        success_rate = valid_count / len(configs)
        assert success_rate >= 0.95, f"验证成功率过低: {success_rate:.2%}"
        assert total_time < 5.0, f"验证压力测试时间过长: {total_time:.3f}s"
        
        avg_time = total_time / len(configs)
        assert avg_time < 0.01, f"平均验证时间过长: {avg_time:.6f}s"
        
        print(f"验证压力测试: {valid_count}/{len(configs)} 成功 ({success_rate:.1%}), 总时间 {total_time:.3f}s")


@pytest.mark.performance
class TestNetKitRealBenchmark:
    """NetKit真实基准测试"""
    
    def test_validation_benchmark(self, benchmark):
        """IP配置验证基准测试"""
        # 基准测试
        result = benchmark(
            validate_ip_config,
            '192.168.1.100',
            '255.255.255.0',
            '192.168.1.1',
            '8.8.8.8,8.8.4.4'
        )
        
        # 验证结果
        assert result['valid'] == True
    
    @patch('netkit.services.netconfig.async_manager.get_async_manager')
    def test_interface_discovery_benchmark(self, mock_async_manager, benchmark):
        """网络接口发现基准测试"""
        # 模拟标准数量的网络接口
        mock_adapters = []
        for i in range(3):  # 3个网络接口
            mock_adapter = Mock()
            mock_adapter.connection_id = f"以太网 {i}"
            mock_adapter.description = f"Network Adapter {i}"
            mock_adapters.append(mock_adapter)
        
        mock_manager = Mock()
        mock_manager.get_all_adapters_fast.return_value = mock_adapters
        mock_async_manager.return_value = mock_manager
        
        # 基准测试
        result = benchmark(get_network_interfaces)
        
        # 验证结果
        assert len(result) == 3
        for interface_name in result:
            assert isinstance(interface_name, str)
            assert len(interface_name) > 0


if __name__ == "__main__":
    # 运行NetKit真实性能测试
    pytest.main([__file__, "-v", "-m", "performance", "--benchmark-only"])