# Deployment Guide

## Overview

This guide covers deploying the WhatsApp Medical Agent to production environments, including Vercel deployment, environment configuration, and monitoring setup.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Vercel Deployment](#vercel-deployment)
- [Database Configuration](#database-configuration)
- [Twilio Configuration](#twilio-configuration)
- [Google Calendar Setup](#google-calendar-setup)
- [Testing Deployment](#testing-deployment)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Accounts
- **Vercel Account**: For hosting the application
- **Supabase Account**: For PostgreSQL database
- **Twilio Account**: For WhatsApp integration
- **Google Cloud Account**: For Calendar API access
- **OpenAI Account**: For AI agent functionality

### Required Tools
- **Git**: Version control
- **Node.js**: For Vercel CLI (optional)
- **Python 3.11+**: Local development

## Environment Setup

### 1. Clone Repository
```bash
git clone https://github.com/your-org/WhatsApp-Agent.git
cd WhatsApp-Agent
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file with the following variables:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Twilio Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=whatsapp:+14155238886
WEBHOOK_VERIFY_TOKEN=your_webhook_verify_token

# Database Configuration
DATABASE_URL=postgresql://postgres:password@db.xxx.supabase.co:5432/postgres

# Google Calendar Configuration
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}
GOOGLE_CALENDAR_ID=your_calendar_id

# Vector Store Configuration
VECTOR_STORE_EN=your_pinecone_index_name
VECTOR_STORE_DE=your_pinecone_index_name_de
VECTOR_STORE_ES=your_pinecone_index_name_es

# Application Configuration
ENVIRONMENT=production
DEBUG=false
PORT=8000

# Test Configuration
TEST_PHONE_NUMBERS=+1234567890,+1987654321
```

## Vercel Deployment

### 1. Install Vercel CLI
```bash
npm install -g vercel
```

### 2. Login to Vercel
```bash
vercel login
```

### 3. Deploy Application
```bash
vercel --prod
```

### 4. Configure Environment Variables
In Vercel dashboard:
1. Go to your project settings
2. Navigate to "Environment Variables"
3. Add all required environment variables
4. Set environment to "Production"

### 5. Update vercel.json
Ensure your `vercel.json` is configured correctly:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "app/app.py",
      "use": "@vercel/python",
      "config": {
        "runtime": "python3.11",
        "installCommand": "pip install -r requirements.txt"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app/app.py"
    }
  ]
}
```

## Database Configuration

### 1. Supabase Setup
1. Create a new Supabase project
2. Go to Settings > Database
3. Copy the connection string
4. Update `DATABASE_URL` in environment variables

### 2. Database Schema
The application will automatically create the required tables:
- `users` - User information
- `messages` - Message history

### 3. Connection Pooling
The application uses connection pooling for better performance:
- **Pool Type**: StaticPool
- **Pre-ping**: Enabled
- **Recycle Time**: 300 seconds

## Twilio Configuration

### 1. WhatsApp Sandbox Setup
1. Go to Twilio Console > Messaging > Try it out > Send a WhatsApp message
2. Follow the setup instructions
3. Note your sandbox number

### 2. Webhook Configuration
1. In Twilio Console, go to Messaging > Settings > WhatsApp sandbox settings
2. Set webhook URL to: `https://your-app.vercel.app/api/webhook`
3. Set HTTP method to: `POST`
4. Save configuration

### 3. Phone Number Format
- **Input Format**: `+1234567890` (without `whatsapp:` prefix)
- **Validation**: Uses libphonenumber for international validation
- **Storage**: Stored as-is in database

## Google Calendar Setup

### 1. Service Account Creation
1. Go to Google Cloud Console
2. Create a new project or select existing
3. Enable Google Calendar API
4. Create a service account
5. Download the JSON credentials
6. Add the JSON as `GOOGLE_SERVICE_ACCOUNT_JSON` environment variable

### 2. Calendar Permissions
1. Share your calendar with the service account email
2. Grant "Make changes to events" permission
3. Set `GOOGLE_CALENDAR_ID` to your calendar ID

### 3. Calendar ID Format
- **Primary Calendar**: `primary`
- **Custom Calendar**: `your-calendar-id@group.calendar.google.com`

## Testing Deployment

### 1. Health Check
```bash
curl https://your-app.vercel.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-01T21:00:00Z",
  "version": "1.0.0"
}
```

### 2. Webhook Test
```bash
curl -X POST "https://your-app.vercel.app/api/webhook" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=+1234567890&Body=Hello, I want to schedule a consultation"
```

### 3. Chat Endpoint Test
```bash
curl -X POST "https://your-app.vercel.app/chat/" \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello, I want to schedule an appointment", "media_urls": [], "audio_urls": []}'
```

### 4. Database Test
```bash
curl -X POST "https://your-app.vercel.app/api/webhook" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=+1234567890&Body=Test database integration"
```

Then check your Supabase database for the new user and messages.

## Monitoring

### 1. Vercel Analytics
- **Function Logs**: Available in Vercel dashboard
- **Performance Metrics**: Response times and error rates
- **Usage Statistics**: Request counts and patterns

### 2. Database Monitoring
- **Supabase Dashboard**: Real-time database metrics
- **Query Performance**: Slow query identification
- **Connection Pooling**: Monitor connection usage

### 3. Application Logs
The application logs important events:
- **Webhook Requests**: All incoming messages
- **Agent Responses**: AI agent decisions
- **Database Operations**: User creation and message storage
- **Error Events**: Detailed error information

### 4. Health Monitoring
Set up monitoring for:
- **Endpoint Availability**: Regular health checks
- **Response Times**: Performance monitoring
- **Error Rates**: Error rate alerts
- **Database Connectivity**: Connection health

## Troubleshooting

### Common Issues

#### 1. Deployment Failures
**Symptoms**: Build fails or deployment times out
**Solutions**:
- Check Python version compatibility (3.11+)
- Verify all dependencies in requirements.txt
- Check for syntax errors in code
- Review Vercel build logs

#### 2. Database Connection Issues
**Symptoms**: `FUNCTION_INVOCATION_FAILED` errors
**Solutions**:
- Verify `DATABASE_URL` format and credentials
- Check Supabase database status
- Ensure connection string is URL-encoded
- Test database connectivity manually

#### 3. Twilio Webhook Issues
**Symptoms**: Messages not received or processed
**Solutions**:
- Verify webhook URL is correct
- Check Twilio sandbox configuration
- Ensure phone number format is correct
- Review webhook logs in Twilio console

#### 4. Google Calendar Issues
**Symptoms**: Calendar operations fail
**Solutions**:
- Verify service account JSON format
- Check calendar permissions
- Ensure calendar ID is correct
- Test API access manually

#### 5. OpenAI API Issues
**Symptoms**: Agent responses fail
**Solutions**:
- Verify API key is valid
- Check API usage limits
- Ensure sufficient credits
- Review OpenAI API status

### Debug Mode
Enable debug logging by setting:
```bash
DEBUG=true
```

This provides detailed logs for troubleshooting.

### Log Analysis
Key log patterns to monitor:
- **🟣 WEBHOOK**: Webhook processing logs
- **📩 WhatsApp message**: Message processing
- **✅ SQLite session**: Session management
- **❌ Error**: Error conditions

## Security Considerations

### 1. Environment Variables
- Never commit `.env` files to version control
- Use Vercel's environment variable management
- Rotate API keys regularly
- Use least-privilege access

### 2. Database Security
- Use connection pooling
- Enable SSL connections
- Implement proper access controls
- Regular security updates

### 3. API Security
- Rate limiting on all endpoints
- Input validation and sanitization
- Error message sanitization
- CORS configuration

## Performance Optimization

### 1. Database Optimization
- Use connection pooling
- Implement proper indexing
- Monitor query performance
- Regular database maintenance

### 2. Application Optimization
- Optimize agent responses
- Implement caching where appropriate
- Monitor memory usage
- Regular performance testing

### 3. Vercel Optimization
- Use appropriate function timeout
- Optimize cold start times
- Monitor function execution time
- Consider edge functions for global performance

## Maintenance

### 1. Regular Updates
- Update dependencies monthly
- Apply security patches promptly
- Monitor for breaking changes
- Test updates in staging first

### 2. Monitoring
- Set up alerts for critical issues
- Regular health check reviews
- Performance trend analysis
- Capacity planning

### 3. Backup Strategy
- Database backups (handled by Supabase)
- Code repository backups
- Configuration backups
- Disaster recovery planning

---

*Last updated: October 2025*
*Version: 1.0*
