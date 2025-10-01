# WhatsApp Agent - Comprehensive Test Strategy

## Overview
This document outlines a comprehensive testing strategy for the Istanbul Medic WhatsApp Agent, covering local development, staging, and production environments.

## Table of Contents
1. [Testing Environments](#testing-environments)
2. [Test Categories](#test-categories)
3. [Local Testing](#local-testing)
4. [Staging Testing](#staging-testing)
5. [Production Testing](#production-testing)
6. [Test Data Management](#test-data-management)
7. [Monitoring & Alerting](#monitoring--alerting)
8. [Rollback Procedures](#rollback-procedures)
9. [Performance Testing](#performance-testing)
10. [Security Testing](#security-testing)

## Testing Environments

### 1. Local Development
- **Purpose**: Development and initial testing
- **URL**: `http://localhost:8000`
- **Database**: SQLite (in-memory or file-based)
- **External Services**: Mocked or test versions
- **Features**: Full debugging, hot reload, test endpoints

### 2. Staging/Preview
- **Purpose**: Pre-production validation
- **URL**: `https://preview.whatsapp-agent.vercel.app` (or similar)
- **Database**: PostgreSQL (staging instance)
- **External Services**: Test/sandbox versions
- **Features**: Production-like environment, limited debugging

### 3. Production
- **Purpose**: Live user interactions
- **URL**: `https://whatsapp-agent.vercel.app`
- **Database**: PostgreSQL (production instance)
- **External Services**: Live services
- **Features**: Full production monitoring, error tracking

## Test Categories

### 1. Unit Tests
- **Scope**: Individual functions and methods
- **Coverage**: Core business logic, utilities, data processing
- **Tools**: pytest, unittest
- **Frequency**: Every commit

### 2. Integration Tests
- **Scope**: Component interactions
- **Coverage**: API endpoints, database operations, external service calls
- **Tools**: pytest, httpx, testcontainers
- **Frequency**: Every PR

### 3. End-to-End Tests
- **Scope**: Complete user workflows
- **Coverage**: Full conversation flows, appointment booking
- **Tools**: Playwright, Selenium
- **Frequency**: Before releases

### 4. Load Tests
- **Scope**: Performance under load
- **Coverage**: Concurrent users, message processing, database performance
- **Tools**: Locust, Artillery
- **Frequency**: Weekly

### 5. Security Tests
- **Scope**: Vulnerability assessment
- **Coverage**: Input validation, authentication, data protection
- **Tools**: OWASP ZAP, custom scripts
- **Frequency**: Monthly

## Local Testing

### Prerequisites
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your test credentials

# Start local services
python -m uvicorn app.app:app --reload --host 0.0.0.0 --port 8000
```

### Test Execution

#### 1. Automated Endpoint Testing
```bash
# Run comprehensive endpoint tests
python test_endpoints.py

# Run specific test categories
python -m pytest tests/unit/
python -m pytest tests/integration/
python -m pytest tests/e2e/
```

#### 2. Manual Testing Checklist

**Health Checks**
- [ ] `GET /health` returns 200
- [ ] Health check includes timestamp and version
- [ ] Database connectivity is verified

**Webhook Testing**
- [ ] `GET /api/webhook` returns verification response
- [ ] `POST /api/webhook` processes Twilio webhooks
- [ ] `POST /whatsapp/webhook` processes WhatsApp messages
- [ ] Form data parsing works correctly
- [ ] Error handling returns proper XML responses

**Chat Interface Testing**
- [ ] `POST /chat/` processes chat messages
- [ ] `POST /chat/stream` streams responses
- [ ] Media URLs are handled correctly
- [ ] Rate limiting works as expected

**Agent Functionality Testing**
- [ ] Intent detection works for scheduling
- [ ] Intent detection works for general queries
- [ ] Intent detection works for cancellations
- [ ] Session memory persists across messages
- [ ] Reset functionality works correctly

**Appointment Scheduling Flow**
- [ ] Initial greeting and consent request
- [ ] Information collection (name, phone, email)
- [ ] Day/time selection
- [ ] Calendar event creation
- [ ] Confirmation and follow-up

**Questionnaire Flow**
- [ ] Post-booking questions appear
- [ ] Skip functionality works
- [ ] Question categories are covered
- [ ] Responses are stored correctly

#### 3. Test Scenarios

**Happy Path Scenarios**
1. Complete appointment booking
2. General service inquiry
3. Appointment cancellation
4. Question skipping
5. Multi-language support

**Edge Cases**
1. Invalid phone number formats
2. Missing required information
3. Very long messages
4. Special characters and emojis
5. Rapid message sequences
6. Network timeouts

**Error Scenarios**
1. Database connection failures
2. External service unavailability
3. Invalid webhook data
4. Rate limit exceeded
5. Malformed requests

## Staging Testing

### Deployment Process
1. **Code Review**: All changes reviewed and approved
2. **Automated Tests**: CI/CD pipeline runs all tests
3. **Staging Deployment**: Automatic deployment to preview environment
4. **Smoke Tests**: Basic functionality verification
5. **Integration Tests**: External service integration testing
6. **User Acceptance Testing**: Manual testing by stakeholders

### Staging Test Checklist

**Environment Validation**
- [ ] Environment variables are correctly set
- [ ] Database connections are working
- [ ] External services are accessible
- [ ] Logging and monitoring are active
- [ ] Error tracking is configured

**Functional Testing**
- [ ] All endpoints respond correctly
- [ ] Agent responses are appropriate
- [ ] Session management works
- [ ] Data persistence is correct
- [ ] Error handling is graceful

**Performance Testing**
- [ ] Response times are acceptable (< 2s)
- [ ] Memory usage is stable
- [ ] Database queries are optimized
- [ ] Rate limiting works correctly
- [ ] Concurrent users are handled

**Security Testing**
- [ ] Input validation is working
- [ ] Rate limiting prevents abuse
- [ ] Sensitive data is protected
- [ ] Webhook signatures are validated
- [ ] CORS policies are correct

## Production Testing

### Pre-Production Checklist
- [ ] All staging tests passed
- [ ] Performance benchmarks met
- [ ] Security scan completed
- [ ] Rollback plan prepared
- [ ] Monitoring alerts configured
- [ ] Team notified of deployment

### Production Monitoring
- [ ] Health check endpoints monitored
- [ ] Error rates tracked
- [ ] Response times measured
- [ ] Database performance monitored
- [ ] External service status checked
- [ ] User feedback collected

## Success Criteria

### Technical Metrics
- [ ] 99.9% uptime
- [ ] < 2s response time (95th percentile)
- [ ] < 1% error rate
- [ ] All endpoints responding correctly

### Functional Metrics
- [ ] Appointment bookings successful
- [ ] User inquiries handled appropriately
- [ ] Session memory working correctly
- [ ] Error messages helpful and clear

### Business Metrics
- [ ] User satisfaction with responses
- [ ] Successful appointment conversions
- [ ] System reliability for business operations
- [ ] No critical issues reported

---

**Last Updated**: September 29, 2025  
**Version**: 1.0  
**Maintainer**: Development Team
