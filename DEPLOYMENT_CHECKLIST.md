# WhatsApp Agent - Deployment Checklist

## Pre-Deployment Checklist

### Code Quality
- [ ] All tests passing locally
- [ ] No linting errors
- [ ] Code reviewed and approved
- [ ] No sensitive data in code
- [ ] Environment variables properly configured

### Local Testing
- [ ] Health check endpoint working
- [ ] All API endpoints responding correctly
- [ ] Agent responses are appropriate
- [ ] Session memory working
- [ ] Error handling graceful
- [ ] Rate limiting functional

### Environment Configuration
- [ ] Vercel project created
- [ ] Environment variables set in Vercel dashboard
- [ ] Database connection configured
- [ ] External service credentials valid
- [ ] Webhook URLs configured

### External Services
- [ ] Twilio account active
- [ ] WhatsApp number verified
- [ ] Google Calendar API enabled
- [ ] OpenAI API key valid
- [ ] Database accessible from Vercel

## Deployment Steps

### 1. Deploy to Preview
```bash
# Deploy to preview environment
vercel --env preview

# Note the preview URL from output
# Example: https://whatsapp-agent-preview.vercel.app
```

### 2. Test Preview Server
```bash
# Run comprehensive preview tests
python test_preview_server.py https://your-preview-url.vercel.app

# Or test manually
curl https://your-preview-url.vercel.app/health
```

### 3. Configure Webhooks
- [ ] Set Twilio webhook URL to preview server
- [ ] Test webhook integration
- [ ] Verify message processing

### 4. Deploy to Production
```bash
# Deploy to production
vercel --prod

# Or promote preview to production
vercel promote https://your-preview-url.vercel.app
```

### 5. Configure Production Webhooks
- [ ] Update Twilio webhook URL to production
- [ ] Test production webhook integration
- [ ] Verify all functionality working

## Post-Deployment Verification

### Health Checks
- [ ] Production health endpoint responding
- [ ] Database connectivity confirmed
- [ ] External services accessible
- [ ] Logging and monitoring active

### Functional Testing
- [ ] Appointment scheduling flow working
- [ ] General inquiries handled correctly
- [ ] Session memory persistent
- [ ] Error handling appropriate
- [ ] Rate limiting enforced

### Performance Testing
- [ ] Response times acceptable (< 2s)
- [ ] Memory usage stable
- [ ] No memory leaks detected
- [ ] Database queries optimized

### Security Testing
- [ ] Input validation working
- [ ] Rate limiting preventing abuse
- [ ] Sensitive data protected
- [ ] Webhook signatures validated

## Monitoring Setup

### Vercel Analytics
- [ ] Analytics enabled
- [ ] Function performance monitored
- [ ] Error rates tracked
- [ ] Response times measured

### Custom Monitoring
- [ ] Health check endpoint monitored
- [ ] Database performance tracked
- [ ] External service status checked
- [ ] Alert thresholds configured

### Logging
- [ ] Application logs configured
- [ ] Error tracking enabled
- [ ] Performance metrics logged
- [ ] Security events tracked

## Rollback Plan

### Automatic Rollback Triggers
- [ ] Error rate > 10% for 5 minutes
- [ ] Response time > 10 seconds for 5 minutes
- [ ] Database connection failures
- [ ] Critical external service failures

### Manual Rollback Process
- [ ] Identify issue and assess impact
- [ ] Execute rollback command
- [ ] Verify system stability
- [ ] Document incident and resolution

### Rollback Commands
```bash
# List recent deployments
vercel ls

# Rollback to previous deployment
vercel rollback [deployment-url]

# Emergency rollback via dashboard
# Go to Vercel dashboard → Deployments → Promote to Production
```

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

## Emergency Contacts

### Development Team
- **Primary**: [Your contact info]
- **Secondary**: [Backup contact]
- **Escalation**: [Manager contact]

### External Services
- **Twilio Support**: [Support contact]
- **Vercel Support**: [Support contact]
- **Database Support**: [Support contact]

### Monitoring Alerts
- **Slack Channel**: #whatsapp-agent-alerts
- **Email**: alerts@yourcompany.com
- **PagerDuty**: [If configured]

## Documentation

### Deployment Records
- [ ] Deployment date and time recorded
- [ ] Version deployed documented
- [ ] Configuration changes noted
- [ ] Issues encountered documented

### Post-Deployment
- [ ] Performance baseline established
- [ ] Monitoring dashboards configured
- [ ] Team notified of deployment
- [ ] User documentation updated

---

**Checklist Version**: 1.0  
**Last Updated**: September 29, 2025  
**Next Review**: [Set review date]
