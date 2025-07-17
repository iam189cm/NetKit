#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据集
包含各种网络配置、系统命令输出和测试场景
"""

# 有效的IP配置数据
VALID_IP_CONFIGS = [
    {
        "name": "家庭网络",
        "ip": "192.168.1.100",
        "mask": "255.255.255.0",
        "gateway": "192.168.1.1",
        "dns": "8.8.8.8,8.8.4.4"
    },
    {
        "name": "办公网络",
        "ip": "192.168.0.50",
        "mask": "255.255.255.0",
        "gateway": "192.168.0.1",
        "dns": "114.114.114.114,223.5.5.5"
    },
    {
        "name": "企业网络",
        "ip": "10.0.1.100",
        "mask": "255.255.0.0",
        "gateway": "10.0.1.1",
        "dns": "8.8.8.8"
    },
    {
        "name": "小型网络",
        "ip": "192.168.1.10",
        "mask": "255.255.255.240",
        "gateway": "192.168.1.1",
        "dns": "8.8.8.8,8.8.4.4"
    }
]

# 无效的IP配置数据
INVALID_IP_CONFIGS = [
    {
        "name": "IP地址无效",
        "ip": "256.256.256.256",
        "mask": "255.255.255.0",
        "gateway": "192.168.1.1",
        "dns": "8.8.8.8",
        "error_type": "invalid_ip"
    },
    {
        "name": "网关不在同一网段",
        "ip": "192.168.1.100",
        "mask": "255.255.255.0",
        "gateway": "192.168.2.1",
        "dns": "8.8.8.8",
        "error_type": "gateway_not_in_network"
    },
    {
        "name": "IP是网络地址",
        "ip": "192.168.1.0",
        "mask": "255.255.255.0",
        "gateway": "192.168.1.1",
        "dns": "8.8.8.8",
        "error_type": "network_address"
    },
    {
        "name": "IP是广播地址",
        "ip": "192.168.1.255",
        "mask": "255.255.255.0",
        "gateway": "192.168.1.1",
        "dns": "8.8.8.8",
        "error_type": "broadcast_address"
    },
    {
        "name": "子网掩码无效",
        "ip": "192.168.1.100",
        "mask": "255.255.255.1",
        "gateway": "192.168.1.1",
        "dns": "8.8.8.8",
        "error_type": "invalid_mask"
    }
]

# 模拟的网络接口数据
MOCK_NETWORK_INTERFACES = [
    "以太网",
    "Wi-Fi",
    "本地连接",
    "无线网络连接",
    "蓝牙网络连接"
]

# 模拟的netsh interface show interface输出
MOCK_NETSH_INTERFACE_OUTPUT = """

Admin State    State          Type             Interface Name
-------------------------------------------------------------------------
已启用          已连接          专用             以太网
已启用          已断开连接      专用             Wi-Fi
已禁用          已断开连接      专用             蓝牙网络连接
已启用          已连接          环回             Loopback Pseudo-Interface 1
"""

# 模拟的网卡详细信息
MOCK_NETWORK_CARD_INFO = {
    "以太网": {
        "name": "以太网",
        "description": "Realtek PCIe GBE Family Controller",
        "status": "已启用",
        "mac": "00:11:22:33:44:55",
        "speed": "1 Gbps",
        "ip": "192.168.1.100",
        "mask": "255.255.255.0",
        "gateway": "192.168.1.1",
        "dns1": "8.8.8.8",
        "dns2": "8.8.4.4"
    },
    "Wi-Fi": {
        "name": "Wi-Fi",
        "description": "Intel(R) Wi-Fi 6 AX200 160MHz",
        "status": "已断开连接",
        "mac": "AA:BB:CC:DD:EE:FF",
        "speed": "未知",
        "ip": "未配置",
        "mask": "未配置",
        "gateway": "未配置",
        "dns1": "未配置",
        "dns2": "未配置"
    }
}

# 模拟的netsh interface ip show config输出
MOCK_NETSH_IP_CONFIG_OUTPUT = """
"以太网" 的配置

    DHCP 已启用:                          否
    IP 地址:                           192.168.1.100
    子网前缀:                          192.168.1.0/24 (mask 255.255.255.0)
    默认网关:                          192.168.1.1
    网关跃点数:                        0
    InterfaceMetric:                   25
    DNS 服务器:                        8.8.8.8
                                      8.8.4.4
    由 DHCP 配置的 DNS:                 否
    注册连接的后缀:                    否
    WINS 服务器:                       无
