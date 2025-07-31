#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NetKit ASCII-Safe Test Runner
Safe for CI environments with encoding limitations
"""

import os
import sys
import argparse
import subprocess
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_command(cmd, description, timeout=300):
    """Execute command with ASCII-safe output"""
    print(f"Executing: {description}")
    print(f"Command: {' '.join(cmd)}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, check=True, cwd=project_root, timeout=timeout)
        end_time = time.time()
        print(f"\nSUCCESS: {description} completed (Time: {end_time - start_time:.2f}s)")
        return True
        
    except subprocess.CalledProcessError as e:
        end_time = time.time()
        print(f"\nFAILED: {description} failed (Time: {end_time - start_time:.2f}s)")
        print(f"Error code: {e.returncode}")
        return False
    except subprocess.TimeoutExpired:
        print(f"\nTIMEOUT: {description} timed out after {timeout}s")
        return False

def setup_test_environment():
    """Setup test environment - ASCII safe"""
    print("Setting up test environment...")
    
    # Set test mode
    os.environ['NETKIT_TEST_MODE'] = '1'
    
    # Create necessary directories
    dirs_to_create = ['reports', 'htmlcov']
    for dir_name in dirs_to_create:
        dir_path = project_root / dir_name
        dir_path.mkdir(exist_ok=True)
        print(f"Created directory: {dir_path}")
    
    # Set Python path
    os.environ['PYTHONPATH'] = str(project_root)
    
    print("Test environment setup completed")

def run_unit_tests(verbose=False, coverage=True):
    """Run unit tests - ASCII safe"""
    cmd = [
        "python", "-m", "pytest", 
        "tests/unit/", 
        "-v" if verbose else "-q",
        "--tb=short",
        "-m", "unit"
    ]
    
    if coverage:
        cmd.extend([
            "--cov=netkit", 
            "--cov=gui",
            "--cov-report=xml",
            "--cov-report=html",
            "--html=reports/unit_report.html",
            "--self-contained-html"
        ])
    
    return run_command(cmd, "Unit Tests")

def run_integration_tests(verbose=False):
    """Run integration tests - ASCII safe"""
    cmd = [
        "python", "-m", "pytest", 
        "tests/integration/", 
        "-v" if verbose else "-q",
        "--tb=short",
        "-m", "integration",
        "--html=reports/integration_report.html", 
        "--self-contained-html"
    ]
    
    return run_command(cmd, "Integration Tests")

def main():
    """Main function - ASCII safe"""
    parser = argparse.ArgumentParser(description="NetKit ASCII-Safe Test Runner")
    parser.add_argument("--type", choices=["unit", "integration", "all"], 
                       default="unit", help="Test type")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--no-coverage", action="store_true", help="Skip coverage check")
    
    args = parser.parse_args()
    
    # Setup environment
    setup_test_environment()
    
    success = True
    
    if args.type in ["unit", "all"]:
        print("\n" + "="*50)
        print("Running Unit Tests")
        print("="*50)
        success &= run_unit_tests(args.verbose, not args.no_coverage)
    
    if args.type in ["integration", "all"]:
        print("\n" + "="*50)
        print("Running Integration Tests")
        print("="*50)
        success &= run_integration_tests(args.verbose)
    
    print("\n" + "="*50)
    if success:
        print("ALL TESTS PASSED!")
    else:
        print("SOME TESTS FAILED - CHECK REPORTS")
    print("="*50)
    
    print("\nTest Reports:")
    print(f"  HTML Reports: {Path('reports').absolute()}")
    print(f"  Coverage: {Path('htmlcov').absolute()}")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()