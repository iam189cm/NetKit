"""
子网计算器核心功能
负责子网计算和子网划分
"""

import ipaddress
from typing import Dict, List, Optional, Tuple
from .ip_validator import IPValidator
from .cidr_converter import CIDRConverter


class SubnetCalculator:
    """子网计算器"""
    
    def __init__(self):
        self.validator = IPValidator()
        self.converter = CIDRConverter()
    
    def calculate_subnet_info(self, ip_str: str, mask_or_cidr: str) -> Dict[str, str]:
        """
        计算子网信息
        
        Args:
            ip_str: IP地址字符串
            mask_or_cidr: 子网掩码或CIDR位数
            
        Returns:
            包含子网信息的字典
        """
        try:
            # 判断是CIDR格式还是子网掩码格式
            if '/' in mask_or_cidr or mask_or_cidr.isdigit() or mask_or_cidr.startswith('/'):
                # CIDR格式
                if mask_or_cidr.startswith('/'):
                    cidr_bits = int(mask_or_cidr[1:])
                else:
                    cidr_bits = int(mask_or_cidr)
                subnet_mask = self.converter.cidr_to_mask(cidr_bits)
            else:
                # 子网掩码格式
                subnet_mask = mask_or_cidr
                cidr_bits = self.converter.mask_to_cidr(subnet_mask)
            
            # 创建网络对象
            network = ipaddress.IPv4Network(f"{ip_str}/{cidr_bits}", strict=False)
            
            # 计算各种信息
            result = {
                '网络地址': str(network.network_address),
                '广播地址': str(network.broadcast_address),
                '子网掩码': subnet_mask,
                'CIDR表示': f"/{cidr_bits}",
                '可用主机范围': self._get_host_range(network),
                '可用主机数': str(self._get_usable_hosts_count(network)),
                '网络位/主机位': f"{cidr_bits}位 / {32-cidr_bits}位",
                'IP地址类型': self._get_ip_type(network),
                '二进制掩码': self.converter.mask_to_binary(subnet_mask)
            }
            
            return result
            
        except Exception as e:
            raise ValueError(f"计算失败: {str(e)}")
    
    def divide_subnet(self, ip_str: str, mask_or_cidr: str, 
                     divide_by: str, value: int) -> List[Dict[str, str]]:
        """
        子网划分
        
        Args:
            ip_str: IP地址字符串
            mask_or_cidr: 子网掩码或CIDR位数
            divide_by: 划分方式 ('subnets' 或 'hosts')
            value: 子网数量或每个子网的主机数
            
        Returns:
            子网列表
        """
        try:
            # 判断是CIDR格式还是子网掩码格式
            if '/' in mask_or_cidr or mask_or_cidr.isdigit() or mask_or_cidr.startswith('/'):
                # CIDR格式
                if mask_or_cidr.startswith('/'):
                    cidr_bits = int(mask_or_cidr[1:])
                else:
                    cidr_bits = int(mask_or_cidr)
            else:
                # 子网掩码格式
                cidr_bits = self.converter.mask_to_cidr(mask_or_cidr)
            
            # 创建网络对象
            network = ipaddress.IPv4Network(f"{ip_str}/{cidr_bits}", strict=False)
            
            if divide_by == 'subnets':
                # 按子网数量划分
                subnets = self._divide_by_subnet_count(network, value)
            else:  # divide_by == 'hosts'
                # 按主机数量划分
                subnets = self._divide_by_host_count(network, value)
            
            # 格式化结果
            result = []
            for i, subnet in enumerate(subnets, 1):
                result.append({
                    '序号': str(i),
                    '子网地址': f"{subnet.network_address}/{subnet.prefixlen}",
                    '可用主机范围': self._get_host_range(subnet),
                    '主机数': str(self._get_usable_hosts_count(subnet))
                })
            
            return result
            
        except Exception as e:
            raise ValueError(f"子网划分失败: {str(e)}")
    
    def _divide_by_subnet_count(self, network: ipaddress.IPv4Network, 
                               subnet_count: int) -> List[ipaddress.IPv4Network]:
        """按子网数量划分"""
        # 计算需要的额外位数
        import math
        extra_bits = math.ceil(math.log2(subnet_count))
        
        # 检查是否可以划分
        new_prefix = network.prefixlen + extra_bits
        if new_prefix > 30:  # 至少保留2位主机位
            raise ValueError(f"无法将 /{network.prefixlen} 网络划分为 {subnet_count} 个子网")
        
        # 执行划分
        subnets = list(network.subnets(new_prefix=new_prefix))
        return subnets[:subnet_count]
    
    def _divide_by_host_count(self, network: ipaddress.IPv4Network, 
                             hosts_per_subnet: int) -> List[ipaddress.IPv4Network]:
        """按主机数量划分"""
        # 计算需要的主机位数
        import math
        # 需要额外2个地址（网络地址和广播地址）
        required_addresses = hosts_per_subnet + 2
        host_bits = math.ceil(math.log2(required_addresses))
        
        # 计算新的前缀长度
        new_prefix = 32 - host_bits
        
        # 检查是否可以划分
        if new_prefix <= network.prefixlen:
            raise ValueError(f"每个子网需要 {hosts_per_subnet} 个主机，超出了原网络容量")
        
        # 执行划分
        subnets = list(network.subnets(new_prefix=new_prefix))
        return subnets
    
    def _get_host_range(self, network: ipaddress.IPv4Network) -> str:
        """获取可用主机范围"""
        hosts = list(network.hosts())
        if not hosts:
            return "无可用主机"
        
        if len(hosts) == 1:
            return str(hosts[0])
        
        return f"{hosts[0]} - {hosts[-1]}"
    
    def _get_usable_hosts_count(self, network: ipaddress.IPv4Network) -> int:
        """获取可用主机数"""
        # 特殊处理 /31 和 /32
        if network.prefixlen == 31:
            return 2
        elif network.prefixlen == 32:
            return 1
        else:
            return network.num_addresses - 2
    
    def _get_ip_type(self, network: ipaddress.IPv4Network) -> str:
        """获取IP地址类型"""
        ip = network.network_address
        
        # 检查是否是私有地址
        if ip.is_private:
            # 判断具体的私有地址范围
            if ip in ipaddress.IPv4Network('10.0.0.0/8'):
                return "私有IP地址 (RFC1918 - A类)"
            elif ip in ipaddress.IPv4Network('172.16.0.0/12'):
                return "私有IP地址 (RFC1918 - B类)"
            elif ip in ipaddress.IPv4Network('192.168.0.0/16'):
                return "私有IP地址 (RFC1918 - C类)"
            else:
                return "私有IP地址"
        
        # 判断传统分类
        first_octet = int(str(ip).split('.')[0])
        if 1 <= first_octet <= 126:
            return "公网IP地址 (A类)"
        elif 128 <= first_octet <= 191:
            return "公网IP地址 (B类)"
        elif 192 <= first_octet <= 223:
            return "公网IP地址 (C类)"
        elif 224 <= first_octet <= 239:
            return "组播地址 (D类)"
        else:
            return "保留地址 (E类)"