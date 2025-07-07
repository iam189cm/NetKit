@echo off
echo ========================================
echo NETKit v1.3 - 单文件发布脚本
echo ========================================
echo.

echo 正在清理旧的发布文件...
if exist "output\Publish" rmdir /s /q "output\Publish"
echo.

echo 开始编译和发布单文件可执行程序...
echo 目标平台: Windows x64
echo 发布模式: Release (自包含单文件)
echo.

dotnet publish src\NETKit\NETKit.csproj -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true -o "output\Publish"

echo.
if %ERRORLEVEL% EQU 0 (
    echo ========================================
    echo 发布成功！
    echo ========================================
    echo 单文件可执行程序位置:
    echo %CD%\output\Publish\NETKit.exe
    echo.
    echo 文件大小:
    for %%A in ("output\Publish\NETKit.exe") do echo %%~zA 字节
    echo.
    echo 你可以将此文件分发给同事使用。
    echo 使用时需要右键选择"以管理员身份运行"。
    echo ========================================
) else (
    echo ========================================
    echo 发布失败！请检查错误信息。
    echo ========================================
)

echo.
pause
