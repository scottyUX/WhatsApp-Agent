#!/usr/bin/env python3
"""
Test Setup Check Script
Quick script to verify test environment is properly configured
"""
import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check Python version"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need Python 3.11+")
        return False

def check_dependencies():
    """Check required dependencies"""
    print("\n📦 Checking dependencies...")
    required_packages = [
        'pytest',
        'pytest-cov',
        'pytest-asyncio',
        'fastapi',
        'openai',
        'twilio'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} - OK")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing_packages.append(package)
    
    return len(missing_packages) == 0

def check_test_structure():
    """Check test directory structure"""
    print("\n📁 Checking test structure...")
    
    required_files = [
        'tests/conftest.py',
        'tests/test_unit.py',
        'scripts/run_tests.py',
        'scripts/pre_deploy_check.py',
        'pytest.ini'
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path} - OK")
        else:
            print(f"❌ {file_path} - Missing")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def check_imports():
    """Check if imports work"""
    print("\n🔗 Checking imports...")
    
    try:
        # Test critical imports
        from app.agents.specialized_agents.scheduling_models import PatientProfile
        from utils.validators import validate_email
        from app.agents.specialized_agents.questionnaire_manager import QuestionnaireManager
        print("✅ Core imports - OK")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def check_test_execution():
    """Check if tests can run"""
    print("\n🧪 Checking test execution...")
    
    try:
        result = subprocess.run([
            'python', '-m', 'pytest', 'tests/test_unit.py', '--collect-only', '-q'
        ], capture_output=True, text=True, check=True)
        
        if "19 items" in result.stdout:
            print("✅ Unit tests can be collected - OK")
            return True
        else:
            print("❌ Unit test collection failed")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Test execution failed: {e}")
        return False

def check_environment():
    """Check environment variables"""
    print("\n🌍 Checking environment...")
    
    required_env_vars = [
        'OPENAI_API_KEY',
        'TWILIO_ACCOUNT_SID',
        'TWILIO_AUTH_TOKEN'
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if os.getenv(var):
            print(f"✅ {var} - Set")
        else:
            print(f"⚠️  {var} - Not set (using test defaults)")
            missing_vars.append(var)
    
    return len(missing_vars) == 0

def run_quick_test():
    """Run a quick test to verify everything works"""
    print("\n🚀 Running quick test...")
    
    try:
        result = subprocess.run([
            'python', 'scripts/run_tests.py', 'unit'
        ], capture_output=True, text=True, check=True)
        
        if "All tests passed!" in result.stdout:
            print("✅ Quick test passed - OK")
            return True
        else:
            print("❌ Quick test failed")
            print("STDOUT:", result.stdout)
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Quick test failed: {e}")
        print("STDOUT:", e.stdout)
        return False

def main():
    """Main check function"""
    print("🔍 WhatsApp Agent Test Setup Check")
    print("=" * 50)
    
    checks = [
        check_python_version,
        check_dependencies,
        check_test_structure,
        check_imports,
        check_environment,
        check_test_execution,
        run_quick_test
    ]
    
    passed = 0
    total = len(checks)
    
    for check in checks:
        if check():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All checks passed! Your test environment is ready.")
        print("\nNext steps:")
        print("1. Run tests: python scripts/run_tests.py unit")
        print("2. Read docs: docs/TESTING.md")
        print("3. Start coding!")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\nTroubleshooting:")
        print("1. Install missing dependencies: pip install -r requirements.txt")
        print("2. Check file structure and imports")
        print("3. Set environment variables if needed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
