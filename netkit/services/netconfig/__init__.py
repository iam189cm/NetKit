"""
网络配置相关服务模块

提供网卡管理、信息获取、IP配置等功能的统一接口
"""

# 网卡选择管理相关
from .interface_manager import (
    get_network_interfaces,
    get_network_interfaces_with_details,
    extract_interface_name_from_display,
    format_interface_display_name,
    get_network_connection_status,
    get_interface_ip_address
)

# 网卡信息获取相关
from .interface_info import (
    get_network_card_info,
    get_network_adapter_hardware_info,
    get_interface_config,
    get_interface_mac_address,
    get_interface_basic_info,
    get_interface_ip_config
)

# IP配置相关
from .ip_configurator import (
    apply_profile,
    validate_ip_config,
    check_network_conflict,
    suggest_ip_config
)

# 为了向后兼容，保持原有的导入方式
__all__ = [
    # 网卡管理
    'get_network_interfaces',
    'get_network_interfaces_with_details',
    'extract_interface_name_from_display',
    'format_interface_display_name',
    'get_network_connection_status',
    'get_interface_ip_address',
    
    # 网卡信息
    'get_network_card_info',
    'get_network_adapter_hardware_info',
    'get_interface_config',
    'get_interface_mac_address',
    'get_interface_basic_info',
    'get_interface_ip_config',
    
    # IP配置
    'apply_profile',
    'validate_ip_config',
    'check_network_conflict',
    'suggest_ip_config'
] 