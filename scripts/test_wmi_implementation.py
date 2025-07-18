#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试WMI实现脚本
用于验证新的WMI网卡信息获取功能
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from netkit.services.netconfig.interface_info import get_network_card_info, NetworkAdapterWMI
from netkit.services.netconfig.interface_manager import get_network_interfaces, get_network_interfaces_with_details


def test_wmi_connection():
    """测试WMI连接"""
    print("=== 测试WMI连接 ===")
    try:
        wmi_adapter = NetworkAdapterWMI()
        adapters = wmi_adapter.get_all_adapters()
        print(f"✓ WMI连接成功，找到 {len(adapters)} 个网络适配器")
        return True
    except Exception as e:
        print(f"✗ WMI连接失败: {e}")
        return False


def test_network_interfaces():
    """测试网络接口列表获取"""
    print("\n=== 测试网络接口列表 ===")
    try:
        # 测试物理网卡
        physical_interfaces = get_network_interfaces(show_all=False)
        print(f"✓ 物理网卡数量: {len(physical_interfaces)}")
        for interface in physical_interfaces:
            print(f"  - {interface}")
        
        # 测试所有网卡
        all_interfaces = get_network_interfaces(show_all=True)
        print(f"✓ 所有网卡数量: {len(all_interfaces)}")
        
        return True
    except Exception as e:
        print(f"✗ 获取网络接口失败: {e}")
        return False


def test_interface_details():
    """测试网卡详细信息获取"""
    print("\n=== 测试网卡详细信息 ===")
    try:
        interfaces = get_network_interfaces(show_all=False)
        if not interfaces:
            print("✗ 没有找到可用的网卡")
            return False
        
        # 测试第一个网卡的详细信息
        test_interface = interfaces[0]
        print(f"测试网卡: {test_interface}")
        
        info = get_network_card_info(test_interface)
        print("网卡详细信息:")
        for key, value in info.items():
            print(f"  {key}: {value}")
        
        # 检查关键信息是否获取成功
        success_count = 0
        total_count = len(info)
        for key, value in info.items():
            if value not in ['未知', '获取失败', '未配置']:
                success_count += 1
        
        success_rate = (success_count / total_count) * 100
        print(f"✓ 信息获取成功率: {success_rate:.1f}% ({success_count}/{total_count})")
        
        return success_rate > 50  # 成功率超过50%认为测试通过
        
    except Exception as e:
        print(f"✗ 获取网卡详细信息失败: {e}")
        return False


def test_interface_display_names():
    """测试网卡显示名称格式化"""
    print("\n=== 测试网卡显示名称 ===")
    try:
        detailed_interfaces = get_network_interfaces_with_details(show_all=False)
        print(f"✓ 带详细信息的网卡数量: {len(detailed_interfaces)}")
        
        for display_name, original_name in detailed_interfaces:
            print(f"  显示名称: {display_name}")
            print(f"  原始名称: {original_name}")
            print()
        
        return True
    except Exception as e:
        print(f"✗ 获取网卡显示名称失败: {e}")
        return False


def main():
    """主测试函数"""
    print("NetKit WMI实现测试")
    print("=" * 50)
    
    tests = [
        ("WMI连接", test_wmi_connection),
        ("网络接口列表", test_network_interfaces),
        ("网卡详细信息", test_interface_details),
        ("网卡显示名称", test_interface_display_names)
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
        print("🎉 所有测试通过！WMI实现工作正常。")
        return 0
    else:
        print("⚠️  部分测试失败，请检查WMI实现。")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 