"""
路由管理器
职责：系统路由操作、命令执行、路由管理
"""

import subprocess
import platform
from typing import Dict


class RouteManager:
    """路由管理器 - 负责系统路由操作"""
    
    def __init__(self):
        self.platform = platform.system()
        
    def get_system_routes(self) -> Dict:
        """获取系统路由表"""
        try:
            # 使用route print命令获取路由表
            cmd = ['route', 'print']
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                encoding='gbk',
                creationflags=self._get_creation_flags()
            )
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': f"获取路由表失败: {result.stderr}"
                }
            
            return {
                'success': True,
                'raw_output': result.stdout
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"获取路由表出错: {str(e)}"
            }
    
    def add_system_route(self, destination: str, netmask: str, gateway: str, metric: int = 1) -> Dict:
        """添加系统路由"""
        try:
            # 构建添加路由命令
            cmd = [
                'route', 'add', 
                destination, 
                'mask', netmask, 
                gateway, 
                'metric', str(metric)
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                encoding='gbk',
                creationflags=self._get_creation_flags()
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
    
    def delete_system_route(self, destination: str, netmask: str = None, gateway: str = None) -> Dict:
        """删除系统路由"""
        try:
            # 构建删除路由命令
            cmd = ['route', 'delete', destination]
            
            # 如果提供了网络掩码，添加到命令中
            if netmask:
                cmd.extend(['mask', netmask])
            
            # 如果提供了网关，添加到命令中
            if gateway:
                cmd.append(gateway)
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                encoding='gbk',
                creationflags=self._get_creation_flags()
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
    
    def execute_route_command(self, cmd_args: list) -> Dict:
        """执行路由命令"""
        try:
            result = subprocess.run(
                cmd_args,
                capture_output=True,
                text=True,
                encoding='gbk',
                creationflags=self._get_creation_flags()
            )
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"执行命令出错: {str(e)}"
            }
    
    def _get_creation_flags(self):
        """获取创建标志（Windows下隐藏控制台窗口）"""
        if self.platform == 'Windows':
            return subprocess.CREATE_NO_WINDOW
        else:
            return 0
    
    def backup_routes(self) -> Dict:
        """备份当前路由表"""
        try:
            route_result = self.get_system_routes()
            if not route_result['success']:
                return {
                    'success': False,
                    'error': "无法获取路由表进行备份"
                }
            
            return {
                'success': True,
                'backup_data': route_result['raw_output'],
                'message': "路由表备份成功"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"备份路由表出错: {str(e)}"
            }