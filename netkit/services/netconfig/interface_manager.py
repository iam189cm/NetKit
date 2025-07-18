"""
网卡选择管理模块 - 高性能异步版本
负责网卡列表的获取、过滤、格式化显示等功能
使用异步数据管理器提供更好的性能和用户体验
"""

import re
from typing import List, Tuple, Optional
from .async_manager import get_async_manager
from .interface_info import get_network_info_service


def get_network_interfaces(show_all: bool = False) -> List[str]:
    """获取网络接口列表
    
    Args:
        show_all (bool): 是否显示所有网卡（包括虚拟网卡），默认False只显示物理网卡
    
    Returns:
        list: 网络接口名称列表
    """
    try:
        async_manager = get_async_manager()
        adapters = async_manager.get_all_adapters_fast(show_all)
        
        # 提取接口名称
        interfaces = [adapter.connection_id for adapter in adapters]
        return interfaces
        
    except Exception as e:
        print(f"获取网络接口失败: {e}")
        return []


def get_network_connection_status(interface_name: str) -> str:
    """获取网络连接状态"""
    try:
        async_manager = get_async_manager()
        
        # 先尝试从缓存获取
        if interface_name in async_manager.adapters_cache:
            adapter = async_manager.adapters_cache[interface_name]
            return adapter.connection_status
        
        # 如果缓存中没有，使用同步方式获取
        service = get_network_info_service()
        basic_info = service.get_interface_basic_info(interface_name)
        return basic_info.get('connection_status', '未知')
        
    except Exception as e:
        print(f"获取网络连接状态失败: {e}")
        return "未知"


def get_interface_ip_address(interface_name: str) -> str:
    """获取网卡IP地址（快速获取）"""
    try:
        async_manager = get_async_manager()
        
        # 先尝试从缓存获取
        if interface_name in async_manager.adapters_cache:
            adapter = async_manager.adapters_cache[interface_name]
            return adapter.ip_addresses[0] if adapter.ip_addresses else "未配置"
        
        # 如果缓存中没有，使用同步方式获取
        service = get_network_info_service()
        ip_config = service.get_interface_ip_config(interface_name)
        return ip_config.get('ip', '未配置')
        
    except Exception as e:
        print(f"获取IP地址失败: {e}")
        return "未配置"


def format_interface_display_name(interface_name: str) -> str:
    """格式化网卡显示名称: [状态] 网卡名称 (制造商 型号) - IP地址"""
    try:
        # 获取连接状态
        status = get_network_connection_status(interface_name)
        
        # 获取IP地址
        ip = get_interface_ip_address(interface_name)
        
        # 获取硬件信息
        hardware_info = get_network_adapter_hardware_info(interface_name)
        manufacturer = hardware_info.get('manufacturer', '未知')
        model = hardware_info.get('model', '未知')
        
        # 格式化硬件信息
        if manufacturer != '未知' and model != '未知':
            # 简化制造商名称
            if 'Intel' in manufacturer:
                manufacturer = 'Intel'
            elif 'Realtek' in manufacturer:
                manufacturer = 'Realtek'
            elif 'Broadcom' in manufacturer:
                manufacturer = 'Broadcom'
            elif 'Qualcomm' in manufacturer:
                manufacturer = 'Qualcomm'
            elif 'VMware' in manufacturer:
                manufacturer = 'VMware'
            elif 'Microsoft' in manufacturer:
                manufacturer = 'Microsoft'
            elif 'Shanghai Best Oray' in manufacturer:
                manufacturer = 'Oray'
            elif 'WireGuard' in manufacturer:
                manufacturer = 'WireGuard'
            elif len(manufacturer) > 15:  # 如果制造商名称太长，截取前15个字符
                manufacturer = manufacturer[:15] + '...'
            
            # 简化型号显示
            if 'Wi-Fi 6E' in model:
                model = model.replace('Wi-Fi 6E ', '')
            elif 'Wi-Fi 6' in model:
                model = model.replace('Wi-Fi 6 ', '')
            elif 'Ethernet' in model:
                model = model.replace('Ethernet ', '')
            elif 'Virtual' in model:
                model = 'Virtual'
            elif 'Userspace Tunnel' in model:
                model = 'Tunnel'
            
            hardware_part = f" ({manufacturer} {model})"
        elif manufacturer != '未知':
            # 只有制造商信息时也进行简化
            if 'Intel' in manufacturer:
                manufacturer = 'Intel'
            elif 'Realtek' in manufacturer:
                manufacturer = 'Realtek'
            elif 'Broadcom' in manufacturer:
                manufacturer = 'Broadcom'
            elif len(manufacturer) > 15:
                manufacturer = manufacturer[:15] + '...'
            hardware_part = f" ({manufacturer})"
        else:
            hardware_part = ""
        
        # 格式化显示名称
        display_name = f"[{status}] {interface_name}{hardware_part} - {ip}"
        
        return display_name
        
    except Exception as e:
        # 如果获取信息失败，返回简单格式
        return f"[未知] {interface_name} - 未知"


def get_network_interfaces_with_details(show_all: bool = False) -> List[Tuple[str, str]]:
    """获取带详细信息的网络接口列表
    
    Args:
        show_all (bool): 是否显示所有网卡（包括虚拟网卡），默认False只显示物理网卡
    
    Returns:
        list: 包含元组的列表，每个元组包含 (显示名称, 原始接口名称)
    """
    try:
        async_manager = get_async_manager()
        return async_manager.get_all_adapters_with_details(show_all)
        
    except Exception as e:
        print(f"获取详细网络接口失败: {e}")
        return []


def extract_interface_name_from_display(display_name: str) -> str:
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


