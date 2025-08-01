#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NetKit 测试质量检查脚本
自动检查测试覆盖率、测试质量等指标
"""

import os
import sys
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any


class TestQualityChecker:
    """测试质量检查器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.reports_dir = project_root / "reports"
        self.coverage_file = project_root / "coverage.xml"
        self.quality_thresholds = {
            'coverage_threshold': 85.0,
            'test_success_rate': 95.0,
            'max_test_duration': 300,  # 5分钟
            'min_test_count': 50
        }
    
    def check_coverage(self) -> Dict[str, Any]:
        """检查代码覆盖率"""
        result = {
            'passed': False,
            'coverage': 0.0,
            'threshold': self.quality_thresholds['coverage_threshold'],
            'details': {}
        }
        
        if not self.coverage_file.exists():
            result['error'] = "覆盖率报告文件不存在"
            return result
        
        try:
            tree = ET.parse(self.coverage_file)
            root = tree.getroot()
            
            # 获取总体覆盖率
            coverage = float(root.get('line-rate', 0)) * 100
            result['coverage'] = round(coverage, 2)
            result['passed'] = coverage >= self.quality_thresholds['coverage_threshold']
            
            # 获取模块覆盖率详情
            packages = root.findall('.//package')
            for package in packages:
                package_name = package.get('name', 'unknown')
                package_coverage = float(package.get('line-rate', 0)) * 100
                result['details'][package_name] = round(package_coverage, 2)
            
        except Exception as e:
            result['error'] = f"解析覆盖率文件失败: {e}"
        
        return result
    
    def check_test_reports(self) -> Dict[str, Any]:
        """检查测试报告"""
        result = {
            'passed': False,
            'test_count': 0,
            'success_rate': 0.0,
            'reports': {}
        }
        
        if not self.reports_dir.exists():
            result['error'] = "测试报告目录不存在"
            return result
        
        total_tests = 0
        total_passed = 0
        
        # 检查HTML报告文件
        report_files = list(self.reports_dir.glob("*_report.html"))
        
        for report_file in report_files:
            report_type = report_file.stem.replace('_report', '')
            try:
                # 简单解析HTML报告（实际项目中可能需要更复杂的解析）
                content = report_file.read_text(encoding='utf-8')
                
                # 提取测试统计信息（这里是简化版本）
                if "passed" in content and "failed" in content:
                    # 假设能从HTML中提取到测试数量
                    result['reports'][report_type] = {
                        'file': str(report_file),
                        'size': report_file.stat().st_size
                    }
                    
            except Exception as e:
                result['reports'][report_type] = {
                    'error': f"解析报告失败: {e}"
                }
        
        # 计算成功率
        if total_tests > 0:
            result['test_count'] = total_tests
            result['success_rate'] = round((total_passed / total_tests) * 100, 2)
            result['passed'] = (
                result['success_rate'] >= self.quality_thresholds['test_success_rate'] and
                total_tests >= self.quality_thresholds['min_test_count']
            )
        
        return result
    
    def check_test_performance(self) -> Dict[str, Any]:
        """检查测试性能"""
        result = {
            'passed': True,
            'warnings': []
        }
        
        # 检查测试文件大小（间接反映测试复杂度）
        test_files = []
        test_dirs = ['tests/unit', 'tests/integration', 'tests/performance']
        
        for test_dir in test_dirs:
            test_path = self.project_root / test_dir
            if test_path.exists():
                test_files.extend(test_path.glob("test_*.py"))
        
        large_files = []
        for test_file in test_files:
            size_kb = test_file.stat().st_size / 1024
            if size_kb > 50:  # 大于50KB的测试文件
                large_files.append({
                    'file': str(test_file.relative_to(self.project_root)),
                    'size_kb': round(size_kb, 1)
                })
        
        if large_files:
            result['warnings'].append(f"发现{len(large_files)}个大型测试文件，建议拆分")
            result['large_files'] = large_files
        
        return result
    
    def generate_quality_report(self) -> Dict[str, Any]:
        """生成质量报告"""
        report = {
            'timestamp': str(Path.cwd()),
            'project': 'NetKit',
            'checks': {}
        }
        
        print("🔍 开始测试质量检查...")
        
        # 检查覆盖率
        print("  📊 检查代码覆盖率...")
        coverage_result = self.check_coverage()
        report['checks']['coverage'] = coverage_result
        
        # 检查测试报告
        print("  📋 检查测试报告...")
        test_result = self.check_test_reports()
        report['checks']['test_reports'] = test_result
        
        # 检查测试性能
        print("  ⚡ 检查测试性能...")
        performance_result = self.check_test_performance()
        report['checks']['performance'] = performance_result
        
        # 计算总体质量得分
        quality_score = self._calculate_quality_score(report['checks'])
        report['quality_score'] = quality_score
        report['passed'] = quality_score >= 80.0
        
        return report
    
    def _calculate_quality_score(self, checks: Dict[str, Any]) -> float:
        """计算质量得分"""
        score = 0.0
        max_score = 100.0
        
        # 覆盖率权重 50%
        coverage = checks.get('coverage', {}).get('coverage', 0)
        score += min(coverage, 100) * 0.5
        
        # 测试成功率权重 30%
        success_rate = checks.get('test_reports', {}).get('success_rate', 0)
        score += min(success_rate, 100) * 0.3
        
        # 性能检查权重 20%
        performance_passed = checks.get('performance', {}).get('passed', False)
        score += (20.0 if performance_passed else 0.0)
        
        return round(score, 1)
    
    def print_quality_report(self, report: Dict[str, Any]):
        """打印质量报告"""
        print("\n" + "="*60)
        print("🏆 NetKit 测试质量报告")
        print("="*60)
        
        # 总体状态
        status = "✅ 通过" if report['passed'] else "❌ 不通过"
        print(f"总体状态: {status}")
        print(f"质量得分: {report['quality_score']}/100")
        print()
        
        # 覆盖率检查
        coverage = report['checks']['coverage']
        if 'error' in coverage:
            print(f"📊 代码覆盖率: ❌ {coverage['error']}")
        else:
            status = "✅" if coverage['passed'] else "❌"
            print(f"📊 代码覆盖率: {status} {coverage['coverage']}% (目标: {coverage['threshold']}%)")
            
            if coverage['details']:
                print("   模块覆盖率详情:")
                for module, cov in coverage['details'].items():
                    print(f"     {module}: {cov}%")
        print()
        
        # 测试报告检查
        test_reports = report['checks']['test_reports']
        if 'error' in test_reports:
            print(f"📋 测试报告: ❌ {test_reports['error']}")
        else:
            status = "✅" if test_reports['passed'] else "❌"
            print(f"📋 测试报告: {status}")
            print(f"   测试数量: {test_reports['test_count']}")
            print(f"   成功率: {test_reports['success_rate']}%")
            
            if test_reports['reports']:
                print("   报告文件:")
                for report_type, info in test_reports['reports'].items():
                    if 'error' in info:
                        print(f"     {report_type}: ❌ {info['error']}")
                    else:
                        size_kb = info['size'] / 1024
                        print(f"     {report_type}: ✅ {size_kb:.1f} KB")
        print()
        
        # 性能检查
        performance = report['checks']['performance']
        status = "✅" if performance['passed'] else "⚠️"
        print(f"⚡ 测试性能: {status}")
        
        if performance['warnings']:
            for warning in performance['warnings']:
                print(f"   ⚠️ {warning}")
                
        if 'large_files' in performance:
            print("   大型测试文件:")
            for file_info in performance['large_files']:
                print(f"     {file_info['file']}: {file_info['size_kb']} KB")
        print()
        
        # 建议
        print("💡 改进建议:")
        if not coverage['passed']:
            print("   - 提高代码覆盖率，添加更多单元测试")
        if not test_reports['passed']:
            print("   - 增加测试用例数量，提高测试成功率")
        if performance['warnings']:
            print("   - 考虑拆分大型测试文件，提高测试可维护性")
        if report['passed']:
            print("   - 测试质量良好，继续保持！")
        
        print("="*60)


def main():
    """主函数"""
    # 确定项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # 创建质量检查器
    checker = TestQualityChecker(project_root)
    
    # 生成质量报告
    report = checker.generate_quality_report()
    
    # 打印报告
    checker.print_quality_report(report)
    
    # 保存报告
    report_file = project_root / "reports" / "quality_report.json"
    report_file.parent.mkdir(exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 详细报告已保存至: {report_file}")
    
    # 返回退出代码
    sys.exit(0 if report['passed'] else 1)


if __name__ == "__main__":
    main()