#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NetKit Compatibility Test Script
Test key functionality across different Windows environments
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

# Switch to project root directory
script_dir = Path(__file__).parent
project_root = script_dir.parent
os.chdir(project_root)
sys.path.insert(0, str(project_root))

def test_system_info():
    """Test system information retrieval"""
    print("[INFO] System Information Test")
    print(f"Operating System: {platform.system()}")
    print(f"Version: {platform.version()}")
    print(f"Release: {platform.release()}")
    print(f"Architecture: {platform.architecture()}")
    
    # Detect if Server version
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                           r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
        product_name = winreg.QueryValueEx(key, "ProductName")[0]
        print(f"Product Name: {product_name}")
        print(f"Is Server Version: {'Server' in product_name}")
        winreg.CloseKey(key)
    except Exception as e:
        print(f"[WARN] Cannot get product info: {e}")

def test_wmi_compatibility():
    """Test WMI functionality compatibility"""
    print("\n[INFO] WMI Compatibility Test")
    try:
        import wmi
        import pythoncom
        
        # Detailed WMI testing
        pythoncom.CoInitialize()
        c = wmi.WMI()
        
        print("1. Test raw WMI adapter query...")
        all_adapters = list(c.Win32_NetworkAdapter())
        print(f"   Found {len(all_adapters)} network adapters")
        
        # Check adapters with NetConnectionID
        named_adapters = [a for a in all_adapters if a.NetConnectionID]
        print(f"   {len(named_adapters)} have connection names")
        
        if named_adapters:
            print("   First few adapters:")
            for adapter in named_adapters[:3]:
                print(f"     - {adapter.NetConnectionID}: {adapter.Description}")
        
        # Test adapter configuration
        print("2. Test adapter configuration query...")
        configs = list(c.Win32_NetworkAdapterConfiguration())
        ip_enabled_configs = [cfg for cfg in configs if cfg.IPEnabled]
        print(f"   Found {len(configs)} configs, {len(ip_enabled_configs)} IP-enabled")
        
        # Test SetGateways method compatibility
        print("3. Test WMI method compatibility...")
        if ip_enabled_configs:
            test_config = ip_enabled_configs[0]
            print(f"   Test config: {test_config.Description}")
            
            # Check SetGateways method
            try:
                method = getattr(test_config, 'SetGateways', None)
                if method:
                    print("   [PASS] SetGateways method exists")
                    # Note: Not actually calling, just checking existence
                else:
                    print("   [FAIL] SetGateways method does not exist")
            except Exception as method_error:
                print(f"   [WARN] Method check failed: {method_error}")
        
        # Now test NetKit's WMI engine
        print("4. Test NetKit WMI engine...")
        from netkit.services.netconfig.wmi_engine import get_wmi_engine
        wmi_engine = get_wmi_engine()
        
        adapters_info = wmi_engine.get_all_adapters_info(show_all=True)
        print(f"   NetKit engine found {len(adapters_info)} adapters")
        
        # Check physical adapter filtering
        physical_adapters = wmi_engine.get_all_adapters_info(show_all=False)
        print(f"   {len(physical_adapters)} identified as physical adapters")
        
        pythoncom.CoUninitialize()
        
    except Exception as e:
        print(f"[ERROR] WMI test failed: {e}")
        import traceback
        traceback.print_exc()
        try:
            pythoncom.CoUninitialize()
        except:
            pass

def test_network_interfaces():
    """Test network interface management"""
    print("\n[INFO] Network Interface Test")
    try:
        from netkit.services.netconfig.interface_manager import get_network_interfaces
        
        # Test show_all=False (default, physical interfaces only)
        interfaces = get_network_interfaces(show_all=False)
        print(f"Physical interfaces: {len(interfaces)}")
        
        # Test show_all=True (show all interfaces)
        all_interfaces = get_network_interfaces(show_all=True)
        print(f"All interfaces: {len(all_interfaces)}")
        
        if interfaces:
            print("Physical interface list:")
            for i, interface in enumerate(interfaces[:5]):
                print(f"  {i+1}. {interface}")
        else:
            print("[WARN] No physical network interfaces found")
            print("This may indicate adapter filtering logic is too strict in current environment")
            
        if all_interfaces:
            print("All interfaces list (first 5):")
            for i, interface in enumerate(all_interfaces[:5]):
                print(f"  {i+1}. {interface}")
                
        # Check environment-specific issues
        is_server = "Server" in platform.version()
        if is_server and len(interfaces) == 0:
            print("[ALERT] Server environment compatibility issue detected:")
            print("   - Physical adapter filtering may be too strict")
            print("   - Recommend using show_all=True in integration tests")
            
    except Exception as e:
        print(f"[ERROR] Network interface test failed: {e}")
        import traceback
        traceback.print_exc()

def test_gui_components():
    """Test GUI component compatibility"""
    print("\n[INFO] GUI Component Test")
    try:
        import ttkbootstrap as tb
        print("[PASS] ttkbootstrap import successful")
        
        # Test themes
        themes = tb.Style().theme_names()
        print(f"[PASS] Available themes: {len(themes)}")
        
        # Test fonts
        try:
            import tkinter.font as tkfont
            root = tb.Window()
            root.withdraw()  # Hide window
            
            default_font = tkfont.nametofont("TkDefaultFont")
            print(f"[PASS] Default font: {default_font['family']} {default_font['size']}")
            
            root.destroy()
            
        except Exception as e:
            print(f"[WARN] Font test failed: {e}")
            
    except Exception as e:
        print(f"[ERROR] GUI component test failed: {e}")

def test_system_commands():
    """Test system command compatibility"""
    print("\n[INFO] System Command Test")
    
    commands = [
        ("ipconfig", "IP Configuration Command"),
        ("route", "Route Command"),
        ("ping", "Ping Command"),
        ("netsh", "Network Shell Command")
    ]
    
    for cmd, desc in commands:
        try:
            result = subprocess.run([cmd, "/?"], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            if result.returncode == 0:
                print(f"[PASS] {desc} available")
            else:
                print(f"[WARN] {desc} return code: {result.returncode}")
        except Exception as e:
            print(f"[ERROR] {desc} test failed: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("NetKit Compatibility Test")
    print("=" * 60)
    
    test_system_info()
    test_wmi_compatibility()
    test_network_interfaces()
    test_gui_components()
    test_system_commands()
    
    print("\n" + "=" * 60)
    print("Compatibility Test Completed")
    print("=" * 60)