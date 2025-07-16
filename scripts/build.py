#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NetKit 构建脚本
用于GitHub Actions和本地构建
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

def run_command(cmd, cwd=None, shell=True):
    """运行命令并返回结果"""
    print(f"Running: {cmd}")
    if cwd:
        print(f"Working directory: {cwd}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=shell,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode != 0:
            print(f"Command failed with return code: {result.returncode}")
            return False
        
        return True
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def clean_build_dirs():
    """清理构建目录"""
    print("Cleaning build directories...")
    
    dirs_to_clean = ['dist', 'build', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Removing {dir_name}...")
            try:
                shutil.rmtree(dir_name, ignore_errors=True)
            except Exception as e:
                print(f"Warning: Could not remove {dir_name}: {e}")
                # 继续执行，不要因为清理失败而停止
    
    # 清理所有 .pyc 文件和 __pycache__ 目录
    try:
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith('.pyc'):
                    try:
                        os.remove(os.path.join(root, file))
                    except OSError:
                        pass
            
            # 清理 __pycache__ 目录
            if '__pycache__' in dirs:
                shutil.rmtree(os.path.join(root, '__pycache__'), ignore_errors=True)
    except Exception as e:
        print(f"Warning: Error cleaning cache files: {e}")
        # 不要因为清理失败而停止构建
    
    return True  # 总是返回True，因为清理失败不应该停止构建

def install_dependencies():
    """安装依赖"""
    print("Installing dependencies...")
    
    # 升级pip
    if not run_command([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip']):
        return False
    
    # 安装requirements
    if not run_command([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt']):
        return False
    
    # 安装PyInstaller
    if not run_command([sys.executable, '-m', 'pip', 'install', 'pyinstaller']):
        return False
    
    return True

def build_executable():
    """构建可执行文件"""
    print("Building executable...")
    
    # 检查spec文件是否存在
    spec_file = Path('scripts') / 'netkit_onefile.spec'
    if not spec_file.exists():
        print(f"Error: {spec_file} not found!")
        print(f"Current working directory: {os.getcwd()}")
        print("Files in scripts directory:")
        scripts_dir = Path('scripts')
        if scripts_dir.exists():
            for file in scripts_dir.iterdir():
                print(f"  {file.name}")
        else:
            print("  Scripts directory does not exist!")
        return False
    
    # 运行PyInstaller - 使用绝对路径
    cmd = [sys.executable, '-m', 'PyInstaller', str(spec_file.absolute()), '--log-level=INFO']
    
    if not run_command(cmd):
        return False
    
    # 检查构建结果
    exe_path = Path('dist/NetKit.exe')
    if not exe_path.exists():
        print("Error: NetKit.exe not found in dist directory!")
        return False
    
    # 显示文件信息
    file_size = exe_path.stat().st_size / (1024 * 1024)  # MB
    print(f"Build successful! NetKit.exe size: {file_size:.1f} MB")
    
    return True

def copy_to_releases():
    """复制到releases目录"""
    print("Copying to releases directory...")
    
    # 确保releases目录存在
    releases_dir = Path('releases')
    releases_dir.mkdir(exist_ok=True)
    
    # 复制exe文件
    src = Path('dist/NetKit.exe')
    dst = releases_dir / 'NetKit.exe'
    
    if src.exists():
        shutil.copy2(src, dst)
        print(f"Copied to {dst}")
        return True
    else:
        print("Error: Source file not found!")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("NetKit Build Script")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print("=" * 50)
    
    # 检查是否在正确的目录
    if not Path('start_netkit.py').exists():
        print("Error: start_netkit.py not found! Please run from project root.")
        return False
    
    # 构建步骤
    steps = [
        ("Clean build directories", clean_build_dirs),
        ("Install dependencies", install_dependencies),
        ("Build executable", build_executable),
        ("Copy to releases", copy_to_releases),
    ]
    
    for step_name, step_func in steps:
        print(f"\n--- {step_name} ---")
        if not step_func():
            print(f"Error: {step_name} failed!")
            return False
    
    print("\n" + "=" * 50)
    print("Build completed successfully!")
    print("=" * 50)
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 