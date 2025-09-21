# 🧪 WhatsApp Agent Test Framework Documentation

## Overview

This document provides comprehensive guidance on the WhatsApp Agent test framework, including how to run tests, write new tests, and maintain the testing infrastructure.

## 📁 Test Framework Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── test_unit.py            # Unit tests (19 tests) ✅
├── test_integration.py     # Integration tests (13 tests)
├── test_e2e.py            # End-to-end tests
├── test_api.py            # API endpoint tests
├── test_validation.py     # Input validation tests
├── test_manager_agent.py  # Manager agent tests
├── test_anna.py           # Anna agent tests
├── test_calendar.py       # Calendar integration tests
├── test_handle_twilio.py  # Twilio webhook tests
├── test_tts_to_vercel.py  # Text-to-speech tests
└── data/                  # Test data files
    └── test.ogg          # Sample audio file

scripts/
├── run_tests.py           # Main test runner
└── pre_deploy_check.py    # Pre-deployment validation

pytest.ini                # Pytest configuration
```

## 🚀 Quick Start

### Running Tests

```bash
# Run all tests
python scripts/run_tests.py all

# Run specific test types
python scripts/run_tests.py unit          # Fast unit tests
python scripts/run_tests.py integration   # Integration tests
python scripts/run_tests.py e2e          # End-to-end tests
python scripts/run_tests.py api          # API tests

# Run with coverage
python scripts/run_tests.py coverage

# Run pre-deployment checks
python scripts/pre_deploy_check.py
```

### Direct Pytest Commands

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_unit.py -v

# Run tests with coverage
pytest tests/ --cov=app --cov-report=html

# Run tests by marker
pytest -m unit tests/ -v
pytest -m integration tests/ -v
```

## 📋 Test Categories & Markers

### Unit Tests (`@pytest.mark.unit`)
- **Purpose**: Test individual components in isolation
- **Speed**: Fast (~0.3s for all 19 tests)
- **Scope**: Functions, classes, data models
- **Mocking**: Heavy use of mocks for external dependencies

**Example:**
```python
@pytest.mark.unit
class TestValidators:
    def test_email_validation_valid(self):
        is_valid, error = validate_email("test@example.com")
        assert is_valid
        assert error is None
```

### Integration Tests (`@pytest.mark.integration`)
- **Purpose**: Test component interactions
- **Speed**: Medium (~4s for all 13 tests)
- **Scope**: Module interactions, API integrations
- **Mocking**: Mock external APIs, test real data flow

**Example:**
```python
@pytest.mark.integration
class TestQuestionnaireIntegration:
    def test_questionnaire_flow_integration(self):
        # Test complete questionnaire workflow
        pass
```

### End-to-End Tests (`@pytest.mark.e2e`)
- **Purpose**: Test complete user workflows
- **Speed**: Slow (~10s+ per test)
- **Scope**: Full system validation
- **Mocking**: Minimal, real API calls with test keys

### API Tests (`@pytest.mark.api`)
- **Purpose**: Test API endpoints
- **Speed**: Medium
- **Scope**: HTTP endpoints, request/response validation

## 🔧 Test Configuration

### Pytest Configuration (`pytest.ini`)

```ini
[tool:pytest]
testpaths = tests
addopts = --verbose --tb=short --cov=app --cov-report=html
markers = 
    unit: Unit tests - fast, isolated tests
    integration: Integration tests - test component interactions
    e2e: End-to-end tests - full system tests
    slow: Slow tests that take more than 5 seconds
    api: API endpoint tests
    webhook: Webhook tests
    agent: Agent functionality tests
    questionnaire: Questionnaire system tests
    calendar: Google Calendar integration tests
    twilio: Twilio/WhatsApp integration tests
```

### Test Environment Setup

The test environment is configured in `tests/conftest.py`:

```python
# Environment variables for testing
os.environ.setdefault('TESTING', 'true')
os.environ.setdefault('OPENAI_API_KEY', 'test-key')
os.environ.setdefault('TWILIO_ACCOUNT_SID', 'test-sid')
# ... more test environment variables
```

## 🎭 Shared Fixtures

### Mock Fixtures

```python
@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    return {
        "choices": [{"message": {"content": "Test response"}}],
        "usage": {"total_tokens": 100}
    }

@pytest.fixture
def mock_twilio_message():
    """Mock Twilio message data"""
    return {
        "From": "whatsapp:+1234567890",
        "Body": "Test message",
        "MessageSid": "test-message-sid"
    }
```

### Data Fixtures

