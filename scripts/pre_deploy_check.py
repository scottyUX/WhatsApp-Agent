#!/usr/bin/env python3
"""
Pre-deployment check script
Runs all necessary checks before deploying to production
"""
import os
import sys
import subprocess
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_environment_variables():
    """Check that all required environment variables are set"""
    print("🔍 Checking environment variables...")
    
    required_vars = [
        'OPENAI_API_KEY',
        'TWILIO_ACCOUNT_SID',
        'TWILIO_AUTH_TOKEN',
        'GOOGLE_PRIVATE_KEY',
        'GOOGLE_CLIENT_EMAIL',
        'GOOGLE_PROJECT_ID',
        'GOOGLE_CALENDAR_ID'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def check_dependencies():
    """Check that all dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    try:
        import openai
        import fastapi
        import uvicorn
        import twilio
        import googleapiclient
        import pytest
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def run_tests():
    """Run all tests"""
    print("🔍 Running tests...")
    
    try:
        # Run unit tests
        result = subprocess.run([
            'python', '-m', 'pytest', 'tests/test_unit.py', '-v', '--tb=short'
        ], capture_output=True, text=True, check=True)
        print("✅ Unit tests passed")
        
        # Run integration tests
        result = subprocess.run([
            'python', '-m', 'pytest', 'tests/test_integration.py', '-v', '--tb=short'
        ], capture_output=True, text=True, check=True)
        print("✅ Integration tests passed")
        
        # Run API tests
        result = subprocess.run([
            'python', '-m', 'pytest', 'tests/test_api.py', '-v', '--tb=short'
        ], capture_output=True, text=True, check=True)
        print("✅ API tests passed")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False

def run_linting():
    """Run code linting"""
    print("🔍 Running code linting...")
    
    try:
        result = subprocess.run([
            'python', '-m', 'black', '--check', 'app/', 'tests/'
        ], capture_output=True, text=True, check=True)
        print("✅ Code linting passed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Linting failed: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False

def check_file_structure():
    """Check that all required files exist"""
    print("🔍 Checking file structure...")
    
    required_files = [
        'app/app.py',
        'app/agents/manager_agent.py',
        'app/agents/specialized_agents/scheduling_agent_2.py',
        'app/agents/specialized_agents/questionnaire_manager.py',
        'app/agents/specialized_agents/questionnaire_questions.py',
        'app/agents/specialized_agents/scheduling_models.py',
        'app/routers/webhook.py',
        'requirements.txt',
        'vercel.json'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files exist")
        return True

def check_imports():
    """Check that all imports work correctly"""
    print("🔍 Checking imports...")
    
    try:
        # Test critical imports
        from app.app import app
        from app.agents.manager_agent import run_manager
        from app.agents.specialized_agents.scheduling_agent_2 import handle_scheduling_request
        from app.agents.specialized_agents.questionnaire_manager import QuestionnaireManager
        from app.agents.specialized_agents.questionnaire_questions import get_question_by_id
        from app.agents.specialized_agents.scheduling_models import PatientProfile
        print("✅ All imports work correctly")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def check_webhook_endpoint():
    """Check that webhook endpoint is accessible"""
    print("🔍 Checking webhook endpoint...")
    
    try:
        from app.app import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get("/api/health")
        
        if response.status_code == 200:
            print("✅ Webhook endpoint is accessible")
            return True
        else:
            print(f"❌ Webhook endpoint returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Webhook endpoint check failed: {e}")
        return False

def generate_deployment_report():
    """Generate deployment readiness report"""
    print("📊 Generating deployment report...")
    
    report = {
        "timestamp": str(Path().cwd()),
        "checks": {
            "environment_variables": check_environment_variables(),
            "dependencies": check_dependencies(),
            "file_structure": check_file_structure(),
            "imports": check_imports(),
            "webhook_endpoint": check_webhook_endpoint(),
            "linting": run_linting(),
            "tests": run_tests()
        }
    }
    
    # Calculate overall status
    all_passed = all(report["checks"].values())
    report["overall_status"] = "PASS" if all_passed else "FAIL"
    
    # Save report
    with open("deployment_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"📄 Deployment report saved to deployment_report.json")
    return all_passed

def main():
    """Main pre-deployment check"""
    print("🚀 WhatsApp Agent Pre-Deployment Check")
    print("=" * 60)
    
    # Set test environment
    os.environ['TESTING'] = 'true'
    os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', 'test-key')
    os.environ['TWILIO_ACCOUNT_SID'] = os.getenv('TWILIO_ACCOUNT_SID', 'test-sid')
    os.environ['TWILIO_AUTH_TOKEN'] = os.getenv('TWILIO_AUTH_TOKEN', 'test-token')
    os.environ['GOOGLE_PRIVATE_KEY'] = os.getenv('GOOGLE_PRIVATE_KEY', 'test-key')
    os.environ['GOOGLE_CLIENT_EMAIL'] = os.getenv('GOOGLE_CLIENT_EMAIL', 'test@example.com')
    os.environ['GOOGLE_PROJECT_ID'] = os.getenv('GOOGLE_PROJECT_ID', 'test-project')
    os.environ['GOOGLE_CALENDAR_ID'] = os.getenv('GOOGLE_CALENDAR_ID', 'test@example.com')
    
    success = generate_deployment_report()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All checks passed! Ready for deployment.")
        sys.exit(0)
    else:
        print("❌ Some checks failed! Fix issues before deploying.")
        sys.exit(1)

if __name__ == "__main__":
    main()

