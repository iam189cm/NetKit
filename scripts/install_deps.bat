@echo off
chcp 65001 > nul
title NetKit 依赖安装脚本

echo.
echo ==========================================
echo    NetKit 依赖安装脚本
echo ==========================================
echo.

REM 切换到项目根目录
cd /d "%~dp0.."

echo 正在安装基础依赖...
pip install ttkbootstrap WMI pywin32

echo.
echo 正在尝试安装 psutil...
echo 注意：在 ARM64 架构上，psutil 可能需要 Microsoft Visual C++ 编译工具
echo.

REM 尝试安装 psutil
pip install psutil --only-binary=all 2>nul
if %errorlevel% neq 0 (
    echo 警告：psutil 安装失败，这可能是由于缺少编译工具
    echo 程序仍然可以正常运行，但某些系统监控功能可能受限
    echo.
    echo 如需安装 psutil，请：
    echo 1. 安装 Microsoft Visual C++ Build Tools
    echo 2. 或使用预编译的 wheel 包
    echo.
) else (
    echo psutil 安装成功！
)

echo.
echo 正在安装测试依赖...
pip install pytest pytest-cov pytest-mock pytest-asyncio pytest-timeout pytest-xdist pytest-html pytest-benchmark coverage mock

echo.
echo 依赖安装完成！
echo 现在可以运行 start.bat 启动程序
echo.
pause 