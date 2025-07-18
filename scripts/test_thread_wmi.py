#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试多线程WMI修复
验证ThreadLocalWMI在多线程环境下的工作情况
"""

import sys
import os
import threading
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from netkit.services.netconfig.interface_info import get_network_card_info, ThreadLocalWMI
from netkit.services.netconfig.interface_manager import get_network_interfaces


def test_single_thread():
    """测试单线程WMI"""
    print("=== 单线程测试 ===")
    try:
        interfaces = get_network_interfaces(show_all=False)
        print(f"✓ 单线程获取网卡成功: {len(interfaces)} 个")
        
        if interfaces:
            info = get_network_card_info(interfaces[0])
            print(f"✓ 单线程获取网卡信息成功: {info['description']}")
        
        return True
    except Exception as e:
        print(f"✗ 单线程测试失败: {e}")
        return False


def test_multi_thread():
    """测试多线程WMI"""
    print("\n=== 多线程测试 ===")
    
    results = []
    errors = []
    
    def worker_thread(thread_id):
        """工作线程"""
        try:
            print(f"线程 {thread_id} 开始...")
            
            # 获取网卡列表
            interfaces = get_network_interfaces(show_all=False)
            print(f"线程 {thread_id} 获取到 {len(interfaces)} 个网卡")
            
            if interfaces:
                # 获取第一个网卡的详细信息
                info = get_network_card_info(interfaces[0])
                print(f"线程 {thread_id} 获取网卡信息: {info['description']}")
                results.append(f"线程 {thread_id} 成功")
            else:
                results.append(f"线程 {thread_id} 无网卡")
                
        except Exception as e:
            error_msg = f"线程 {thread_id} 失败: {e}"
            print(error_msg)
            errors.append(error_msg)
        finally:
            # 清理线程本地的WMI连接
            ThreadLocalWMI.cleanup()
    
    # 创建5个工作线程
    threads = []
    for i in range(5):
        thread = threading.Thread(target=worker_thread, args=(i,))
        threads.append(thread)
    
    # 启动所有线程
    for thread in threads:
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    # 分析结果
    print(f"\n多线程测试结果:")
    print(f"成功: {len(results)} 个线程")
    print(f"失败: {len(errors)} 个线程")
    
    if errors:
        print("错误详情:")
        for error in errors:
            print(f"  - {error}")
    
    return len(errors) == 0


def test_concurrent_access():
    """测试并发访问"""
    print("\n=== 并发访问测试 ===")
    
    def concurrent_worker(thread_id, barrier):
        """并发工作线程"""
        try:
            # 等待所有线程准备就绪
            barrier.wait()
            
            # 同时访问WMI
            interfaces = get_network_interfaces(show_all=False)
            if interfaces:
                info = get_network_card_info(interfaces[0])
                print(f"并发线程 {thread_id} 成功: {info['name']}")
                return True
            else:
                print(f"并发线程 {thread_id} 无网卡")
                return False
                
        except Exception as e:
            print(f"并发线程 {thread_id} 失败: {e}")
            return False
        finally:
            ThreadLocalWMI.cleanup()
    
    # 创建屏障，确保所有线程同时开始
    barrier = threading.Barrier(3)
    threads = []
    results = []
    
    def thread_wrapper(thread_id):
        result = concurrent_worker(thread_id, barrier)
        results.append(result)
    
    # 创建3个并发线程
    for i in range(3):
        thread = threading.Thread(target=thread_wrapper, args=(i,))
        threads.append(thread)
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    success_count = sum(results)
    print(f"并发测试结果: {success_count}/3 成功")
    
    return success_count == 3


def main():
    """主测试函数"""
    print("NetKit 多线程WMI修复测试")
    print("=" * 50)
    
    tests = [
        ("单线程WMI", test_single_thread),
        ("多线程WMI", test_multi_thread),
        ("并发访问WMI", test_concurrent_access)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} 测试通过")
            else:
                print(f"✗ {test_name} 测试失败")
        except Exception as e:
            print(f"✗ {test_name} 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！多线程WMI修复成功。")
        return 0
    else:
        print("⚠️  部分测试失败，多线程WMI可能仍有问题。")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 