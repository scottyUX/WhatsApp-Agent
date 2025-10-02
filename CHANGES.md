# Changes Documentation

## Overview
This document outlines the current changes on the `feature/merge-agent-with-database` branch, focusing on the integration of a new database architecture with enhanced entity relationships and improved message handling.

## Core File Changes

#### 1. **app/agents/manager_agent.py**
**Key Changes**:

**Old Streaming** (Single chunk):
```python
# Get the full response first
result = await run_manager(user_input, context, session=None)
# For now, yield the full response as a single chunk
yield full_response
```

**New Streaming** (Real-time):
```python
async def _run_leaf_streaming(agent_obj, user_input, context, session):
    result = Runner.run_streamed(agent_obj, user_input, context=context, session=session)
    async for event in result.stream_events():
        if event.type == "raw_response_event":
            yield event.data.delta  # Stream individual tokens
        elif event.type == "run_item_stream_event":
            # Handle tool calls, message outputs, etc.
```

**Enhanced**: `run_manager_streaming()` now provides real token-level streaming with proper reset handling and agent switching support.

#### 2. **app/database/entities/message.py & user.py**
**Status**: Reverted to previous version with enhanced entity relationships and conversation-based architecture.

#### 3. **app/database/repositories/message_repository.py & user_repository.py** 
**Status**: Reverted to previous version with conversation-based API and enhanced user management methods.

#### 4. **app/routers/chat_router.py**
**Updated to Use V1 Methods**:
- Chat endpoint: `handle_incoming_chat_message()` → `handle_incoming_chat_message_v1()`
- Stream endpoint: `handle_incoming_chat_message_streaming()` → `handle_incoming_chat_message_streaming_v1()`
- **Reason**: V1 methods provide full database relationship support with proper user tracking

#### 5. **app/services/history_service.py**
**Dual Architecture Support**:
**New V1 Methods** (Full Database Architecture):
- `get_or_create_connection()` - Manages user connections across channels (WhatsApp/web)
- `get_or_create_conversation()` - Handles conversation threading
- `log_incoming_message_v1()` - Stores user messages with full context
- `log_outgoing_message_v1()` - Stores agent responses with full context
- `get_message_history_v1()` - Retrieves conversation history
**Legacy Methods**: Original simple methods still available for backward compatibility

#### 6. **app/services/message_service.py**
**Dual Implementation Architecture**:

**Current Implementation** (Simplified):
```python
# Simple phone-based storage
chat_phone = f"chat_{user_id}"
await self.history_service.store_message(
    phone_number=chat_phone,
    content=content,
    direction="incoming",
    media_urls=image_urls or []
)
```
- Uses basic phone number storage (`chat_{user_id}`)
- SQLite session memory for WhatsApp only
- Simple message storage without full relationships

**V1 Implementation** (Full Database):
```python
# Extract device/IP info for user tracking
device_id = RequestUtils.get_device_id_from_headers(request)
ip_address = RequestUtils.get_ip_address_from_headers(request)

# Create full entity relationships
connection = self.history_service.get_or_create_connection(
    channel="chat",
    device_id=device_id,
    ip_address=ip_address
)
user = connection.user
conversation = self.history_service.get_or_create_conversation(
    user_id=user.id,
    connection_id=connection.id
)

# Store message with full context
current_message = self.history_service.log_incoming_message_v1(
    conversation_id=conversation.id,
    content=message
)
```
**Previous Version (V1) Benefits**: Extracts device ID and IP address from request headers to uniquely identify web users, creates proper User → Connection → Conversation → Message relationships for full conversation threading and analytics.

## Current Status

- **Web Chat**: Uses V1 methods (`*_v1`) - Full database relationships
- **WhatsApp**: Uses current methods - Simplified with SQLite sessions  
- **Streaming**: Enhanced with proper token-level streaming in manager_agent

## Database Structure (V1)

```
User
├── connections (1:many)
│   ├── conversations (1:many)
│   │   └── messages (1:many)
│   │       └── media (1:many)
```

This provides full traceability and relationship management for all user interactions across communication channels.
