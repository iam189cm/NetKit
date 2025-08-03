# -*- coding: utf-8 -*-
"""
静态路由管理服务模块

提供路由表获取、路由添加/删除、参数验证、异步处理等服务
"""

# 主服务接口
from .route import RouteService

# 服务组件
from .route_manager import RouteManager
from .route_parser import RouteParser
from .route_validator import RouteValidator
from .async_route_handler import AsyncRouteHandler

# 向后兼容的函数接口
from .route import add_route, delete_route, get_routes

# 导出主要服务类
__all__ = [
    'RouteService',  # 主服务接口
    'RouteManager',  # 路由管理器
    'RouteParser',   # 路由解析器
    'RouteValidator',  # 路由验证器
    'AsyncRouteHandler',  # 异步处理器
    # 兼容性函数
    'add_route',
    'delete_route', 
    'get_routes'
]