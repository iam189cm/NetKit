"""
网络配置相关UI组件模块

提供网卡选择、信息显示、配置表单、状态显示等UI组件
"""

# 主视图
from .netconfig_view import NetConfigView

# 各个子组件
from .interface_selector import InterfaceSelectorWidget
from .info_display import InfoDisplayWidget
from .config_form import ConfigFormWidget
from .status_display import StatusDisplayWidget

# 为了向后兼容，保持原有的导入方式
__all__ = [
    'NetConfigView',
    'InterfaceSelectorWidget',
    'InfoDisplayWidget',
    'ConfigFormWidget',
    'StatusDisplayWidget'
] 