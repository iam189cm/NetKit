"""
测试netsh方法清除网关
验证netsh命令是否能彻底清除静态网关
"""

import subprocess
import sys
import os
import time

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from netkit.services.netconfig.interface_manager import get_network_interfaces


def test_netsh_gateway_clear():
    """测试netsh命令清除网关的效果"""
    
    print("=== NetSH网关清除测试 ===\n")
    
    # 获取可用的网络接口
    interfaces = get_network_interfaces()
    if not interfaces:
        print("❌ 没有找到可用的网络接口")
        return False
    
    # 显示可用接口
    print("可用的网络接口:")
    for i, interface in enumerate(interfaces):
        print(f"  {i+1}. {interface}")
    
    # 让用户选择接口
    try:
        choice = input(f"\n请选择要测试的接口 (1-{len(interfaces)}): ")
        interface_index = int(choice) - 1
        if interface_index < 0 or interface_index >= len(interfaces):
            print("❌ 无效的选择")
            return False
        
        test_interface = interfaces[interface_index]
        print(f"✅ 选择的接口: {test_interface}")
        
    except (ValueError, KeyboardInterrupt):
        print("❌ 测试被取消")
        return False
    
    print("\n" + "="*60)
    print("⚠️  重要提示:")
    print("1. 此测试会临时更改您的网络配置")
    print("2. 建议在测试环境中运行")
    print("3. 测试过程中可能短暂中断网络连接")
    print("4. 测试完成后会恢复为DHCP配置")
    print("="*60)
    
    confirm = input("\n确认继续测试? (输入 'yes' 继续): ")
    if confirm.lower() != 'yes':
        print("❌ 测试被取消")
        return False
    
    print(f"\n🔧 开始测试接口: {test_interface}")
    
    # 步骤1: 显示当前配置
    print("\n📋 步骤1: 显示当前网络配置")
    show_current_config(test_interface)
    
    # 步骤2: 设置测试静态IP配置
    print("\n📋 步骤2: 设置测试静态IP配置")
    static_ip = "192.168.100.100"
    static_mask = "255.255.255.0"
    static_gateway = "192.168.100.1"
    
    print(f"设置静态IP: {static_ip}")
    print(f"设置子网掩码: {static_mask}")
    print(f"设置测试网关: {static_gateway}")
    
    # 使用netsh设置静态IP
    static_cmd = f'netsh interface ipv4 set address name="{test_interface}" source=static addr={static_ip} mask={static_mask} gateway={static_gateway}'
    
    result = run_netsh_command(static_cmd, "设置静态IP配置")
    if not result:
        return False
    
    # 等待配置生效
    print("⏳ 等待静态配置生效...")
    time.sleep(3)
    
    # 步骤3: 验证静态配置
    print("\n📋 步骤3: 验证静态配置是否生效")
    show_current_config(test_interface)
    
    # 步骤4: 使用netsh切换到DHCP
    print("\n📋 步骤4: 使用netsh切换到DHCP模式")
    print("这里应该会清除之前的静态网关...")
    
    dhcp_cmd = f'netsh interface ipv4 set address name="{test_interface}" source=dhcp'
    
    result = run_netsh_command(dhcp_cmd, "切换到DHCP模式")
    if not result:
        return False
    
    # 等待DHCP配置生效
    print("⏳ 等待DHCP配置生效...")
    time.sleep(5)
    
    # 步骤5: 验证DHCP配置并检查网关是否被清除
    print("\n📋 步骤5: 验证DHCP配置（检查静态网关是否被清除）")
    show_current_config(test_interface)
    
    # 步骤6: 检查路由表
    print("\n📋 步骤6: 检查路由表中的网关信息")
    check_route_table(static_gateway)
    
    print("\n🎉 测试完成！")
    print("\n📊 请检查上面的输出：")
    print("1. 如果在步骤5中没有看到测试网关192.168.100.1，说明netsh成功清除了静态网关")
    print("2. 如果在路由表中没有看到测试网关，说明清除彻底")
    print("3. 如果仍然看到测试网关，说明需要其他方法")
    
    return True


def show_current_config(interface_name):
    """显示当前网络配置"""
    try:
        cmd = f'netsh interface ipv4 show config name="{interface_name}"'
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ 当前网络配置:")
            print(result.stdout)
        else:
            print(f"❌ 获取配置失败: {result.stderr}")
            
    except Exception as e:
        print(f"❌ 获取配置时出错: {str(e)}")


def check_route_table(gateway_ip):
    """检查路由表中是否还有指定的网关"""
    try:
        cmd = 'route print'
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            encoding='gbk',  # Windows route命令通常使用GBK编码
            timeout=10
        )
        
        if result.returncode == 0:
            if gateway_ip in result.stdout:
                print(f"⚠️  在路由表中仍然发现测试网关 {gateway_ip}")
                # 显示相关行
                lines = result.stdout.split('\n')
                for line in lines:
                    if gateway_ip in line:
                        print(f"   相关路由: {line.strip()}")
            else:
                print(f"✅ 路由表中未发现测试网关 {gateway_ip}")
        else:
            print(f"❌ 获取路由表失败: {result.stderr}")
            
    except Exception as e:
        print(f"❌ 检查路由表时出错: {str(e)}")


def run_netsh_command(cmd, description):
    """执行netsh命令"""
    try:
        print(f"执行命令: {cmd}")
        
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"✅ {description} 成功")
            if result.stdout.strip():
                print(f"输出: {result.stdout}")
            return True
        else:
            print(f"❌ {description} 失败")
            print(f"错误: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 执行{description}时出错: {str(e)}")
        return False


def main():
    """主函数"""
    try:
        print("NetSH网关清除测试工具")
        print("用于验证netsh命令是否能彻底清除静态网关")
        print("="*60)
        
        success = test_netsh_gateway_clear()
        
        if success:
            print("\n✅ 测试执行完成")
            print("请根据输出结果判断netsh方法的效果")
        else:
            print("\n❌ 测试执行失败")
            
    except KeyboardInterrupt:
        print("\n⏹️  测试被用户取消")
    except Exception as e:
        print(f"\n❌ 测试过程中出现异常: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 