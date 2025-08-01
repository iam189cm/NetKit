"""
NetKit - 网络工具包

一个用于网络配置、测试和管理的Python工具包
"""

__version__ = "2.0.0"
__author__ = "NetKit Team"
__description__ = "网络工具包 - 提供网络配置、Ping测试、路由管理等功能"

# 导入主要服务模块
try:
    from . import services
    from . import utils
except ImportError:
    # 在某些测试环境中可能无法导入所有模块
    pass

__all__ = [
    "services",
    "utils",
    "__version__",
    "__author__",
    "__description__"
]
