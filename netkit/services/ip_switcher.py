
import subprocess
import re
import json
import os
from pathlib import Path


def get_network_interfaces():
    """获取网络接口列表"""
    try:
        cmd = ['netsh', 'interface', 'show', 'interface']
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode != 0:
            return []
            
        interfaces = []
        lines = result.stdout.split('\n')
        
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
                            interfaces.append(interface_name)
                        
        return interfaces
        
    except Exception as e:
        print(f"获取网络接口失败: {e}")
        return []


def get_network_card_info(interface_name):
    """获取网卡详细信息"""
    try:
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
            'dns2': '未配置'
        }
        
        # 获取接口基本信息
        cmd_interface = ['netsh', 'interface', 'show', 'interface', f'name={interface_name}']
        result_interface = subprocess.run(cmd_interface, capture_output=True, text=True, encoding='gbk', errors='ignore')
        
        if result_interface.returncode == 0 and result_interface.stdout:
            lines = result_interface.stdout.split('\n')
            for line in lines:
                if '管理状态' in line or 'Administrative state' in line:
                    info['status'] = line.split(':')[-1].strip()
                elif '类型' in line or 'Type' in line:
                    info['description'] = line.split(':')[-1].strip()
        
        # 获取物理地址
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
                            info['mac'] = mac
                    break
        
        # 获取IP配置信息
        cmd_ip = ['netsh', 'interface', 'ip', 'show', 'config', f'name={interface_name}']
        result_ip = subprocess.run(cmd_ip, capture_output=True, text=True, encoding='gbk', errors='ignore')
        
        if result_ip.returncode == 0 and result_ip.stdout:
            lines = result_ip.stdout.split('\n')
            dns_servers = []
            
            for line in lines:
                line = line.strip()
                if 'IP Address' in line or 'IP 地址' in line:
                    ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                    if ip_match:
                        info['ip'] = ip_match.group(1)
                elif 'Subnet Prefix' in line or '子网前缀' in line:
                    # 提取子网掩码
                    mask_match = re.search(r'/(\d+)', line)
                    if mask_match:
                        prefix = int(mask_match.group(1))
                        # 转换CIDR为点分十进制
                        mask_int = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
                        info['mask'] = f"{(mask_int >> 24) & 0xFF}.{(mask_int >> 16) & 0xFF}.{(mask_int >> 8) & 0xFF}.{mask_int & 0xFF}"
                elif 'Default Gateway' in line or '默认网关' in line:
                    gateway_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                    if gateway_match:
                        info['gateway'] = gateway_match.group(1)
                elif 'DNS Servers' in line or 'DNS 服务器' in line:
                    dns_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                    if dns_match:
                        dns_servers.append(dns_match.group(1))
                elif re.match(r'^\s*\d+\.\d+\.\d+\.\d+\s*$', line):
                    # 额外的DNS服务器行
                    dns_servers.append(line.strip())
            
            # 设置DNS服务器
            if len(dns_servers) > 0:
                info['dns1'] = dns_servers[0]
            if len(dns_servers) > 1:
                info['dns2'] = dns_servers[1]
        
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
            'dns2': '获取失败'
        }


