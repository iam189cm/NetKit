"""
网卡信息模块 - 高性能版本
基于WMI查询引擎的高性能网卡信息获取
"""

from typing import Dict, List, Optional
from .wmi_engine import get_wmi_engine, NetworkAdapterInfo
import logging
import time

class NetworkInfoService:
    """网卡信息服务"""
    
    def __init__(self):
        self.wmi_engine = get_wmi_engine()
        self.logger = logging.getLogger(__name__)
    
    def get_network_card_info(self, interface_name: str, force_refresh=False) -> Dict[str, str]:
        """获取网卡完整信息（保持原有接口兼容性）"""
        try:
            adapter_info = self.wmi_engine.get_adapter_info(interface_name, force_refresh)
            if not adapter_info:
                return self._get_default_info(interface_name)
            
            return self._convert_to_legacy_format(adapter_info)
            
        except Exception as e:
            self.logger.error(f"获取网卡信息失败: {e}")
            return self._get_error_info(interface_name)
    
    def get_all_network_cards_info(self, show_all=False, force_refresh=False) -> List[NetworkAdapterInfo]:
        """获取所有网卡信息（新接口）"""
        return self.wmi_engine.get_all_adapters_info(show_all, force_refresh)
    
    def get_network_adapter_hardware_info(self, interface_name: str) -> Dict[str, str]:
        """获取网卡硬件信息（兼容接口）"""
        try:
            adapter_info = self.wmi_engine.get_adapter_info(interface_name)
            if not adapter_info:
                return self._get_default_hardware_info()
            
            return {
                'manufacturer': adapter_info.manufacturer,
                'model': adapter_info.model,
                'full_description': adapter_info.description,
                'speed': adapter_info.speed
            }
            
        except Exception as e:
            self.logger.error(f"获取网卡硬件信息失败: {e}")
            return self._get_error_hardware_info()
    
    def get_interface_basic_info(self, interface_name: str) -> Dict[str, str]:
        """获取网卡基本信息（兼容接口）"""
        try:
            adapter_info = self.wmi_engine.get_adapter_info(interface_name)
            if not adapter_info:
                return {'status': '未知', 'type': '未知'}
            
            return {
                'status': adapter_info.status,
                'type': adapter_info.adapter_type,
                'connection_status': adapter_info.connection_status
            }
            
        except Exception as e:
            self.logger.error(f"获取网卡基本信息失败: {e}")
            return {'status': '获取失败', 'type': '获取失败'}
    
    def get_interface_ip_config(self, interface_name: str) -> Dict[str, str]:
        """获取网卡IP配置信息（兼容接口）"""
        try:
            adapter_info = self.wmi_engine.get_adapter_info(interface_name)
            if not adapter_info:
                return self._get_default_ip_config()
            
            return {
                'ip': adapter_info.ip_addresses[0] if adapter_info.ip_addresses else '未配置',
                'mask': adapter_info.subnet_masks[0] if adapter_info.subnet_masks else '未配置',
                'gateway': adapter_info.gateways[0] if adapter_info.gateways else '未配置',
                'dns1': adapter_info.dns_servers[0] if len(adapter_info.dns_servers) > 0 else '未配置',
                'dns2': adapter_info.dns_servers[1] if len(adapter_info.dns_servers) > 1 else '未配置'
            }
            
        except Exception as e:
            self.logger.error(f"获取网卡IP配置失败: {e}")
            return self._get_error_ip_config()
    
    def get_interface_mac_address(self, interface_name: str) -> str:
        """获取网卡MAC地址（兼容接口）"""
        try:
            adapter_info = self.wmi_engine.get_adapter_info(interface_name)
            if not adapter_info:
                return "未知"
            
            return adapter_info.mac_address
            
        except Exception as e:
            self.logger.error(f"获取MAC地址失败: {e}")
            return "获取失败"
    
    def get_interface_config(self, interface_name: str) -> Optional[str]:
        """获取指定接口的当前配置（兼容接口）"""
        try:
            adapter_info = self.wmi_engine.get_adapter_info(interface_name)
            if not adapter_info:
                return None
            
            # 构建配置信息字符串
            config_lines = [
                f'"{interface_name}" 的配置',
                "",
                f"    DHCP 已启用:                          {'是' if adapter_info.dhcp_enabled else '否'}",
            ]
            
            if adapter_info.ip_addresses:
                config_lines.append(f"    IP 地址:                           {adapter_info.ip_addresses[0]}")
            
            if adapter_info.subnet_masks:
                config_lines.append(f"    子网掩码:                          {adapter_info.subnet_masks[0]}")
            
            if adapter_info.gateways:
                config_lines.append(f"    默认网关:                          {adapter_info.gateways[0]}")
            
            if adapter_info.dns_servers:
                config_lines.append(f"    DNS 服务器:                        {adapter_info.dns_servers[0]}")
                for dns in adapter_info.dns_servers[1:]:
                    config_lines.append(f"                                      {dns}")
            
            return '\n'.join(config_lines)
            
        except Exception as e:
            self.logger.error(f"获取接口配置失败: {e}")
            return None
    
    def _convert_to_legacy_format(self, adapter_info: NetworkAdapterInfo) -> Dict[str, str]:
        """转换为旧版格式以保持兼容性"""
        return {
            'name': adapter_info.connection_id,
            'description': adapter_info.description,
            'status': adapter_info.status,
            'mac': adapter_info.mac_address,
            'speed': adapter_info.speed,
            'ip': adapter_info.ip_addresses[0] if adapter_info.ip_addresses else '未配置',
            'mask': adapter_info.subnet_masks[0] if adapter_info.subnet_masks else '未配置',
            'gateway': adapter_info.gateways[0] if adapter_info.gateways else '未配置',
            'dns1': adapter_info.dns_servers[0] if len(adapter_info.dns_servers) > 0 else '未配置',
            'dns2': adapter_info.dns_servers[1] if len(adapter_info.dns_servers) > 1 else '未配置',
            'manufacturer': adapter_info.manufacturer,
            'model': adapter_info.model
        }
    
    def _get_default_info(self, interface_name: str) -> Dict[str, str]:
        """获取默认信息"""
        return {
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
    
    def _get_error_info(self, interface_name: str) -> Dict[str, str]:
        """获取错误信息"""
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
    
    def _get_default_hardware_info(self) -> Dict[str, str]:
        """获取默认硬件信息"""
        return {
            'manufacturer': '未知',
            'model': '未知',
            'full_description': '未知',
            'speed': '未知'
        }
    
    def _get_error_hardware_info(self) -> Dict[str, str]:
        """获取错误硬件信息"""
        return {
            'manufacturer': '获取失败',
            'model': '获取失败',
            'full_description': '获取失败',
            'speed': '获取失败'
        }
    
    def _get_default_ip_config(self) -> Dict[str, str]:
        """获取默认IP配置"""
        return {
            'ip': '未配置',
            'mask': '未配置',
            'gateway': '未配置',
            'dns1': '未配置',
            'dns2': '未配置'
        }
    
    def _get_error_ip_config(self) -> Dict[str, str]:
        """获取错误IP配置"""
        return {
            'ip': '获取失败',
            'mask': '获取失败',
            'gateway': '获取失败',
            'dns1': '获取失败',
            'dns2': '获取失败'
        }

# 全局服务实例
_network_info_service = None

def get_network_info_service() -> NetworkInfoService:
    """获取网卡信息服务实例"""
    global _network_info_service
    if _network_info_service is None:
        _network_info_service = NetworkInfoService()
    return _network_info_service

# 保持原有接口兼容性
def get_network_card_info(interface_name: str) -> Dict[str, str]:
    """获取网卡信息（兼容接口）"""
    return get_network_info_service().get_network_card_info(interface_name)

def get_network_adapter_hardware_info(interface_name: str) -> Dict[str, str]:
    """获取网卡硬件信息（兼容接口）"""
    return get_network_info_service().get_network_adapter_hardware_info(interface_name)

def get_interface_basic_info(interface_name: str) -> Dict[str, str]:
    """获取网卡基本信息（兼容接口）"""
    return get_network_info_service().get_interface_basic_info(interface_name)

def get_interface_ip_config(interface_name: str) -> Dict[str, str]:
    """获取网卡IP配置信息（兼容接口）"""
    return get_network_info_service().get_interface_ip_config(interface_name)

def get_interface_mac_address(interface_name: str) -> str:
    """获取网卡MAC地址（兼容接口）"""
    return get_network_info_service().get_interface_mac_address(interface_name)

def get_interface_config(interface_name: str) -> Optional[str]:
    """获取指定接口的当前配置（兼容接口）"""
    return get_network_info_service().get_interface_config(interface_name)

# 为了兼容性，保留一些原有的类和函数
class ThreadLocalWMI:
    """线程本地的WMI连接管理器（兼容性保留）"""
    
    @classmethod
    def get_connection(cls):
        """获取当前线程的WMI连接"""
        # 使用新的WMI引擎
        return get_wmi_engine()
    
    @classmethod
    def cleanup(cls):
        """清理当前线程的WMI连接"""
        pass

class NetworkAdapterWMI:
    """网络适配器WMI管理类（兼容性保留）"""
    
    def __init__(self):
        """初始化WMI连接"""
        self.wmi_engine = get_wmi_engine()
    
    def get_all_adapters(self):
        """获取所有网络适配器"""
        try:
            adapters_info = self.wmi_engine.get_all_adapters_info(show_all=True)
            # 转换为兼容格式
            return [self._create_adapter_mock(info) for info in adapters_info]
        except Exception as e:
            print(f"获取网络适配器列表失败: {e}")
            return []
    
    def get_adapter_by_connection_id(self, connection_id: str):
        """根据连接ID获取网络适配器"""
        try:
            adapter_info = self.wmi_engine.get_adapter_info(connection_id)
            if adapter_info:
                return self._create_adapter_mock(adapter_info)
            return None
        except Exception as e:
            print(f"获取网络适配器失败 ({connection_id}): {e}")
            return None
    
    def get_adapter_configuration(self, adapter_index: int):
        """获取网络适配器配置"""
        # 这个方法在新架构中不再需要，因为配置信息已经包含在NetworkAdapterInfo中
        # 但为了兼容性，创建一个模拟对象
        return self._create_config_mock()
    
    def _create_adapter_mock(self, adapter_info: NetworkAdapterInfo):
        """创建适配器模拟对象"""
        class AdapterMock:
            def __init__(self, info):
                self.Name = info.name
                self.NetConnectionID = info.connection_id
                self.Description = info.description
                self.MACAddress = info.mac_address
                self.Manufacturer = info.manufacturer
                self.Speed = info.speed
                self.AdapterType = info.adapter_type
                self.NetConnectionStatus = 2 if info.connection_status == "已连接" else 0
                self.NetEnabled = info.enabled
                self.Index = info.adapter_index
                self.PhysicalAdapter = info.physical_adapter
        
        return AdapterMock(adapter_info)
    
    def _create_config_mock(self):
        """创建配置模拟对象"""
        class ConfigMock:
            def __init__(self):
                self.DHCPEnabled = False
                self.IPAddress = []
                self.IPSubnet = []
                self.DefaultIPGateway = []
                self.DNSServerSearchOrder = []
                self.Index = 0
        
        return ConfigMock()

# 其他兼容性函数
def format_speed(speed) -> str:
    """格式化速度信息（兼容函数）"""
    if not speed or speed == 0:
        return "未知"
    
    try:
        speed_val = int(speed)
        if speed_val >= 1000000000:  # 1 Gbps
            return f"{speed_val // 1000000000} Gbps"
        elif speed_val >= 1000000:  # 1 Mbps
            return f"{speed_val // 1000000} Mbps"
        elif speed_val >= 1000:  # 1 Kbps
            return f"{speed_val // 1000} Kbps"
        else:
            return f"{speed_val} bps"
    except (ValueError, TypeError):
        return "未知"

def format_mac_address(mac_address: str) -> str:
    """格式化MAC地址（兼容函数）"""
    if not mac_address:
        return "未知"
    
    import re
    # 移除所有分隔符
    mac_clean = re.sub(r'[:-]', '', mac_address.upper())
    
    # 重新格式化为 XX-XX-XX-XX-XX-XX
    if len(mac_clean) == 12:
        return '-'.join([mac_clean[i:i+2] for i in range(0, 12, 2)])
    
    return mac_address

def get_connection_status_text(status_code) -> str:
    """获取连接状态文本（兼容函数）"""
    status_map = {
        0: "已断开",
        1: "正在连接",
        2: "已连接",
        3: "正在断开",
        4: "硬件不存在",
        5: "硬件已禁用",
        6: "硬件故障",
        7: "媒体已断开",
        8: "正在验证",
        9: "验证失败",
        10: "验证成功",
        11: "正在获取地址",
        12: "无效地址"
    }
    return status_map.get(status_code, "未知")

def extract_manufacturer_info(description: str) -> Dict[str, str]:
    """从描述中提取制造商和型号信息（兼容函数）"""
    service = get_network_info_service()
    return service.wmi_engine._extract_manufacturer_info(description) 