# WhatsApp Agent Documentation

This directory contains comprehensive documentation for the WhatsApp Medical Agent system.

## Documentation Structure

- **[Scheduling Agent](./SCHEDULING_AGENT.md)** - Complete guide to Anna, the consultation scheduling agent
- **[Architecture](./ARCHITECTURE.md)** - System architecture and design patterns
- **[API Reference](./API_REFERENCE.md)** - API endpoints and usage
- **[Deployment Guide](./DEPLOYMENT_GUIDE.md)** - Deployment and configuration guide
- **[Testing Guide](./TESTING_GUIDE.md)** - Testing strategies and procedures
- **[Chat Integration](./CHAT_INTEGRATION.md)** - Website chat integration guide
- **[Database Test Plan](./DB_TEST_PLAN.md)** - Database testing and validation procedures

## Quick Start

1. **For Developers**: Start with [Architecture](./ARCHITECTURE.md) to understand the system design
2. **For QA**: See [Testing Guide](./TESTING_GUIDE.md) for comprehensive test procedures
3. **For Operations**: Check [Deployment Guide](./DEPLOYMENT_GUIDE.md) for production setup
4. **For Frontend**: See [Chat Integration](./CHAT_INTEGRATION.md) for website integration

## Key Features

- **Multi-Agent Architecture** - Manager pattern with specialized agents
- **Dual Integration** - WhatsApp webhook and website chat endpoints
- **Database Integration** - PostgreSQL with full message persistence
- **Session Memory** - SQLite-based conversation persistence (WhatsApp only)
- **Phone Validation** - International phone number validation with libphonenumber
- **Appointment Management** - Full CRUD operations for consultations
- **Patient Questionnaire** - Comprehensive medical information collection
- **Streaming Responses** - Real-time chat responses for website integration
- **User Management** - Automatic user creation and message tracking

## Support

For questions or issues, refer to the specific documentation files or contact the development team.
