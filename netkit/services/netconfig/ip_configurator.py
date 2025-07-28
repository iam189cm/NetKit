"""
IP配置模块
负责IP地址配置的应用、验证、冲突检查等功能
"""

import subprocess
import re
import ipaddress
import wmi
import pythoncom
import threading
from .interface_manager import get_network_interfaces
from .interface_info import get_interface_config


def apply_profile(interface_name, ip_mode, dns_mode, ip_config, dns_config):
    """
    应用IP配置文件 - 支持四种配置组合模式
    
    Args:
        interface_name: 网卡接口名称（NetConnectionID，如"以太网"）
        ip_mode: IP配置模式 ('auto' | 'manual')
        dns_mode: DNS配置模式 ('auto' | 'manual')
        ip_config: IP配置参数 {'ip': '', 'mask': '', 'gateway': ''}
        dns_config: DNS配置参数 {'dns1': '', 'dns2': ''}
    
    Returns:
        dict: {'success': bool, 'message': str, 'error': str}
    """
    try:
        # 初始化COM
        pythoncom.CoInitialize()
        
        # 连接到WMI
        c = wmi.WMI()
        
        # 通过NetConnectionID查找网络适配器
        target_adapter = None
        for adapter in c.Win32_NetworkAdapter():
            if adapter.NetConnectionID == interface_name:
                target_adapter = adapter
                break
        
        if not target_adapter:
            return {
                'success': False,
                'error': f"找不到网络适配器连接: {interface_name}"
            }
        
        # 通过适配器Index查找对应的配置
        adapter_config = None
        for config in c.Win32_NetworkAdapterConfiguration():
            if config.Index == target_adapter.Index:
                adapter_config = config
                break
        
        if not adapter_config:
            return {
                'success': False,
                'error': f"找不到网络适配器配置: {interface_name} (Index: {target_adapter.Index})"
            }
        
        # 根据四种组合模式应用配置
        if ip_mode == "auto" and dns_mode == "auto":
            # 组合1: 自动IP + 自动DNS (纯DHCP)
            return _apply_full_dhcp(adapter_config)
            
        elif ip_mode == "auto" and dns_mode == "manual":
            # 组合2: 自动IP + 手动DNS (DHCP IP + 静态DNS)
            return _apply_dhcp_with_static_dns(adapter_config, dns_config)
            
        elif ip_mode == "manual" and dns_mode == "auto":
            # 组合3: 手动IP + 自动DNS (静态IP + DHCP DNS)
            return _apply_static_ip_with_dhcp_dns(adapter_config, ip_config)
            
        elif ip_mode == "manual" and dns_mode == "manual":
            # 组合4: 手动IP + 手动DNS (纯静态)
            return _apply_full_static(adapter_config, ip_config, dns_config)
            
        else:
            return {
                'success': False,
                'error': f"无效的配置模式: ip_mode={ip_mode}, dns_mode={dns_mode}"
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f"WMI配置失败: {str(e)}"
        }
    finally:
        # 清理COM
        try:
            pythoncom.CoUninitialize()
        except:
            pass


def _apply_full_dhcp_with_netsh_fallback(adapter_config, interface_name):
    """使用netsh作为备选方案的DHCP配置方法"""
    try:
        # 方案1：尝试使用netsh命令直接设置DHCP（最可靠的方法）
        import subprocess
        
        # 使用netsh设置为DHCP，这会自动清除所有静态设置包括网关
        cmd = f'netsh interface ipv4 set address name="{interface_name}" source=dhcp'
        
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            encoding='utf-8',
            timeout=30
        )
        
        if result.returncode == 0:
            # netsh成功，继续设置DNS
            dns_cmd = f'netsh interface ipv4 set dns name="{interface_name}" source=dhcp'
            dns_result = subprocess.run(
                dns_cmd,
                shell=True,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=30
            )
            
            if dns_result.returncode == 0:
                return {
                    'success': True,
                    'message': "使用netsh命令成功启用完全DHCP模式，已彻底清除静态网关设置"
                }
            else:
                return {
                    'success': False,
                    'error': f"netsh设置DNS失败: {dns_result.stderr}"
                }
        else:
            # netsh失败，回退到WMI方法
            return None  # 表示需要回退
            
    except Exception as e:
        # netsh方法失败，回退到WMI方法
        return None


