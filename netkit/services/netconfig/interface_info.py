"""
网卡信息模块
负责获取网卡的硬件信息、详细配置信息等
"""

import subprocess
import re
import locale


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


def get_network_adapter_hardware_info(interface_name):
    """获取网卡硬件信息（制造商、型号等）"""
    try:
        # 使用WMIC获取网卡硬件信息
        cmd = ['wmic', 'nic', 'where', f'NetConnectionID="{interface_name}"', 
               'get', 'Name,Manufacturer,Description,PhysicalAdapter,Speed', '/format:csv']
        output = run_netsh_command(cmd)
        
        if output:
            lines = output.split('\n')
            for line in lines:
                if line.strip() and not line.startswith('Node'):
                    parts = line.split(',')
                    if len(parts) >= 6:
                        manufacturer = parts[2].strip() if parts[2].strip() else '未知'
                        description = parts[1].strip() if parts[1].strip() else '未知'
                        name = parts[3].strip() if parts[3].strip() else '未知'
                        speed = parts[5].strip() if parts[5].strip() else '未知'
                        
                        # 处理速度信息
                        if speed and speed != '未知' and speed.isdigit():
                            speed_mbps = int(speed) // 1000000  # 转换为Mbps
                            speed = f"{speed_mbps} Mbps"
                        elif speed == '未知' or not speed:
                            speed = '未知'
                        
                        # 提取简化的制造商名称
                        if manufacturer != '未知':
                            if 'Intel' in manufacturer:
                                manufacturer = 'Intel'
                            elif 'Realtek' in manufacturer:
                                manufacturer = 'Realtek'
                            elif 'Broadcom' in manufacturer:
                                manufacturer = 'Broadcom'
                            elif 'Qualcomm' in manufacturer:
                                manufacturer = 'Qualcomm'
                            elif 'Microsoft' in manufacturer:
                                manufacturer = 'Microsoft'
                            elif 'VMware' in manufacturer:
                                manufacturer = 'VMware'
                        
                        # 提取简化的型号信息
                        model = '未知'
                        if description != '未知':
                            # 去掉制造商名称，提取型号
                            desc_lower = description.lower()
                            if 'realtek' in desc_lower and 'pcie' in desc_lower:
                                model = 'PCIe GBE'
                            elif 'intel' in desc_lower and 'wi-fi' in desc_lower:
                                if 'ax200' in desc_lower:
                                    model = 'AX200 160MHz'
                                elif 'ax201' in desc_lower:
                                    model = 'AX201 160MHz'
                                else:
                                    model = 'Wi-Fi 6'
                            elif 'usb' in desc_lower:
                                model = 'USB Adapter'
                            elif 'virtual' in desc_lower:
                                model = 'Virtual'
                            elif 'bluetooth' in desc_lower:
                                model = 'Bluetooth'
                            elif 'dedicated' in desc_lower:
                                model = '专用网卡'
                            else:
                                # 尝试提取型号信息
                                words = description.split()
                                if len(words) > 2:
                                    model = ' '.join(words[-2:])
                                else:
                                    model = description
                        
                        return {
                            'manufacturer': manufacturer,
                            'model': model,
                            'full_description': description,
                            'speed': speed
                        }
        
        return {
            'manufacturer': '未知',
            'model': '未知',
            'full_description': '未知',
            'speed': '未知'
        }
        
    except Exception as e:
        return {
            'manufacturer': '未知',
            'model': '未知',
            'full_description': '未知',
            'speed': '未知'
        }


def get_interface_mac_address(interface_name):
    """获取网卡MAC地址"""
    try:
        cmd = ['getmac', '/fo', 'csv', '/v']
        output = run_netsh_command(cmd)
        
        if output:
            lines = output.split('\n')
            for line in lines:
                if interface_name in line:
                    parts = line.split(',')
                    if len(parts) >= 3:
                        mac = parts[2].strip('"')
                        if mac != 'N/A':
                            return mac
        return '未知'
    except:
        return '未知'


def get_interface_basic_info(interface_name):
    """获取网卡基本信息（状态、类型等）"""
    try:
        cmd = ['netsh', 'interface', 'show', 'interface', f'name={interface_name}']
        output = run_netsh_command(cmd)
        
        info = {
            'status': '未知',
            'type': '未知'
        }
        
        if output:
            lines = output.split('\n')
            for line in lines:
                if '管理状态' in line or 'Administrative state' in line:
                    status = line.split(':')[-1].strip()
                    # 状态本地化
                    if status.lower() == 'enabled':
                        info['status'] = '已启用'
                    elif status.lower() == 'disabled':
                        info['status'] = '已禁用'
                    else:
                        info['status'] = status
                elif '类型' in line or 'Type' in line:
                    type_info = line.split(':')[-1].strip()
                    # 类型本地化
                    if type_info.lower() == 'dedicated':
                        info['type'] = '专用'
                    elif type_info.lower() == 'loopback':
                        info['type'] = '环回'
                    else:
                        info['type'] = type_info
        
        return info
        
    except Exception as e:
        return {
            'status': '获取失败',
            'type': '获取失败'
        }


