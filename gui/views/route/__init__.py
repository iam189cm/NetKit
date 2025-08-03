# -*- coding: utf-8 -*-
"""
静态路由管理UI模块

提供路由表显示、路由添加/删除、结果展示等功能的完整UI界面
"""

# 主视图
from .route_view import RouteFrame

# UI组件
from .route_table_widget import RouteTableWidget
from .route_form_widget import RouteFormWidget
from .action_buttons_widget import ActionButtonsWidget
from .result_display_widget import ResultDisplayWidget

# 为了向后兼容，保持原有的导入方式
__all__ = [
    'RouteFrame',  # 主视图
    'RouteTableWidget',  # 路由表组件
    'RouteFormWidget',   # 表单组件
    'ActionButtonsWidget',  # 按钮组件
    'ResultDisplayWidget'   # 结果显示组件
]