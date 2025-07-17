"""
网卡选择管理模块
负责网卡列表的获取、过滤、格式化显示等功能
"""

import subprocess
import re
from .interface_info import get_network_adapter_hardware_info


def get_network_interfaces(show_all=False):
    """获取网络接口列表
    
    Args:
        show_all (bool): 是否显示所有网卡（包括虚拟网卡），默认False只显示物理网卡
    
    Returns:
        list: 网络接口名称列表
    """
    try:
        cmd = ['netsh', 'interface', 'show', 'interface']
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode != 0:
            return []
            
        interfaces = []
        lines = result.stdout.split('\n')
        
        # 虚拟网卡关键字（用于过滤）
        virtual_keywords = [
            'VMware', 'VirtualBox', 'Hyper-V', 'Virtual', 'vEthernet',
            'TAP', 'Tunnel', 'Loopback', 'Teredo', 'ISATAP', 'Bluetooth',
            'VPN', 'PPP', 'WAN Miniport', 'Microsoft Wi-Fi Direct',
            'Microsoft Hosted Network', 'Microsoft ISATAP', 'Microsoft Teredo',
            'VirtualBox Host-Only', 'VMware Virtual Ethernet'
        ]
        
        # 跳过标题行，查找接口信息
        for line in lines:
            if line.strip() and not line.startswith('Admin') and not line.startswith('---'):
                # 解析接口行，格式通常是: 状态 类型 接口名称
                parts = line.split()
                if len(parts) >= 4:
                    # 接口名称可能包含空格，取最后几个部分
                    interface_name = ' '.join(parts[3:])
                    if interface_name and interface_name not in interfaces:
                        # 只返回启用的网络接口
                        if parts[0].strip() == "已启用" or parts[0].strip() == "Enabled":
                            # 如果不显示所有网卡，则过滤虚拟网卡
                            if not show_all:
                                # 检查是否为虚拟网卡
                                is_virtual = any(keyword.lower() in interface_name.lower() 
                                               for keyword in virtual_keywords)
                                if not is_virtual:
                                    interfaces.append(interface_name)
                            else:
                                interfaces.append(interface_name)
                        
        return interfaces
        
    except Exception as e:
        print(f"获取网络接口失败: {e}")
        return []


def get_network_connection_status(interface_name):
    """获取网络连接状态"""
    try:
        cmd = ['netsh', 'interface', 'show', 'interface', f'name={interface_name}']
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='gbk', errors='ignore')
        
        if result.returncode == 0 and result.stdout:
            lines = result.stdout.split('\n')
            for line in lines:
                if '连接状态' in line or 'Connect state' in line:
                    state = line.split(':')[-1].strip()
                    if '已连接' in state or 'Connected' in state:
                        return '已连接'
                    elif '已断开' in state or 'Disconnected' in state:
                        return '已断开'
                    else:
                        return '未知'
        return '未知'
    except:
        return '未知'


def get_interface_ip_address(interface_name):
    """获取网卡IP地址（快速获取）"""
    try:
        cmd_ip = ['netsh', 'interface', 'ip', 'show', 'config', f'name={interface_name}']
        result_ip = subprocess.run(cmd_ip, capture_output=True, text=True, encoding='gbk', errors='ignore')
        
        if result_ip.returncode == 0 and result_ip.stdout:
            lines = result_ip.stdout.split('\n')
            for line in lines:
                line = line.strip()
                if 'IP Address' in line or 'IP 地址' in line:
                    ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                    if ip_match:
                        return ip_match.group(1)
        return '未配置'
    except:
        return '未配置'


def format_interface_display_name(interface_name):
    """格式化网卡显示名称: [状态] 网卡名称 (制造商 型号) - IP地址"""
    try:
        # 获取连接状态
        status = get_network_connection_status(interface_name)
        
        # 获取硬件信息
        hardware_info = get_network_adapter_hardware_info(interface_name)
        manufacturer = hardware_info.get('manufacturer', '未知')
        model = hardware_info.get('model', '未知')
        
        if manufacturer == '未知' and model == '未知':
            hw_display = '未知'
        elif manufacturer == '未知':
            hw_display = model
        elif model == '未知':
            hw_display = manufacturer
        else:
            hw_display = f"{manufacturer} {model}"
        
        # 获取IP地址
        ip = get_interface_ip_address(interface_name)
        
        # 组合显示名称
        display_name = f"[{status}] {interface_name} ({hw_display}) - {ip}"
        
        return display_name
        
    except Exception as e:
        # 如果获取信息失败，返回简单格式
        return f"[未知] {interface_name} (未知) - 未知"


def get_network_interfaces_with_details(show_all=False):
    """获取带详细信息的网络接口列表
    
    Returns:
        list: 包含元组的列表，每个元组包含 (显示名称, 原始接口名称)
    """
    try:
        # 先获取基本的网络接口列表
        basic_interfaces = get_network_interfaces(show_all=show_all)
        
        # 为每个接口生成详细的显示名称
        detailed_interfaces = []
        for interface in basic_interfaces:
            display_name = format_interface_display_name(interface)
            detailed_interfaces.append((display_name, interface))
        
        return detailed_interfaces
        
    except Exception as e:
        print(f"获取详细网络接口失败: {e}")
        return []


def extract_interface_name_from_display(display_name):
    """从显示名称中提取原始接口名称"""
    try:
        # 显示格式: [状态] 网卡名称 (制造商 型号) - IP地址
        # 提取 "] " 和 " (" 之间的内容
        start_idx = display_name.find('] ') + 2
        end_idx = display_name.find(' (')
        if start_idx > 1 and end_idx > start_idx:
            return display_name[start_idx:end_idx]
        else:
            # 如果格式不匹配，返回原始字符串
            return display_name
    except:
        return display_name 