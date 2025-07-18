#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量更新视图文件的 DPI 适配脚本
"""

import os
import re
import glob

def update_file_dpi(file_path):
    """更新单个文件的 DPI 适配"""
    print(f"正在更新文件: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 添加 ui_helper 导入（如果没有的话）
    if 'from netkit.utils.ui_helper import ui_helper' not in content:
        # 在 ttkbootstrap 导入后添加
        content = re.sub(
            r'(from ttkbootstrap\.constants import \*\n)',
            r'\1from netkit.utils.ui_helper import ui_helper\n',
            content
        )
    
    # 替换字体设置
    font_patterns = [
        # Microsoft YaHei 字体
        (r"font=\('Microsoft YaHei', (\d+), 'bold'\)", r"font=ui_helper.get_font(\1, 'bold')"),
        (r"font=\('Microsoft YaHei', (\d+)\)", r"font=ui_helper.get_font(\1)"),
        # Consolas 字体
        (r"font=\('Consolas', (\d+), 'bold'\)", r"font=('Consolas', ui_helper.scale_size(\1), 'bold')"),
        (r"font=\('Consolas', (\d+)\)", r"font=('Consolas', ui_helper.scale_size(\1))"),
    ]
    
    for pattern, replacement in font_patterns:
        content = re.sub(pattern, replacement, content)
    
    # 移除 Button 控件的 font 参数（ttkbootstrap 不支持）
    content = re.sub(r'(\s+font=ui_helper\.get_font\([^)]+\),?\n)', '', content)
    
    # 替换尺寸设置
    size_patterns = [
        # padding 参数
        (r'padding=(\d+)', r'padding=ui_helper.get_padding(\1)'),
        # width 参数
        (r'width=(\d+)(?![.\d])', r'width=ui_helper.scale_size(\1)'),
        # height 参数
        (r'height=(\d+)(?![.\d])', r'height=ui_helper.scale_size(\1)'),
        # length 参数
        (r'length=(\d+)', r'length=ui_helper.scale_size(\1)'),
        # pady 参数
        (r'pady=(\d+)', r'pady=ui_helper.get_padding(\1)'),
        (r'pady=\((\d+), (\d+)\)', r'pady=(ui_helper.get_padding(\1), ui_helper.get_padding(\2))'),
        (r'pady=\(0, (\d+)\)', r'pady=(0, ui_helper.get_padding(\1))'),
        (r'pady=\((\d+), 0\)', r'pady=(ui_helper.get_padding(\1), 0)'),
        # padx 参数
        (r'padx=(\d+)', r'padx=ui_helper.get_padding(\1)'),
        (r'padx=\((\d+), (\d+)\)', r'padx=(ui_helper.get_padding(\1), ui_helper.get_padding(\2))'),
        (r'padx=\(0, (\d+)\)', r'padx=(0, ui_helper.get_padding(\1))'),
        (r'padx=\((\d+), 0\)', r'padx=(ui_helper.get_padding(\1), 0)'),
    ]
    
    for pattern, replacement in size_patterns:
        content = re.sub(pattern, replacement, content)
    
    # 如果内容有变化，写回文件
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ 已更新")
    else:
        print(f"  - 无需更新")

def main():
    """主函数"""
    # 获取项目根目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # 要更新的视图文件模式
    view_patterns = [
        os.path.join(project_root, 'gui', 'views', '*.py'),
        os.path.join(project_root, 'gui', 'views', '*', '*.py'),
    ]
    
    # 收集所有视图文件
    view_files = []
    for pattern in view_patterns:
        view_files.extend(glob.glob(pattern))
    
    # 过滤掉 __init__.py 文件
    view_files = [f for f in view_files if not f.endswith('__init__.py')]
    
    print(f"找到 {len(view_files)} 个视图文件需要更新:")
    for file_path in view_files:
        print(f"  - {os.path.relpath(file_path, project_root)}")
    
    print("\n开始更新...")
    
    # 更新每个文件
    for file_path in view_files:
        try:
            update_file_dpi(file_path)
        except Exception as e:
            print(f"  ✗ 更新失败: {e}")
    
    print("\n更新完成!")

if __name__ == '__main__':
    main() 