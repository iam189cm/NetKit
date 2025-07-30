#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络配置性能测试
测试网络配置服务的性能表现
"""

import pytest
import time
import statistics
from unittest.mock import Mock, patch
from concurrent.futures import ThreadPoolExecutor, as_completed

# 导入测试目标
from netkit.services.netconfig import (
    get_network_interfaces,
    validate_ip_config,
    apply_profile,
    get_interface_config
)


@pytest.mark.performance
class TestNetworkConfigPerformance:
    """网络配置性能测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.test_configs = [
            {
                'ip': f'192.168.1.{i}',
                'mask': '255.255.255.0',
                'gateway': '192.168.1.1',
                'dns1': '8.8.8.8',
                'dns2': '8.8.4.4'
            }
            for i in range(100, 200)
        ]
    
    @patch('netkit.services.netconfig.wmi_engine.get_network_adapters')
    def test_interface_discovery_performance(self, mock_wmi):
        """测试网络接口发现性能"""
        # 模拟大量网络接口
        mock_wmi.return_value = [
            {
                'Name': f'Ethernet {i}',
                'Description': f'Network Adapter {i}',
                'DeviceID': f'DEVICE_{i:03d}',
                'MACAddress': f'00:11:22:33:44:{i:02x}',
                'NetConnectionStatus': 2,
                'ConfigManagerErrorCode': 0
            }
            for i in range(50)  # 50个网络接口
        ]
        
        # 执行性能测试
        times = []
        for _ in range(10):
            start_time = time.time()
            interfaces = get_network_interfaces()
            end_time = time.time()
            times.append(end_time - start_time)
        
        # 性能断言
        avg_time = statistics.mean(times)
        max_time = max(times)
        
        assert len(interfaces) == 50
        assert avg_time < 1.0, f"平均接口发现时间过长: {avg_time:.3f}s"
        assert max_time < 2.0, f"最大接口发现时间过长: {max_time:.3f}s"
        
        print(f"接口发现性能: 平均 {avg_time:.3f}s, 最大 {max_time:.3f}s")
    
    def test_ip_validation_performance(self):
        """测试IP配置验证性能"""
        # 执行大量验证操作
        times = []
        
        for config in self.test_configs:
            start_time = time.time()
            is_valid, errors = validate_ip_config(config)
            end_time = time.time()
            times.append(end_time - start_time)
            
            assert is_valid, f"配置验证失败: {config}"
        
        # 性能断言
        avg_time = statistics.mean(times)
        max_time = max(times)
        total_time = sum(times)
        
        assert avg_time < 0.01, f"平均验证时间过长: {avg_time:.6f}s"
        assert max_time < 0.05, f"最大验证时间过长: {max_time:.6f}s"
        assert total_time < 1.0, f"总验证时间过长: {total_time:.3f}s"
        
        print(f"IP验证性能: 平均 {avg_time:.6f}s, 最大 {max_time:.6f}s, 总计 {total_time:.3f}s")
    
    @patch('subprocess.run')
    def test_configuration_application_performance(self, mock_subprocess):
        """测试配置应用性能"""
        # 模拟快速的netsh命令响应
        mock_subprocess.return_value = Mock(
            returncode=0,
            stdout="配置成功",
            stderr=""
        )
        
        # 执行配置应用性能测试
        times = []
        interface_name = "Test Ethernet"
        
        for config in self.test_configs[:10]:  # 测试10个配置
            start_time = time.time()
            success = apply_profile(interface_name, config)
            end_time = time.time()
            times.append(end_time - start_time)
            
            assert success, f"配置应用失败: {config}"
        
        # 性能断言
        avg_time = statistics.mean(times)
        max_time = max(times)
        
        assert avg_time < 2.0, f"平均配置应用时间过长: {avg_time:.3f}s"
        assert max_time < 5.0, f"最大配置应用时间过长: {max_time:.3f}s"
        
        print(f"配置应用性能: 平均 {avg_time:.3f}s, 最大 {max_time:.3f}s")
    
    @patch('subprocess.run')
    @patch('netkit.services.netconfig.wmi_engine.get_network_adapters')
    def test_concurrent_operations_performance(self, mock_wmi, mock_subprocess):
        """测试并发操作性能"""
        # 模拟网络接口
        mock_wmi.return_value = [
            {
                'Name': f'Ethernet {i}',
                'Description': f'Network Adapter {i}',
                'DeviceID': f'DEVICE_{i:03d}',
                'MACAddress': f'00:11:22:33:44:{i:02x}',
                'NetConnectionStatus': 2,
                'ConfigManagerErrorCode': 0
            }
            for i in range(10)
        ]
        
        # 模拟快速命令响应
        mock_subprocess.return_value = Mock(
            returncode=0,
            stdout="操作成功",
            stderr=""
        )
        
        def get_interface_info(interface_name):
            """获取接口信息的任务函数"""
            return get_interface_config(interface_name)
        
        # 并发性能测试
        interface_names = [f'Ethernet {i}' for i in range(10)]
        
        # 顺序执行基准测试
        start_time = time.time()
        sequential_results = []
        for name in interface_names:
            result = get_interface_info(name)
            sequential_results.append(result)
        sequential_time = time.time() - start_time
        
        # 并发执行测试
        start_time = time.time()
        concurrent_results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(get_interface_info, name) for name in interface_names]
            for future in as_completed(futures):
                result = future.result()
                concurrent_results.append(result)
        concurrent_time = time.time() - start_time
        
        # 性能断言
        assert len(sequential_results) == 10
        assert len(concurrent_results) == 10
        assert concurrent_time < sequential_time, "并发执行应该更快"
        
        speedup = sequential_time / concurrent_time
        assert speedup > 1.5, f"并发加速比不足: {speedup:.2f}x"
        
        print(f"并发性能: 顺序 {sequential_time:.3f}s, 并发 {concurrent_time:.3f}s, 加速比 {speedup:.2f}x")


