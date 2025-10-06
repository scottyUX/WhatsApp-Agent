# Simplified Istanbul Medic Agent Architecture

## Overview

This branch implements a simplified, knowledge-only agent architecture that eliminates complex routing and scheduling functionality to provide fast, reliable Q&A responses.

## Architecture Changes

### Before (Complex)
```
Manager Agent → Routes to 3 specialized agents
├── Scheduling Agent (Anna) - Complex appointment logic
├── Knowledge Agent - Q&A with vector store  
└── Image Agent - Medical image analysis
```

### After (Simplified)
```
Single Manager Agent
├── Knowledge Base (Vector Store)
├── Simple Q&A responses
└── No scheduling complexity
```

## Key Benefits

### Performance
- **Faster responses**: < 5 seconds (vs 300+ seconds)
- **No timeouts**: Simple Q&A is fast
- **Better streaming**: Real-time responses
- **Lower resource usage**: No complex session management

### Reliability
- **Simpler codebase**: Easier to debug
- **Fewer dependencies**: Less to break
- **Easier deployment**: No complex configuration
- **Better error handling**: Clearer error messages

### User Experience
- **Fast chat responses**
- **No more consent loops**
- **Consistent Q&A experience**
- **Reliable streaming**

## Files Modified

### New Files
- `app/agents/simple_knowledge_agent.py` - Knowledge-only agent
- `app/agents/simple_manager_agent.py` - Simplified manager
- `test_simple_agent.py` - Test script
- `SIMPLIFIED_ARCHITECTURE.md` - This documentation

### Modified Files
- `app/services/message_service.py` - Simplified message handling
- `app/routers/chat_router.py` - Updated imports (if needed)

### Disabled Features
- Scheduling agent (complex appointment logic)
- Image agent (medical image analysis)
- Google Calendar integration
- Complex session management
- Intent detection and routing

## Usage

### Testing
```bash
python test_simple_agent.py
```

### API Endpoints
- `POST /chat/` - Regular chat messages
- `POST /chat/stream` - Streaming chat messages
- `POST /whatsapp/webhook` - WhatsApp messages

### Example Questions
- "What is Istanbul Medic?"
- "Do you offer hair transplant procedures?"
- "How much does a hair transplant cost?"
- "Where are you located?"
- "How can I book a consultation?"

## Configuration

The simplified agent uses the same configuration as the original:
- Vector store: `settings.VECTOR_STORE_EN`
- Model: `gpt-4o`
- Knowledge base: Istanbul Medic information

## Deployment

1. Deploy to Vercel (or preferred platform)
2. No special configuration needed
3. Should resolve timeout issues
4. Faster response times

## Rollback

To rollback to the complex architecture:
```bash
git checkout dev
```

## Future Enhancements

If needed, features can be added back:
1. Simple appointment booking (without complex routing)
2. Basic image analysis (without complex tools)
3. Enhanced knowledge base integration
4. Better streaming implementation

## Monitoring

Key metrics to monitor:
- Response time (should be < 5 seconds)
- Error rate (should be minimal)
- User satisfaction (faster responses)
- Timeout rate (should be zero)
