#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NetKit 包安装配置
"""

from setuptools import setup, find_packages

# 读取README文件
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "NetKit - 网络工具包"

# 读取requirements.txt
try:
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
except FileNotFoundError:
    requirements = []

setup(
    name="netkit",
    version="2.1.0",
    author="NetKit Team",
    author_email="",
    description="网络工具包 - 提供网络配置、Ping测试、路由管理等功能",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/iam189cm/NetKit",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.12",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-cov>=4.0.0",
            "pytest-html>=4.0.0",
            "pytest-benchmark>=5.0.0",
            "pytest-asyncio>=1.0.0",
            "pytest-mock>=3.0.0",
            "pytest-timeout>=2.0.0",
            "pytest-xdist>=3.0.0",
            "black>=24.0.0",
            "isort>=5.0.0",
            "flake8>=7.0.0",
            "bandit>=1.7.0",
            "safety>=3.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "netkit=scripts.start:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)