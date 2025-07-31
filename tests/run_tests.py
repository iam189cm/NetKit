#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NetKit 测试运行脚本
支持运行不同类型的测试：单元测试、集成测试、GUI测试、性能测试
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path


def run_command(cmd, description=""):
    """运行命令并返回结果"""
    print(f"\n{'='*60}")
    print(f"执行: {description}")
    print(f"命令: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    start_time = time.time()
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        end_time = time.time()
        print(f"\n✅ {description} 完成 (耗时: {end_time - start_time:.2f}s)")
        return True
    except subprocess.CalledProcessError as e:
        end_time = time.time()
        print(f"\n❌ {description} 失败 (耗时: {end_time - start_time:.2f}s)")
        print(f"错误代码: {e.returncode}")
        return False


def setup_test_environment():
    """设置测试环境"""
    print("🔧 设置测试环境...")
    
    # 切换到项目根目录（测试脚本在tests子目录中）
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    
    # 创建必要的目录
    os.makedirs("reports", exist_ok=True)
    os.makedirs("htmlcov", exist_ok=True)
    
    # 设置环境变量
    os.environ['NETKIT_TEST_MODE'] = '1'
    os.environ['PYTHONPATH'] = str(Path.cwd())
    
    print("✅ 测试环境设置完成")


def run_unit_tests(verbose=False, coverage=True):
    """运行单元测试"""
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/unit/",
        "-v" if verbose else "",
        "--tb=short",
        "-m", "unit"
    ]
    
    if coverage:
        cmd.extend([
            "--cov=netkit",
            "--cov=gui",
            "--cov-report=html:htmlcov",
            "--cov-report=xml:coverage.xml",
            "--cov-report=term-missing"
        ])
    
    cmd.extend([
        "--html=reports/unit_report.html",
        "--self-contained-html"
    ])
    
    # 过滤空字符串
    cmd = [c for c in cmd if c]
    
    return run_command(cmd, "单元测试")


def run_integration_tests(verbose=False):
    """运行集成测试"""
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/integration/",
        "-v" if verbose else "",
        "--tb=short",
        "-m", "integration",
        "--html=reports/integration_report.html",
        "--self-contained-html"
    ]
    
    # 过滤空字符串
    cmd = [c for c in cmd if c]
    
    return run_command(cmd, "集成测试")


def run_gui_tests(verbose=False):
    """运行GUI测试"""
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/gui/",
        "-v" if verbose else "",
        "--tb=short",
        "-m", "gui",
        "--html=reports/gui_report.html",
        "--self-contained-html"
    ]
    
    # 过滤空字符串
    cmd = [c for c in cmd if c]
    
    return run_command(cmd, "GUI测试")


def run_performance_tests(verbose=False, include_slow=False):
    """运行性能测试"""
    markers = "performance"
    if not include_slow:
        markers += " and not slow"
    
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/performance/",
        "-v" if verbose else "",
        "--tb=short",
        "-m", markers,
        "--html=reports/performance_report.html",
        "--self-contained-html"
    ]
    
    # 过滤空字符串
    cmd = [c for c in cmd if c]
    
    return run_command(cmd, "性能测试")


def run_stress_tests(verbose=False):
    """运行压力测试"""
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/performance/",
        "-v" if verbose else "",
        "--tb=short",
        "-m", "stress",
        "--html=reports/stress_report.html",
        "--self-contained-html"
    ]
    
    # 过滤空字符串
    cmd = [c for c in cmd if c]
    
    return run_command(cmd, "压力测试")


def run_all_tests(verbose=False, include_slow=False):
    """运行所有测试"""
    print("🚀 开始运行所有测试...")
    
    results = []
    
    # 运行各种测试
    results.append(("单元测试", run_unit_tests(verbose, coverage=True)))
    results.append(("集成测试", run_integration_tests(verbose)))
    results.append(("GUI测试", run_gui_tests(verbose)))
    results.append(("性能测试", run_performance_tests(verbose, include_slow)))
    
    if include_slow:
        results.append(("压力测试", run_stress_tests(verbose)))
    
    # 检查覆盖率
    if run_coverage_check():
        results.append(("覆盖率检查", True))
    else:
        results.append(("覆盖率检查", False))
    
    # 输出结果汇总
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name:20} {status}")
        if not passed:
            all_passed = False
    
    print("="*60)
    if all_passed:
        print("🎉 所有测试通过！")
        return True
    else:
        print("⚠️  部分测试失败，请检查详细报告")
        return False


def run_coverage_check():
    """检查测试覆盖率"""
    cmd = [sys.executable, "-m", "coverage", "report", "--fail-under=85"]
    
    return run_command(cmd, "覆盖率检查")


def generate_coverage_report():
    """生成覆盖率报告"""
    print("📊 生成覆盖率报告...")
    
    # HTML报告
    cmd_html = [sys.executable, "-m", "coverage", "html", "-d", "htmlcov"]
    run_command(cmd_html, "生成HTML覆盖率报告")
    
    # XML报告
    cmd_xml = [sys.executable, "-m", "coverage", "xml", "-o", "coverage.xml"]
    run_command(cmd_xml, "生成XML覆盖率报告")
    
    # 控制台报告
    cmd_report = [sys.executable, "-m", "coverage", "report", "--show-missing"]
    run_command(cmd_report, "显示覆盖率报告")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="NetKit 测试运行器")
    parser.add_argument("--type", choices=["unit", "integration", "gui", "performance", "stress", "all"], 
                       default="all", help="测试类型")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--no-coverage", action="store_true", help="跳过覆盖率检查")
    parser.add_argument("--include-slow", action="store_true", help="包含慢速测试")
    parser.add_argument("--coverage-only", action="store_true", help="仅生成覆盖率报告")
    
    args = parser.parse_args()
    
    # 设置测试环境（包含切换到项目根目录）
    setup_test_environment()
    
    # 检查是否在项目根目录（更新检查方式）
    if not Path("scripts/start.py").exists():
        print("❌ 无法找到项目启动脚本，请确保在正确的项目目录中运行")
        sys.exit(1)
    
    # 仅生成覆盖率报告
    if args.coverage_only:
        generate_coverage_report()
        return
    
    success = False
    
    # 运行指定类型的测试
    if args.type == "unit":
        success = run_unit_tests(args.verbose, not args.no_coverage)
    elif args.type == "integration":
        success = run_integration_tests(args.verbose)
    elif args.type == "gui":
        success = run_gui_tests(args.verbose)
    elif args.type == "performance":
        success = run_performance_tests(args.verbose, args.include_slow)
    elif args.type == "stress":
        success = run_stress_tests(args.verbose)
    elif args.type == "all":
        success = run_all_tests(args.verbose, args.include_slow)
    
    # 生成覆盖率报告
    if not args.no_coverage and args.type in ["unit", "all"]:
        generate_coverage_report()
    
    # 输出报告位置
    print("\n📋 测试报告位置:")
    print(f"  HTML报告: {Path('reports').absolute()}")
    print(f"  覆盖率报告: {Path('htmlcov').absolute()}")
    print(f"  XML覆盖率: {Path('coverage.xml').absolute()}")
    
    # 退出代码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()