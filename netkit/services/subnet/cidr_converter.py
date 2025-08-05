"""
CIDR格式转换器
负责CIDR和子网掩码之间的相互转换
"""

from typing import Tuple, Optional


class CIDRConverter:
    """CIDR格式转换器"""
    
    # CIDR到子网掩码的映射表
    CIDR_TO_MASK = {
        0: '0.0.0.0',
        1: '128.0.0.0',
        2: '192.0.0.0',
        3: '224.0.0.0',
        4: '240.0.0.0',
        5: '248.0.0.0',
        6: '252.0.0.0',
        7: '254.0.0.0',
        8: '255.0.0.0',
        9: '255.128.0.0',
        10: '255.192.0.0',
        11: '255.224.0.0',
        12: '255.240.0.0',
        13: '255.248.0.0',
        14: '255.252.0.0',
        15: '255.254.0.0',
        16: '255.255.0.0',
        17: '255.255.128.0',
        18: '255.255.192.0',
        19: '255.255.224.0',
        20: '255.255.240.0',
        21: '255.255.248.0',
        22: '255.255.252.0',
        23: '255.255.254.0',
        24: '255.255.255.0',
        25: '255.255.255.128',
        26: '255.255.255.192',
        27: '255.255.255.224',
        28: '255.255.255.240',
        29: '255.255.255.248',
        30: '255.255.255.252',
        31: '255.255.255.254',
        32: '255.255.255.255'
    }
    
    @staticmethod
    def cidr_to_mask(cidr_bits: int) -> Optional[str]:
        """
        将CIDR位数转换为子网掩码
        
        Args:
            cidr_bits: CIDR位数
            
        Returns:
            子网掩码字符串，如果无效返回None
        """
        return CIDRConverter.CIDR_TO_MASK.get(cidr_bits)
    
    @staticmethod
    def mask_to_cidr(mask_str: str) -> Optional[int]:
        """
        将子网掩码转换为CIDR位数
        
        Args:
            mask_str: 子网掩码字符串
            
        Returns:
            CIDR位数，如果无效返回None
        """
        # 反向查找
        for cidr, mask in CIDRConverter.CIDR_TO_MASK.items():
            if mask == mask_str:
                return cidr
        return None
    
    @staticmethod
    def mask_to_binary(mask_str: str) -> str:
        """
        将子网掩码转换为二进制表示
        
        Args:
            mask_str: 子网掩码字符串
            
        Returns:
            二进制字符串，用点分隔
        """
        try:
            octets = mask_str.split('.')
            binary_parts = []
            for octet in octets:
                value = int(octet)
                binary_parts.append(format(value, '08b'))
            return '.'.join(binary_parts)
        except:
            return ""
    
    @staticmethod
    def parse_cidr_input(input_str: str) -> Tuple[Optional[str], Optional[int]]:
        """
        解析CIDR输入，支持多种格式
        
        Args:
            input_str: 输入字符串，可以是 "/24" 或 "24"
            
        Returns:
            (子网掩码, CIDR位数)
        """
        input_str = input_str.strip()
        
        # 如果是CIDR格式
        if input_str.startswith('/'):
            input_str = input_str[1:]
        
        try:
            cidr_bits = int(input_str)
            if 0 <= cidr_bits <= 32:
                mask = CIDRConverter.cidr_to_mask(cidr_bits)
                return mask, cidr_bits
        except ValueError:
            pass
            
        return None, None
    
    @staticmethod
    def calculate_host_bits(cidr_bits: int) -> int:
        """
        计算主机位数
        
        Args:
            cidr_bits: CIDR位数（网络位）
            
        Returns:
            主机位数
        """
        return 32 - cidr_bits
    
    @staticmethod
    def calculate_max_hosts(cidr_bits: int) -> int:
        """
        计算最大可用主机数
        
        Args:
            cidr_bits: CIDR位数
            
        Returns:
            最大可用主机数
        """
        host_bits = CIDRConverter.calculate_host_bits(cidr_bits)
        
        # 特殊处理 /31 和 /32
        if cidr_bits == 31:
            return 2  # RFC 3021 允许/31用于点对点链路
        elif cidr_bits == 32:
            return 1  # 单个主机
        else:
            # 减去网络地址和广播地址
            return (2 ** host_bits) - 2