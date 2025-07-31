
import subprocess
import re
import ipaddress
import platform
from typing import List, Dict, Optional


class RouteService:
    """静态路由管理服务类"""
    
    def __init__(self):
        pass
    
    def get_route_table(self) -> Dict:
        """获取当前路由表"""
        try:
            # 使用route print命令获取路由表
            cmd = ['route', 'print']
            
            # Windows平台下隐藏控制台窗口，避免弹出黑色命令行窗口
            if platform.system() == 'Windows':
                creationflags = subprocess.CREATE_NO_WINDOW
            else:
                creationflags = 0
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                encoding='gbk',
                creationflags=creationflags  # 隐藏Windows控制台窗口
            )
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': f"获取路由表失败: {result.stderr}"
                }
            
            routes = self.parse_route_table(result.stdout)
            
            return {
                'success': True,
                'routes': routes,
                'raw_output': result.stdout
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"获取路由表出错: {str(e)}"
            }
    
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
            try:
                ipaddress.IPv4Address(network_dest)
                ipaddress.IPv4Address(netmask)
                ipaddress.IPv4Address(gateway)
                ipaddress.IPv4Address(interface)
                int(metric)
            except:
                return None
            
            # 计算CIDR格式的网络地址
            try:
                network = ipaddress.IPv4Network(f"{network_dest}/{netmask}", strict=False)
                cidr_network = str(network)
            except:
                cidr_network = f"{network_dest}/{netmask}"
            
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
    
    def add_route(self, destination: str, netmask: str, gateway: str, metric: int = 1) -> Dict:
        """添加静态路由"""
        try:
            # 验证输入参数
            validation = self.validate_route_params(destination, netmask, gateway, metric)
            if not validation['valid']:
                return {
                    'success': False,
                    'error': validation['error']
                }
            
            # 构建添加路由命令
            cmd = [
                'route', 'add', 
                destination, 
                'mask', netmask, 
                gateway, 
                'metric', str(metric)
            ]
            
            # Windows平台下隐藏控制台窗口，避免弹出黑色命令行窗口
            if platform.system() == 'Windows':
                creationflags = subprocess.CREATE_NO_WINDOW
            else:
                creationflags = 0
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                encoding='gbk',
                creationflags=creationflags  # 隐藏Windows控制台窗口
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'message': f"路由添加成功: {destination} mask {netmask} gateway {gateway} metric {metric}"
                }
            else:
                return {
                    'success': False,
                    'error': f"添加路由失败: {result.stderr.strip()}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"添加路由出错: {str(e)}"
            }
    
    def delete_route(self, destination: str, netmask: str = None, gateway: str = None) -> Dict:
        """删除静态路由"""
        try:
            # 验证目标网络地址
            try:
                ipaddress.IPv4Address(destination)
            except:
                return {
                    'success': False,
                    'error': f"无效的目标网络地址: {destination}"
                }
            
            # 构建删除路由命令
            cmd = ['route', 'delete', destination]
            
            # 如果提供了网络掩码，添加到命令中
            if netmask:
                cmd.extend(['mask', netmask])
            
            # 如果提供了网关，添加到命令中
            if gateway:
                cmd.append(gateway)
            
            # Windows平台下隐藏控制台窗口，避免弹出黑色命令行窗口
            if platform.system() == 'Windows':
                creationflags = subprocess.CREATE_NO_WINDOW
            else:
                creationflags = 0
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                encoding='gbk',
                creationflags=creationflags  # 隐藏Windows控制台窗口
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'message': f"路由删除成功: {destination}"
                }
            else:
                return {
                    'success': False,
                    'error': f"删除路由失败: {result.stderr.strip()}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"删除路由出错: {str(e)}"
            }
    
    def validate_route_params(self, destination: str, netmask: str, gateway: str, metric: int) -> Dict:
        """验证路由参数"""
        try:
            # 验证目标网络地址
            ipaddress.IPv4Address(destination)
            
            # 验证子网掩码
            mask_addr = ipaddress.IPv4Address(netmask)
            mask_int = int(mask_addr)
            
            # 验证子网掩码是否有效（必须是连续的1）
            if mask_int != 0:  # 允许0.0.0.0作为默认路由的掩码
                # 计算掩码中1的个数
                ones_count = bin(mask_int).count('1')
                expected_mask = (0xFFFFFFFF << (32 - ones_count)) & 0xFFFFFFFF
                if mask_int != expected_mask:
                    return {
                        'valid': False,
                        'error': f"无效的子网掩码: {netmask}"
                    }
            
            # 验证网关地址
            ipaddress.IPv4Address(gateway)
            
            # 验证跃点数
            if not isinstance(metric, int) or metric < 1 or metric > 9999:
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
    
    def check_route_conflict(self, destination: str, netmask: str) -> Dict:
        """检查路由冲突"""
        try:
            # 获取当前路由表
            route_result = self.get_route_table()
            if not route_result['success']:
                return {
                    'conflict': False,
                    'message': "无法检查路由冲突"
                }
            
            # 检查是否存在相同的路由
            for route in route_result['routes']:
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
    
    def backup_route_table(self) -> Dict:
        """备份当前路由表"""
        try:
            route_result = self.get_route_table()
            if not route_result['success']:
                return {
                    'success': False,
                    'error': "无法获取路由表进行备份"
                }
            
            # 这里可以将路由表保存到文件
            # 暂时返回路由表数据
            return {
                'success': True,
                'backup_data': route_result['routes'],
                'message': "路由表备份成功"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"备份路由表出错: {str(e)}"
            }


# 向后兼容的简单函数
def add_route(dest, mask, gateway, metric=1):
    """添加路由（向后兼容）"""
    service = RouteService()
    result = service.add_route(dest, mask, gateway, metric)
    if not result['success']:
        raise Exception(result['error'])


def delete_route(dest, mask=None, gateway=None):
    """删除路由（向后兼容）"""
    service = RouteService()
    result = service.delete_route(dest, mask, gateway)
    if not result['success']:
        raise Exception(result['error'])


def get_routes():
    """获取路由表（向后兼容）"""
    service = RouteService()
    result = service.get_route_table()
    if result['success']:
        return result['routes']
    else:
        raise Exception(result['error'])