"""

# 模拟的getmac命令输出
MOCK_GETMAC_OUTPUT = """
"主机名","网络适配器","物理地址","传输名称"
"DESKTOP-TEST","以太网","00-11-22-33-44-55","\\Device\\Tcpip_{12345678-1234-1234-1234-123456789012}"
"DESKTOP-TEST","Wi-Fi","AA-BB-CC-DD-EE-FF","\\Device\\Tcpip_{87654321-4321-4321-4321-210987654321}"
"""

# 性能测试数据
PERFORMANCE_TEST_DATA = {
    "network_interfaces_count": [1, 5, 10, 20, 50],
    "ip_validation_iterations": [100, 500, 1000, 5000],
    "concurrent_operations": [1, 5, 10, 20],
    "large_dns_lists": [
        "8.8.8.8",
        "8.8.8.8,8.8.4.4",
        "8.8.8.8,8.8.4.4,114.114.114.114,223.5.5.5",
        ",".join([f"8.8.8.{i}" for i in range(1, 11)])
    ]
}

# 边界测试数据
BOUNDARY_TEST_DATA = {
    "ip_addresses": [
        "0.0.0.0",
        "127.0.0.1",
        "255.255.255.255",
        "192.168.1.1",
        "10.0.0.1",
        "172.16.0.1"
    ],
    "subnet_masks": [
        "0.0.0.0",
        "128.0.0.0",
        "255.0.0.0",
        "255.255.0.0",
        "255.255.255.0",
        "255.255.255.255"
    ],
    "long_interface_names": [
        "以太网",
        "非常长的网络接口名称测试",
        "Network Interface with Very Long Name for Testing",
        "网络接口名称包含特殊字符!@#$%^&*()",
        "A" * 100  # 100字符长度
    ]
}

# 错误场景测试数据
ERROR_SCENARIOS = {
    "netsh_failures": [
        {
            "command": "netsh interface show interface",
            "returncode": 1,
            "stderr": "系统找不到指定的文件。"
        },
        {
            "command": "netsh interface ip set address",
            "returncode": 1,
            "stderr": "参数不正确。"
        }
    ],
    "permission_errors": [
        {
            "operation": "apply_profile",
            "error": "拒绝访问。"
        },
        {
            "operation": "get_network_interfaces",
            "error": "需要管理员权限。"
        }
    ],
    "network_errors": [
        {
            "scenario": "网络接口不存在",
            "interface": "不存在的网卡",
            "error": "找不到指定的网络接口。"
        },
        {
            "scenario": "网络接口已禁用",
            "interface": "已禁用的网卡",
            "error": "网络接口已禁用。"
        }
    ]
}

# GUI测试数据
GUI_TEST_DATA = {
    "input_sequences": [
        {
            "name": "正常IP配置输入",
            "steps": [
                ("ip_entry", "192.168.1.100"),
                ("mask_entry", "255.255.255.0"),
                ("gateway_entry", "192.168.1.1"),
                ("dns1_entry", "8.8.8.8"),
                ("dns2_entry", "8.8.4.4")
            ]
        },
        {
            "name": "DHCP配置",
            "steps": [
                ("dhcp_check", True)
            ]
        },
        {
            "name": "清空所有字段",
            "steps": [
                ("ip_entry", ""),
                ("mask_entry", ""),
                ("gateway_entry", ""),
                ("dns1_entry", ""),
                ("dns2_entry", "")
            ]
        }
    ],
    "user_interactions": [
        "click_refresh_button",
        "select_interface",
        "toggle_dhcp",
        "apply_configuration",
        "clear_status"
    ]
}

# Windows版本特定测试数据
WINDOWS_VERSION_DATA = {
    "windows_10": {
        "netsh_output_format": "traditional",
        "encoding": "gbk",
        "interface_names": ["以太网", "Wi-Fi", "本地连接"]
    },
    "windows_11": {
        "netsh_output_format": "modern",
        "encoding": "utf-8",
        "interface_names": ["以太网", "Wi-Fi", "WLAN"]
    }
}

# 压力测试数据
STRESS_TEST_DATA = {
    "concurrent_users": [1, 5, 10, 20],
    "operation_counts": [100, 500, 1000],
    "memory_limits": [100, 200, 500],  # MB
    "timeout_scenarios": [1, 5, 10, 30]  # seconds
} 