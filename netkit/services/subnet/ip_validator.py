"""
IP地址验证器
负责验证IP地址的合法性，包括特殊地址检查
"""

import ipaddress
from typing import Tuple, Optional


class IPValidator:
    """IP地址验证器"""
    
    @staticmethod
    def validate_ip_address(ip_str: str) -> Tuple[bool, Optional[str]]:
        """
        验证IP地址的合法性
        
        Args:
            ip_str: IP地址字符串
            
        Returns:
            (是否有效, 错误消息)
        """
        try:
            # 基本格式验证
            ip = ipaddress.ip_address(ip_str)
            
            # 检查特殊地址
            if str(ip) == '0.0.0.0':
                return False, "0.0.0.0 是保留地址，请输入有效的IP地址"
                
            if str(ip) == '255.255.255.255':
                return False, "255.255.255.255 是广播地址，请输入有效的IP地址"
                
            if ip.is_loopback:
                return False, f"{ip} 是回环地址，请输入有效的IP地址"
                
            if ip.is_multicast:
                return False, f"{ip} 是组播地址，请输入有效的IP地址"
                
            # 240.0.0.0/4 保留地址段（除了255.255.255.255）
            if int(ip) >= 4026531840 and int(ip) < 4294967295:  # 240.0.0.0 - 255.255.255.254
                return False, f"{ip} 是保留地址，请输入有效的IP地址"
                
            return True, None
            
        except ValueError:
            return False, "无效的IP地址格式"
    
    @staticmethod
    def validate_subnet_mask(mask_str: str) -> Tuple[bool, Optional[str]]:
        """
        验证子网掩码的合法性
        
        Args:
            mask_str: 子网掩码字符串
            
        Returns:
            (是否有效, 错误消息)
        """
        try:
            # 解析子网掩码
            octets = mask_str.split('.')
            if len(octets) != 4:
                return False, "子网掩码必须是点分十进制格式"
                
            # 转换为二进制
            binary_str = ''
            for octet in octets:
                try:
                    value = int(octet)
                    if value < 0 or value > 255:
                        return False, "子网掩码每个字节必须在0-255之间"
                    binary_str += format(value, '08b')
                except ValueError:
                    return False, "子网掩码必须是数字"
            
            # 检查是否是连续的1后跟连续的0
            if '01' in binary_str:
                return False, "无效的子网掩码，掩码位必须连续"
                
            # 检查是否全0或全1
            ones_count = binary_str.count('1')
            if ones_count == 0:
                return False, "子网掩码不能为0.0.0.0"
            if ones_count == 32:
                return False, "子网掩码不能为255.255.255.255"
                
            return True, None
            
        except Exception:
            return False, "无效的子网掩码格式"
    
    @staticmethod
    def validate_cidr(cidr_bits: int) -> Tuple[bool, Optional[str]]:
        """
        验证CIDR位数的合法性
        
        Args:
            cidr_bits: CIDR位数
            
        Returns:
            (是否有效, 错误消息)
        """
        if not isinstance(cidr_bits, int):
            return False, "CIDR位数必须是整数"
            
        if cidr_bits < 1 or cidr_bits > 32:
            return False, "CIDR位数必须在1-32之间"
            
        return True, None
    
    @staticmethod
    def validate_network_with_mask(ip_str: str, mask_str: str) -> Tuple[bool, Optional[str]]:
        """
        验证IP地址和子网掩码的组合是否有效
        
        Args:
            ip_str: IP地址字符串
            mask_str: 子网掩码字符串
            
        Returns:
            (是否有效, 错误消息)
        """
        # 先验证IP地址
        valid, error = IPValidator.validate_ip_address(ip_str)
        if not valid:
            return False, error
            
        # 再验证子网掩码
        valid, error = IPValidator.validate_subnet_mask(mask_str)
        if not valid:
            return False, error
            
        return True, None
    
    @staticmethod
    def validate_cidr_notation(cidr_str: str) -> Tuple[bool, Optional[str], Optional[Tuple[str, int]]]:
        """
        验证CIDR表示法
        
        Args:
            cidr_str: CIDR字符串，如 "192.168.1.0/24"
            
        Returns:
            (是否有效, 错误消息, (IP地址, CIDR位数))
        """
        try:
            parts = cidr_str.split('/')
            if len(parts) != 2:
                return False, "CIDR格式错误，应为 IP地址/掩码位数", None
                
            ip_str = parts[0]
            
            # 验证IP地址
            valid, error = IPValidator.validate_ip_address(ip_str)
            if not valid:
                return False, error, None
                
            # 验证CIDR位数
            try:
                cidr_bits = int(parts[1])
            except ValueError:
                return False, "CIDR位数必须是数字", None
                
            valid, error = IPValidator.validate_cidr(cidr_bits)
            if not valid:
                return False, error, None
                
            return True, None, (ip_str, cidr_bits)
            
        except Exception as e:
            return False, f"CIDR格式错误: {str(e)}", None