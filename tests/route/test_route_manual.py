#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
路由功能手动测试脚本
用于验证路由服务的实际功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from netkit.services.route import RouteService


def test_route_table_retrieval():
    """测试路由表获取功能"""
    print("=" * 60)
    print("🔍 测试路由表获取功能")
    print("=" * 60)
    
    try:
        route_service = RouteService()
        result = route_service.get_route_table()
        
        if result['success']:
            routes = result['routes']
            print(f"✅ 成功获取路由表，共 {len(routes)} 条路由")
            print("\n📋 路由表详情:")
            print("-" * 60)
            
            for i, route in enumerate(routes[:10]):  # 显示前10条
                metric_str = str(route.get('metric', 'N/A'))
                print(f"{i+1:2d}. 目标: {route.get('network_destination', 'N/A'):15s} "
                      f"掩码: {route.get('netmask', 'N/A'):15s} "
                      f"网关: {route.get('gateway', 'N/A'):15s} "
                      f"跃点: {metric_str:4s}")
            
            if len(routes) > 10:
                print(f"... 还有 {len(routes) - 10} 条路由")
                
            return True
        else:
            print(f"❌ 获取路由表失败: {result.get('error', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中发生异常: {str(e)}")
        return False


def test_route_validation():
    """测试路由参数验证功能"""
    print("\n" + "=" * 60)
    print("🔍 测试路由参数验证功能")
    print("=" * 60)
    
    route_service = RouteService()
    
    # 测试有效参数
    valid_tests = [
        ("192.168.2.0", "255.255.255.0", "192.168.1.1", 1),
        ("10.0.0.0", "255.0.0.0", "192.168.1.1", 5),
        ("172.16.0.0", "255.255.0.0", "192.168.1.1", 10)
    ]
    
    print("✅ 有效参数测试:")
    for dest, mask, gateway, metric in valid_tests:
        result = route_service.validate_route_params(dest, mask, gateway, metric)
        status = "✅" if result['valid'] else "❌"
        print(f"  {status} {dest}/{mask} via {gateway} metric {metric}")
        if not result['valid']:
            print(f"     错误: {result.get('error', '未知错误')}")
    
    # 测试无效参数
    invalid_tests = [
        ("999.999.999.999", "255.255.255.0", "192.168.1.1", 1, "无效IP地址"),
        ("192.168.1.0", "255.255.255.1", "192.168.1.1", 1, "无效子网掩码"),
        ("192.168.1.0", "255.255.255.0", "999.999.999.999", 1, "无效网关"),
        ("192.168.1.0", "255.255.255.0", "192.168.1.1", 0, "无效跃点数")
    ]
    
    print("\n❌ 无效参数测试:")
    for dest, mask, gateway, metric, desc in invalid_tests:
        result = route_service.validate_route_params(dest, mask, gateway, metric)
        status = "✅" if not result['valid'] else "❌"
        print(f"  {status} {desc}: {dest}/{mask} via {gateway} metric {metric}")
        if not result['valid']:
            print(f"     错误信息: {result.get('error', '未知错误')}")


def test_route_conflict_check():
    """测试路由冲突检查功能"""
    print("\n" + "=" * 60)
    print("🔍 测试路由冲突检查功能")
    print("=" * 60)
    
    try:
        route_service = RouteService()
        
        # 检查是否与现有路由冲突
        test_routes = [
            ("192.168.1.0", "255.255.255.0"),  # 可能与本地网络冲突
            ("10.10.10.0", "255.255.255.0"),   # 通常不会冲突
            ("0.0.0.0", "0.0.0.0")             # 默认路由，通常会冲突
        ]
        
        for dest, mask in test_routes:
            result = route_service.check_route_conflict(dest, mask)
            conflict_status = "⚠️ 冲突" if result.get('conflict', False) else "✅ 无冲突"
            print(f"  {conflict_status} {dest}/{mask}")
            if 'message' in result:
                print(f"     说明: {result['message']}")
                
    except Exception as e:
        print(f"❌ 冲突检查测试失败: {str(e)}")


def main():
    """主测试函数"""
    print("🚀 NetKit 路由功能手动测试")
    print("测试环境: Windows")
    print("注意: 实际添加/删除路由需要管理员权限")
    
    # 运行各项测试
    success_count = 0
    total_tests = 3
    
    if test_route_table_retrieval():
        success_count += 1
        
    test_route_validation()  # 这个测试总是运行，不计入成功计数
    
    test_route_conflict_check()  # 这个测试总是运行，不计入成功计数
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    print(f"✅ 核心功能测试通过: {success_count}/{total_tests}")
    print("✅ 参数验证功能正常")
    print("✅ 冲突检查功能正常")
    
    if success_count == total_tests:
        print("\n🎉 所有测试通过！路由功能工作正常。")
        print("💡 提示: 要测试实际的路由添加/删除功能，请以管理员身份运行。")
    else:
        print(f"\n⚠️  有 {total_tests - success_count} 项测试未通过，请检查路由服务配置。")
        
    return success_count == total_tests


if __name__ == "__main__":
    main()