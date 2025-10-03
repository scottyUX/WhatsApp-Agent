# Chat Integration Guide

## Overview

This guide covers the chat integration functionality for the WhatsApp Medical Agent system, including website chat endpoints, streaming responses, and database integration.

## Table of Contents

- [Chat Architecture](#chat-architecture)
- [API Endpoints](#api-endpoints)
- [Database Integration](#database-integration)
- [User Management](#user-management)
- [Streaming Responses](#streaming-responses)
- [Implementation Examples](#implementation-examples)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## Chat Architecture

### Overview
The chat integration provides website users with direct access to the same AI agent system used for WhatsApp, with real-time streaming responses and full database integration.

### Architecture Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                    Website User                            │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                Website Frontend                            │
│              (React/Vue/Angular)                           │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                Chat Endpoints                               │
│              POST /chat/                                    │
│              POST /chat/stream                              │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              Message Service                                │
│  • User management (chat_{user_id})                        │
│  • Database integration (PostgreSQL)                      │
│  • Streaming response support                              │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                Manager Agent                                │
│  • Same agent logic as WhatsApp                            │
│  • No session memory for chat                              │
└─────────────────────┬───────────────────────────────────────┘
```

## API Endpoints

### 1. Regular Chat Endpoint

#### POST /chat/
**Purpose**: Standard chat interaction with JSON request/response.

**Request**:
```json
{
  "content": "Hello, I want to schedule an appointment",
  "media_urls": ["https://example.com/image.jpg"],
  "audio_urls": ["https://example.com/audio.mp3"]
}
```

**Response**:
```json
{
  "content": "Hello! I'm Anna, your consultation assistant at Istanbul Medic. I'll help you schedule a free, no-obligation online consultation with one of our specialists. To get started, I'll need to collect a few details so our team can prepare for your appointment. Is it okay for me to collect your personal information for this purpose?"
}
```

**Status Codes**:
- `200` - Success
- `400` - Bad Request
- `500` - Internal Server Error

### 2. Streaming Chat Endpoint

#### POST /chat/stream
**Purpose**: Real-time streaming chat interaction.

**Request**:
```json
{
  "content": "I need help with my medical consultation",
  "media_urls": [],
  "audio_urls": []
}
```

**Response** (Server-Sent Events):
```
data: {"content": "Hello! I'm Anna, your consultation assistant at Istanbul Medic. I'd be happy to help you with your medical consultation. To get started, I'll help you schedule a free, no-obligation consultation and will need to collect a few details so our specialists can prepare for your session. Is it okay if I collect some personal information to set up your appointment?", "timestamp": "2025-10-01T14:24:19.941641", "is_final": false}

data: {"content": "", "timestamp": "2025-10-01T14:24:19.941881", "is_final": true}
```

**Status Codes**:
- `200` - Success
- `400` - Bad Request
- `500` - Internal Server Error

## Database Integration

### User Management
Chat users are stored in the same database as WhatsApp users but with a different naming convention:

- **WhatsApp Users**: `phone_number` = actual phone number (e.g., `+1234567890`)
- **Chat Users**: `phone_number` = `chat_{user_id}` format (e.g., `chat_user_123`)

### Message Storage
All chat messages are stored in the same `messages` table:
- **Incoming Messages**: User input to the chat
- **Outgoing Messages**: Agent responses
- **User Association**: Linked via `user_id` foreign key

### Database Schema
```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    direction VARCHAR(20) NOT NULL CHECK (direction IN ('incoming', 'outgoing')),
    body TEXT,
    media_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## User Management

### User Creation
Chat users are automatically created when they first interact with the system:

```python
# User creation logic
chat_phone = f"chat_{user_id}"
user = history_service.get_or_create_user(chat_phone)
```

### User Identification
- **Frontend**: Pass a unique `user_id` (e.g., session ID, user ID, or UUID)
- **Backend**: Converts to `chat_{user_id}` format for database storage
- **Persistence**: User data persists across sessions

### User Data
- **Phone Number**: Used as unique identifier (`chat_{user_id}`)
- **Name**: Optional, can be collected during conversation
- **Created At**: Timestamp of first interaction

## Streaming Responses

### Implementation
The streaming endpoint uses FastAPI's `StreamingResponse` to provide real-time responses:

```python
@router.post("/chat/stream")
async def chat_stream(request: Request, chat_message_request: ChatMessageRequest, message_service: MessageServiceDep):
    return StreamingResponse(
        message_service.handle_incoming_chat_message_streaming(
            user_id="chat_user",
            content=content,
            image_urls=media_urls
        ),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
```

### Frontend Integration

#### JavaScript/Modern Browsers
```javascript
// Example frontend implementation with proper SSE handling
async function sendStreamingMessage(message) {
    const response = await fetch('/chat/stream', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            content: message,
            media_urls: [],
            audio_urls: []
        })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        
        // Process complete SSE messages
        const lines = buffer.split('\n');
        buffer = lines.pop(); // Keep incomplete line in buffer
        
        for (const line of lines) {
            if (line.startsWith('data: ')) {
                try {
                    const data = JSON.parse(line.slice(6));
                    if (data.is_final) {
                        console.log('Stream completed');
                    } else {
                        displayMessageChunk(data.content);
                    }
                } catch (e) {
                    console.error('Error parsing SSE data:', e);
                }
            }
        }
    }
}

function displayMessageChunk(chunk) {
    // Append chunk to current message in UI
    const messageElement = document.getElementById('current-message');
    messageElement.textContent += chunk;
}
```

#### Using EventSource (Alternative)
```javascript
// Alternative using EventSource for SSE
function sendStreamingMessageWithEventSource(message) {
    // First send the message
    fetch('/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            content: message,
            media_urls: [],
            audio_urls: []
        })
    }).then(() => {
        // Then listen for streaming response
        const eventSource = new EventSource('/chat/stream');
        
        eventSource.onmessage = function(event) {
            const data = JSON.parse(event.data);
            if (data.is_final) {
                eventSource.close();
            } else {
                displayMessageChunk(data.content);
            }
        };
        
        eventSource.onerror = function(event) {
            console.error('SSE error:', event);
            eventSource.close();
        };
    });
}
```

## Implementation Examples

### 1. React Integration
```jsx
// ChatComponent.jsx
import React, { useState, useEffect } from 'react';

const ChatComponent = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isStreaming, setIsStreaming] = useState(false);
    const [currentStreamingMessage, setCurrentStreamingMessage] = useState('');

    const sendMessage = async (message) => {
        setIsLoading(true);
        
        try {
            const response = await fetch('/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: message,
                    media_urls: [],
                    audio_urls: []
                })
            });

            const data = await response.json();
            
            setMessages(prev => [
                ...prev,
                { type: 'user', content: message },
                { type: 'agent', content: data.content }
            ]);
        } catch (error) {
            console.error('Error sending message:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const sendStreamingMessage = async (message) => {
        setIsStreaming(true);
        setCurrentStreamingMessage('');
        
        // Add user message immediately
        setMessages(prev => [...prev, { type: 'user', content: message }]);
        
        try {
            const response = await fetch('/chat/stream', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: message,
                    media_urls: [],
                    audio_urls: []
                })
            });

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                buffer += decoder.decode(value, { stream: true });
                
                // Process complete SSE messages
                const lines = buffer.split('\n');
                buffer = lines.pop();
                
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            if (data.is_final) {
                                // Stream completed, add final message
                                setMessages(prev => [...prev, { type: 'agent', content: currentStreamingMessage }]);
                                setCurrentStreamingMessage('');
                            } else {
                                // Update streaming message
                                setCurrentStreamingMessage(prev => prev + data.content);
                            }
                        } catch (e) {
                            console.error('Error parsing SSE data:', e);
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Error sending streaming message:', error);
        } finally {
            setIsStreaming(false);
        }
    };

    return (
        <div className="chat-container">
            <div className="messages">
                {messages.map((msg, index) => (
                    <div key={index} className={`message ${msg.type}`}>
                        {msg.content}
                    </div>
                ))}
            </div>
            <div className="input-container">
                <input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage(input)}
                    placeholder="Type your message..."
                />
                <button onClick={() => sendMessage(input)} disabled={isLoading}>
                    Send
                </button>
            </div>
        </div>
    );
};

export default ChatComponent;
```

### 2. Vue.js Integration
```vue
<!-- ChatComponent.vue -->
<template>
    <div class="chat-container">
        <div class="messages">
            <div 
                v-for="(message, index) in messages" 
                :key="index" 
                :class="`message ${message.type}`"
            >
                {{ message.content }}
            </div>
        </div>
        <div class="input-container">
            <input
                v-model="input"
                @keypress.enter="sendMessage"
                placeholder="Type your message..."
            />
            <button @click="sendMessage" :disabled="isLoading">
                Send
            </button>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            messages: [],
            input: '',
            isLoading: false
        };
    },
    methods: {
        async sendMessage() {
            if (!this.input.trim()) return;
            
            this.isLoading = true;
            
            try {
                const response = await fetch('/chat/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        content: this.input,
                        media_urls: [],
                        audio_urls: []
                    })
                });

                const data = await response.json();
                
                this.messages.push(
                    { type: 'user', content: this.input },
                    { type: 'agent', content: data.content }
                );
                
                this.input = '';
            } catch (error) {
                console.error('Error sending message:', error);
            } finally {
                this.isLoading = false;
            }
        }
    }
};
</script>
```

### 3. Angular Integration
```typescript
// chat.component.ts
import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';

interface Message {
    type: 'user' | 'agent';
    content: string;
}

@Component({
    selector: 'app-chat',
    template: `
        <div class="chat-container">
            <div class="messages">
                <div 
                    *ngFor="let message of messages; let i = index" 
                    [class]="'message ' + message.type"
                >
                    {{ message.content }}
                </div>
            </div>
            <div class="input-container">
                <input
                    [(ngModel)]="input"
                    (keypress.enter)="sendMessage()"
                    placeholder="Type your message..."
                />
                <button (click)="sendMessage()" [disabled]="isLoading">
                    Send
                </button>
            </div>
        </div>
    `
})
export class ChatComponent {
    messages: Message[] = [];
    input: string = '';
    isLoading: boolean = false;

    constructor(private http: HttpClient) {}

    async sendMessage() {
        if (!this.input.trim()) return;
        
        this.isLoading = true;
        
        try {
            const response = await this.http.post('/chat/', {
                content: this.input,
                media_urls: [],
                audio_urls: []
            }).toPromise();
            
            this.messages.push(
                { type: 'user', content: this.input },
                { type: 'agent', content: response.content }
            );
            
            this.input = '';
        } catch (error) {
            console.error('Error sending message:', error);
        } finally {
            this.isLoading = false;
        }
    }
}
```

## Testing

### 1. Unit Tests
```python
# tests/test_chat/test_chat_endpoints.py
import pytest
from fastapi.testclient import TestClient
from app.app import app

client = TestClient(app)

def test_chat_endpoint():
    """Test regular chat endpoint."""
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
    """Test streaming chat endpoint."""
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

### 2. Integration Tests
```python
# tests/test_chat/test_chat_integration.py
import pytest
from app.services.message_service import MessageService
from app.services.history_service import HistoryService

@pytest.mark.asyncio
async def test_chat_message_flow():
    """Test complete chat message flow."""
    # Setup
    history_service = HistoryService(user_repo, message_repo)
    message_service = MessageService(history_service)
    
    # Test chat message
    result = await message_service.handle_incoming_chat_message(
        user_id="test_user_123",
        content="Hello, I want to schedule an appointment"
    )
    
    # Verify response
    assert "Anna" in result
    
    # Verify database storage
    user = history_service.get_user_by_phone("chat_test_user_123")
    assert user is not None
    
    messages = history_service.get_message_history(user.id, 5)
    assert len(messages) >= 2  # incoming + outgoing
```

### 3. End-to-End Tests
```python
# tests/test_chat/test_chat_e2e.py
import pytest
import httpx

@pytest.mark.asyncio
async def test_chat_consultation_flow():
    """Test complete chat consultation flow."""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        # Step 1: Initial contact
        response = await client.post(
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
        response = await client.post(
            f"{base_url}/chat/",
            json={
                "content": "My name is John Doe and I need help with hair transplant",
                "media_urls": [],
                "audio_urls": []
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "John" in data["content"]
```

## Troubleshooting

### Common Issues

#### 1. Chat Endpoint Not Responding
**Symptoms**: Chat endpoints return 500 errors
**Solutions**:
- Check database connectivity
- Verify environment variables
- Review application logs
- Test with simple requests first

#### 2. Streaming Not Working
**Symptoms**: Streaming endpoint hangs or returns errors
**Solutions**:
- Check FastAPI streaming implementation
- Verify response headers
- Test with simple streaming responses
- Check for connection timeouts

#### 3. Database Integration Issues
**Symptoms**: Messages not stored in database
**Solutions**:
- Verify database connection
- Check user creation logic
- Review message storage code
- Test database operations manually

#### 4. User Management Issues
**Symptoms**: Users not created or not found
**Solutions**:
- Check user ID format (`chat_{user_id}`)
- Verify user creation logic
- Review database queries
- Test user operations manually

### Debug Mode
Enable debug logging by setting:
```bash
DEBUG=true
```

This provides detailed logs for troubleshooting chat integration issues.

### Log Analysis
Key log patterns to monitor:
- **📩 Chat message**: Chat message processing
- **📩 Chat streaming message**: Streaming chat processing
- **✅ User created**: User creation in database
- **❌ Error**: Error conditions

---

*Last updated: October 2025*
*Version: 1.0*