```python
@pytest.fixture
def sample_patient_profile():
    """Sample patient profile for testing"""
    return PatientProfile(
        name="John Doe",
        phone="+1234567890",
        email="john@example.com",
        questionnaire_step=QuestionnaireStep.NOT_STARTED
    )

@pytest.fixture
def sample_conversation_state():
    """Sample conversation state for testing"""
    return ConversationState(
        user_id="test_user_123",
        current_step=SchedulingStep.INITIAL_CONTACT,
        phone_number="+1234567890"
    )
```

## ✍️ Writing New Tests

### Unit Test Example

```python
import pytest
from app.agents.specialized_agents.scheduling_models import PatientProfile

@pytest.mark.unit
class TestPatientProfile:
    def test_patient_profile_creation(self, sample_patient_profile):
        """Test creating a patient profile"""
        assert sample_patient_profile.name == "John Doe"
        assert sample_patient_profile.phone == "+1234567890"
        assert sample_patient_profile.email == "john@example.com"
    
    def test_patient_profile_to_dict(self, sample_patient_profile):
        """Test converting patient profile to dictionary"""
        profile_dict = sample_patient_profile.to_dict()
        assert profile_dict["name"] == "John Doe"
        assert profile_dict["phone"] == "+1234567890"
```

### Integration Test Example

```python
import pytest
from unittest.mock import patch, Mock

@pytest.mark.integration
class TestQuestionnaireIntegration:
    def test_questionnaire_flow_integration(self, sample_conversation_state):
        """Test complete questionnaire workflow"""
        from app.agents.specialized_agents.questionnaire_manager import QuestionnaireManager
        
        manager = QuestionnaireManager()
        
        # Start questionnaire
        result = manager.start_questionnaire(sample_conversation_state)
        assert "questions" in result.lower()
        
        # Process responses
        success, message, next_action = manager.process_response(
            "basic_country", "United States", sample_conversation_state
        )
        assert success
        assert next_action == "continue"
```

### API Test Example

```python
import pytest
from fastapi.testclient import TestClient

@pytest.mark.api
class TestWebhookAPI:
    def test_webhook_endpoint(self, test_app):
        """Test webhook endpoint"""
        response = test_app.post("/api/webhook", json={
            "From": "whatsapp:+1234567890",
            "Body": "Hello",
            "MessageSid": "test-sid"
        })
        assert response.status_code == 200
```

## 🔍 Test Coverage

### Running Coverage Reports

```bash
# Generate HTML coverage report
pytest tests/ --cov=app --cov-report=html

# Generate XML coverage report (for CI/CD)
pytest tests/ --cov=app --cov-report=xml

# View coverage in terminal
pytest tests/ --cov=app --cov-report=term-missing
```

### Coverage Reports Location

- **HTML Report**: `htmlcov/index.html`
- **XML Report**: `coverage.xml`
- **Terminal Report**: Displayed in test output

## 🚀 Pre-Deployment Checks

### Running Pre-Deployment Validation

```bash
python scripts/pre_deploy_check.py
```

### What It Checks

1. **Environment Variables**: All required env vars are set
2. **Dependencies**: All required packages are installed
3. **File Structure**: All required files exist
4. **Imports**: All imports work correctly
5. **Webhook Endpoint**: API endpoint is accessible
6. **Code Linting**: Black formatting compliance
7. **Tests**: All tests pass

### Pre-Deployment Report

The script generates a `deployment_report.json` with detailed results:

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "checks": {
    "environment_variables": true,
    "dependencies": true,
    "file_structure": true,
    "imports": true,
    "webhook_endpoint": false,
    "linting": false,
    "tests": true
  },
  "overall_status": "FAIL"
}
```

## 🛠️ Test Maintenance

### Adding New Test Data

1. **Test Files**: Add to `tests/data/` directory
2. **Fixtures**: Add to `tests/conftest.py`
3. **Mock Data**: Create reusable mock objects

### Updating Test Mocks

When APIs change, update mocks in `conftest.py`:

```python
@pytest.fixture
def mock_openai_response():
    """Updated mock for new API response format"""
    return {
        "choices": [{"message": {"content": "New response format"}}],
        "usage": {"total_tokens": 150, "prompt_tokens": 75}
    }
