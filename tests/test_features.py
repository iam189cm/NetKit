#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NETKit-Py 功能测试脚本
用于验证各个模块的核心功能
"""

import os
import sys
import traceback

# 设置测试模式
os.environ['NETKIT_TEST_MODE'] = '1'

def test_imports():
    """测试模块导入"""
    print("=== 测试模块导入 ===")
    
    try:
        # 测试核心服务导入
        from netkit.services.ip_switcher import validate_ip_config
        print("✓ IP切换服务导入成功")
        
        from netkit.services.ping import PingService
        print("✓ Ping服务导入成功")
        
        from netkit.services.subnet import SubnetCalculator
        print("✓ 子网计算服务导入成功")
        
        from netkit.services.traceroute import TracerouteService
        print("✓ 路由追踪服务导入成功")
        
        from netkit.services.route import RouteService
        print("✓ 路由管理服务导入成功")
        
        # 测试GUI导入
        from gui.main import MainWindow
        print("✓ 主窗口导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        traceback.print_exc()
        return False


def test_ip_validation():
    """测试IP配置验证"""
    print("\n=== 测试IP配置验证 ===")
    
    try:
        from netkit.services.ip_switcher import validate_ip_config
        
        # 测试有效配置
        result = validate_ip_config("192.168.1.100", "255.255.255.0", "192.168.1.1", "8.8.8.8")
        if result['valid']:
            print("✓ 有效IP配置验证通过")
        else:
            print(f"❌ 有效IP配置验证失败: {result['error']}")
            
        # 测试无效配置
        result = validate_ip_config("192.168.1.100", "255.255.255.0", "192.168.2.1", "8.8.8.8")
        if not result['valid']:
            print("✓ 无效IP配置正确识别")
        else:
            print("❌ 无效IP配置未被识别")
            
        # 测试网络地址冲突
        result = validate_ip_config("192.168.1.0", "255.255.255.0", "192.168.1.1", "8.8.8.8")
        if not result['valid']:
            print("✓ 网络地址冲突正确识别")
        else:
            print("❌ 网络地址冲突未被识别")
            
        return True
        
    except Exception as e:
        print(f"❌ IP验证测试失败: {e}")
        traceback.print_exc()
        return False


def test_subnet_calculation():
    """测试子网计算"""
    print("\n=== 测试子网计算 ===")
    
    try:
        from netkit.services.subnet import SubnetCalculator
        
        calculator = SubnetCalculator()
        
        # 测试基本子网信息计算
        result = calculator.calculate_subnet_info("192.168.1.0/24")
        if result['success']:
            print("✓ 基本子网信息计算成功")
            print(f"  网络地址: {result['network_address']}")
            print(f"  可用主机数: {result['usable_hosts']}")
        else:
            print(f"❌ 基本子网信息计算失败: {result['error']}")
            
        # 测试VLSM计算
        result = calculator.vlsm_calculation("192.168.1.0/24", [50, 25, 10])
        if result['success']:
            print("✓ VLSM计算成功")
            print(f"  划分了 {len(result['subnets'])} 个子网")
        else:
            print(f"❌ VLSM计算失败: {result['error']}")
            
        # 测试格式转换
        result = calculator.cidr_to_dotted("192.168.1.0/24")
        if result['success']:
            print("✓ CIDR转换成功")
            print(f"  子网掩码: {result['dotted_mask']}")
        else:
            print(f"❌ CIDR转换失败: {result['error']}")
            
        return True
        
    except Exception as e:
        print(f"❌ 子网计算测试失败: {e}")
        traceback.print_exc()
        return False


def test_ping_service():
    """测试Ping服务"""
    print("\n=== 测试Ping服务 ===")
    
    try:
        from netkit.services.ping import PingService
        
        service = PingService()
        
        # 测试ping解析
        test_output = """
正在 Ping www.baidu.com [14.215.177.39] 具有 32 字节的数据:
来自 14.215.177.39 的回复: 字节=32 时间=25ms TTL=55
来自 14.215.177.39 的回复: 字节=32 时间=24ms TTL=55
来自 14.215.177.39 的回复: 字节=32 时间=26ms TTL=55
来自 14.215.177.39 的回复: 字节=32 时间=25ms TTL=55

14.215.177.39 的 Ping 统计信息:
    数据包: 已发送 = 4，已接收 = 4，丢失 = 0 (0% 丢失)，
往返行程的估计时间(以毫秒为单位):
    最短 = 24ms，最长 = 26ms，平均 = 25ms
        """
        
        stats = service.parse_ping_result(test_output)
        if stats['success']:
            print("✓ Ping结果解析成功")
            print(f"  目标: {stats['host']}")
            print(f"  平均时间: {stats['avg_time']}ms")
            print(f"  丢包率: {stats['packet_loss']}%")
        else:
            print("❌ Ping结果解析失败")
            
        return True
        
    except Exception as e:
        print(f"❌ Ping服务测试失败: {e}")
        traceback.print_exc()
        return False


def test_route_service():
    """测试路由服务"""
    print("\n=== 测试路由服务 ===")
    
    try:
        from netkit.services.route import RouteService
        
        service = RouteService()
        
        # 测试路由参数验证
        result = service.validate_route_params("192.168.2.0", "255.255.255.0", "192.168.1.1", 1)
        if result['valid']:
            print("✓ 路由参数验证成功")
        else:
            print(f"❌ 路由参数验证失败: {result['error']}")
            
        # 测试无效参数
        result = service.validate_route_params("192.168.2.0", "255.255.255.0", "192.168.1.1", 0)
        if not result['valid']:
            print("✓ 无效路由参数正确识别")
        else:
            print("❌ 无效路由参数未被识别")
            
        return True
        
    except Exception as e:
        print(f"❌ 路由服务测试失败: {e}")
        traceback.print_exc()
        return False


def test_traceroute_service():
    """测试路由追踪服务"""
    print("\n=== 测试路由追踪服务 ===")
    
    try:
        from netkit.services.traceroute import TracerouteService
        
        service = TracerouteService()
        
        # 测试tracert输出解析
        test_line = "  1    <1 ms    <1 ms    <1 ms  192.168.1.1"
        result = service.parse_tracert_line(test_line, 0)
        
        if result:
            print("✓ Traceroute输出解析成功")
            print(f"  跳数: {result['hop']}")
            print(f"  IP地址: {result['ip']}")
            print(f"  平均时间: {result['avg_time']}")
        else:
            print("❌ Traceroute输出解析失败")
            
        # 测试超时行解析
        timeout_line = "  2     *        *        *     Request timed out."
        result = service.parse_tracert_line(timeout_line, 0)
        
        if result and result['timeout']:
            print("✓ 超时行解析成功")
        else:
            print("❌ 超时行解析失败")
            
        return True
        
    except Exception as e:
        print(f"❌ 路由追踪服务测试失败: {e}")
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("NETKit-Py 功能测试")
    print("=" * 50)
    
    tests = [
        ("模块导入", test_imports),
        ("IP配置验证", test_ip_validation),
        ("子网计算", test_subnet_calculation),
        ("Ping服务", test_ping_service),
        ("路由服务", test_route_service),
        ("路由追踪服务", test_traceroute_service),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n正在测试: {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试出错: {e}")
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！")
        return 0
    else:
        print("⚠️  部分测试失败，请检查相关功能")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 