def _apply_full_dhcp(adapter_config):
    """组合1: 纯DHCP模式 (自动IP + 自动DNS) - 多重方案确保成功"""
    try:
        # 获取接口名称用于netsh命令
        interface_name = None
        try:
            # 尝试获取接口名称
            pythoncom.CoInitialize()
            c = wmi.WMI()
            
            for adapter in c.Win32_NetworkAdapter():
                if adapter.Index == adapter_config.Index:
                    interface_name = adapter.NetConnectionID
                    break
        except Exception:
            pass
        finally:
            try:
                pythoncom.CoUninitialize()
            except:
                pass
        
        # 方案1：如果有接口名称，尝试使用netsh命令（最可靠）
        if interface_name:
            netsh_result = _apply_full_dhcp_with_netsh_fallback(adapter_config, interface_name)
            if netsh_result is not None:
                return netsh_result
        
        # 方案2：netsh失败或无接口名称，使用强化的WMI方法
        # 步骤1：先释放DHCP租约（如果存在）
        try:
            adapter_config.ReleaseDHCPLease()
        except Exception:
            pass
        
        # 步骤2：临时启用DHCP来清除静态设置
        adapter_config.EnableDHCP()
        
        # 步骤3：获取当前的IP信息（用于临时静态设置）
        import time
        time.sleep(2)
        
        # 重新获取adapter配置以获取DHCP分配的IP
        try:
            pythoncom.CoInitialize()
            c = wmi.WMI()
            
            # 重新获取配置
            for config in c.Win32_NetworkAdapterConfiguration():
                if config.Index == adapter_config.Index:
                    current_adapter_config = config
                    break
            else:
                current_adapter_config = adapter_config
            
            # 获取当前IP信息
            if current_adapter_config.IPAddress and len(current_adapter_config.IPAddress) > 0:
                current_ip = current_adapter_config.IPAddress[0]
                current_mask = current_adapter_config.IPSubnet[0] if current_adapter_config.IPSubnet else "255.255.255.0"
                
                # 步骤4：临时设置为静态IP（不设置网关）
                current_adapter_config.EnableStatic([current_ip], [current_mask])
                time.sleep(1)
                
                # 步骤5：最后设置为DHCP（这样可以确保网关被清除）
                result_ip = current_adapter_config.EnableDHCP()
                if result_ip[0] != 0:
                    return {
                        'success': False,
                        'error': f"最终启用DHCP失败，错误代码: {result_ip[0]}"
                    }
            else:
                # 如果没有IP信息，直接使用原始方法
                result_ip = adapter_config.EnableDHCP()
                if result_ip[0] != 0:
                    return {
                        'success': False,
                        'error': f"启用DHCP失败，错误代码: {result_ip[0]}"
                    }
                
        except Exception as e:
            # 如果复杂方法失败，回退到简单方法
            result_ip = adapter_config.EnableDHCP()
            if result_ip[0] != 0:
                return {
                    'success': False,
                    'error': f"启用DHCP失败，错误代码: {result_ip[0]}"
                }
        finally:
            try:
                pythoncom.CoUninitialize()
            except:
                pass
        
        # 步骤6：设置DNS为自动获取
        result_dns = adapter_config.SetDNSServerSearchOrder()
        if result_dns[0] != 0:
            return {
                'success': False,
                'error': f"设置DNS为自动获取失败，错误代码: {result_dns[0]}"
            }
        
        return {
            'success': True,
            'message': "使用WMI强力方法启用完全DHCP模式，已尽力清除静态网关设置"
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"应用完全DHCP配置时出错: {str(e)}"
        }