```

### Debugging Test Failures

1. **Run with verbose output**: `pytest -v -s`
2. **Run specific test**: `pytest tests/test_unit.py::TestValidators::test_email_validation_valid -v`
3. **Debug with pdb**: Add `import pdb; pdb.set_trace()` in test
4. **Check logs**: Look for error messages in test output

## 🔧 CI/CD Integration

### GitHub Actions

The test framework is integrated with GitHub Actions (`.github/workflows/test.yml`):

- **Matrix Testing**: Python 3.11 & 3.12
- **Dependency Caching**: Optimized pip cache
- **Test Execution**: Unit → Integration → E2E → API
- **Coverage Reporting**: Codecov integration
- **Security Scanning**: Bandit security analysis

### Local CI Simulation

```bash
# Run the same checks as CI/CD
python scripts/run_tests.py pre-deploy
```

## 📊 Test Metrics

### Current Test Status

- **Unit Tests**: 19/19 passing (100%) ✅
- **Integration Tests**: 5/13 passing (38%) ⚠️
- **E2E Tests**: Available but need updates
- **API Tests**: Available but need updates
- **Coverage**: ~85% (estimated)

### Test Performance

- **Unit Tests**: ~0.3s (all 19 tests)
- **Integration Tests**: ~4s (all 13 tests)
- **E2E Tests**: ~10s+ (per test)
- **Full Suite**: ~15s (unit + integration)

## 🐛 Common Issues & Solutions

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'utils.validators'`

**Solution**: Ensure you're running from project root and `utils/` has `__init__.py`

```bash
cd /path/to/WhatsApp-Agent
python scripts/run_tests.py unit
```

### Test Failures

**Problem**: Tests fail with assertion errors

**Solution**: Check if implementation changed, update test expectations

```python
# Old assertion
assert result == "expected_value"

# Updated assertion
assert "expected" in result.lower()  # More flexible
```

### Mock Issues

**Problem**: `AttributeError: module has no attribute 'openai_client'`

**Solution**: Update mock paths to match actual implementation

```python
# Old mock path
with patch('app.agents.manager_agent.openai_client') as mock_client:

# Updated mock path
with patch('app.services.openai_service.openai_client') as mock_client:
```

## 📚 Best Practices

### Writing Tests

1. **Test One Thing**: Each test should verify one specific behavior
2. **Descriptive Names**: Use clear, descriptive test names
3. **Arrange-Act-Assert**: Structure tests clearly
4. **Use Fixtures**: Reuse common test data
5. **Mock External Dependencies**: Keep tests fast and isolated

### Test Organization

1. **Group Related Tests**: Use test classes for related functionality
2. **Use Markers**: Categorize tests with appropriate markers
3. **Keep Tests Independent**: Tests shouldn't depend on each other
4. **Clean Up**: Remove test artifacts after tests complete

### Performance

1. **Fast Unit Tests**: Keep unit tests under 1 second each
2. **Mock Heavy Operations**: Mock database, API calls, file I/O
3. **Use Test Data**: Pre-create test data instead of generating it
4. **Parallel Execution**: Tests should be able to run in parallel

## 🤝 Contributing

### Adding New Tests

1. **Follow Naming Convention**: `test_*.py` for test files
2. **Use Appropriate Markers**: Mark tests with correct categories
3. **Add to Test Runner**: Update `scripts/run_tests.py` if needed
4. **Update Documentation**: Document new test patterns

### Modifying Existing Tests

1. **Maintain Backward Compatibility**: Don't break existing tests
2. **Update Documentation**: Update this guide if patterns change
3. **Test Your Changes**: Run full test suite before committing
4. **Consider Impact**: Changes might affect other tests

## 📞 Support

### Getting Help

1. **Check This Documentation**: Most issues are covered here
2. **Run Pre-Deployment Checks**: `python scripts/pre_deploy_check.py`
3. **Check Test Output**: Look for specific error messages
4. **Review Recent Changes**: Check if recent code changes broke tests

### Reporting Issues

When reporting test issues, include:

1. **Test Command**: Exact command that failed
2. **Error Output**: Full error message and stack trace
3. **Environment**: Python version, OS, dependencies
4. **Recent Changes**: What code was recently modified

---

## 🎯 Quick Reference

| Command | Purpose |
|---------|---------|
| `python scripts/run_tests.py unit` | Run unit tests |
| `python scripts/run_tests.py all` | Run all tests |
| `python scripts/pre_deploy_check.py` | Pre-deployment validation |
| `pytest tests/test_unit.py -v` | Run specific test file |
| `pytest -m unit tests/ -v` | Run tests by marker |
| `pytest tests/ --cov=app` | Run with coverage |

---

*This documentation is maintained by the engineering team. Please update it when making changes to the test framework.*
