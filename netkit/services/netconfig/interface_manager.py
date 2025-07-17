"""
网卡选择管理模块
负责网卡列表的获取、过滤、格式化显示等功能
"""

import subprocess
import re
import locale
from .interface_info import get_network_adapter_hardware_info


def run_netsh_command(cmd, timeout=30):
    """
    运行netsh命令并处理编码问题
    
    Args:
        cmd: 命令列表
        timeout: 超时时间（秒）
    
    Returns:
        str: 命令输出结果，如果失败返回空字符串
    """
    encodings_to_try = [
        'utf-8',           # 首先尝试UTF-8
        'gbk',             # 然后尝试GBK
        'cp936',           # 中文简体
        'utf-16',          # Unicode
        locale.getpreferredencoding(),  # 系统默认编码
        'ascii'            # 最后尝试ASCII
    ]
    
    for encoding in encodings_to_try:
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                encoding=encoding, 
                errors='ignore',
                timeout=timeout
            )
            
            if result.returncode == 0 and result.stdout:
                # 检查输出是否包含明显的乱码
                output = result.stdout.strip()
                if output and not _contains_obvious_mojibake(output):
                    return output
                    
        except (UnicodeDecodeError, subprocess.TimeoutExpired, OSError):
            continue
    
    # 如果所有编码都失败，尝试使用bytes模式
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=timeout)
        if result.returncode == 0 and result.stdout:
            # 尝试用多种编码解码bytes
            for encoding in encodings_to_try:
                try:
                    decoded = result.stdout.decode(encoding, errors='ignore')
                    if decoded and not _contains_obvious_mojibake(decoded):
                        return decoded
                except (UnicodeDecodeError, AttributeError):
                    continue
    except (subprocess.TimeoutExpired, OSError):
        pass
    
    return ""


def _contains_obvious_mojibake(text):
    """
    检查文本是否包含明显的乱码
    
    Args:
        text: 要检查的文本
    
    Returns:
        bool: True如果包含乱码，False否则
    """
    # 检查是否包含大量问号或其他替换字符
    if text.count('?') > len(text) * 0.1:  # 超过10%是问号
        return True
    
    # 检查是否包含明显的乱码模式
    mojibake_patterns = [
        r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]',  # 控制字符
        r'[锘垄]',  # 常见的UTF-8 BOM乱码
        r'\ufffd{2,}',  # 连续的替换字符
    ]
    
    for pattern in mojibake_patterns:
        if re.search(pattern, text):
            return True
    
    return False


def get_network_interfaces(show_all=False):
    """获取网络接口列表
    
    Args:
        show_all (bool): 是否显示所有网卡（包括虚拟网卡），默认False只显示物理网卡
    
    Returns:
        list: 网络接口名称列表
    """
    try:
        cmd = ['netsh', 'interface', 'show', 'interface']
        output = run_netsh_command(cmd)
        
        if not output:
            return []
            
        interfaces = []
        lines = output.split('\n')
        
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
            line = line.strip()
            if line and not line.startswith('Admin') and not line.startswith('---') and not line.startswith('管理'):
                # 解析接口行，格式通常是: 状态 类型 接口名称
                parts = line.split()
                if len(parts) >= 4:
                    # 接口名称可能包含空格，取最后几个部分
                    interface_name = ' '.join(parts[3:])
                    if interface_name and interface_name not in interfaces:
                        # 只返回启用的网络接口
                        status = parts[0].strip()
                        if status in ["已启用", "Enabled"]:
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
        output = run_netsh_command(cmd)
        
        if output:
            lines = output.split('\n')
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
        cmd = ['netsh', 'interface', 'ip', 'show', 'config', f'name={interface_name}']
        output = run_netsh_command(cmd)
        
        if output:
            lines = output.split('\n')
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
    """格式化网卡显示名称: [状态] 网卡名称 - IP地址"""
    try:
        # 获取连接状态
        status = get_network_connection_status(interface_name)
        
        # 获取IP地址
        ip = get_interface_ip_address(interface_name)
        
        # 简化显示格式，去掉制造商和型号信息
        display_name = f"[{status}] {interface_name} - {ip}"
        
        return display_name
        
    except Exception as e:
        # 如果获取信息失败，返回简单格式
        return f"[未知] {interface_name} - 未知"


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
        # 新的显示格式: [状态] 网卡名称 - IP地址
        # 提取 "] " 和 " - " 之间的内容
        start_idx = display_name.find('] ') + 2
        end_idx = display_name.find(' - ')
        if start_idx > 1 and end_idx > start_idx:
            return display_name[start_idx:end_idx]
        else:
            # 如果格式不匹配，返回原始字符串
            return display_name
    except:
        return display_name 