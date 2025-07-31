@echo off
chcp 65001 > nul
title Netkit 网络工具箱

echo.
echo ==========================================
echo    Netkit 网络工程师工具箱
echo ==========================================
echo.

REM 切换到项目根目录（脚本文件在scripts子目录中）
cd /d "%~dp0.."

echo 正在启动程序...
python scripts/start.py

echo.
echo 程序已退出，按任意键关闭窗口...
pause > nul