def _apply_dhcp_with_static_dns(adapter_config, dns_config):
    """组合2: DHCP IP + 静态DNS - 多重方案确保成功"""
    try:
        # 获取接口名称用于netsh命令
        interface_name = None
        try:
            pythoncom.CoInitialize()
            c = wmi.WMI()
            
            for adapter in c.Win32_NetworkAdapter():
                if adapter.Index == adapter_config.Index:
                    interface_name = adapter.NetConnectionID
                    break
        except Exception:
            pass
        finally:
            try:
                pythoncom.CoUninitialize()
            except:
                pass
        
        # 方案1：如果有接口名称，尝试使用netsh命令设置DHCP IP
        if interface_name:
            try:
                import subprocess
                
                # 使用netsh设置为DHCP IP，这会清除静态网关
                cmd = f'netsh interface ipv4 set address name="{interface_name}" source=dhcp'
                
                result = subprocess.run(
                    cmd, 
                    shell=True, 
                    capture_output=True, 
                    text=True, 
                    encoding='utf-8',
                    timeout=30
                )
                
                if result.returncode == 0:
                    # netsh IP设置成功，继续设置静态DNS
                    dns_servers = []
                    if dns_config.get('dns1'):
                        dns_servers.append(dns_config['dns1'])
                    if dns_config.get('dns2'):
                        dns_servers.append(dns_config['dns2'])
                    
                    if dns_servers:
                        result_dns = adapter_config.SetDNSServerSearchOrder(dns_servers)
                        if result_dns[0] != 0:
                            return {
                                'success': False,
                                'error': f"设置DNS服务器失败，错误代码: {result_dns[0]}"
                            }
                    
                    return {
                        'success': True,
                        'message': f"使用netsh命令成功启用DHCP IP + 静态DNS模式，DNS服务器: {', '.join(dns_servers)}，已彻底清除静态网关设置"
                    }
            except Exception:
                # netsh方法失败，继续使用WMI方法
                pass
        
        # 方案2：netsh失败或无接口名称，使用WMI方法
        # 步骤1：先释放DHCP租约（如果存在）
        try:
            adapter_config.ReleaseDHCPLease()
        except Exception:
            pass
        
        # 步骤2：启用DHCP获取IP、子网掩码和网关
        result_ip = adapter_config.EnableDHCP()
        if result_ip[0] != 0:
            return {
                'success': False,
                'error': f"启用DHCP失败，错误代码: {result_ip[0]}"
            }
        
        # 步骤3：设置静态DNS服务器
        dns_servers = []
        if dns_config.get('dns1'):
            dns_servers.append(dns_config['dns1'])
        if dns_config.get('dns2'):
            dns_servers.append(dns_config['dns2'])
        
        if dns_servers:
            result_dns = adapter_config.SetDNSServerSearchOrder(dns_servers)
            if result_dns[0] != 0:
                return {
                    'success': False,
                    'error': f"设置DNS服务器失败，错误代码: {result_dns[0]}"
                }
        
        return {
            'success': True,
            'message': f"使用WMI方法启用DHCP IP + 静态DNS模式，DNS服务器: {', '.join(dns_servers)}，已尽力清除静态网关设置"
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"应用DHCP IP + 静态DNS配置时出错: {str(e)}"
        }


