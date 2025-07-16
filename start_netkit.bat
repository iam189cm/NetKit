@echo off
chcp 65001 > nul
title Netkit 网络工具箱

echo.
echo ==========================================
echo    Netkit 网络工程师工具箱
echo ==========================================
echo.

cd /d "%~dp0"

echo 正在启动程序...
python start_netkit.py

echo.
echo 程序已退出，按任意键关闭窗口...
pause > nul 