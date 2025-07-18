#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NetKit 性能基准测试脚本
用于测试和对比优化前后的性能表现
"""

import sys
import os
import time
import threading
import traceback
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置测试模式
os.environ['NETKIT_TEST_MODE'] = '1'

class PerformanceBenchmark:
    """性能基准测试类"""
    
    def __init__(self):
        self.results = {}
        self.test_start_time = None
        
    def run_all_tests(self):
        """运行所有性能测试"""
        print("=" * 60)
        print("NetKit 性能基准测试")
        print("=" * 60)
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        self.test_start_time = time.time()
        
        # 测试项目
        tests = [
            ("模块导入性能", self.test_import_performance),
            ("WMI连接性能", self.test_wmi_connection),
            ("网卡列表获取性能", self.test_get_interfaces),
            ("单个网卡信息获取性能", self.test_get_single_card_info),
            ("网卡信息批量获取性能", self.test_get_multiple_cards_info),
            ("界面创建性能", self.test_ui_creation),
            ("网卡刷新性能", self.test_interface_refresh),
            ("多线程WMI性能", self.test_multithreaded_wmi)
        ]
        
        for test_name, test_func in tests:
            print(f"正在测试: {test_name}")
            try:
                result = test_func()
                self.results[test_name] = result
                print(f"✓ {test_name}: {result:.3f}秒")
            except Exception as e:
                error_msg = f"测试失败: {str(e)}"
                self.results[test_name] = error_msg
                print(f"✗ {test_name}: {error_msg}")
                # 打印详细错误信息用于调试
                traceback.print_exc()
            print()
        
        self.print_summary()
    
    def test_import_performance(self):
        """测试模块导入性能"""
        start_time = time.time()
        
        try:
            from netkit.services.netconfig import get_network_interfaces
            from netkit.services.netconfig import get_network_card_info
            from netkit.services.netconfig import get_network_interfaces_with_details
        except ImportError as e:
            print(f"导入失败: {e}")
            return -1
        
        return time.time() - start_time
    
    def test_wmi_connection(self):
        """测试WMI连接性能"""
        start_time = time.time()
        
        try:
            from netkit.services.netconfig.interface_info import NetworkAdapterWMI
            wmi_adapter = NetworkAdapterWMI()
            # 执行一个简单的WMI查询
            adapters = wmi_adapter.get_all_adapters()
            return time.time() - start_time
        except Exception as e:
            print(f"WMI连接失败: {e}")
            return -1
    
    def test_get_interfaces(self):
        """测试获取网卡列表性能"""
        start_time = time.time()
        
        try:
            from netkit.services.netconfig import get_network_interfaces
            interfaces = get_network_interfaces()
            print(f"    找到 {len(interfaces)} 个网卡")
            return time.time() - start_time
        except Exception as e:
            print(f"获取网卡列表失败: {e}")
            return -1
    
    def test_get_single_card_info(self):
        """测试获取单个网卡信息性能"""
        try:
            from netkit.services.netconfig import get_network_interfaces, get_network_card_info
            interfaces = get_network_interfaces()
            
            if not interfaces:
                print("    没有可用网卡")
                return -1
            
            interface_name = interfaces[0]
            print(f"    测试网卡: {interface_name}")
            
            start_time = time.time()
            info = get_network_card_info(interface_name)
            end_time = time.time()
            
            # 检查信息完整性
            unknown_count = sum(1 for v in info.values() if v in ['未知', '获取失败'])
            total_fields = len(info)
            accuracy = (total_fields - unknown_count) / total_fields * 100
            print(f"    信息准确性: {accuracy:.1f}% ({total_fields-unknown_count}/{total_fields})")
            
            return end_time - start_time
            
        except Exception as e:
            print(f"获取网卡信息失败: {e}")
            return -1
    
    def test_get_multiple_cards_info(self):
        """测试获取多个网卡信息性能"""
        try:
            from netkit.services.netconfig import get_network_interfaces, get_network_card_info
            interfaces = get_network_interfaces()
            
            if not interfaces:
                print("    没有可用网卡")
                return -1
            
            # 最多测试5个网卡
            test_interfaces = interfaces[:5]
            print(f"    测试 {len(test_interfaces)} 个网卡")
            
            start_time = time.time()
            for interface in test_interfaces:
                info = get_network_card_info(interface)
            end_time = time.time()
            
            avg_time = (end_time - start_time) / len(test_interfaces)
            print(f"    平均每个网卡: {avg_time:.3f}秒")
            
            return end_time - start_time
            
        except Exception as e:
            print(f"批量获取网卡信息失败: {e}")
            return -1
    
    def test_ui_creation(self):
        """测试界面创建性能"""
        start_time = time.time()
        
        try:
            import ttkbootstrap as tb
            from gui.views.netconfig.netconfig_view import NetConfigView
            
            # 创建测试窗口
            root = tb.Window(themename='darkly')
            root.withdraw()  # 隐藏窗口
            
            # 创建网络配置视图
            netconfig_view = NetConfigView(root)
            
            end_time = time.time()
            
            # 清理
            root.destroy()
            
            return end_time - start_time
            
        except Exception as e:
            print(f"界面创建失败: {e}")
            return -1
    
    def test_interface_refresh(self):
        """测试网卡刷新性能"""
        try:
            from netkit.services.netconfig import get_network_interfaces_with_details
            
            start_time = time.time()
            interfaces_with_details = get_network_interfaces_with_details()
            end_time = time.time()
            
            print(f"    获取 {len(interfaces_with_details)} 个详细网卡信息")
            
            return end_time - start_time
            
        except Exception as e:
            print(f"网卡刷新失败: {e}")
            return -1
    
    def test_multithreaded_wmi(self):
        """测试多线程WMI性能"""
        try:
            from netkit.services.netconfig.interface_info import NetworkAdapterWMI
            
            results = []
            errors = []
            
            def worker(thread_id):
                try:
                    start_time = time.time()
                    wmi_adapter = NetworkAdapterWMI()
                    adapters = wmi_adapter.get_all_adapters()
                    end_time = time.time()
                    results.append((thread_id, end_time - start_time))
                except Exception as e:
                    errors.append((thread_id, str(e)))
            
            # 创建3个线程同时访问WMI
            threads = []
            start_time = time.time()
            
            for i in range(3):
                thread = threading.Thread(target=worker, args=(i,))
                threads.append(thread)
                thread.start()
            
            # 等待所有线程完成
            for thread in threads:
                thread.join()
            
            end_time = time.time()
            
            print(f"    成功线程: {len(results)}/3")
            print(f"    失败线程: {len(errors)}/3")
            if errors:
                for thread_id, error in errors:
                    print(f"    线程{thread_id}错误: {error}")
            
            return end_time - start_time
            
        except Exception as e:
            print(f"多线程WMI测试失败: {e}")
            return -1
    
    def print_summary(self):
        """打印测试总结"""
        print("=" * 60)
        print("测试总结")
        print("=" * 60)
        
        total_time = time.time() - self.test_start_time
        print(f"总测试时间: {total_time:.3f}秒")
        print()
        
        # 按性能分类
        fast_tests = []
        slow_tests = []
        failed_tests = []
        
        for test_name, result in self.results.items():
            if isinstance(result, str):  # 错误信息
                failed_tests.append((test_name, result))
            elif result < 0:  # 失败
                failed_tests.append((test_name, "测试失败"))
            elif result < 1.0:  # 快速
                fast_tests.append((test_name, result))
            else:  # 慢速
                slow_tests.append((test_name, result))
        
        if fast_tests:
            print("✓ 快速测试 (< 1秒):")
            for test_name, result in fast_tests:
                print(f"  {test_name}: {result:.3f}秒")
            print()
        
        if slow_tests:
            print("⚠ 慢速测试 (≥ 1秒):")
            for test_name, result in slow_tests:
                print(f"  {test_name}: {result:.3f}秒")
            print()
        
        if failed_tests:
            print("✗ 失败测试:")
            for test_name, result in failed_tests:
                print(f"  {test_name}: {result}")
            print()
        
        # 性能评估
        print("性能评估:")
        if len(slow_tests) == 0:
            print("  整体性能: 优秀")
        elif len(slow_tests) <= 2:
            print("  整体性能: 良好")
        elif len(slow_tests) <= 4:
            print("  整体性能: 一般")
        else:
            print("  整体性能: 需要优化")
        
        if failed_tests:
            print(f"  失败率: {len(failed_tests)}/{len(self.results)} ({len(failed_tests)/len(self.results)*100:.1f}%)")
        
        print()
        print("建议:")
        if slow_tests:
            print("- 以下测试项目需要优化:")
            for test_name, result in slow_tests:
                print(f"  · {test_name}")
        if failed_tests:
            print("- 以下测试项目需要修复:")
            for test_name, result in failed_tests:
                print(f"  · {test_name}")
        
        print()
        print("=" * 60)

def main():
    """主函数"""
    benchmark = PerformanceBenchmark()
    benchmark.run_all_tests()

if __name__ == "__main__":
    main() 