# WhatsApp Agent - Deployment Guide

## Quick Deployment to Preview Server

### Prerequisites
1. **Vercel CLI installed**: `npm i -g vercel`
2. **Vercel account**: Connected to your GitHub repository
3. **Environment variables**: Configured in Vercel dashboard
4. **All tests passing**: Local testing completed

### Pre-Deployment Checklist
- [ ] All endpoints tested locally
- [ ] Environment variables configured
- [ ] Database migrations ready (if any)
- [ ] External service credentials valid
- [ ] No critical errors in logs
- [ ] Performance benchmarks met

### Step 1: Configure Environment Variables

#### Required Environment Variables
```bash
# OpenAI
OPENAI_API_KEY=your_openai_key

# Twilio
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_whatsapp_number

# Google Calendar
GOOGLE_CALENDAR_CREDENTIALS=your_service_account_json
GOOGLE_CALENDAR_ID=your_calendar_id

# Database
DATABASE_URL=your_postgresql_url

# App Configuration
DEBUG=false
ENVIRONMENT=staging
```

#### Set in Vercel Dashboard
1. Go to your Vercel project dashboard
2. Navigate to Settings → Environment Variables
3. Add each variable for "Production" and "Preview" environments
4. Ensure sensitive values are marked as "Encrypted"

### Step 2: Deploy to Preview

```bash
# Install Vercel CLI if not already installed
npm i -g vercel

# Login to Vercel (if not already logged in)
vercel login

# Deploy to preview environment
vercel --env preview

# Or deploy specific branch
vercel --env preview --git-branch feature/your-branch
```

### Step 3: Verify Deployment

#### Health Check
```bash
# Get the preview URL from Vercel output
curl https://your-preview-url.vercel.app/health
```

#### Test Key Endpoints
```bash
# Test webhook verification
curl https://your-preview-url.vercel.app/api/webhook

# Test chat endpoint
curl -X POST https://your-preview-url.vercel.app/chat/ \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello, I want to schedule an appointment"}'

# Test WhatsApp webhook
curl -X POST https://your-preview-url.vercel.app/whatsapp/webhook \
  -F "Body=Test message" \
  -F "From=+1234567890"
```

### Step 4: Configure Webhooks

#### Twilio Webhook Configuration
1. Go to Twilio Console → Phone Numbers → Manage → Active Numbers
2. Select your WhatsApp number
3. Set webhook URL to: `https://your-preview-url.vercel.app/api/webhook`
4. Set HTTP method to: `POST`
5. Save configuration

#### Test Webhook Integration
```bash
# Send test message via Twilio (if you have test credentials)
# Or use the test endpoint
curl https://your-preview-url.vercel.app/test/message
```

### Step 5: Monitor and Validate

#### Check Vercel Logs
```bash
# View function logs
vercel logs https://your-preview-url.vercel.app

# Follow logs in real-time
vercel logs https://your-preview-url.vercel.app --follow
```

#### Monitor Key Metrics
- Response times
- Error rates
- Function execution duration
- Memory usage
- Database connections

### Step 6: Production Deployment

Once preview testing is complete:

```bash
# Deploy to production
vercel --prod

# Or promote preview to production
vercel promote https://your-preview-url.vercel.app
```

## Environment-Specific Configurations

### Preview Environment
- **Database**: Staging PostgreSQL instance
- **External Services**: Test/sandbox versions
- **Logging**: Debug level enabled
- **Rate Limiting**: Relaxed for testing
- **Monitoring**: Basic monitoring enabled

### Production Environment
- **Database**: Production PostgreSQL instance
- **External Services**: Live services
- **Logging**: Info level (errors and important events)
- **Rate Limiting**: Strict limits enforced
- **Monitoring**: Full monitoring and alerting

## Troubleshooting

### Common Issues

#### 1. Environment Variables Not Loading
```bash
# Check if variables are set
vercel env ls

# Pull environment variables locally
vercel env pull .env.local
```

#### 2. Database Connection Issues
- Verify `DATABASE_URL` is correct
- Check if database allows connections from Vercel IPs
- Ensure database is running and accessible

#### 3. External Service Failures
- Verify API keys are correct
- Check service quotas and limits
- Ensure webhook URLs are accessible

#### 4. Function Timeout Issues
- Check function execution time in Vercel logs
- Optimize slow operations
- Consider increasing timeout limits

### Debug Commands

```bash
# Check deployment status
vercel ls

# View specific deployment
vercel inspect https://your-deployment-url.vercel.app

# Check environment variables
vercel env ls

# View function logs
vercel logs https://your-deployment-url.vercel.app --function=api/webhook

# Test locally with production environment
vercel dev --env production
```

## Rollback Procedures

### Quick Rollback
```bash
# List recent deployments
vercel ls

# Rollback to previous deployment
vercel rollback [deployment-url]

# Or rollback to specific commit
vercel rollback [commit-hash]
```

### Emergency Rollback
1. Go to Vercel dashboard
2. Navigate to Deployments
3. Find last known good deployment
4. Click "Promote to Production"

## Monitoring and Alerting

### Vercel Analytics
- Enable in Vercel dashboard
- Monitor function performance
- Track error rates and response times

### Custom Monitoring
```python
# Add to your application
import logging
from datetime import datetime

# Log important events
logging.info(f"Appointment booked: {user_id} at {datetime.now()}")
logging.error(f"Database error: {error_message}")
```

### Health Check Endpoint
```python
# Already implemented in your app
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": "production"
    }
```

## Security Considerations

### Environment Variables
- Never commit sensitive data to git
- Use Vercel's encrypted environment variables
- Rotate keys regularly
- Use different keys for different environments

### Webhook Security
- Validate Twilio webhook signatures
- Implement rate limiting
- Sanitize all inputs
- Log security events

### Database Security
- Use connection pooling
- Implement query timeouts
- Monitor for suspicious activity
- Regular security updates

## Performance Optimization

### Function Optimization
- Minimize cold start time
- Optimize imports
- Use connection pooling
- Implement caching where appropriate

### Database Optimization
- Use indexes on frequently queried columns
- Implement query optimization
- Monitor slow queries
- Use read replicas if needed

### External Service Optimization
- Implement retry logic with exponential backoff
- Use async operations where possible
- Cache frequently accessed data
- Monitor API rate limits

## Next Steps After Deployment

1. **Monitor Performance**: Watch metrics for 24-48 hours
2. **Test Real Scenarios**: Use actual WhatsApp numbers for testing
3. **Gather Feedback**: Collect user feedback and system performance data
4. **Optimize**: Make improvements based on real-world usage
5. **Scale**: Adjust resources based on demand

---

**Last Updated**: September 29, 2025  
**Version**: 1.0  
**Maintainer**: Development Team
