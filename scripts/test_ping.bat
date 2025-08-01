@echo off
chcp 65001 > nul
echo ========================================
echo NetKit Ping功能测试
echo ========================================
echo.

REM 设置测试环境
set NETKIT_TEST_MODE=1
set NETKIT_LOCAL_TEST=1

echo 📡 开始测试Ping功能...
echo.

echo [1/3] 测试单个目标Ping...
python -m pytest tests/ping/test_ping_service.py -k "test_ping_single_target" -v
if errorlevel 1 goto :failed

echo.
echo [2/3] 测试批量Ping...
python -m pytest tests/ping/test_ping_service.py -k "test_ping_multiple_targets" -v
if errorlevel 1 goto :failed

echo.
echo [3/3] 测试Ping结果解析...
python -m pytest tests/ping/test_ping_service.py -k "test_ping_result_parsing" -v
if errorlevel 1 goto :failed

echo.
echo ✅ Ping功能测试全部通过！
echo.
pause
exit /b 0

:failed
echo.
echo ❌ Ping功能测试失败！
echo 请检查网络连接
echo.
pause
exit /b 1