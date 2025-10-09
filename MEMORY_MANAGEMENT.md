# Memory Management Configuration

This document explains the advanced memory management features implemented using the OpenAI Agents SDK.

## Overview

The system now uses OpenAI's `OpenAIConversationsSession` with advanced context management to provide intelligent memory for medical consultation conversations.

## Configuration

### Environment Variables

```bash
# Memory Management Settings
CONTEXT_LIMIT=8          # Total turns to keep in context
KEEP_LAST_N_TURNS=3      # Turns to keep verbatim (others summarized)
```

### Memory Strategy

- **Context Limit: 8** - Keeps last 8 conversation turns in memory
- **Keep Last 3 Turns** - Recent exchanges stay verbatim for accuracy
- **Automatic Summarization** - Older context compressed into structured summaries

## Benefits for Medical Consultations

### ✅ Improved User Experience
- Agent remembers user's hair loss pattern across long sessions
- Maintains context about previous consultation preferences
- Remembers specific questions and concerns raised

### ✅ Cost Efficiency
- Summaries reduce token usage for long conversations
- Intelligent context trimming prevents token overflow
- Optimized for medical consultation workflows

### ✅ Better Performance
- Faster response times with optimized context
- Reduced API costs through smart memory management
- Better handling of multi-turn medical discussions

## Admin Endpoints (Debug Mode Only)

### Clear User Memory
```bash
DELETE /chat/memory/{user_id}
```

### Get User Memory
```bash
GET /chat/memory/{user_id}
```

## Memory Types

### 1. Context Trimming
- **Use Case**: Tool-heavy operations, short workflows
- **Pros**: Zero latency, deterministic, cost-efficient
- **Cons**: Limited long-range memory

### 2. Context Summarization
- **Use Case**: Long conversations, planning/coaching
- **Pros**: Long-range memory, better UX, cost-controlled
- **Cons**: Potential summarization loss

## Implementation Details

Based on [OpenAI Agents SDK Session Memory](https://cookbook.openai.com/examples/agents_sdk/session_memory) and [Official Sessions Documentation](https://openai.github.io/openai-agents-python/sessions/).

### Session Creation
```python
session = OpenAIConversationsSession(
    conversation_id=conversation_id,
    context_limit=settings.CONTEXT_LIMIT,
    keep_last_n_turns=settings.KEEP_LAST_N_TURNS,
)
```

### Memory Operations
- `get_items()` - Retrieve conversation history
- `add_items()` - Store new conversation items
- `clear_session()` - Reset conversation memory
- `pop_item()` - Remove last item (for corrections)

## Monitoring

The system logs memory operations for debugging:
- Session creation with configuration
- Item count in memory
- Memory clearing operations
- Error handling for memory operations

## Best Practices

1. **Monitor Token Usage** - Watch for context overflow
2. **Test Long Conversations** - Verify memory works across extended sessions
3. **Debug Memory Issues** - Use admin endpoints to inspect session state
4. **Tune Parameters** - Adjust `CONTEXT_LIMIT` and `KEEP_LAST_N_TURNS` based on usage patterns

## Troubleshooting

### Memory Not Persisting
- Check OpenAI API key configuration
- Verify conversation ID generation
- Review session creation logs

### High Token Usage
- Reduce `CONTEXT_LIMIT` if conversations are too long
- Increase `KEEP_LAST_N_TURNS` if recent context is critical
- Monitor summarization quality

### Poor Context Retention
- Increase `CONTEXT_LIMIT` for longer memory
- Adjust `KEEP_LAST_N_TURNS` for better recent context
- Review conversation flow and agent instructions