@pytest.mark.performance
@pytest.mark.slow
class TestNetworkConfigStress:
    """网络配置压力测试"""
    
    @patch('subprocess.run')
    @patch('netkit.services.netconfig.wmi_engine.get_network_adapters')
    def test_rapid_configuration_changes(self, mock_wmi, mock_subprocess):
        """测试快速配置更改压力"""
        # 模拟网络接口
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
        
        # 模拟命令响应
        mock_subprocess.return_value = Mock(
            returncode=0,
            stdout="配置成功",
            stderr=""
        )
        
        # 快速配置更改测试
        configs = [
            {
                'ip': f'192.168.1.{100 + i}',
                'mask': '255.255.255.0',
                'gateway': '192.168.1.1',
                'dns1': '8.8.8.8',
                'dns2': '8.8.4.4'
            }
            for i in range(50)
        ]
        
        start_time = time.time()
        success_count = 0
        
        for config in configs:
            try:
                success = apply_profile('Test Ethernet', config)
                if success:
                    success_count += 1
            except Exception as e:
                print(f"配置失败: {e}")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 压力测试断言
        assert success_count >= 45, f"成功率过低: {success_count}/50"
        assert total_time < 60, f"总时间过长: {total_time:.3f}s"
        
        avg_time_per_config = total_time / len(configs)
        assert avg_time_per_config < 2.0, f"平均配置时间过长: {avg_time_per_config:.3f}s"
        
        print(f"压力测试: {success_count}/50 成功, 总时间 {total_time:.3f}s, 平均 {avg_time_per_config:.3f}s/配置")
    
    @patch('netkit.services.netconfig.wmi_engine.get_network_adapters')
    def test_memory_usage_stress(self, mock_wmi):
        """测试内存使用压力"""
        import psutil
        import os
        
        # 模拟大量网络接口
        mock_wmi.return_value = [
            {
                'Name': f'Ethernet {i}',
                'Description': f'Network Adapter {i}',
                'DeviceID': f'DEVICE_{i:06d}',
                'MACAddress': f'{(i % 256):02x}:11:22:33:44:55',
                'NetConnectionStatus': 2,
                'ConfigManagerErrorCode': 0
            }
            for i in range(1000)  # 1000个网络接口
        ]
        
        # 获取初始内存使用
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 执行大量接口发现操作
        for _ in range(10):
            interfaces = get_network_interfaces()
            assert len(interfaces) == 1000
        
        # 检查内存使用
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # 内存使用断言
        assert memory_increase < 100, f"内存增长过多: {memory_increase:.2f}MB"
        
        print(f"内存使用: 初始 {initial_memory:.2f}MB, 最终 {final_memory:.2f}MB, 增长 {memory_increase:.2f}MB")


@pytest.mark.performance
class TestNetworkConfigBenchmark:
    """网络配置基准测试"""
    
    def test_validation_benchmark(self, benchmark):
        """IP配置验证基准测试"""
        config = {
            'ip': '192.168.1.100',
            'mask': '255.255.255.0',
            'gateway': '192.168.1.1',
            'dns1': '8.8.8.8',
            'dns2': '8.8.4.4'
        }
        
        # 基准测试
        result = benchmark(validate_ip_config, config)
        
        # 验证结果
        is_valid, errors = result
        assert is_valid
        assert len(errors) == 0
    
    @patch('netkit.services.netconfig.wmi_engine.get_network_adapters')
    def test_interface_discovery_benchmark(self, mock_wmi, benchmark):
        """网络接口发现基准测试"""
        # 模拟标准数量的网络接口
        mock_wmi.return_value = [
            {
                'Name': f'Ethernet {i}',
                'Description': f'Network Adapter {i}',
                'DeviceID': f'DEVICE_{i:03d}',
                'MACAddress': f'00:11:22:33:44:{i:02x}',
                'NetConnectionStatus': 2,
                'ConfigManagerErrorCode': 0
            }
            for i in range(5)  # 5个网络接口
        ]
        
        # 基准测试
        result = benchmark(get_network_interfaces)
        
        # 验证结果
        assert len(result) == 5
        for interface in result:
            assert 'name' in interface
            assert 'status' in interface


if __name__ == "__main__":
    # 运行性能测试
    pytest.main([__file__, "-v", "-m", "performance", "--benchmark-only"])