"""
IP配置模块
负责IP地址配置的应用、验证、冲突检查等功能
"""

import subprocess
import re
import ipaddress
from .interface_manager import get_network_interfaces
from .interface_info import get_interface_config


def apply_profile(interface_name, ip, mask, gateway, dns=None, dhcp=False):
    """应用IP配置文件"""
    try:
        if dhcp:
            # DHCP模式
            cmd_dhcp = [
                'netsh', 'interface', 'ip', 'set', 'address',
                f'name={interface_name}', 'source=dhcp'
            ]
            
            result_dhcp = subprocess.run(cmd_dhcp, capture_output=True, text=True, encoding='gbk', errors='ignore')
            
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
            
            result_dns_dhcp = subprocess.run(cmd_dns_dhcp, capture_output=True, text=True, encoding='gbk', errors='ignore')
            
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
            
            result_ip = subprocess.run(cmd_ip, capture_output=True, text=True, encoding='gbk', errors='ignore')
            
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
                    
                    result_dns = subprocess.run(cmd_dns, capture_output=True, text=True, encoding='gbk', errors='ignore')
                    
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
            'error': f"应用配置时发生异常: {str(e)}"
        }


def validate_ip_config(ip, mask, gateway, dns=""):
    """验证IP配置的有效性"""
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
        
        # 验证DNS服务器（如果提供）
        warnings = []
        if dns:
            dns_servers = [d.strip() for d in dns.split(',') if d.strip()]
            for dns_server in dns_servers:
                try:
                    ipaddress.IPv4Address(dns_server)
                except Exception:
                    return {
                        'valid': False,
                        'error': f"无效的DNS服务器地址: {dns_server}"
                    }
        
        # 检查是否是私有网络
        if ip_addr.is_private:
            warnings.append("使用私有IP地址")
        
        # 检查是否是常见的网络配置
        if str(network.network_address) == '192.168.1.0' and network.prefixlen == 24:
            warnings.append("使用常见的家庭网络配置")
        
        return {
            'valid': True,
            'warnings': warnings,
            'message': "IP配置验证通过"
        }
        
    except ValueError as e:
        return {
            'valid': False,
            'error': f"IP地址格式错误: {str(e)}"
        }
    except Exception as e:
        return {
            'valid': False,
            'error': f"验证配置时发生异常: {str(e)}"
        }


def check_network_conflict(ip, mask, gateway):
    """检查网络配置冲突"""
    try:
        # 获取当前网络接口配置（包括虚拟网卡，用于冲突检查）
        interfaces = get_network_interfaces(show_all=True)
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
            'has_conflict': True
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