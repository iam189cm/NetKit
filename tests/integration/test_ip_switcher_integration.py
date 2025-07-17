#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网卡配置集成测试
测试服务层与界面层的完整交互流程
"""

import pytest
import tkinter as tk
import ttkbootstrap as tb
import unittest.mock as mock
import threading
import time
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# 设置测试环境
os.environ['NETKIT_TEST_MODE'] = '1'

# 导入测试目标
from gui.views.ip_switcher_view import IPSwitcherFrame
from netkit.services.ip_switcher import (
    get_network_interfaces,
    get_network_card_info,
    apply_profile,
    validate_ip_config,
    save_profile,
    load_profiles
)

# 导入测试数据
from tests.test_data import (
    VALID_IP_CONFIGS,
    INVALID_IP_CONFIGS,
    MOCK_NETWORK_INTERFACES,
    MOCK_NETWORK_CARD_INFO,
    MOCK_NETSH_INTERFACE_OUTPUT,
    MOCK_NETSH_IP_CONFIG_OUTPUT,
    MOCK_GETMAC_OUTPUT,
    ERROR_SCENARIOS,
    PERFORMANCE_TEST_DATA,
    STRESS_TEST_DATA
)


class TestEndToEndWorkflow:
    """端到端工作流测试"""
    
    @pytest.fixture
    def root_window(self):
        """创建测试窗口"""
        root = tb.Window(themename='darkly')
        root.withdraw()
        yield root
        root.destroy()
    
    @pytest.fixture
    def ip_switcher_frame(self, root_window):
        """创建IPSwitcherFrame实例"""
        frame = IPSwitcherFrame(root_window)
        return frame
    
    @pytest.fixture
    def temp_config_dir(self, tmp_path):
        """创建临时配置目录"""
        config_dir = tmp_path / ".netkit_py"
        config_dir.mkdir()
        return config_dir
    
    @pytest.mark.integration
    def test_complete_static_ip_configuration(self, ip_switcher_frame, temp_config_dir):
        """测试完整的静态IP配置流程"""
        with patch('subprocess.run') as mock_run:
            with patch('netkit.services.ip_switcher.get_config_dir') as mock_get_config_dir:
                # 设置模拟返回值
                mock_get_config_dir.return_value = temp_config_dir
                mock_run.side_effect = [
                    # get_network_interfaces
                    mock.Mock(returncode=0, stdout=MOCK_NETSH_INTERFACE_OUTPUT),
                    # get_network_card_info - interface info
                    mock.Mock(returncode=0, stdout="管理状态: 已启用\n类型: 专用"),
                    # get_network_card_info - mac info
                    mock.Mock(returncode=0, stdout=MOCK_GETMAC_OUTPUT),
                    # get_network_card_info - ip config
                    mock.Mock(returncode=0, stdout=MOCK_NETSH_IP_CONFIG_OUTPUT),
                    # apply_profile - set IP
                    mock.Mock(returncode=0, stdout=""),
                    # apply_profile - set DNS 1
                    mock.Mock(returncode=0, stdout=""),
                    # apply_profile - set DNS 2
                    mock.Mock(returncode=0, stdout="")
                ]
                
                # 1. 刷新网络接口
                ip_switcher_frame.refresh_interfaces()
                
                # 验证接口列表已加载
                assert "以太网" in ip_switcher_frame.interface_combo['values']
                
                # 2. 选择网络接口
                ip_switcher_frame.interface_var.set("以太网")
                ip_switcher_frame.on_interface_selected()
                
                # 验证网卡信息已显示
                assert ip_switcher_frame.name_label.cget('text') == "以太网"
                assert ip_switcher_frame.ip_label.cget('text') == "192.168.1.100"
                
                # 3. 配置静态IP
                ip_switcher_frame.dhcp_var.set(False)
                ip_switcher_frame.on_dhcp_changed()
                
                # 4. 输入配置信息
                config = VALID_IP_CONFIGS[0]
                for entry, value in [
                    (ip_switcher_frame.ip_entry, config['ip']),
                    (ip_switcher_frame.mask_entry, config['mask']),
                    (ip_switcher_frame.gateway_entry, config['gateway']),
                    (ip_switcher_frame.dns1_entry, "8.8.8.8"),
                    (ip_switcher_frame.dns2_entry, "8.8.4.4")
                ]:
                    entry.delete(0, tk.END)
                    entry.insert(0, value)
                
                # 5. 应用配置
                ip_switcher_frame.apply_config()
                
                # 验证所有命令都被调用
                assert mock_run.call_count >= 5
                
                # 验证状态显示成功消息
                status_content = ip_switcher_frame.status_text.get('1.0', tk.END)
                assert "成功" in status_content


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"]) 