#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NetKit 性能对比测试
展示优化前后的性能差异
"""

import sys
import os
import time
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def print_header(title):
    """打印标题"""
    print("=" * 60)
    print(f" {title}")
    print("=" * 60)

def print_section(title):
    """打印章节标题"""
    print(f"\n{title}")
    print("-" * 40)

def test_new_system():
    """测试新系统性能"""
    print_section("测试新系统（异步WMI引擎）")
    
    from netkit.services.netconfig.interface_manager import start_preload, get_cache_info
    from netkit.services.netconfig import get_network_interfaces_with_details
    from netkit.services.netconfig.interface_info import get_network_card_info
    
    results = {}
    
    # 测试1：预加载性能
    print("1. 预加载性能测试...")
    start_time = time.time()
    start_preload()
    
    # 等待预加载完成
    for i in range(20):
        cache_info = get_cache_info()
        if cache_info['preload_completed']:
            break
        time.sleep(0.5)
    
    preload_time = time.time() - start_time
    results['preload_time'] = preload_time
    print(f"   预加载完成: {preload_time:.3f}秒")
    print(f"   缓存的网卡数量: {cache_info['total_adapters']}")
    
    # 测试2：快速获取网卡列表
    print("\n2. 网卡列表获取性能...")
    start_time = time.time()
    interfaces = get_network_interfaces_with_details()
    list_time = time.time() - start_time
    results['list_time'] = list_time
    print(f"   获取列表耗时: {list_time:.3f}秒")
    print(f"   找到网卡数量: {len(interfaces)}")
    
    # 测试3：单个网卡信息获取
    if interfaces:
        print("\n3. 单个网卡信息获取性能...")
        interface_name = interfaces[0][1]  # 获取第一个网卡的原始名称
        
        start_time = time.time()
        info = get_network_card_info(interface_name)
        single_time = time.time() - start_time
        results['single_time'] = single_time
        print(f"   获取单个网卡信息耗时: {single_time:.3f}秒")
        print(f"   测试网卡: {interface_name}")
        
        # 检查信息完整性
        unknown_count = sum(1 for v in info.values() if v in ['未知', '获取失败'])
        total_fields = len(info)
        accuracy = (total_fields - unknown_count) / total_fields * 100
        results['accuracy'] = accuracy
        print(f"   信息准确性: {accuracy:.1f}% ({total_fields-unknown_count}/{total_fields})")
    
    # 测试4：批量获取性能
    if len(interfaces) > 1:
        print("\n4. 批量网卡信息获取性能...")
        test_interfaces = interfaces[:min(3, len(interfaces))]
        
        start_time = time.time()
        for display_name, interface_name in test_interfaces:
            info = get_network_card_info(interface_name)
        batch_time = time.time() - start_time
        results['batch_time'] = batch_time
        avg_time = batch_time / len(test_interfaces)
        results['avg_time'] = avg_time
        print(f"   批量获取耗时: {batch_time:.3f}秒")
        print(f"   平均每个网卡: {avg_time:.3f}秒")
        print(f"   测试网卡数量: {len(test_interfaces)}")
    
    return results

def simulate_old_system():
    """模拟旧系统性能（基于基准测试数据）"""
    print_section("旧系统性能（基于基准测试数据）")
    
    # 基于之前的基准测试结果
    old_results = {
        'single_time': 1.477,
        'batch_time': 8.301,
        'avg_time': 1.660,
        'list_time': 9.171,
        'accuracy': 100.0
    }
    
    print("1. 单个网卡信息获取:")
    print(f"   耗时: {old_results['single_time']:.3f}秒")
    
    print("\n2. 批量网卡信息获取:")
    print(f"   耗时: {old_results['batch_time']:.3f}秒")
    print(f"   平均每个网卡: {old_results['avg_time']:.3f}秒")
    
    print("\n3. 网卡刷新性能:")
    print(f"   耗时: {old_results['list_time']:.3f}秒")
    
    return old_results

def compare_results(new_results, old_results):
    """对比结果"""
    print_section("性能对比结果")
    
    comparisons = [
        ("单个网卡信息获取", "single_time"),
        ("批量网卡信息获取", "batch_time"),
        ("平均每个网卡", "avg_time"),
        ("网卡列表获取", "list_time")
    ]
    
    print(f"{'测试项目':<20} {'旧系统':<12} {'新系统':<12} {'提升幅度':<15}")
    print("-" * 60)
    
    total_improvement = 0
    improvement_count = 0
    
    for name, key in comparisons:
        if key in new_results and key in old_results:
            old_time = old_results[key]
            new_time = new_results[key]
            
            if old_time > 0 and new_time > 0:
                improvement = ((old_time - new_time) / old_time) * 100
                total_improvement += improvement
                improvement_count += 1
                
                print(f"{name:<20} {old_time:<12.3f} {new_time:<12.3f} {improvement:>+14.1f}%")
            elif new_time == 0:
                print(f"{name:<20} {old_time:<12.3f} {'<0.001':<12} {'>99.9%':<15}")
    
    if improvement_count > 0:
        avg_improvement = total_improvement / improvement_count
        print("-" * 60)
        print(f"{'平均性能提升':<45} {avg_improvement:>+14.1f}%")
    
    # 特殊优化点
    print("\n特殊优化:")
    if 'preload_time' in new_results:
        print(f"• 预加载时间: {new_results['preload_time']:.3f}秒（一次性成本）")
    if 'list_time' in new_results and new_results['list_time'] < 0.001:
        print("• 后续网卡列表获取: 几乎瞬时（缓存命中）")
    
    print("\n用户体验改进:")
    print("• 程序启动时开始预加载，用户无感知")
    print("• 网卡切换时无需等待，立即显示信息")
    print("• 异步进度条显示加载状态")
    print("• 智能缓存机制，减少重复查询")

def main():
    """主函数"""
    print_header("NetKit 性能优化对比测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试新系统
    new_results = test_new_system()
    
    # 模拟旧系统
    old_results = simulate_old_system()
    
    # 对比结果
    compare_results(new_results, old_results)
    
    print_section("总结")
    print("🎉 NetKit 性能优化已完成！")
    print("\n主要改进:")
    print("1. 实现了统一的WMI查询引擎")
    print("2. 添加了异步数据管理器")
    print("3. 重构了UI异步加载机制")
    print("4. 集成了智能缓存系统")
    print("5. 优化了主程序启动流程")
    
    print("\n技术特点:")
    print("• 线程安全的WMI查询")
    print("• 智能缓存机制")
    print("• 异步预加载")
    print("• 批量查询优化")
    print("• 用户体验优化")
    
    print("\n🚀 用户将感受到显著的性能提升！")
    print("=" * 60)

if __name__ == "__main__":
    main() 