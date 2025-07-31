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
        from netkit.services.netconfig.wmi_engine import WMIQueryEngine
        wmi_engine = WMIQueryEngine()
        
        # 测试网络适配器查询
        print("测试网络适配器查询...")
        adapters = wmi_engine.get_network_adapters()
        print(f"✅ 找到 {len(adapters)} 个网络适配器")
        
        # 测试网络配置查询
        print("测试网络配置查询...")
        configs = wmi_engine.get_network_adapter_configurations()
        print(f"✅ 找到 {len(configs)} 个网络配置")
        
    except Exception as e:
        print(f"❌ WMI测试失败: {e}")

def test_network_interfaces():
    """测试网络接口管理"""
    print("\n🔍 网络接口测试")
    try:
        from netkit.services.netconfig.interface_manager import get_network_interfaces
        
        interfaces = get_network_interfaces()
        print(f"✅ 找到 {len(interfaces)} 个网络接口")
        
        for i, interface in enumerate(interfaces[:3]):  # 只显示前3个
            print(f"  {i+1}. {interface}")
            
    except Exception as e:
        print(f"❌ 网络接口测试失败: {e}")

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