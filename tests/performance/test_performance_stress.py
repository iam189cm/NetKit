#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网卡配置性能和压力测试
测试系统在高负载和极限条件下的表现
"""

import pytest
import time
import threading
import psutil
import gc
import unittest.mock as mock
import tkinter as tk
import ttkbootstrap as tb
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import patch, MagicMock
import os

# 设置测试环境
os.environ['NETKIT_TEST_MODE'] = '1'

# 导入测试目标
from gui.views.ip_switcher_view import IPSwitcherFrame
from netkit.services.ip_switcher import (
    get_network_interfaces,
    get_network_card_info,
    apply_profile,
    validate_ip_config,
    save_profile,
    load_profiles
)

# 导入测试数据
from tests.test_data import (
    VALID_IP_CONFIGS,
    MOCK_NETWORK_INTERFACES,
    MOCK_NETWORK_CARD_INFO,
    MOCK_NETSH_INTERFACE_OUTPUT,
    MOCK_NETSH_IP_CONFIG_OUTPUT,
    MOCK_GETMAC_OUTPUT,
    PERFORMANCE_TEST_DATA,
    STRESS_TEST_DATA
)


@pytest.mark.performance
class TestServicePerformance:
    """服务层性能测试"""
    
    @pytest.mark.benchmark
    def test_get_network_interfaces_performance(self, benchmark):
        """测试获取网络接口性能"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = MOCK_NETSH_INTERFACE_OUTPUT
            
            result = benchmark(get_network_interfaces)
            assert isinstance(result, list)
            assert len(result) > 0
    
    @pytest.mark.benchmark
    def test_get_network_card_info_performance(self, benchmark):
        """测试获取网卡信息性能"""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = [
                mock.Mock(returncode=0, stdout="管理状态: 已启用\n类型: 专用"),
                mock.Mock(returncode=0, stdout=MOCK_GETMAC_OUTPUT),
                mock.Mock(returncode=0, stdout=MOCK_NETSH_IP_CONFIG_OUTPUT)
            ]
            
            result = benchmark(get_network_card_info, "以太网")
            assert result['name'] == "以太网"
    
    @pytest.mark.benchmark
    @pytest.mark.parametrize("config", VALID_IP_CONFIGS)
    def test_validate_ip_config_performance(self, benchmark, config):
        """测试IP配置验证性能"""
        def validate_config():
            return validate_ip_config(
                config['ip'],
                config['mask'],
                config['gateway'],
                config['dns']
            )
        
        result = benchmark(validate_config)
        assert result['valid'] is True
    
    @pytest.mark.benchmark
    def test_apply_profile_performance(self, benchmark):
        """测试应用配置性能"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = ""
            
            def apply_config():
                return apply_profile(
                    "以太网",
                    "192.168.1.100",
                    "255.255.255.0",
                    "192.168.1.1",
                    "8.8.8.8",
                    dhcp=False
                )
            
            result = benchmark(apply_config)
            assert result['success'] is True
    
    @pytest.mark.benchmark
    @pytest.mark.parametrize("iterations", PERFORMANCE_TEST_DATA["ip_validation_iterations"])
    def test_batch_ip_validation_performance(self, benchmark, iterations):
        """测试批量IP验证性能"""
        configs = VALID_IP_CONFIGS * (iterations // len(VALID_IP_CONFIGS) + 1)
        configs = configs[:iterations]
        
        def batch_validate():
            results = []
            for config in configs:
                result = validate_ip_config(
                    config['ip'],
                    config['mask'],
                    config['gateway'],
                    config['dns']
                )
                results.append(result)
            return results
        
        results = benchmark(batch_validate)
        assert len(results) == iterations
        assert all(result['valid'] for result in results)


@pytest.mark.performance
class TestGUIPerformance:
    """GUI性能测试"""
    
    @pytest.fixture
    def root_window(self):
        root = tb.Window(themename='darkly')
        root.withdraw()
        yield root
        root.destroy()
    
    @pytest.fixture
    def ip_switcher_frame(self, root_window):
        frame = IPSwitcherFrame(root_window)
        return frame
    
    @pytest.mark.benchmark
    def test_frame_initialization_performance(self, benchmark, root_window):
        """测试界面初始化性能"""
        def create_frame():
            frame = IPSwitcherFrame(root_window)
            return frame
        
        frame = benchmark(create_frame)
        assert frame is not None
    
    @pytest.mark.benchmark
    def test_interface_refresh_performance(self, benchmark, ip_switcher_frame):
        """测试接口刷新性能"""
        with patch('netkit.services.ip_switcher.get_network_interfaces') as mock_get_interfaces:
            mock_get_interfaces.return_value = MOCK_NETWORK_INTERFACES
            
            def refresh_interfaces():
                ip_switcher_frame.refresh_interfaces()
                return ip_switcher_frame.interface_combo['values']
            
            result = benchmark(refresh_interfaces)
            assert len(result) > 0
    
    @pytest.mark.benchmark
    def test_interface_selection_performance(self, benchmark, ip_switcher_frame):
        """测试接口选择性能"""
        with patch('netkit.services.ip_switcher.get_network_card_info') as mock_get_info:
            mock_get_info.return_value = MOCK_NETWORK_CARD_INFO["以太网"]
            
            def select_interface():
                ip_switcher_frame.interface_var.set("以太网")
                ip_switcher_frame.on_interface_selected()
            
            benchmark(select_interface)
    
    @pytest.mark.benchmark
    @pytest.mark.parametrize("interface_count", [10, 50, 100])
    def test_large_interface_list_performance(self, benchmark, ip_switcher_frame, interface_count):
        """测试大量接口列表性能"""
        large_interface_list = [f"接口_{i}" for i in range(interface_count)]
        
        with patch('netkit.services.ip_switcher.get_network_interfaces') as mock_get_interfaces:
            mock_get_interfaces.return_value = large_interface_list
            
            def refresh_large_list():
                ip_switcher_frame.refresh_interfaces()
                return len(ip_switcher_frame.interface_combo['values'])
            
            result = benchmark(refresh_large_list)
            assert result == interface_count


@pytest.mark.stress
class TestStressTest:
    """压力测试"""
    
    @pytest.fixture
    def root_window(self):
        root = tb.Window(themename='darkly')
        root.withdraw()
        yield root
        root.destroy()
    
    @pytest.fixture
    def ip_switcher_frame(self, root_window):
        frame = IPSwitcherFrame(root_window)
        return frame
    
    @pytest.mark.parametrize("operation_count", STRESS_TEST_DATA["operation_counts"])
    def test_repeated_interface_refresh_stress(self, ip_switcher_frame, operation_count):
        """测试重复刷新接口的压力"""
        with patch('netkit.services.ip_switcher.get_network_interfaces') as mock_get_interfaces:
            mock_get_interfaces.return_value = MOCK_NETWORK_INTERFACES
            
            success_count = 0
            errors = []
            
            for i in range(operation_count):
                try:
                    ip_switcher_frame.refresh_interfaces()
                    success_count += 1
                except Exception as e:
                    errors.append(f"Operation {i}: {str(e)}")
            
            success_rate = success_count / operation_count
            assert success_rate >= 0.95, f"Success rate: {success_rate:.2%}, Errors: {errors[:5]}"
    
    @pytest.mark.parametrize("concurrent_count", STRESS_TEST_DATA["concurrent_users"])
    def test_concurrent_operations_stress(self, ip_switcher_frame, concurrent_count):
        """测试并发操作压力"""
        with patch('netkit.services.ip_switcher.get_network_interfaces') as mock_get_interfaces:
            mock_get_interfaces.return_value = MOCK_NETWORK_INTERFACES
            
            def operation():
                try:
                    ip_switcher_frame.refresh_interfaces()
                    ip_switcher_frame.interface_var.set("以太网")
                    ip_switcher_frame.dhcp_var.set(True)
                    ip_switcher_frame.on_dhcp_changed()
                    return True
                except Exception as e:
                    return False
            
            with ThreadPoolExecutor(max_workers=concurrent_count) as executor:
                futures = [executor.submit(operation) for _ in range(concurrent_count)]
                results = [future.result() for future in as_completed(futures)]
            
            success_count = sum(results)
            success_rate = success_count / concurrent_count
            assert success_rate >= 0.90, f"Concurrent success rate: {success_rate:.2%}"
    
    @pytest.mark.slow
    def test_memory_leak_stress(self, ip_switcher_frame):
        """测试内存泄漏压力"""
        import gc
        
        with patch('netkit.services.ip_switcher.get_network_interfaces') as mock_get_interfaces:
            mock_get_interfaces.return_value = MOCK_NETWORK_INTERFACES
            
            # 获取初始内存使用
            gc.collect()
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # 执行大量操作
            for i in range(1000):
                ip_switcher_frame.refresh_interfaces()
                ip_switcher_frame.interface_var.set("以太网")
                ip_switcher_frame.dhcp_var.set(i % 2 == 0)
                ip_switcher_frame.on_dhcp_changed()
                
                # 定期清理
                if i % 100 == 0:
                    gc.collect()
            
            # 最终内存检查
            gc.collect()
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            # 验证内存增长在合理范围内
            assert memory_increase < 100, f"Memory leak detected: {memory_increase:.2f} MB increase"
    
    @pytest.mark.parametrize("timeout", STRESS_TEST_DATA["timeout_scenarios"])
    def test_timeout_stress(self, ip_switcher_frame, timeout):
        """测试超时压力"""
        with patch('netkit.services.ip_switcher.get_network_interfaces') as mock_get_interfaces:
            def slow_operation():
                time.sleep(timeout)
                return MOCK_NETWORK_INTERFACES
            
            mock_get_interfaces.side_effect = slow_operation
            
            start_time = time.time()
            try:
                ip_switcher_frame.refresh_interfaces()
                success = True
            except Exception:
                success = False
            end_time = time.time()
            
            actual_time = end_time - start_time
            
            # 验证操作时间
            assert actual_time >= timeout - 0.1, f"Operation too fast: {actual_time:.2f}s"
            
            # 对于合理的超时时间，操作应该成功
            if timeout <= 10:
                assert success, f"Operation failed with {timeout}s timeout"
    
    @pytest.mark.slow
    def test_gui_responsiveness_stress(self, ip_switcher_frame):
        """测试GUI响应性压力"""
        with patch('netkit.services.ip_switcher.get_network_interfaces') as mock_get_interfaces:
            # 模拟变化的响应时间
            def variable_delay():
                import random
                time.sleep(random.uniform(0.01, 0.1))
                return MOCK_NETWORK_INTERFACES
            
            mock_get_interfaces.side_effect = variable_delay
            
            response_times = []
            
            for i in range(50):
                start_time = time.time()
                ip_switcher_frame.refresh_interfaces()
                end_time = time.time()
                response_times.append(end_time - start_time)
            
            # 验证响应时间统计
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            
            assert avg_response_time < 0.5, f"Average response time too high: {avg_response_time:.3f}s"
            assert max_response_time < 1.0, f"Max response time too high: {max_response_time:.3f}s"


@pytest.mark.load
class TestLoadTest:
    """负载测试"""
    
    @pytest.fixture
    def root_window(self):
        root = tb.Window(themename='darkly')
        root.withdraw()
        yield root
        root.destroy()
    
    @pytest.fixture
    def ip_switcher_frame(self, root_window):
        frame = IPSwitcherFrame(root_window)
        return frame
    
    def test_sustained_load(self, ip_switcher_frame):
        """测试持续负载"""
        with patch('netkit.services.ip_switcher.get_network_interfaces') as mock_get_interfaces:
            mock_get_interfaces.return_value = MOCK_NETWORK_INTERFACES
            
            # 持续运行5分钟的负载测试
            end_time = time.time() + 300  # 5分钟
            operation_count = 0
            errors = []
            
            while time.time() < end_time:
                try:
                    ip_switcher_frame.refresh_interfaces()
                    ip_switcher_frame.interface_var.set("以太网")
                    ip_switcher_frame.dhcp_var.set(operation_count % 2 == 0)
                    ip_switcher_frame.on_dhcp_changed()
                    operation_count += 1
                    
                    # 短暂休息
                    time.sleep(0.1)
                    
                except Exception as e:
                    errors.append(str(e))
            
            # 验证负载测试结果
            error_rate = len(errors) / operation_count if operation_count > 0 else 1
            assert error_rate < 0.01, f"Error rate too high: {error_rate:.2%}"
            assert operation_count > 1000, f"Operation count too low: {operation_count}"
    
    def test_peak_load(self, ip_switcher_frame):
        """测试峰值负载"""
        with patch('netkit.services.ip_switcher.get_network_interfaces') as mock_get_interfaces:
            mock_get_interfaces.return_value = MOCK_NETWORK_INTERFACES
            
            # 模拟峰值负载：短时间内大量操作
            operations_per_second = 100
            duration = 10  # 10秒
            
            def worker():
                operations = 0
                errors = 0
                start_time = time.time()
                
                while time.time() - start_time < duration:
                    try:
                        ip_switcher_frame.refresh_interfaces()
                        operations += 1
                        time.sleep(1.0 / operations_per_second)
                    except Exception:
                        errors += 1
                
                return operations, errors
            
            # 启动多个工作线程
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(worker) for _ in range(5)]
                results = [future.result() for future in as_completed(futures)]
            
            total_operations = sum(ops for ops, _ in results)
            total_errors = sum(errors for _, errors in results)
            
            error_rate = total_errors / total_operations if total_operations > 0 else 1
            assert error_rate < 0.05, f"Peak load error rate too high: {error_rate:.2%}"
    
    @pytest.mark.parametrize("memory_limit", STRESS_TEST_DATA["memory_limits"])
    def test_memory_constrained_load(self, ip_switcher_frame, memory_limit):
        """测试内存受限负载"""
        with patch('netkit.services.ip_switcher.get_network_interfaces') as mock_get_interfaces:
            mock_get_interfaces.return_value = MOCK_NETWORK_INTERFACES
            
            process = psutil.Process()
            operation_count = 0
            
            # 在内存限制下运行操作
            while True:
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                
                if current_memory > memory_limit:
                    break
                
                try:
                    ip_switcher_frame.refresh_interfaces()
                    ip_switcher_frame.interface_var.set("以太网")
                    operation_count += 1
                    
                    # 定期清理
                    if operation_count % 10 == 0:
                        gc.collect()
                        
                except Exception:
                    break
            
            # 验证在内存限制下仍能执行一定数量的操作
            assert operation_count > 50, f"Too few operations under memory limit: {operation_count}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"]) 