def apply_profile(interface_name, ip, mask, gateway, dns=None, dhcp=False):
    """应用IP配置文件"""
    try:
        if dhcp:
            # DHCP模式
            cmd_dhcp = [
                'netsh', 'interface', 'ip', 'set', 'address',
                f'name={interface_name}', 'source=dhcp'
            ]
            
            result_dhcp = subprocess.run(cmd_dhcp, capture_output=True, text=True, encoding='utf-8')
            
            if result_dhcp.returncode != 0:
                return {
                    'success': False,
                    'error': f"启用DHCP失败: {result_dhcp.stderr}"
                }
            
            # 设置DNS为自动获取
            cmd_dns_dhcp = [
                'netsh', 'interface', 'ip', 'set', 'dns',
                f'name={interface_name}', 'source=dhcp'
            ]
            
            result_dns_dhcp = subprocess.run(cmd_dns_dhcp, capture_output=True, text=True, encoding='utf-8')
            
            if result_dns_dhcp.returncode != 0:
                return {
                    'success': False,
                    'error': f"设置DNS为DHCP失败: {result_dns_dhcp.stderr}"
                }
            
            return {
                'success': True,
                'message': f"DHCP配置已成功应用到接口 '{interface_name}'"
            }
        else:
            # 静态IP模式
            cmd_ip = [
                'netsh', 'interface', 'ip', 'set', 'address',
                f'name={interface_name}', 'source=static',
                f'addr={ip}', f'mask={mask}', f'gateway={gateway}'
            ]
            
            result_ip = subprocess.run(cmd_ip, capture_output=True, text=True, encoding='utf-8')
            
            if result_ip.returncode != 0:
                return {
                    'success': False,
                    'error': f"设置IP地址失败: {result_ip.stderr}"
                }
                
            # 设置DNS（如果提供）
            if dns:
                dns_servers = [d.strip() for d in dns.split(',') if d.strip()]
                for i, dns_server in enumerate(dns_servers):
                    if i == 0:
                        # 设置主DNS
                        cmd_dns = [
                            'netsh', 'interface', 'ip', 'set', 'dns',
                            f'name={interface_name}', 'static', dns_server
                        ]
                    else:
                        # 添加备用DNS
                        cmd_dns = [
                            'netsh', 'interface', 'ip', 'add', 'dns',
                            f'name={interface_name}', dns_server, 'index=2'
                        ]
                    
                    result_dns = subprocess.run(cmd_dns, capture_output=True, text=True, encoding='utf-8')
                    
                    if result_dns.returncode != 0:
                        return {
                            'success': False,
                            'error': f"设置DNS失败: {result_dns.stderr}"
                        }
                    
            return {
                'success': True,
                'message': f"静态IP配置已成功应用到接口 '{interface_name}'"
            }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"执行命令时出错: {str(e)}"
        }


def get_interface_config(interface_name):
    """获取指定接口的当前配置"""
    try:
        cmd = ['netsh', 'interface', 'ip', 'show', 'config', f'name={interface_name}']
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode != 0:
            return None
            
        return result.stdout
        
    except Exception as e:
        print(f"获取接口配置失败: {e}")
        return None


def get_config_dir():
    """获取配置文件目录"""
    config_dir = Path.home() / '.netkit_py'
    config_dir.mkdir(exist_ok=True)
    return config_dir


def save_profile(name, interface, ip, mask, gateway, dns=""):
    """保存IP配置文件"""
    try:
        config_dir = get_config_dir()
        profiles_file = config_dir / 'ip_profiles.json'
        
        # 读取现有配置
        profiles = {}
        if profiles_file.exists():
            with open(profiles_file, 'r', encoding='utf-8') as f:
                profiles = json.load(f)
        
        # 添加新配置
        profiles[name] = {
            'interface': interface,
            'ip': ip,
            'mask': mask,
            'gateway': gateway,
            'dns': dns
        }
        
        # 保存配置
        with open(profiles_file, 'w', encoding='utf-8') as f:
            json.dump(profiles, f, indent=2, ensure_ascii=False)
            
        return {'success': True, 'message': f"配置文件 '{name}' 已保存"}
        
    except Exception as e:
        return {'success': False, 'error': f"保存配置失败: {str(e)}"}


