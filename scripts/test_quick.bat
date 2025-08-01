@echo off
chcp 65001 > nul
echo ========================================
echo NetKit 快速测试
echo ========================================
echo.

REM 设置测试环境
set NETKIT_TEST_MODE=1
set NETKIT_LOCAL_TEST=1

echo ⚡ 运行快速测试验证核心功能...
echo.

echo [1/2] 🔧 基础功能测试...
python -c "
import sys
sys.path.insert(0, '.')
try:
    from netkit.services.netconfig import get_network_interfaces
    from netkit.services.ping import PingService
    
    # 测试网络接口获取
    interfaces = get_network_interfaces()
    print(f'✅ 发现 {len(interfaces)} 个网络接口')
    
    # 测试Ping服务
    ping_service = PingService()
    result = ping_service.ping_single('127.0.0.1', count=1, timeout=1000)
    if result['success']:
        print('✅ Ping服务正常')
    else:
        print('❌ Ping服务异常')
        sys.exit(1)
        
    print('✅ 核心功能正常')
except Exception as e:
    print(f'❌ 核心功能异常: {e}')
    sys.exit(1)
"
if errorlevel 1 goto :failed

echo.
echo [2/2] 🖥️ GUI模块导入测试...
python -c "
import sys
sys.path.insert(0, '.')
try:
    from gui.views.netconfig.netconfig_view import NetConfigView
    from gui.views.ping.visual_ping_view import VisualPingView
    print('✅ GUI模块导入正常')
except Exception as e:
    print(f'❌ GUI模块导入异常: {e}')
    sys.exit(1)
"
if errorlevel 1 goto :failed

echo.
echo ✅ 快速测试通过！核心功能正常
echo.
pause
exit /b 0

:failed
echo.
echo ❌ 快速测试失败！
echo 请检查代码或依赖
echo.
pause
exit /b 1