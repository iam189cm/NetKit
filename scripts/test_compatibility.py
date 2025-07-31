#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NetKit 兼容性测试脚本
测试在不同Windows环境下的关键功能
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

# 切换到项目根目录
script_dir = Path(__file__).parent
project_root = script_dir.parent
os.chdir(project_root)
sys.path.insert(0, str(project_root))

def test_system_info():
    """测试系统信息获取"""
    print("🔍 系统信息测试")
    print(f"操作系统: {platform.system()}")
    print(f"版本: {platform.version()}")
    print(f"发行版: {platform.release()}")
    print(f"架构: {platform.architecture()}")
    
    # 检测是否为Server版本
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                           r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
        product_name = winreg.QueryValueEx(key, "ProductName")[0]
        print(f"产品名称: {product_name}")
        print(f"是否Server版本: {'Server' in product_name}")
        winreg.CloseKey(key)
    except Exception as e:
        print(f"⚠️ 无法获取产品信息: {e}")

def test_wmi_compatibility():
    """测试WMI功能兼容性"""
    print("\n🔍 WMI兼容性测试")
    try:
        import wmi
        import pythoncom
        
        # 详细的WMI测试
        pythoncom.CoInitialize()
        c = wmi.WMI()
        
        print("1. 测试原始WMI适配器查询...")
        all_adapters = list(c.Win32_NetworkAdapter())
        print(f"   发现 {len(all_adapters)} 个网络适配器")
        
        # 检查有NetConnectionID的适配器
        named_adapters = [a for a in all_adapters if a.NetConnectionID]
        print(f"   其中 {len(named_adapters)} 个有连接名称")
        
        if named_adapters:
            print("   前几个适配器:")
            for adapter in named_adapters[:3]:
                print(f"     - {adapter.NetConnectionID}: {adapter.Description}")
        
        # 测试适配器配置
        print("2. 测试适配器配置查询...")
        configs = list(c.Win32_NetworkAdapterConfiguration())
        ip_enabled_configs = [cfg for cfg in configs if cfg.IPEnabled]
        print(f"   发现 {len(configs)} 个配置，{len(ip_enabled_configs)} 个启用IP")
        
        # 测试SetGateways方法兼容性
        print("3. 测试WMI方法兼容性...")
        if ip_enabled_configs:
            test_config = ip_enabled_configs[0]
            print(f"   测试配置: {test_config.Description}")
            
            # 检查SetGateways方法
            try:
                method = getattr(test_config, 'SetGateways', None)
                if method:
                    print("   ✅ SetGateways方法存在")
                    # 注意：不实际调用，只检查存在性
                else:
                    print("   ❌ SetGateways方法不存在")
            except Exception as method_error:
                print(f"   ⚠️ 方法检查失败: {method_error}")
        
        # 现在测试NetKit的WMI引擎
        print("4. 测试NetKit WMI引擎...")
        from netkit.services.netconfig.wmi_engine import get_wmi_engine
        wmi_engine = get_wmi_engine()
        
        adapters_info = wmi_engine.get_all_adapters_info(show_all=True)
        print(f"   NetKit引擎找到 {len(adapters_info)} 个适配器")
        
        # 检查物理适配器过滤
        physical_adapters = wmi_engine.get_all_adapters_info(show_all=False)
        print(f"   其中 {len(physical_adapters)} 个被识别为物理适配器")
        
        pythoncom.CoUninitialize()
        
    except Exception as e:
        print(f"❌ WMI测试失败: {e}")
        import traceback
        traceback.print_exc()
        try:
            pythoncom.CoUninitialize()
        except:
            pass

def test_network_interfaces():
    """测试网络接口管理"""
    print("\n🔍 网络接口测试")
    try:
        from netkit.services.netconfig.interface_manager import get_network_interfaces
        
        # 测试show_all=False (默认，只显示物理接口)
        interfaces = get_network_interfaces(show_all=False)
        print(f"物理接口: {len(interfaces)} 个")
        
        # 测试show_all=True (显示所有接口)
        all_interfaces = get_network_interfaces(show_all=True)
        print(f"所有接口: {len(all_interfaces)} 个")
        
        if interfaces:
            print("物理接口列表:")
            for i, interface in enumerate(interfaces[:5]):
                print(f"  {i+1}. {interface}")
        else:
            print("⚠️ 没有找到物理网络接口")
            print("这可能表明适配器过滤逻辑在当前环境中过于严格")
            
        if all_interfaces:
            print("所有接口列表 (前5个):")
            for i, interface in enumerate(all_interfaces[:5]):
                print(f"  {i+1}. {interface}")
                
        # 检查环境特定问题
        is_server = "Server" in platform.version()
        if is_server and len(interfaces) == 0:
            print("🚨 Server环境兼容性问题检测:")
            print("   - 物理适配器过滤可能过于严格")
            print("   - 建议在集成测试中使用show_all=True")
            
    except Exception as e:
        print(f"❌ 网络接口测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_gui_components():
    """测试GUI组件兼容性"""
    print("\n🔍 GUI组件测试")
    try:
        import ttkbootstrap as tb
        print("✅ ttkbootstrap导入成功")
        
        # 测试主题
        themes = tb.Style().theme_names()
        print(f"✅ 可用主题: {len(themes)} 个")
        
        # 测试字体
        try:
            import tkinter.font as tkfont
            root = tb.Window()
            root.withdraw()  # 隐藏窗口
            
            default_font = tkfont.nametofont("TkDefaultFont")
            print(f"✅ 默认字体: {default_font['family']} {default_font['size']}")
            
            root.destroy()
            
        except Exception as e:
            print(f"⚠️ 字体测试失败: {e}")
            
    except Exception as e:
        print(f"❌ GUI组件测试失败: {e}")

def test_system_commands():
    """测试系统命令兼容性"""
    print("\n🔍 系统命令测试")
    
    commands = [
        ("ipconfig", "IP配置命令"),
        ("route", "路由命令"),
        ("ping", "Ping命令"),
        ("netsh", "网络Shell命令")
    ]
    
    for cmd, desc in commands:
        try:
            result = subprocess.run([cmd, "/?"], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            if result.returncode == 0:
                print(f"✅ {desc} 可用")
            else:
                print(f"⚠️ {desc} 返回码: {result.returncode}")
        except Exception as e:
            print(f"❌ {desc} 测试失败: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("NetKit 兼容性测试")
    print("=" * 60)
    
    test_system_info()
    test_wmi_compatibility()
    test_network_interfaces()
    test_gui_components()
    test_system_commands()
    
    print("\n" + "=" * 60)
    print("兼容性测试完成")
    print("=" * 60)