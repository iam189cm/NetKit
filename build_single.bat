@echo off
echo ================================
echo 正在构建 NetKit 单文件版本...
echo ================================

python scripts/build.py

if exist "dist\NetKit.exe" (
    echo.
    echo ================================
    echo 构建成功！
    echo 可执行文件位置: dist\NetKit.exe
    echo 发布文件位置: releases\NetKit.exe
    echo ================================
    
    echo.
    echo 是否要运行测试？(Y/N)
    set /p choice=
    if /i "%choice%"=="Y" (
        echo 正在启动程序进行测试...
        start "" "releases\NetKit.exe"
    )
) else (
    echo.
    echo ================================
    echo 构建失败！请检查错误信息。
    echo ================================
)

echo.
echo 构建完成，按任意键退出...
pause > nul 