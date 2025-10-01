# Testing Guide

## Overview

This guide provides comprehensive testing procedures for the WhatsApp Medical Agent system, covering unit tests, integration tests, and end-to-end testing scenarios.

## Table of Contents

- [Testing Strategy](#testing-strategy)
- [Test Environment Setup](#test-environment-setup)
- [Unit Testing](#unit-testing)
- [Integration Testing](#integration-testing)
- [End-to-End Testing](#end-to-end-testing)
- [Database Testing](#database-testing)
- [API Testing](#api-testing)
- [Performance Testing](#performance-testing)
- [Test Automation](#test-automation)
- [Troubleshooting](#troubleshooting)

## Testing Strategy

### Test Pyramid
```
    ┌─────────────────┐
    │   E2E Tests     │  ← Few, high-level
    │   (Manual)      │
    ├─────────────────┤
    │ Integration     │  ← Some, medium-level
    │ Tests           │
    ├─────────────────┤
    │   Unit Tests    │  ← Many, low-level
    │   (Automated)   │
    └─────────────────┘
```

### Test Categories
1. **Unit Tests**: Individual component testing
2. **Integration Tests**: Component interaction testing
3. **End-to-End Tests**: Full user journey testing
4. **Database Tests**: Data persistence and retrieval
5. **API Tests**: Endpoint functionality and responses
6. **Performance Tests**: Load and stress testing

## Test Environment Setup

### 1. Local Development
```bash
# Clone repository
git clone https://github.com/your-org/WhatsApp-Agent.git
cd WhatsApp-Agent

# Install dependencies
pip install -r requirements.txt

# Install test dependencies
pip install pytest pytest-asyncio httpx

# Set up test environment
cp .env.example .env.test
# Edit .env.test with test values
```

### 2. Test Database
```bash
# Use separate test database
DATABASE_URL=postgresql://user:pass@localhost:5432/whatsapp_agent_test
```

### 3. Test Configuration
```python
# test_config.py
import os

# Test environment variables
os.environ["ENVIRONMENT"] = "testing"
os.environ["DEBUG"] = "true"
os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test_db"
```

## Unit Testing

### 1. Agent Testing
```python
# tests/test_agents/test_scheduling_agent.py
import pytest
from app.agents.specialized_agents.scheduling_agent import agent

@pytest.mark.asyncio
async def test_scheduling_agent_response():
    """Test scheduling agent responds appropriately."""
    result = await agent.run("I want to schedule a consultation")
    assert "Anna" in result
    assert "consultation" in result.lower()

@pytest.mark.asyncio
async def test_phone_validation():
    """Test phone number validation."""
    # Test valid numbers
    valid_numbers = ["+1 415 555 2671", "+44 20 7946 0958"]
    for number in valid_numbers:
        result = await agent.run(f"My phone number is {number}")
        assert "thank you" in result.lower()
    
    # Test invalid numbers
    invalid_numbers = ["+1234", "1234567890"]
    for number in invalid_numbers:
        result = await agent.run(f"My phone number is {number}")
        assert "complete phone number" in result.lower()
```

### 2. Service Testing
```python
# tests/test_services/test_message_service.py
import pytest
from app.services.message_service import MessageService
from app.services.history_service import HistoryService

@pytest.mark.asyncio
async def test_whatsapp_message_handling():
    """Test WhatsApp message processing."""
    # Mock dependencies
    history_service = Mock(spec=HistoryService)
    message_service = MessageService(history_service)
    
    result = await message_service.handle_incoming_whatsapp_message(
        phone_number="+1234567890",
        body="Hello, I want to schedule a consultation"
    )
    
    assert "Anna" in result
    assert history_service.store_message.called

@pytest.mark.asyncio
async def test_chat_message_handling():
    """Test chat message processing."""
    history_service = Mock(spec=HistoryService)
    message_service = MessageService(history_service)
    
    result = await message_service.handle_incoming_chat_message(
        user_id="test_user",
        content="Hello, I need help"
    )
    
    assert "Anna" in result
    assert history_service.store_message.called
```

### 3. Database Testing
```python
# tests/test_database/test_repositories.py
import pytest
from app.database.repositories.user_repository import UserRepository
from app.database.repositories.message_repository import MessageRepository

@pytest.fixture
def db_session():
    """Create test database session."""
    # Setup test database
    pass

def test_user_creation(db_session):
    """Test user creation."""
    user_repo = UserRepository(db_session)
    user = user_repo.create(phone_number="+1234567890", name="Test User")
    
    assert user.phone_number == "+1234567890"
    assert user.name == "Test User"
    assert user.id is not None

def test_message_creation(db_session):
    """Test message creation."""
    message_repo = MessageRepository(db_session)
    message = message_repo.create(
        user_id="test-user-id",
        direction="incoming",
        body="Test message"
    )
    
    assert message.direction == "incoming"
    assert message.body == "Test message"
    assert message.id is not None
```

## Integration Testing

### 1. API Integration Tests
```python
# tests/test_integration/test_api.py
import pytest
import httpx
from fastapi.testclient import TestClient
from app.app import app

client = TestClient(app)

def test_webhook_endpoint():
    """Test webhook endpoint integration."""
    response = client.post(
        "/api/webhook",
        data={
            "From": "+1234567890",
            "Body": "Hello, I want to schedule a consultation"
        }
    )
    
    assert response.status_code == 200
    assert "Anna" in response.text

def test_chat_endpoint():
    """Test chat endpoint integration."""
    response = client.post(
        "/chat/",
        json={
            "content": "Hello, I want to schedule an appointment",
            "media_urls": [],
            "audio_urls": []
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "content" in data
    assert "Anna" in data["content"]

def test_chat_streaming_endpoint():
    """Test chat streaming endpoint integration."""
    response = client.post(
        "/chat/stream",
        json={
            "content": "I need help with my medical consultation",
            "media_urls": [],
            "audio_urls": []
        }
    )
    
    assert response.status_code == 200
    assert "Anna" in response.text
```

### 2. Database Integration Tests
```python
# tests/test_integration/test_database.py
import pytest
from app.database.db import get_db
from app.services.history_service import HistoryService
from app.services.message_service import MessageService

@pytest.mark.asyncio
async def test_message_flow():
    """Test complete message flow with database."""
    # Get database session
    db = next(get_db())
    
    # Create services
    history_service = HistoryService(db)
    message_service = MessageService(history_service)
    
    # Test WhatsApp message
    result = await message_service.handle_incoming_whatsapp_message(
        phone_number="+1234567890",
        body="Hello, I want to schedule a consultation"
    )
    
    # Verify database records
    user = history_service.get_user_by_phone("+1234567890")
    assert user is not None
    
    messages = history_service.get_message_history(user.id, 5)
    assert len(messages) >= 2  # incoming + outgoing
    
    # Test chat message
    chat_result = await message_service.handle_incoming_chat_message(
        user_id="test_chat_user",
        content="Hello, I need help"
    )
    
    # Verify chat user creation
    chat_user = history_service.get_user_by_phone("chat_test_chat_user")
    assert chat_user is not None
```

## End-to-End Testing

### 1. WhatsApp Flow Testing
```python
# tests/test_e2e/test_whatsapp_flow.py
import pytest
import httpx

@pytest.mark.asyncio
async def test_complete_consultation_flow():
    """Test complete consultation scheduling flow."""
    base_url = "http://localhost:8000"
    
    # Step 1: Initial contact
    response = await httpx.post(
        f"{base_url}/api/webhook",
        data={
            "From": "+1234567890",
            "Body": "Hello, I want to schedule a consultation"
        }
    )
    assert response.status_code == 200
    assert "Anna" in response.text
    
    # Step 2: Provide name
    response = await httpx.post(
        f"{base_url}/api/webhook",
        data={
            "From": "+1234567890",
            "Body": "My name is John Doe"
        }
    )
    assert response.status_code == 200
    assert "John" in response.text
    
    # Step 3: Provide phone number
    response = await httpx.post(
        f"{base_url}/api/webhook",
        data={
            "From": "+1234567890",
            "Body": "My phone number is +1 415 555 2671"
        }
    )
    assert response.status_code == 200
    assert "thank you" in response.text.lower()
    
    # Step 4: Provide email
    response = await httpx.post(
        f"{base_url}/api/webhook",
        data={
            "From": "+1234567890",
            "Body": "My email is john@example.com"
        }
    )
    assert response.status_code == 200
    assert "email" in response.text.lower()
```

### 2. Chat Flow Testing
```python
# tests/test_e2e/test_chat_flow.py
import pytest
import httpx

@pytest.mark.asyncio
async def test_chat_consultation_flow():
    """Test complete chat consultation flow."""
    base_url = "http://localhost:8000"
    
    # Step 1: Initial contact
    response = await httpx.post(
        f"{base_url}/chat/",
        json={
            "content": "Hello, I want to schedule an appointment",
            "media_urls": [],
            "audio_urls": []
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "Anna" in data["content"]
    
    # Step 2: Provide information
    response = await httpx.post(
        f"{base_url}/chat/",
        json={
            "content": "My name is Jane Smith and I need help with hair transplant",
            "media_urls": [],
            "audio_urls": []
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "Jane" in data["content"]
```

## Database Testing

### 1. Database Schema Tests
```python
# tests/test_database/test_schema.py
import pytest
from sqlalchemy import text
from app.database.db import engine

def test_database_connection():
    """Test database connectivity."""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1

def test_tables_exist():
    """Test required tables exist."""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_name IN ('users', 'messages')
        """))
        tables = [row[0] for row in result]
        assert 'users' in tables
        assert 'messages' in tables

def test_table_constraints():
    """Test table constraints."""
    with engine.connect() as conn:
        # Test direction constraint
        result = conn.execute(text("""
            SELECT constraint_name 
            FROM information_schema.check_constraints 
            WHERE constraint_name LIKE '%direction%'
        """))
        constraints = [row[0] for row in result]
        assert len(constraints) > 0
```

### 2. Data Integrity Tests
```python
# tests/test_database/test_integrity.py
import pytest
from app.database.repositories.user_repository import UserRepository
from app.database.repositories.message_repository import MessageRepository

def test_user_message_relationship():
    """Test user-message foreign key relationship."""
    # Create user
    user_repo = UserRepository(db_session)
    user = user_repo.create(phone_number="+1234567890")
    
    # Create message
    message_repo = MessageRepository(db_session)
    message = message_repo.create(
        user_id=user.id,
        direction="incoming",
        body="Test message"
    )
    
    # Verify relationship
    assert message.user_id == user.id

def test_message_direction_constraint():
    """Test message direction constraint."""
    message_repo = MessageRepository(db_session)
    
    # Valid directions should work
    message1 = message_repo.create(
        user_id="test-user-id",
        direction="incoming",
        body="Test message"
    )
    assert message1.direction == "incoming"
    
    message2 = message_repo.create(
        user_id="test-user-id",
        direction="outgoing",
        body="Test message"
    )
    assert message2.direction == "outgoing"
```

## API Testing

### 1. Webhook Testing
```python
# tests/test_api/test_webhook.py
import pytest
from fastapi.testclient import TestClient
from app.app import app

client = TestClient(app)

def test_webhook_get():
    """Test webhook GET endpoint (Twilio verification)."""
    response = client.get("/api/webhook")
    assert response.status_code == 200

def test_webhook_post_valid():
    """Test webhook POST with valid data."""
    response = client.post(
        "/api/webhook",
        data={
            "From": "+1234567890",
            "Body": "Hello, I want to schedule a consultation"
        }
    )
    assert response.status_code == 200
    assert "Anna" in response.text

def test_webhook_post_with_media():
    """Test webhook POST with media."""
    response = client.post(
        "/api/webhook",
        data={
            "From": "+1234567890",
            "Body": "See this image",
            "MediaUrl0": "https://example.com/image.jpg",
            "NumMedia": "1",
            "MediaContentType0": "image/jpeg"
        }
    )
    assert response.status_code == 200

def test_webhook_post_invalid_data():
    """Test webhook POST with invalid data."""
    response = client.post(
        "/api/webhook",
        data={
            "From": "",
            "Body": ""
        }
    )
    # Should still return 200 but with error message
    assert response.status_code == 200
```

### 2. Chat API Testing
```python
# tests/test_api/test_chat.py
import pytest
from fastapi.testclient import TestClient
from app.app import app

client = TestClient(app)

def test_chat_post():
    """Test chat POST endpoint."""
    response = client.post(
        "/chat/",
        json={
            "content": "Hello, I want to schedule an appointment",
            "media_urls": [],
            "audio_urls": []
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "content" in data
    assert "Anna" in data["content"]

def test_chat_stream():
    """Test chat streaming endpoint."""
    response = client.post(
        "/chat/stream",
        json={
            "content": "I need help with my medical consultation",
            "media_urls": [],
            "audio_urls": []
        }
    )
    assert response.status_code == 200
    assert "Anna" in response.text

def test_chat_invalid_json():
    """Test chat endpoint with invalid JSON."""
    response = client.post(
        "/chat/",
        json={
            "content": "Hello"
            # Missing required fields
        }
    )
    # Should still work with defaults
    assert response.status_code == 200
```

## Performance Testing

### 1. Load Testing
```python
# tests/test_performance/test_load.py
import pytest
import asyncio
import httpx
import time

@pytest.mark.asyncio
async def test_concurrent_requests():
    """Test system under concurrent load."""
    base_url = "http://localhost:8000"
    
    async def make_request():
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/chat/",
                json={
                    "content": "Hello, I want to schedule an appointment",
                    "media_urls": [],
                    "audio_urls": []
                }
            )
            return response.status_code
    
    # Test 10 concurrent requests
    start_time = time.time()
    tasks = [make_request() for _ in range(10)]
    results = await asyncio.gather(*tasks)
    end_time = time.time()
    
    # All requests should succeed
    assert all(status == 200 for status in results)
    
    # Should complete within reasonable time
    assert end_time - start_time < 10  # 10 seconds max
```

### 2. Database Performance Testing
```python
# tests/test_performance/test_database.py
import pytest
import time
from app.database.repositories.message_repository import MessageRepository

def test_message_query_performance():
    """Test message query performance."""
    message_repo = MessageRepository(db_session)
    
    # Create test user
    user_id = "test-user-id"
    
    # Create test messages
    for i in range(100):
        message_repo.create(
            user_id=user_id,
            direction="incoming",
            body=f"Test message {i}"
        )
    
    # Test query performance
    start_time = time.time()
    messages = message_repo.get_recent_by_user(user_id, 10)
    end_time = time.time()
    
    # Query should be fast
    assert end_time - start_time < 0.1  # 100ms max
    assert len(messages) == 10
```

## Test Automation

### 1. GitHub Actions
```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-asyncio httpx
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=app
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

### 2. Test Commands
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_agents/test_scheduling_agent.py

# Run with coverage
pytest --cov=app

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_agents/test_scheduling_agent.py::test_phone_validation
```

## Troubleshooting

### Common Test Issues

#### 1. Database Connection Issues
**Symptoms**: Tests fail with database connection errors
**Solutions**:
- Ensure test database is running
- Check DATABASE_URL configuration
- Verify database permissions
- Use test-specific database

#### 2. Async Test Issues
**Symptoms**: Async tests hang or fail
**Solutions**:
- Use `pytest-asyncio` plugin
- Mark async tests with `@pytest.mark.asyncio`
- Ensure proper async/await usage
- Check for unclosed connections

#### 3. Mock Issues
**Symptoms**: Tests fail due to external dependencies
**Solutions**:
- Mock external API calls
- Use test doubles for databases
- Mock file system operations
- Use dependency injection

#### 4. Environment Issues
**Symptoms**: Tests behave differently in different environments
**Solutions**:
- Use consistent test environment
- Mock environment variables
- Use test-specific configuration
- Isolate test data

### Test Data Management

#### 1. Test Fixtures
```python
# conftest.py
import pytest
from app.database.db import SessionLocal

@pytest.fixture
def db_session():
    """Create test database session."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def test_user(db_session):
    """Create test user."""
    from app.database.repositories.user_repository import UserRepository
    user_repo = UserRepository(db_session)
    return user_repo.create(phone_number="+1234567890", name="Test User")
```

#### 2. Test Cleanup
```python
# conftest.py
@pytest.fixture(autouse=True)
def cleanup_database(db_session):
    """Clean up database after each test."""
    yield
    # Clean up test data
    db_session.execute(text("DELETE FROM messages"))
    db_session.execute(text("DELETE FROM users"))
    db_session.commit()
```

---

*Last updated: October 2025*
*Version: 1.0*
