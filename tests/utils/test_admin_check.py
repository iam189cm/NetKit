#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
管理员权限检查测试
"""

import pytest
from unittest.mock import Mock, patch

# 导入工具模块
from netkit.utils.admin_check import is_admin, require_admin


class TestAdminCheck:
    """管理员权限检查测试"""
    
    @patch('netkit.utils.admin_check.ctypes.windll.shell32.IsUserAnAdmin')
    def test_is_admin_true(self, mock_is_admin):
        """测试管理员权限检查 - 是管理员"""
        mock_is_admin.return_value = 1
        
        result = is_admin()
        
        assert result == True
        mock_is_admin.assert_called_once()
    
    @patch('netkit.utils.admin_check.ctypes.windll.shell32.IsUserAnAdmin')
    def test_is_admin_false(self, mock_is_admin):
        """测试管理员权限检查 - 不是管理员"""
        mock_is_admin.return_value = 0
        
        result = is_admin()
        
        assert result == False
        mock_is_admin.assert_called_once()
    
    @patch('netkit.utils.admin_check.is_admin')
    def test_require_admin_success(self, mock_is_admin):
        """测试要求管理员权限 - 成功"""
        mock_is_admin.return_value = True
        
        # 应该不抛出异常
        require_admin()
        
        mock_is_admin.assert_called_once()
    
    @patch('netkit.utils.admin_check.is_admin')
    def test_require_admin_failure(self, mock_is_admin):
        """测试要求管理员权限 - 失败"""
        mock_is_admin.return_value = False
        
        # 应该抛出异常
        with pytest.raises(PermissionError):
            require_admin()
        
        mock_is_admin.assert_called_once()


if __name__ == "__main__":
    # 运行管理员权限检查测试
    pytest.main([__file__, "-v"])