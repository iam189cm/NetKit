
import subprocess
import re
import ipaddress
import platform
from typing import List, Dict, Optional

# 导入拆分后的组件
from .route_manager import RouteManager
from .route_parser import RouteParser
from .route_validator import RouteValidator
from .async_route_handler import AsyncRouteHandler


class RouteService:
    """静态路由管理服务类 - 主服务接口"""
    
    def __init__(self):
        self.manager = RouteManager()
        self.parser = RouteParser()
        self.validator = RouteValidator()
        self.async_handler = AsyncRouteHandler()
    
    def get_route_table(self) -> Dict:
        """获取当前路由表"""
        try:
            # 使用路由管理器获取系统路由
            result = self.manager.get_system_routes()
            
            if not result['success']:
                return result
            
            # 使用解析器解析路由表
            routes = self.parser.parse_route_table(result['raw_output'])
            
            return {
                'success': True,
                'routes': routes,
                'raw_output': result['raw_output']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"获取路由表出错: {str(e)}"
            }
    
    # 以下方法已迁移到RouteParser类中，保留为兼容性接口
    def parse_route_table(self, route_output: str) -> List[Dict]:
        """解析路由表输出（兼容性接口）"""
        return self.parser.parse_route_table(route_output)
    
    def parse_route_line(self, line: str) -> Optional[Dict]:
        """解析单行路由信息（兼容性接口）"""
        return self.parser.parse_route_line(line)
    
    def determine_route_type(self, network_dest: str, netmask: str, gateway: str) -> str:
        """判断路由类型（兼容性接口）"""
        return self.parser.determine_route_type(network_dest, netmask, gateway)
    
    # 新增方法：异步操作支持
    def execute_async(self, operation: str, callback, *args, **kwargs):
        """异步执行操作"""
        operations_map = {
            'get_routes': self.get_route_table,
            'add_route': self.add_route,
            'delete_route': self.delete_route,
            'backup_routes': self.backup_route_table
        }
        
        if operation in operations_map:
            return self.async_handler.execute_async(operations_map[operation], callback, *args, **kwargs)
        else:
            raise ValueError(f"不支持的异步操作: {operation}")
    
    def cleanup(self):
        """清理资源"""
        if hasattr(self, 'async_handler'):
            self.async_handler.cleanup()
    
    def add_route(self, destination: str, netmask: str, gateway: str, metric: int = 1) -> Dict:
        """添加静态路由"""
        try:
            # 使用验证器验证输入参数
            validation = self.validator.validate_route_params(destination, netmask, gateway, metric)
            if not validation['valid']:
                return {
                    'success': False,
                    'error': validation['error']
                }
            
            # 使用路由管理器添加路由
            return self.manager.add_system_route(destination, netmask, gateway, metric)
                
        except Exception as e:
            return {
                'success': False,
                'error': f"添加路由出错: {str(e)}"
            }
    
    def delete_route(self, destination: str, netmask: str = None, gateway: str = None) -> Dict:
        """删除静态路由"""
        try:
            # 使用验证器验证删除参数
            validation = self.validator.validate_deletion_params(destination, netmask, gateway)
            if not validation['valid']:
                return {
                    'success': False,
                    'error': validation['error']
                }
            
            # 使用路由管理器删除路由
            return self.manager.delete_system_route(destination, netmask, gateway)
                
        except Exception as e:
            return {
                'success': False,
                'error': f"删除路由出错: {str(e)}"
            }
    
    def validate_route_params(self, destination: str, netmask: str, gateway: str, metric: int) -> Dict:
        """验证路由参数"""
        return self.validator.validate_route_params(destination, netmask, gateway, metric)
    
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
            
            # 使用验证器检查冲突
            return self.validator.check_route_conflict(destination, netmask, route_result['routes'])
            
        except Exception as e:
            return {
                'conflict': False,
                'message': f"检查路由冲突出错: {str(e)}"
            }
    
    def backup_route_table(self) -> Dict:
        """备份当前路由表"""
        return self.manager.backup_routes()


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
