"""
网卡信息模块
负责获取网卡的硬件信息、详细配置信息等
"""

import subprocess
import re


def get_network_adapter_hardware_info(interface_name):
    """获取网卡硬件信息（制造商、型号等）"""
    try:
        # 使用WMIC获取网卡硬件信息
        cmd = ['wmic', 'nic', 'where', f'NetConnectionID="{interface_name}"', 
               'get', 'Name,Manufacturer,Description,PhysicalAdapter', '/format:csv']
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='gbk', errors='ignore')
        
        if result.returncode == 0 and result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.strip() and not line.startswith('Node'):
                    parts = line.split(',')
                    if len(parts) >= 5:
                        manufacturer = parts[2].strip() if parts[2].strip() else '未知'
                        description = parts[1].strip() if parts[1].strip() else '未知'
                        name = parts[3].strip() if parts[3].strip() else '未知'
                        
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
                            'full_description': description
                        }
        
        return {
            'manufacturer': '未知',
            'model': '未知',
            'full_description': '未知'
        }
        
    except Exception as e:
        return {
            'manufacturer': '未知',
            'model': '未知',
            'full_description': '未知'
        }


def get_interface_mac_address(interface_name):
    """获取网卡MAC地址"""
    try:
        cmd_mac = ['getmac', '/fo', 'csv', '/v']
        result_mac = subprocess.run(cmd_mac, capture_output=True, text=True, encoding='gbk', errors='ignore')
        
        if result_mac.returncode == 0 and result_mac.stdout:
            lines = result_mac.stdout.split('\n')
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
        cmd_interface = ['netsh', 'interface', 'show', 'interface', f'name={interface_name}']
        result_interface = subprocess.run(cmd_interface, capture_output=True, text=True, encoding='gbk', errors='ignore')
        
        info = {
            'status': '未知',
            'type': '未知'
        }
        
        if result_interface.returncode == 0 and result_interface.stdout:
            lines = result_interface.stdout.split('\n')
            for line in lines:
                if '管理状态' in line or 'Administrative state' in line:
                    info['status'] = line.split(':')[-1].strip()
                elif '类型' in line or 'Type' in line:
                    info['type'] = line.split(':')[-1].strip()
        
        return info
        
    except Exception as e:
        return {
            'status': '获取失败',
            'type': '获取失败'
        }


def get_interface_ip_config(interface_name):
    """获取网卡IP配置信息"""
    try:
        cmd_ip = ['netsh', 'interface', 'ip', 'show', 'config', f'name={interface_name}']
        result_ip = subprocess.run(cmd_ip, capture_output=True, text=True, encoding='gbk', errors='ignore')
        
        config = {
            'ip': '未配置',
            'mask': '未配置',
            'gateway': '未配置',
            'dns1': '未配置',
            'dns2': '未配置'
        }
        
        if result_ip.returncode == 0 and result_ip.stdout:
            lines = result_ip.stdout.split('\n')
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
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode != 0:
            return None
            
        return result.stdout
        
    except Exception as e:
        print(f"获取接口配置失败: {e}")
        return None 