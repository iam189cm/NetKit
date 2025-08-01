@echo off
chcp 65001 > nul
echo ========================================
echo NetKit 本机完整测试套件
echo ========================================
echo.

REM 检查Python环境
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到Python环境
    echo 请确保Python已安装并添加到PATH
    pause
    exit /b 1
)

REM 检查依赖
echo 🔍 检查测试依赖...
pip show pytest > nul 2>&1
if errorlevel 1 (
    echo 📦 安装测试依赖...
    pip install pytest pytest-html pytest-cov
)

echo.
echo 🚀 开始运行测试...
echo.

REM 设置测试模式
set NETKIT_TEST_MODE=1
set NETKIT_LOCAL_TEST=1

echo [1/5] 🌐 测试网络配置功能...
python -m pytest tests/netconfig/ -v --tb=short
if errorlevel 1 (
    echo ❌ 网络配置测试失败
    goto :test_failed
)

echo.
echo [2/5] 📡 测试Ping功能...
python -m pytest tests/ping/ -v --tb=short
if errorlevel 1 (
    echo ❌ Ping功能测试失败
    goto :test_failed
)

echo.
echo [3/5] 🛣️ 测试路由功能...
python -m pytest tests/route/ -v --tb=short
if errorlevel 1 (
    echo ❌ 路由功能测试失败
    goto :test_failed
)

echo.
echo [4/5] 🖥️ 测试GUI功能...
python -m pytest tests/gui/ -v --tb=short
if errorlevel 1 (
    echo ❌ GUI功能测试失败
    goto :test_failed
)

echo.
echo [5/5] 🔧 测试工具类...
python -m pytest tests/utils/ -v --tb=short
if errorlevel 1 (
    echo ❌ 工具类测试失败
    goto :test_failed
)

echo.
echo ========================================
echo ✅ 所有测试通过！
echo ========================================
echo.
echo 💡 测试建议：
echo   - 定期运行此测试套件确保功能正常
echo   - 修改网络相关代码后必须运行测试
echo   - 发现问题及时修复，不要积累技术债务
echo.
pause
exit /b 0

:test_failed
echo.
echo ========================================
echo ❌ 测试失败！
echo ========================================
echo.
echo 🔍 故障排除建议：
echo   1. 检查网络连接是否正常
echo   2. 确认以管理员权限运行
echo   3. 检查防火墙设置
echo   4. 查看详细错误信息
echo.
pause
exit /b 1