def _apply_static_ip_with_dhcp_dns(adapter_config, ip_config):
    """组合3: 静态IP + DHCP DNS - 使用专家推荐的方法清除网关"""
    try:
        # 获取当前配置信息，以便保存需要的IP设置
        current_ip = ip_config.get('ip', '')
        current_mask = ip_config.get('mask', '')
        current_gateway = ip_config.get('gateway', '')
        
        if not current_ip or not current_mask:
            return {
                'success': False,
                'error': "IP地址和子网掩码不能为空"
            }
        
        # 步骤1：先启用DHCP（这会清除所有静态设置，包括旧的网关）
        result_dhcp = adapter_config.EnableDHCP()
        if result_dhcp[0] != 0:
            return {
                'success': False,
                'error': f"清除网关设置失败，错误代码: {result_dhcp[0]}"
            }
        
        # 等待一小段时间让DHCP设置生效
        import time
        time.sleep(1)
        
        # 步骤2：立即设置为静态IP（只设置IP、掩码和网关，不影响DNS）
        if current_gateway:
            # 如果有网关，设置完整的静态IP配置
            result_static = adapter_config.EnableStatic([current_ip], [current_mask])
            if result_static[0] != 0:
                return {
                    'success': False,
                    'error': f"设置静态IP失败，错误代码: {result_static[0]}"
                }
            
            # 设置网关
            result_gateway = adapter_config.SetGateways([current_gateway])
            if result_gateway[0] != 0:
                return {
                    'success': False,
                    'error': f"设置网关失败，错误代码: {result_gateway[0]}"
                }
        else:
            # 如果没有网关，只设置IP和掩码
            result_static = adapter_config.EnableStatic([current_ip], [current_mask])
            if result_static[0] != 0:
                return {
                    'success': False,
                    'error': f"设置静态IP失败，错误代码: {result_static[0]}"
                }
        
        # 步骤3：设置DNS为自动获取（DHCP DNS）
        result_dns = adapter_config.SetDNSServerSearchOrder()
        if result_dns[0] != 0:
            return {
                'success': False,
                'error': f"设置DNS为自动获取失败，错误代码: {result_dns[0]}"
            }
        
        gateway_msg = f"，网关: {current_gateway}" if current_gateway else "，无网关"
        return {
            'success': True,
            'message': f"已成功启用静态IP + DHCP DNS模式，IP: {current_ip}，掩码: {current_mask}{gateway_msg}"
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"应用静态IP + DHCP DNS配置时出错: {str(e)}"
        }


def _apply_full_static(adapter_config, ip_config, dns_config):
    """组合4: 纯静态模式 (静态IP + 静态DNS)"""
    try:
        # 设置静态IP
        ip_addresses = [ip_config['ip']]
        subnet_masks = [ip_config['mask']]
        gateways = [ip_config['gateway']] if ip_config['gateway'] else []
        
        result_ip = adapter_config.EnableStatic(ip_addresses, subnet_masks)
        if result_ip[0] != 0:
            return {
                'success': False,
                'error': f"设置静态IP失败，错误代码: {result_ip[0]}"
            }
        
        # 设置网关
        if gateways:
            result_gateway = adapter_config.SetGateways(gateways)
            if result_gateway[0] != 0:
                return {
                    'success': False,
                    'error': f"设置网关失败，错误代码: {result_gateway[0]}"
                }
        
        # 设置静态DNS
        dns_servers = []
        if dns_config['dns1']:
            dns_servers.append(dns_config['dns1'])
        if dns_config['dns2']:
            dns_servers.append(dns_config['dns2'])
        
        if dns_servers:
            result_dns = adapter_config.SetDNSServerSearchOrder(dns_servers)
            if result_dns[0] != 0:
                return {
                    'success': False,
                    'error': f"设置静态DNS失败，错误代码: {result_dns[0]}"
                }
        else:
            # 如果没有DNS服务器，清空DNS设置
            result_dns = adapter_config.SetDNSServerSearchOrder()
            if result_dns[0] != 0:
                return {
                    'success': False,
                    'error': f"清空DNS设置失败，错误代码: {result_dns[0]}"
                }
        
        gateway_info = f"，网关: {ip_config['gateway']}" if ip_config['gateway'] else "，无网关"
        dns_info = f"，DNS: {', '.join(dns_servers)}" if dns_servers else "，无DNS"
        return {
            'success': True,
            'message': f"已成功启用完全静态模式，IP: {ip_config['ip']}/{ip_config['mask']}{gateway_info}{dns_info}"
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"应用完全静态配置时出错: {str(e)}"
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
        
        warnings = []
        
        # 验证网关地址（如果提供）
        if gateway and gateway.strip():
            try:
                gateway_addr = ipaddress.IPv4Address(gateway)
                
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
            except ValueError:
                return {
                    'valid': False,
                    'error': f"无效的网关地址格式: {gateway}"
                }
        else:
            warnings.append("未设置默认网关，仅适用于局域网内部通信")
        
        # 验证DNS服务器（如果提供）
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