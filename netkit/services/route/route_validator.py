"""
路由参数验证器
职责：参数验证、冲突检查、数据校验
"""

import ipaddress
from typing import Dict, List


class RouteValidator:
    """路由参数验证器 - 负责参数验证和冲突检查"""
    
    def __init__(self):
        pass
    
    def validate_route_params(self, destination: str, netmask: str, gateway: str, metric: int) -> Dict:
        """验证路由参数"""
        try:
            # 验证目标网络地址
            if not self.validate_ip_address(destination):
                return {
                    'valid': False,
                    'error': f"无效的目标网络地址: {destination}"
                }
            
            # 验证子网掩码
            netmask_result = self.validate_netmask(netmask)
            if not netmask_result['valid']:
                return netmask_result
            
            # 验证网关地址
            if not self.validate_ip_address(gateway):
                return {
                    'valid': False,
                    'error': f"无效的网关地址: {gateway}"
                }
            
            # 验证跃点数
            if not self.validate_metric(metric):
                return {
                    'valid': False,
                    'error': f"无效的跃点数: {metric}，必须在1-9999之间"
                }
            
            return {'valid': True}
            
        except Exception as e:
            return {
                'valid': False,
                'error': f"参数验证失败: {str(e)}"
            }
    
    def validate_ip_address(self, ip_str: str) -> bool:
        """验证IP地址格式"""
        try:
            ipaddress.IPv4Address(ip_str)
            return True
        except:
            return False
    
    def validate_netmask(self, mask_str: str) -> Dict:
        """验证子网掩码"""
        try:
            mask_addr = ipaddress.IPv4Address(mask_str)
            mask_int = int(mask_addr)
            
            # 验证子网掩码是否有效（必须是连续的1）
            if mask_int != 0:  # 允许0.0.0.0作为默认路由的掩码
                # 计算掩码中1的个数
                ones_count = bin(mask_int).count('1')
                expected_mask = (0xFFFFFFFF << (32 - ones_count)) & 0xFFFFFFFF
                if mask_int != expected_mask:
                    return {
                        'valid': False,
                        'error': f"无效的子网掩码: {mask_str}"
                    }
            
            return {'valid': True}
            
        except Exception as e:
            return {
                'valid': False,
                'error': f"子网掩码验证失败: {str(e)}"
            }
    
    def validate_metric(self, metric: int) -> bool:
        """验证跃点数"""
        return isinstance(metric, int) and 1 <= metric <= 9999
    
    def check_route_conflict(self, destination: str, netmask: str, existing_routes: List[Dict]) -> Dict:
        """检查路由冲突"""
        try:
            # 检查是否存在相同的路由
            for route in existing_routes:
                if route['network_destination'] == destination and route['netmask'] == netmask:
                    return {
                        'conflict': True,
                        'message': f"路由冲突: 已存在到 {destination} mask {netmask} 的路由",
                        'existing_route': route
                    }
            
            return {
                'conflict': False,
                'message': "无路由冲突"
            }
            
        except Exception as e:
            return {
                'conflict': False,
                'message': f"检查路由冲突出错: {str(e)}"
            }
    
    def validate_route_data(self, route_data: Dict) -> Dict:
        """验证完整的路由数据"""
        required_fields = ['destination', 'netmask', 'gateway', 'metric']
        
        # 检查必需字段
        for field in required_fields:
            if field not in route_data or not route_data[field]:
                return {
                    'valid': False,
                    'error': f"缺少必需字段: {field}"
                }
        
        # 验证各个字段
        return self.validate_route_params(
            route_data['destination'],
            route_data['netmask'],
            route_data['gateway'],
            route_data['metric']
        )
    
    def validate_deletion_params(self, destination: str, netmask: str = None, gateway: str = None) -> Dict:
        """验证删除路由的参数"""
        try:
            # 验证目标网络地址
            if not self.validate_ip_address(destination):
                return {
                    'valid': False,
                    'error': f"无效的目标网络地址: {destination}"
                }
            
            # 如果提供了子网掩码，验证它
            if netmask and not self.validate_ip_address(netmask):
                return {
                    'valid': False,
                    'error': f"无效的子网掩码: {netmask}"
                }
            
            # 如果提供了网关，验证它
            if gateway and not self.validate_ip_address(gateway):
                return {
                    'valid': False,
                    'error': f"无效的网关地址: {gateway}"
                }
            
            return {'valid': True}
            
        except Exception as e:
            return {
                'valid': False,
                'error': f"删除参数验证失败: {str(e)}"
            }
    
    def is_system_route(self, route: Dict) -> bool:
        """判断是否为系统路由（不建议删除）"""
        route_type = route.get('route_type', '')
        network_dest = route.get('network_destination', '')
        
        # 系统关键路由类型
        system_types = ['环回路由', '本地路由']
        if route_type in system_types:
            return True
        
        # 环回地址
        if network_dest.startswith('127.'):
            return True
        
        return False