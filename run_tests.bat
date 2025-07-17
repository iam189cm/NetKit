@echo off
echo ====================================
echo NetKit 测试运行器
echo ====================================

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python环境
    echo 请确保Python已安装并添加到PATH
    pause
    exit /b 1
)

REM 检查是否在项目根目录
if not exist "start_netkit.py" (
    echo 错误: 请在项目根目录运行此脚本
    pause
    exit /b 1
)

REM 显示菜单
echo.
echo 请选择测试类型:
echo 1. 单元测试
echo 2. 集成测试
echo 3. GUI测试
echo 4. 性能测试
echo 5. 压力测试
echo 6. 所有测试
echo 7. 快速测试（不包含慢速测试）
echo 8. 仅生成覆盖率报告
echo 9. 退出
echo.

set /p choice=请输入选择 (1-9): 

if "%choice%"=="1" (
    echo 运行单元测试...
    python scripts/run_tests.py --type unit --verbose
) else if "%choice%"=="2" (
    echo 运行集成测试...
    python scripts/run_tests.py --type integration --verbose
) else if "%choice%"=="3" (
    echo 运行GUI测试...
    python scripts/run_tests.py --type gui --verbose
) else if "%choice%"=="4" (
    echo 运行性能测试...
    python scripts/run_tests.py --type performance --verbose
) else if "%choice%"=="5" (
    echo 运行压力测试...
    python scripts/run_tests.py --type stress --verbose
) else if "%choice%"=="6" (
    echo 运行所有测试（包含慢速测试）...
    python scripts/run_tests.py --type all --verbose --include-slow
) else if "%choice%"=="7" (
    echo 运行快速测试...
    python scripts/run_tests.py --type all --verbose
) else if "%choice%"=="8" (
    echo 生成覆盖率报告...
    python scripts/run_tests.py --coverage-only
) else if "%choice%"=="9" (
    echo 退出
    exit /b 0
) else (
    echo 无效选择，请重试
    pause
    goto :eof
)

echo.
echo ====================================
echo 测试完成
echo ====================================
echo.
echo 查看测试报告:
echo   HTML报告: reports\
echo   覆盖率报告: htmlcov\index.html
echo.

pause 