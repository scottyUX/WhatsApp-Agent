# 🚀 Test Framework Quick Reference

## Essential Commands

```bash
# Run all tests
python scripts/run_tests.py all

# Run specific test types
python scripts/run_tests.py unit          # Fast unit tests (19 tests)
python scripts/run_tests.py integration   # Integration tests (13 tests)
python scripts/run_tests.py e2e          # End-to-end tests
python scripts/run_tests.py api          # API tests

# Pre-deployment checks
python scripts/pre_deploy_check.py

# Direct pytest commands
pytest tests/test_unit.py -v             # Run unit tests
pytest -m unit tests/ -v                 # Run by marker
pytest tests/ --cov=app                  # Run with coverage
```

## Test Categories

| Marker | Purpose | Speed | Count |
|--------|---------|-------|-------|
| `@pytest.mark.unit` | Individual components | Fast | 19 ✅ |
| `@pytest.mark.integration` | Component interactions | Medium | 13 |
| `@pytest.mark.e2e` | Full workflows | Slow | - |
| `@pytest.mark.api` | API endpoints | Medium | - |

## File Structure

```
tests/
├── conftest.py              # Shared fixtures
├── test_unit.py            # Unit tests (19) ✅
├── test_integration.py     # Integration tests (13)
├── test_e2e.py            # E2E tests
├── test_api.py            # API tests
└── data/                  # Test data

scripts/
├── run_tests.py           # Test runner
└── pre_deploy_check.py    # Pre-deployment checks
```

## Writing Tests

### Unit Test Template
```python
@pytest.mark.unit
class TestMyComponent:
    def test_my_function(self, sample_data):
        result = my_function(sample_data)
        assert result == expected_value
```

### Integration Test Template
```python
@pytest.mark.integration
class TestMyIntegration:
    def test_component_interaction(self, mock_external_service):
        result = component_a.process(component_b.get_data())
        assert result.success
```

## Common Fixtures

```python
# Use these in your tests
sample_patient_profile      # Patient data
sample_conversation_state   # Conversation state
mock_openai_response       # OpenAI API mock
mock_twilio_message        # Twilio message mock
test_app                   # FastAPI test client
```

## Debugging

```bash
# Run specific test with verbose output
pytest tests/test_unit.py::TestValidators::test_email_validation_valid -v -s

# Run with debugger
pytest tests/test_unit.py -v -s --pdb

# Check coverage
pytest tests/ --cov=app --cov-report=term-missing
```

## Current Status

- ✅ **Unit Tests**: 19/19 passing
- ⚠️ **Integration Tests**: 5/13 passing (needs updates)
- ✅ **Test Framework**: Fully functional
- ✅ **Pre-deployment**: Working
- ⚠️ **Code Formatting**: Needs `black .`

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Import errors | Run from project root, check `__init__.py` files |
| Test failures | Check if implementation changed, update assertions |
| Mock errors | Update mock paths to match actual implementation |
| Slow tests | Use mocks for external dependencies |

---

*For detailed documentation, see `docs/TESTING.md`*
