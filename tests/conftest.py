#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pytest 配置文件
设置测试环境和通用fixtures
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "netkit"))
sys.path.insert(0, str(project_root / "gui"))

# 设置环境变量
os.environ["PYTHONPATH"] = os.pathsep.join([
    str(project_root),
    str(project_root / "netkit"),
    str(project_root / "gui"),
    os.environ.get("PYTHONPATH", "")
])

import pytest
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """设置测试环境"""
    # 确保所有必要的目录存在
    test_dirs = [
        project_root / "reports",
        project_root / "htmlcov",
        project_root / "tests" / "temp"
    ]
    
    for test_dir in test_dirs:
        test_dir.mkdir(exist_ok=True)
    
    yield
    
    # 清理临时文件
    temp_dir = project_root / "tests" / "temp"
    if temp_dir.exists():
        import shutil
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass

@pytest.fixture
def mock_windows_environment(monkeypatch):
    """模拟Windows环境"""
    monkeypatch.setattr("sys.platform", "win32")
    monkeypatch.setenv("OS", "Windows_NT")
    return True

@pytest.fixture
def temp_dir():
    """提供临时目录"""
    temp_path = project_root / "tests" / "temp"
    temp_path.mkdir(exist_ok=True)
    return temp_path