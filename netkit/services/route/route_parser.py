"""
路由表解析器
职责：路由表输出解析、数据转换、格式化
"""

import ipaddress
from typing import List, Dict, Optional


class RouteParser:
    """路由表解析器 - 负责解析路由表输出"""
    
    def __init__(self):
        pass
    
    def parse_route_table(self, route_output: str) -> List[Dict]:
        """解析路由表输出"""
        routes = []
        
        # 寻找IPv4路由表部分
        lines = route_output.split('\n')
        in_ipv4_section = False
        
        for line in lines:
            line = line.strip()
            
            # 找到IPv4路由表开始
            if 'IPv4 Route Table' in line or 'IPv4 路由表' in line:
                in_ipv4_section = True
                continue
            
            # 找到IPv6部分或结束，停止解析
            if in_ipv4_section and ('IPv6 Route Table' in line or 'IPv6 路由表' in line):
                break
            
            # 跳过标题行和分隔线
            if not in_ipv4_section or not line or line.startswith('=') or \
               'Network Destination' in line or 'Netmask' in line or \
               '网络目标' in line or '网络掩码' in line:
                continue
            
            # 解析路由行
            route_info = self.parse_route_line(line)
            if route_info:
                routes.append(route_info)
        
        return routes
    
    def parse_route_line(self, line: str) -> Optional[Dict]:
        """解析单行路由信息"""
        try:
            # 路由行格式: 网络目标 网络掩码 网关 接口 跃点数
            # 例如: 0.0.0.0          0.0.0.0      192.168.1.1     192.168.1.100    25
            parts = line.split()
            
            if len(parts) < 5:
                return None
            
            network_dest = parts[0]
            netmask = parts[1]
            gateway = parts[2]
            interface = parts[3]
            metric = parts[4]
            
            # 验证IP地址格式
            if not self._validate_route_parts(network_dest, netmask, gateway, interface, metric):
                return None
            
            # 计算CIDR格式的网络地址
            cidr_network = self._calculate_cidr_network(network_dest, netmask)
            
            # 判断路由类型
            route_type = self.determine_route_type(network_dest, netmask, gateway)
            
            return {
                'network_destination': network_dest,
                'netmask': netmask,
                'gateway': gateway,
                'interface': interface,
                'metric': int(metric),
                'cidr_network': cidr_network,
                'route_type': route_type
            }
            
        except Exception as e:
            return None
    
    def determine_route_type(self, network_dest: str, netmask: str, gateway: str) -> str:
        """判断路由类型"""
        if network_dest == '0.0.0.0' and netmask == '0.0.0.0':
            return '默认路由'
        elif network_dest == '127.0.0.0':
            return '环回路由'
        elif network_dest.startswith('224.'):
            return '多播路由'
        elif gateway == '127.0.0.1':
            return '本地路由'
        elif network_dest == gateway:
            return '直连路由'
        else:
            return '静态路由'
    
    def _validate_route_parts(self, network_dest: str, netmask: str, gateway: str, interface: str, metric: str) -> bool:
        """验证路由各部分的格式"""
        try:
            # 验证网络目标
            ipaddress.IPv4Address(network_dest)
            
            # 验证子网掩码
            ipaddress.IPv4Address(netmask)
            
            # 网关可能是"在链路上"或"On-link"，不需要验证
            if gateway not in ['在链路上', 'On-link']:
                ipaddress.IPv4Address(gateway)
                
            # 验证接口
            ipaddress.IPv4Address(interface)
            
            # 验证跃点数
            int(metric)
            
            return True
            
        except:
            return False
    
    def _calculate_cidr_network(self, network_dest: str, netmask: str) -> str:
        """计算CIDR格式的网络地址"""
        try:
            network = ipaddress.IPv4Network(f"{network_dest}/{netmask}", strict=False)
            return str(network)
        except:
            return f"{network_dest}/{netmask}"
    
    def format_route_data(self, routes: List[Dict]) -> List[Dict]:
        """格式化路由数据"""
        formatted_routes = []
        
        for route in routes:
            formatted_route = {
                'network_destination': route.get('network_destination', ''),
                'netmask': route.get('netmask', ''),
                'gateway': route.get('gateway', ''),
                'interface': route.get('interface', ''),
                'metric': route.get('metric', 0),
                'route_type': route.get('route_type', '未知'),
                'cidr_network': route.get('cidr_network', '')
            }
            formatted_routes.append(formatted_route)
            
        return formatted_routes
    
    def filter_routes_by_type(self, routes: List[Dict], route_type: str) -> List[Dict]:
        """按路由类型筛选路由"""
        return [route for route in routes if route.get('route_type') == route_type]
    
    def sort_routes(self, routes: List[Dict], sort_by: str = 'metric') -> List[Dict]:
        """排序路由"""
        if sort_by == 'metric':
            return sorted(routes, key=lambda x: x.get('metric', 0))
        elif sort_by == 'destination':
            return sorted(routes, key=lambda x: x.get('network_destination', ''))
        else:
            return routes