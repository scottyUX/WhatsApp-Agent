# Persistent Session Management

## Overview

This document describes the persistent session management system implemented to solve conversation state resets in serverless environments. The system ensures that chat conversations maintain their context across multiple messages and serverless function restarts.

## Problem Statement

### Original Issue
- **In-memory session store** in serverless environment
- **Session data lost** between function restarts
- **Conversation resets** on every message
- **Poor user experience** with repeated introductions

### Root Cause
```python
# Old implementation - in-memory storage
_session_store: Dict[str, Dict[str, Any]] = {}  # Lost on restart!
```

In serverless environments (Vercel, AWS Lambda), each request might be handled by a different instance, causing session data to be lost.

## Solution Architecture

### High-Level Design
```
Frontend (Device ID) → Backend (Session Service) → Database (PostgreSQL)
```

### Key Components

#### 1. Session Service (`app/services/session_service.py`)
- **Purpose**: Manages persistent session storage
- **Features**: Device ID tracking, TTL management, error handling
- **Database**: Uses existing `conversation_states` table

#### 2. Database Schema Extensions
```sql
-- Added to conversation_states table
ALTER TABLE conversation_states 
ADD COLUMN active_agent VARCHAR(50),
ADD COLUMN locked_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN session_ttl INTEGER NOT NULL DEFAULT 86400;
```

#### 3. Manager Agent Updates (`app/agents/manager_agent.py`)
- **Replaced**: In-memory `_session_store` with `SessionService`
- **Added**: Database connection management
- **Enhanced**: Error handling and logging

## Implementation Details

### Session Service API

#### Core Methods
```python
class SessionService:
    def get_session_lock(self, device_id: str) -> Optional[str]
    def set_session_lock(self, device_id: str, agent_key: str) -> bool
    def clear_session_lock(self, device_id: str) -> bool
    def cleanup_expired_sessions(self) -> int
```

#### Session Lifecycle
1. **Create**: `set_session_lock(device_id, "scheduling")`
2. **Retrieve**: `get_session_lock(device_id)` → `"scheduling"`
3. **Clear**: `clear_session_lock(device_id)` → `None`

### Database Integration

#### Connection Flow
```
Device ID → Connection → User → Conversation State
```

#### Session Storage
```python
conversation_state = ConversationState(
    patient_profile_id=device_id,  # Using device_id as identifier
    active_agent="scheduling",
    locked_at=datetime.now(),
    session_ttl=86400  # 24 hours
)
```

### Error Handling

#### Database Connection Issues
```python
try:
    active_agent = session_service.get_session_lock(device_id)
except Exception as e:
    log.error(f"Session error: {e}")
    return None  # Fallback to stateless mode
```

#### Session Expiration
```python
if session_service._is_session_expired(conversation_state):
    session_service.clear_session_lock(device_id)
    # Start new session
```

## Configuration

### Environment Variables
```bash
# Database connection (existing)
DATABASE_URL=postgresql://user:pass@host:port/db

# Session TTL (optional, defaults to 24 hours)
DEFAULT_SESSION_TTL=86400
```

### Session TTL Options
```python
# Short sessions (1 hour)
conversation_state.session_ttl = 3600

# Long sessions (7 days)
conversation_state.session_ttl = 604800

# Default (24 hours)
conversation_state.session_ttl = 86400
```

## Usage Examples

### Basic Session Management
```python
# Initialize session service
db = SessionLocal()
session_service = SessionService(db)

# Set session lock
success = session_service.set_session_lock("device-123", "scheduling")

# Get active agent
active_agent = session_service.get_session_lock("device-123")
# Returns: "scheduling"

# Clear session
session_service.clear_session_lock("device-123")
```

### Manager Agent Integration
```python
# In manager_agent.py
def _get_lock(wa_id: str) -> Optional[str]:
    session_service = _get_session_service()
    return session_service.get_session_lock(wa_id)

def _set_lock(wa_id: str, agent_key: str) -> None:
    session_service = _get_session_service()
    session_service.set_session_lock(wa_id, agent_key)
```

### Frontend Integration
```javascript
// Ensure device ID is sent with each request
const deviceId = ensureDeviceId();
headers.set('X-Device-ID', deviceId);
```

## Testing

### Unit Tests
```python
# Test session service
def test_set_session_lock_success():
    session_service = SessionService(mock_db)
    result = session_service.set_session_lock("device-123", "scheduling")
    assert result is True

def test_get_session_lock_expired():
    # Test expired session handling
    pass
```

### Integration Tests
```python
# Test full conversation flow
def test_conversation_persistence():
    # Send first message
    result1 = await run_manager("Hello", context)
    
    # Send second message (should maintain context)
    result2 = await run_manager("I want to schedule", context)
    
    # Verify no reset message
    assert "I've reset our conversation" not in result2
```

### Load Testing
```python
# Test multiple concurrent sessions
async def test_concurrent_sessions():
    tasks = []
    for i in range(100):
        device_id = f"device-{i}"
        task = run_manager("Hello", {"user_id": device_id})
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    # Verify all sessions work independently
```

## Monitoring and Debugging

### Logging
```python
# Session operations
log.info(f"Session lock set: {device_id} -> {agent_key}")
log.info(f"Session lock retrieved: {device_id} -> {active_agent}")
log.info(f"Session lock cleared: {device_id}")

# Cleanup operations
expired_count = session_service.cleanup_expired_sessions()
log.info(f"Cleaned up {expired_count} expired sessions")
```