def get_adapter_detailed_info(interface_name: str) -> Optional[dict]:
    """获取网卡的详细技术信息"""
    try:
        async_manager = get_async_manager()
        
        # 先尝试从缓存获取
        if interface_name in async_manager.adapters_cache:
            adapter = async_manager.adapters_cache[interface_name]
            return {
                'name': adapter.name,
                'description': adapter.description,
                'manufacturer': adapter.manufacturer,
                'mac_address': adapter.mac_address,
                'speed': adapter.speed,
                'adapter_type': adapter.adapter_type,
                'connection_status': adapter.connection_status,
                'physical_adapter': adapter.physical_adapter,
                'dhcp_enabled': adapter.dhcp_enabled,
                'ip_addresses': adapter.ip_addresses,
                'subnet_masks': adapter.subnet_masks,
                'gateways': adapter.gateways,
                'dns_servers': adapter.dns_servers
            }
        
        # 如果缓存中没有，使用同步方式获取
        service = get_network_info_service()
        info = service.get_network_card_info(interface_name)
        
        return {
            'name': info.get('name', '未知'),
            'description': info.get('description', '未知'),
            'manufacturer': info.get('manufacturer', '未知'),
            'mac_address': info.get('mac', '未知'),
            'speed': info.get('speed', '未知'),
            'adapter_type': '未知',
            'connection_status': info.get('status', '未知'),
            'physical_adapter': None,
            'dhcp_enabled': None,
            'ip_addresses': [info.get('ip', '未配置')] if info.get('ip') != '未配置' else [],
            'subnet_masks': [info.get('mask', '未配置')] if info.get('mask') != '未配置' else [],
            'gateways': [info.get('gateway', '未配置')] if info.get('gateway') != '未配置' else [],
            'dns_servers': [dns for dns in [info.get('dns1'), info.get('dns2')] if dns and dns != '未配置']
        }
        
    except Exception as e:
        print(f"获取网卡详细信息失败: {e}")
        return None


def extract_interface_name_from_display(display_name: str) -> str:
    """从显示名称中提取原始接口名称"""
    if not display_name:
        return ""
    
    # 格式: [状态] 网卡名称 (制造商 型号) - IP地址
    # 提取网卡名称部分
    try:
        # 移除状态部分 [状态] 
        if display_name.startswith('[') and ']' in display_name:
            display_name = display_name.split(']', 1)[1].strip()
        
        # 移除IP地址部分 - IP地址
        if ' - ' in display_name:
            display_name = display_name.split(' - ')[0].strip()
        
        # 移除硬件信息部分 (制造商 型号)
        if ' (' in display_name and display_name.endswith(')'):
            display_name = display_name.split(' (')[0].strip()
        
        return display_name
        
    except Exception as e:
        print(f"提取接口名称失败: {e}")
        return display_name


# 兼容性函数 - 保持原有的接口不变
def is_physical_adapter(adapter) -> bool:
    """检查是否为物理网络适配器（兼容性函数）"""
    if not adapter:
        return False
    
    # 如果是NetworkAdapterInfo对象
    if hasattr(adapter, 'physical_adapter'):
        return adapter.physical_adapter
    
    # 如果是WMI适配器对象，使用原有逻辑
    if hasattr(adapter, 'PhysicalAdapter') and adapter.PhysicalAdapter is not None:
        return bool(adapter.PhysicalAdapter)
    
    # 通过描述判断
    name = (getattr(adapter, 'Name', '') or "").lower()
    description = (getattr(adapter, 'Description', '') or "").lower()
    
    # 虚拟适配器关键字
    virtual_keywords = [
        'virtual', 'vmware', 'virtualbox', 'hyper-v', 'vethernet',
        'tap', 'tunnel', 'loopback', 'teredo', 'isatap', 'bluetooth',
        'vpn', 'ppp', 'wan miniport', 'microsoft wi-fi direct',
        'microsoft hosted network', 'microsoft isatap', 'microsoft teredo',
        'virtualbox host-only', 'vmware virtual ethernet', 'microsoft kernel debug',
        'wfp', 'qos', 'filter', 'miniport'
    ]
    
    # 检查是否包含虚拟适配器关键字
    for keyword in virtual_keywords:
        if keyword in name or keyword in description:
            return False
    
    # 检查是否包含物理网卡的关键词
    physical_keywords = [
        'intel', 'realtek', 'broadcom', 'qualcomm', 'atheros',
        'marvell', 'nvidia', 'mediatek', 'ethernet', 'wi-fi', 'wireless'
    ]
    
    for keyword in physical_keywords:
        if keyword in description:
            return True
    
    # 如果无法确定，默认认为是物理适配器
    return True


def get_connection_status_text(status_code) -> str:
    """获取连接状态文本（兼容性函数）"""
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


# 异步管理器相关的新接口
def start_preload():
    """启动预加载"""
    async_manager = get_async_manager()
    async_manager.start_preload()


def refresh_all_adapters():
    """刷新所有网卡信息"""
    async_manager = get_async_manager()
    async_manager.refresh_all_adapters()


def refresh_adapter(interface_name: str):
    """刷新特定网卡信息"""
    async_manager = get_async_manager()
    async_manager.refresh_adapter(interface_name)


def get_cache_info():
    """获取缓存信息"""
    async_manager = get_async_manager()
    return async_manager.get_cache_info()


def is_cache_valid(max_age_seconds=300) -> bool:
    """检查缓存是否有效"""
    async_manager = get_async_manager()
    return async_manager.is_cache_valid(max_age_seconds)


def clear_cache():
    """清空缓存"""
    async_manager = get_async_manager()
    async_manager.clear_cache() 