def load_profiles():
    """加载所有IP配置文件"""
    try:
        config_dir = get_config_dir()
        profiles_file = config_dir / 'ip_profiles.json'
        
        if not profiles_file.exists():
            return {}
            
        with open(profiles_file, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        return {}


def delete_profile(name):
    """删除IP配置文件"""
    try:
        config_dir = get_config_dir()
        profiles_file = config_dir / 'ip_profiles.json'
        
        if not profiles_file.exists():
            return {'success': False, 'error': '配置文件不存在'}
            
        with open(profiles_file, 'r', encoding='utf-8') as f:
            profiles = json.load(f)
            
        if name not in profiles:
            return {'success': False, 'error': f"配置 '{name}' 不存在"}
            
        del profiles[name]
        
        with open(profiles_file, 'w', encoding='utf-8') as f:
            json.dump(profiles, f, indent=2, ensure_ascii=False)
            
        return {'success': True, 'message': f"配置 '{name}' 已删除"}
        
    except Exception as e:
        return {'success': False, 'error': f"删除配置失败: {str(e)}"}


def validate_ip_config(ip, mask, gateway, dns=""):
    """验证IP配置的有效性"""
    import ipaddress
    
    try:
        # 验证IP地址
        ip_addr = ipaddress.IPv4Address(ip)
        
        # 验证子网掩码
        mask_addr = ipaddress.IPv4Address(mask)
        mask_int = int(mask_addr)
        
        # 验证子网掩码是否有效（必须是连续的1）
        if mask_int != 0:
            ones_count = bin(mask_int).count('1')
            expected_mask = (0xFFFFFFFF << (32 - ones_count)) & 0xFFFFFFFF
            if mask_int != expected_mask:
                return {
                    'valid': False,
                    'error': f"无效的子网掩码: {mask}，必须是连续的1"
                }
        
        # 验证网关地址
        gateway_addr = ipaddress.IPv4Address(gateway)
        
        # 创建网络对象进行进一步验证
        try:
            network = ipaddress.IPv4Network(f"{ip}/{mask}", strict=False)
        except Exception as e:
            return {
                'valid': False,
                'error': f"无法创建网络: {str(e)}"
            }
        
        # 检查IP地址是否在网络范围内
        if ip_addr not in network:
            return {
                'valid': False,
                'error': f"IP地址 {ip} 不在网络 {network} 范围内"
            }
        
        # 检查IP地址是否是网络地址或广播地址
        if ip_addr == network.network_address:
            return {
                'valid': False,
                'error': f"IP地址 {ip} 是网络地址，不能用作主机地址"
            }
        
        if ip_addr == network.broadcast_address:
            return {
                'valid': False,
                'error': f"IP地址 {ip} 是广播地址，不能用作主机地址"
            }
        
        # 检查网关是否在同一网络内
        if gateway_addr not in network:
            return {
                'valid': False,
                'error': f"网关地址 {gateway} 不在网络 {network} 范围内"
            }
        
        # 检查网关是否是网络地址或广播地址
        if gateway_addr == network.network_address:
            return {
                'valid': False,
                'error': f"网关地址 {gateway} 是网络地址，不能用作网关"
            }
        
        if gateway_addr == network.broadcast_address:
            return {
                'valid': False,
                'error': f"网关地址 {gateway} 是广播地址，不能用作网关"
            }
        
        # 检查IP和网关是否相同
        if ip_addr == gateway_addr:
            return {
                'valid': False,
                'error': "IP地址和网关地址不能相同"
            }
        
        # 验证DNS（如果提供）
        if dns:
            dns_servers = [d.strip() for d in dns.split(',') if d.strip()]
            for i, dns_server in enumerate(dns_servers, 1):
                try:
                    dns_addr = ipaddress.IPv4Address(dns_server)
                    
                    # 检查DNS服务器地址的有效性
                    if dns_addr.is_loopback:
                        return {
                            'valid': False,
                            'error': f"DNS服务器 {i} ({dns_server}) 不能是环回地址"
                        }
                    
                    if dns_addr.is_multicast:
                        return {
                            'valid': False,
                            'error': f"DNS服务器 {i} ({dns_server}) 不能是多播地址"
                        }
                    
                    if dns_addr.is_reserved:
                        return {
                            'valid': False,
                            'error': f"DNS服务器 {i} ({dns_server}) 是保留地址"
                        }
                        
                except Exception as e:
                    return {
                        'valid': False,
                        'error': f"DNS服务器 {i} ({dns_server}) 格式无效: {str(e)}"
                    }
        
        # 检查常见的配置错误
        warnings = []
        
        # 检查是否使用了私有地址
        if not ip_addr.is_private and not ip_addr.is_global:
            warnings.append(f"IP地址 {ip} 既不是私有地址也不是公网地址")
        
        # 检查子网掩码长度
        prefix_length = network.prefixlen
        if prefix_length < 8:
            warnings.append(f"子网掩码 /{prefix_length} 可能过于宽泛")
        elif prefix_length > 30:
            warnings.append(f"子网掩码 /{prefix_length} 可能过于狭窄，可用主机数很少")
        
        # 检查常用的DNS服务器
        if dns:
            dns_servers = [d.strip() for d in dns.split(',') if d.strip()]
            common_dns = ['8.8.8.8', '8.8.4.4', '114.114.114.114', '223.5.5.5']
            if not any(dns_server in common_dns for dns_server in dns_servers):
                warnings.append("建议使用知名的公共DNS服务器")
        
        result = {'valid': True}
        if warnings:
            result['warnings'] = warnings
            
        return result
        
    except Exception as e:
        return {
            'valid': False,
            'error': f"验证过程出错: {str(e)}"
        }


def check_network_conflict(ip, mask, gateway):
    """检查网络配置冲突"""
    try:
        # 获取当前网络接口配置
        interfaces = get_network_interfaces()
        conflicts = []
        
        for interface in interfaces:
            config = get_interface_config(interface)
            if config:
                # 解析当前配置（简单实现）
                lines = config.split('\n')
                current_ip = None
                current_mask = None
                current_gateway = None
                
                for line in lines:
                    if 'IP Address' in line or 'IP 地址' in line:
                        # 提取IP地址
                        import re
                        ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                        if ip_match:
                            current_ip = ip_match.group(1)
                    elif 'Subnet Mask' in line or '子网掩码' in line:
                        # 提取子网掩码
                        mask_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                        if mask_match:
                            current_mask = mask_match.group(1)
                    elif 'Default Gateway' in line or '默认网关' in line:
                        # 提取默认网关
                        gateway_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                        if gateway_match:
                            current_gateway = gateway_match.group(1)
                
                # 检查IP冲突
                if current_ip and current_ip == ip:
                    conflicts.append(f"IP地址 {ip} 已在接口 {interface} 上使用")
                
                # 检查网关冲突
                if current_gateway and current_gateway == gateway:
                    conflicts.append(f"网关地址 {gateway} 已在接口 {interface} 上使用")
        
        return {
            'conflicts': conflicts,
            'has_conflict': len(conflicts) > 0
        }
        
    except Exception as e:
        return {
            'conflicts': [f"检查网络冲突时出错: {str(e)}"],
            'has_conflict': False
        }


def suggest_ip_config(interface_name):
    """为指定接口建议IP配置"""
    try:
        # 获取接口当前配置
        config = get_interface_config(interface_name)
        if not config:
            return {
                'success': False,
                'error': f"无法获取接口 {interface_name} 的配置"
            }
        
        suggestions = []
        
        # 常用的私有网络配置
        common_configs = [
            {
                'name': '家庭网络(192.168.1.x)',
                'ip': '192.168.1.100',
                'mask': '255.255.255.0',
                'gateway': '192.168.1.1',
                'dns': '8.8.8.8,114.114.114.114'
            },
            {
                'name': '办公网络(192.168.0.x)',
                'ip': '192.168.0.100',
                'mask': '255.255.255.0',
                'gateway': '192.168.0.1',
                'dns': '8.8.8.8,223.5.5.5'
            },
            {
                'name': '企业网络(10.0.0.x)',
                'ip': '10.0.0.100',
                'mask': '255.255.255.0',
                'gateway': '10.0.0.1',
                'dns': '8.8.8.8,8.8.4.4'
            }
        ]
        
        # 验证每个建议配置
        for config in common_configs:
            validation = validate_ip_config(
                config['ip'], 
                config['mask'], 
                config['gateway'], 
                config['dns']
            )
            
            if validation['valid']:
                suggestions.append(config)
        
        return {
            'success': True,
            'suggestions': suggestions
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"生成配置建议时出错: {str(e)}"
        }
