"""
IP地址范围解析模块

支持多种IP地址格式的解析：
- 单个IP地址：192.168.1.1
- IP地址范围：192.168.1.1-192.168.1.100
- CIDR网络：192.168.1.0/24
- 主机名：www.example.com
"""

import ipaddress


def parse_ip_range(ip_range_str):
    """
    解析IP范围字符串，返回IP地址列表
    
    Args:
        ip_range_str (str): IP范围字符串
        
    Returns:
        list: IP地址列表
        
    Raises:
        ValueError: 当IP范围格式无效时
        
    Examples:
        >>> parse_ip_range("192.168.1.1")
        ['192.168.1.1']
        
        >>> parse_ip_range("192.168.1.1-192.168.1.3")
        ['192.168.1.1', '192.168.1.2', '192.168.1.3']
        
        >>> parse_ip_range("192.168.1.0/30")
        ['192.168.1.1', '192.168.1.2']
    """
    ips = []
    ip_range_str = ip_range_str.strip()
    
    try:
        # 检查是否是CIDR格式 (如 192.168.1.0/24)
        if '/' in ip_range_str:
            network = ipaddress.IPv4Network(ip_range_str, strict=False)
            ips = [str(ip) for ip in network.hosts()]
        
        # 检查是否是范围格式 (如 192.168.1.1-192.168.1.100)
        elif '-' in ip_range_str:
            start_ip, end_ip = ip_range_str.split('-', 1)
            start_ip = start_ip.strip()
            end_ip = end_ip.strip()
            
            # 验证IP地址格式
            start_addr = ipaddress.IPv4Address(start_ip)
            end_addr = ipaddress.IPv4Address(end_ip)
            
            if start_addr > end_addr:
                raise ValueError("起始IP地址不能大于结束IP地址")
            
            # 生成IP范围
            current = start_addr
            while current <= end_addr:
                ips.append(str(current))
                current += 1
        
        # 单个IP地址或主机名
        else:
            # 尝试验证是否为IP地址
            try:
                ipaddress.IPv4Address(ip_range_str)
                ips = [ip_range_str]
            except:
                # 如果不是IP地址，可能是主机名
                ips = [ip_range_str]
    
    except Exception as e:
        raise ValueError(f"无效的IP范围格式: {str(e)}")
    
    return ips


def validate_ip_address(ip_str):
    """
    验证IP地址格式是否正确
    
    Args:
        ip_str (str): IP地址字符串
        
    Returns:
        bool: 是否为有效的IP地址
    """
    try:
        ipaddress.IPv4Address(ip_str.strip())
        return True
    except:
        return False


def get_network_info(ip_range_str):
    """
    获取网络范围信息
    
    Args:
        ip_range_str (str): IP范围字符串
        
    Returns:
        dict: 包含网络信息的字典
    """
    try:
        ips = parse_ip_range(ip_range_str)
        
        info = {
            'input': ip_range_str,
            'total_hosts': len(ips),
            'first_ip': ips[0] if ips else None,
            'last_ip': ips[-1] if ips else None,
            'is_single_host': len(ips) == 1,
            'is_range': '-' in ip_range_str,
            'is_cidr': '/' in ip_range_str
        }
        
        # 如果是CIDR格式，添加网络信息
        if '/' in ip_range_str:
            try:
                network = ipaddress.IPv4Network(ip_range_str, strict=False)
                info.update({
                    'network_address': str(network.network_address),
                    'broadcast_address': str(network.broadcast_address),
                    'netmask': str(network.netmask),
                    'prefix_length': network.prefixlen
                })
            except:
                pass
                
        return info
        
    except Exception as e:
        return {
            'input': ip_range_str,
            'error': str(e),
            'total_hosts': 0
        } 