### Metrics
- **Active Sessions**: Number of current session locks
- **Session Duration**: Average time sessions are held
- **Cleanup Rate**: Number of expired sessions cleaned up
- **Error Rate**: Failed session operations

### Database Queries
```sql
-- Check active sessions
SELECT active_agent, COUNT(*) as count
FROM conversation_states 
WHERE active_agent IS NOT NULL 
GROUP BY active_agent;

-- Check expired sessions
SELECT COUNT(*) as expired_count
FROM conversation_states 
WHERE active_agent IS NOT NULL 
AND locked_at < NOW() - INTERVAL '24 hours';

-- Session duration analysis
SELECT 
    active_agent,
    AVG(EXTRACT(EPOCH FROM (NOW() - locked_at))) as avg_duration_seconds
FROM conversation_states 
WHERE active_agent IS NOT NULL 
GROUP BY active_agent;
```

## Migration Guide

### From In-Memory to Persistent

#### Step 1: Database Migration
```sql
-- Run the migration script
\i migrations/add_session_lock_fields.sql
```

#### Step 2: Update Code
```python
# Old code
_session_store: Dict[str, Dict[str, Any]] = {}

# New code
session_service = SessionService(db)
```

#### Step 3: Deploy
```bash
# Deploy with new session service
git push origin feat/persistent-session-storage
```

### Rollback Plan
```python
# If issues occur, can temporarily revert to in-memory
# by commenting out session service calls
# and uncommenting old _session_store code
```

## Performance Considerations

### Database Load
- **Indexes**: Added on `active_agent` and `locked_at` columns
- **Connection Pooling**: Reuse database connections
- **Query Optimization**: Efficient lookups by device ID

### Memory Usage
- **No In-Memory Storage**: All data in database
- **Connection Management**: Proper connection cleanup
- **TTL Cleanup**: Regular cleanup of expired sessions

### Scalability
- **Horizontal Scaling**: Works across multiple instances
- **Database Scaling**: Can use read replicas for reads
- **Caching**: Can add Redis layer if needed

## Security Considerations

### Device ID Validation
```python
# Validate device ID format
def validate_device_id(device_id: str) -> bool:
    # UUID format validation
    try:
        uuid.UUID(device_id)
        return True
    except ValueError:
        return False
```

### Session Isolation
- **Device-based**: Each device gets isolated session
- **No Cross-Device**: Sessions don't leak between devices
- **TTL Enforcement**: Automatic cleanup prevents stale sessions

### Data Privacy
- **Minimal Storage**: Only store necessary session data
- **Automatic Cleanup**: TTL ensures data doesn't persist indefinitely
- **No Sensitive Data**: Only agent names and timestamps stored

## Troubleshooting

### Common Issues

#### 1. Session Not Persisting
**Symptoms**: Conversations still reset between messages
**Causes**: 
- Database connection issues
- Device ID not being passed correctly
- Session service not being called

**Solutions**:
```python
# Check database connection
db = SessionLocal()
session_service = SessionService(db)

# Verify device ID
device_id = request.headers.get("X-Device-ID")
log.info(f"Device ID: {device_id}")

# Test session operations
result = session_service.set_session_lock(device_id, "test")
log.info(f"Session set result: {result}")
```

#### 2. Database Errors
**Symptoms**: Session operations failing with database errors
**Causes**:
- Database connection issues
- Missing columns in conversation_states table
- Permission issues

**Solutions**:
```sql
-- Check if columns exist
\d conversation_states

-- Run migration if needed
\i migrations/add_session_lock_fields.sql

-- Check permissions
GRANT ALL ON conversation_states TO your_user;
```

#### 3. Performance Issues
**Symptoms**: Slow session operations
**Causes**:
- Missing database indexes
- Too many concurrent connections
- Inefficient queries

**Solutions**:
```sql
-- Add indexes
CREATE INDEX idx_conversation_states_active_agent ON conversation_states(active_agent);
CREATE INDEX idx_conversation_states_locked_at ON conversation_states(locked_at);

-- Monitor query performance
EXPLAIN ANALYZE SELECT * FROM conversation_states WHERE active_agent = 'scheduling';
```

### Debug Mode
```python
# Enable debug logging
import logging
logging.getLogger("session_service").setLevel(logging.DEBUG)

# Add debug prints
log.debug(f"Session operation: {operation} for device {device_id}")
```

## Future Enhancements

### Planned Features
1. **Redis Caching**: Add Redis layer for faster lookups
2. **Session Analytics**: Detailed session metrics and reporting
3. **Custom TTL**: Per-user or per-agent TTL configuration
4. **Session Sharing**: Allow session sharing between devices
5. **Session Backup**: Backup sessions to prevent data loss

### Performance Optimizations
1. **Connection Pooling**: Optimize database connections
2. **Query Caching**: Cache frequent queries
3. **Batch Operations**: Batch session operations
4. **Async Cleanup**: Background cleanup of expired sessions

## Conclusion

The persistent session management system successfully solves the conversation reset issue in serverless environments by:

- ✅ **Eliminating conversation resets**
- ✅ **Providing seamless user experience**
- ✅ **Scaling across multiple instances**
- ✅ **Maintaining data consistency**
- ✅ **Supporting easy monitoring and debugging**

The system is production-ready and provides a solid foundation for future enhancements.
