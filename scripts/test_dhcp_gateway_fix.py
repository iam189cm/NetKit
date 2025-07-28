"""
测试DHCP网关清除修复
验证从静态IP切换到DHCP时，是否正确清除了之前的静态网关设置
"""

import sys
import os
import time

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from netkit.services.netconfig.ip_configurator import apply_profile
from netkit.services.netconfig.interface_manager import get_network_interfaces
from netkit.services.netconfig.interface_info import get_interface_config


def test_dhcp_gateway_clear():
    """测试DHCP配置时是否正确清除静态网关"""
    
    print("=== DHCP网关清除修复测试 ===\n")
    
    # 获取可用的网络接口
    interfaces = get_network_interfaces()
    if not interfaces:
        print("❌ 没有找到可用的网络接口")
        return False
    
    # 选择第一个接口进行测试
    test_interface = interfaces[0]
    print(f"🔧 使用测试接口: {test_interface}")
    
    # 步骤1：获取当前配置
    print("\n📋 步骤1: 获取当前网络配置")
    current_config = get_interface_config(test_interface)
    if current_config:
        print("✅ 当前配置获取成功")
        print("当前配置摘要:")
        lines = current_config.split('\n')[:10]  # 只显示前10行
        for line in lines:
            if line.strip():
                print(f"   {line.strip()}")
    else:
        print("❌ 无法获取当前配置")
        return False
    
    # 步骤2：设置静态IP配置（包含网关）
    print("\n📋 步骤2: 设置静态IP配置（包含测试网关）")
    static_config = {
        'ip': '192.168.100.100',
        'mask': '255.255.255.0', 
        'gateway': '192.168.100.1'  # 这是我们要测试清除的网关
    }
    
    dns_config = {
        'dns1': '8.8.8.8',
        'dns2': '8.8.4.4'
    }
    
    print(f"设置静态IP: {static_config['ip']}")
    print(f"设置子网掩码: {static_config['mask']}")
    print(f"设置网关: {static_config['gateway']}")
    
    result = apply_profile(
        interface_name=test_interface,
        ip_mode='manual',
        dns_mode='manual', 
        ip_config=static_config,
        dns_config=dns_config
    )
    
    if result['success']:
        print("✅ 静态IP配置应用成功")
        print(f"   消息: {result['message']}")
    else:
        print(f"❌ 静态IP配置失败: {result['error']}")
        return False
    
    # 等待配置生效
    print("⏳ 等待配置生效...")
    time.sleep(3)
    
    # 步骤3：验证静态配置是否生效
    print("\n📋 步骤3: 验证静态配置")
    static_verification = get_interface_config(test_interface)
    if static_verification:
        print("✅ 静态配置验证:")
        # 检查是否包含我们设置的网关
        if '192.168.100.1' in static_verification:
            print("   ✅ 发现测试网关 192.168.100.1")
        else:
            print("   ⚠️  未发现测试网关（可能配置未生效）")
    
    # 步骤4：切换到DHCP模式
    print("\n📋 步骤4: 切换到DHCP模式（这里应该清除静态网关）")
    
    result = apply_profile(
        interface_name=test_interface,
        ip_mode='auto',  # 自动获取IP
        dns_mode='auto', # 自动获取DNS
        ip_config={},
        dns_config={}
    )
    
    if result['success']:
        print("✅ DHCP配置应用成功")
        print(f"   消息: {result['message']}")
        
        # 检查消息中是否提到清除网关
        if "清除" in result['message'] and "网关" in result['message']:
            print("   ✅ 确认：消息中提到清除了静态网关设置")
        else:
            print("   ⚠️  注意：消息中未明确提到清除网关")
    else:
        print(f"❌ DHCP配置失败: {result['error']}")
        return False
    
    # 等待DHCP配置生效
    print("⏳ 等待DHCP配置生效...")
    time.sleep(5)
    
    # 步骤5：验证DHCP配置并检查网关是否被清除
    print("\n📋 步骤5: 验证DHCP配置（检查静态网关是否被清除）")
    dhcp_verification = get_interface_config(test_interface)
    
    if dhcp_verification:
        print("✅ DHCP配置验证:")
        
        # 检查是否还存在我们之前设置的静态网关
        if '192.168.100.1' in dhcp_verification:
            print("   ❌ 问题：仍然发现测试网关 192.168.100.1（网关未被清除）")
            print("   🔍 这表明修复可能不完全有效")
            
            # 显示相关的网关信息
            lines = dhcp_verification.split('\n')
            for line in lines:
                if '192.168.100.1' in line or 'Gateway' in line or '网关' in line:
                    print(f"      相关行: {line.strip()}")
            
            return False
        else:
            print("   ✅ 成功：未发现之前的测试网关 192.168.100.1")
            print("   ✅ 静态网关已被正确清除")
            
            # 显示当前的网关信息
            lines = dhcp_verification.split('\n')
            gateway_found = False
            for line in lines:
                if 'Gateway' in line or '网关' in line:
                    print(f"      当前网关: {line.strip()}")
                    gateway_found = True
            
            if not gateway_found:
                print("      当前网关: 无网关信息或正在获取中")
    
    print("\n🎉 测试完成！")
    return True


def main():
    """主函数"""
    try:
        print("开始测试DHCP网关清除修复...")
        print("⚠️  注意：此测试会临时更改网络配置，请确保在测试环境中运行")
        print("⚠️  测试完成后建议手动检查网络连接是否正常")
        
        input("\n按Enter键继续测试，或Ctrl+C取消...")
        
        success = test_dhcp_gateway_clear()
        
        if success:
            print("\n✅ 测试结果：DHCP网关清除修复可能有效")
            print("建议：请手动验证网络连接是否正常工作")
        else:
            print("\n❌ 测试结果：发现问题，需要进一步调试")
            
    except KeyboardInterrupt:
        print("\n⏹️  测试被用户取消")
    except Exception as e:
        print(f"\n❌ 测试过程中出现异常: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 