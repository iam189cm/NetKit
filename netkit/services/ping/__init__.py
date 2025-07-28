"""
NetKit Ping服务模块

提供完整的ping网络测试功能，包括：
- 单次ping测试
- 批量ping测试  
- 连续ping测试
- IP范围解析
- 结果统计分析
"""

from .ip_parser import parse_ip_range
from .ping_executor import PingExecutor
from .result_parser import PingResultParser
from .stats_manager import PingStatsManager
from .ping_service import PingService

# 向后兼容的简单函数
from .ping_service import ping, ping_with_stats

__all__ = [
    'PingService',
    'PingExecutor', 
    'PingResultParser',
    'PingStatsManager',
    'parse_ip_range',
    'ping',
    'ping_with_stats'
] 