def get_interface_ip_config(interface_name):
    """获取网卡IP配置信息"""
    try:
        cmd = ['netsh', 'interface', 'ip', 'show', 'config', f'name={interface_name}']
        output = run_netsh_command(cmd)
        
        config = {
            'ip': '未配置',
            'mask': '未配置',
            'gateway': '未配置',
            'dns1': '未配置',
            'dns2': '未配置'
        }
        
        if output:
            lines = output.split('\n')
            dns_servers = []
            
            for line in lines:
                line = line.strip()
                if 'IP Address' in line or 'IP 地址' in line:
                    ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                    if ip_match:
                        config['ip'] = ip_match.group(1)
                elif 'Subnet Prefix' in line or '子网前缀' in line:
                    # 提取子网掩码
                    mask_match = re.search(r'/(\d+)', line)
                    if mask_match:
                        prefix = int(mask_match.group(1))
                        # 转换CIDR为点分十进制
                        mask_int = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
                        config['mask'] = f"{(mask_int >> 24) & 0xFF}.{(mask_int >> 16) & 0xFF}.{(mask_int >> 8) & 0xFF}.{mask_int & 0xFF}"
                elif 'Default Gateway' in line or '默认网关' in line:
                    gateway_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                    if gateway_match:
                        config['gateway'] = gateway_match.group(1)
                elif 'DNS Servers' in line or 'DNS 服务器' in line:
                    dns_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                    if dns_match:
                        dns_servers.append(dns_match.group(1))
                elif re.match(r'^\s*\d+\.\d+\.\d+\.\d+\s*$', line):
                    # 额外的DNS服务器行
                    dns_servers.append(line.strip())
            
            # 设置DNS服务器
            if len(dns_servers) > 0:
                config['dns1'] = dns_servers[0]
            if len(dns_servers) > 1:
                config['dns2'] = dns_servers[1]
        
        return config
        
    except Exception as e:
        return {
            'ip': '获取失败',
            'mask': '获取失败',
            'gateway': '获取失败',
            'dns1': '获取失败',
            'dns2': '获取失败'
        }


def get_network_card_info(interface_name):
    """获取网卡完整详细信息"""
    try:
        # 初始化信息结构
        info = {
            'name': interface_name,
            'description': '未知',
            'status': '未知',
            'mac': '未知',
            'speed': '未知',
            'ip': '未配置',
            'mask': '未配置',
            'gateway': '未配置',
            'dns1': '未配置',
            'dns2': '未配置',
            'manufacturer': '未知',
            'model': '未知'
        }
        
        # 获取网卡硬件信息
        hardware_info = get_network_adapter_hardware_info(interface_name)
        info['manufacturer'] = hardware_info['manufacturer']
        info['model'] = hardware_info['model']
        info['description'] = hardware_info['full_description']
        info['speed'] = hardware_info['speed']
        
        # 获取接口基本信息
        basic_info = get_interface_basic_info(interface_name)
        info['status'] = basic_info['status']
        
        # 如果硬件信息获取失败，使用netsh的描述
        if info['description'] == '未知':
            info['description'] = basic_info['type']
        
        # 获取物理地址
        info['mac'] = get_interface_mac_address(interface_name)
        
        # 获取IP配置信息
        ip_config = get_interface_ip_config(interface_name)
        info.update(ip_config)
        
        return info
        
    except Exception as e:
        print(f"获取网卡信息失败: {e}")
        return {
            'name': interface_name,
            'description': '获取失败',
            'status': '获取失败',
            'mac': '获取失败',
            'speed': '获取失败',
            'ip': '获取失败',
            'mask': '获取失败',
            'gateway': '获取失败',
            'dns1': '获取失败',
            'dns2': '获取失败',
            'manufacturer': '获取失败',
            'model': '获取失败'
        }


def get_interface_config(interface_name):
    """获取指定接口的当前配置（原始输出）"""
    try:
        cmd = ['netsh', 'interface', 'ip', 'show', 'config', f'name={interface_name}']
        output = run_netsh_command(cmd)
        
        if not output:
            return None
            
        return output
        
    except Exception as e:
        print(f"获取接口配置失败: {e}")
        return None 