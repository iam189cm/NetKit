@echo off
echo ================================
echo 正在构建 Netkit 单文件版本...
echo ================================

REM 清理之前的构建文件
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

echo 正在安装/更新PyInstaller...
pip install pyinstaller

echo 开始构建单个exe文件...
pyinstaller scripts/netkit_onefile.spec

if exist "dist\NETKit-Py.exe" (
    echo.
    echo ================================
    echo 构建成功！
    echo 可执行文件位置: dist\NETKit-Py.exe
    echo ================================
    
    REM 确保releases目录存在
    if not exist "releases" mkdir "releases"
    
    REM 复制exe文件到发布目录
    copy "dist\NETKit-Py.exe" "releases\Netkit.exe"
    echo 已复制到发布目录: releases\Netkit.exe
    
    echo.
    echo 是否要运行测试？(Y/N)
    set /p choice=
    if /i "%choice%"=="Y" (
        echo 正在启动程序进行测试...
        start "" "releases\Netkit.exe"
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