@echo off
chcp 65001 > nul
echo ========================================
echo NetKit 网络配置功能测试
echo ========================================
echo.

REM 设置测试环境
set NETKIT_TEST_MODE=1
set NETKIT_LOCAL_TEST=1

echo 🌐 开始测试网络配置功能...
echo.

echo [1/4] 测试网络接口管理...
python -m pytest tests/netconfig/test_netconfig_service.py -k "test_get_network_interfaces" -v
if errorlevel 1 goto :failed

echo.
echo [2/4] 测试IP配置验证...
python -m pytest tests/netconfig/test_netconfig_service.py -k "test_validate_ip_config" -v
if errorlevel 1 goto :failed

echo.
echo [3/4] 测试网络配置应用...
python -m pytest tests/netconfig/test_netconfig_integration.py -k "test_apply_profile" -v
if errorlevel 1 goto :failed

echo.
echo [4/4] 测试端到端流程...
python -m pytest tests/netconfig/test_netconfig_e2e.py -v
if errorlevel 1 goto :failed

echo.
echo ✅ 网络配置功能测试全部通过！
echo.
pause
exit /b 0

:failed
echo.
echo ❌ 网络配置功能测试失败！
echo 请检查网络环境和管理员权限
echo.
pause
exit /b 1