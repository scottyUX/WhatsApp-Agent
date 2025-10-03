## Database Test Plan (Merge: Agent + Database)

Scope: Validate end-to-end persistence and retrieval for WhatsApp Agent after the merge, covering entities, repositories, services, and operational behaviors in Preview/Prod.

### 1) Preconditions
- DATABASE_URL configured (Preview/Prod)
- App deployed and reachable
- Twilio webhook set to POST /api/webhook
- Credentials: read-only SQL access to the database (Supabase console is fine)

### 2) Smoke Checks (Schema & Connectivity)
- Connect to DB (drivers/console) and run:
```sql
select now();
select 1;
```
- Tables exist (current implementation uses simplified schema):
```sql
select table_name from information_schema.tables where table_schema = 'public'
  and table_name in ('users','messages');
```
- Columns sanity (users, messages):
```sql
select column_name, data_type from information_schema.columns 
 where table_name = 'users';
select column_name, data_type from information_schema.columns 
 where table_name = 'messages';
```
- Note: Current implementation uses simplified schema with direct user-message relationship (no separate conversations/connections tables)

### 3) Core Persistence: Inbound + Outbound Messages
Goal: When a WhatsApp message arrives, we store one incoming and one outgoing record and (optionally) media.

Steps:
1. Send a message via WhatsApp UI (or curl) to POST /api/webhook:
```bash
curl -X POST "$BASE_URL/api/webhook" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=+1TESTNUMBER&Body=hello from db test"
```
2. Query user auto-creation:
```sql
select id, phone_number, name, created_at
from users
where phone_number = '+1TESTNUMBER';
```
Expect: one row returned.
3. Query recent messages:
```sql
select direction, body, media_url, created_at
from messages
where user_id = '<USER_ID>'
order by created_at desc
limit 10;
```
Expect: at least two rows: one incoming (body = sent text), one outgoing (agent reply).

### 4) Media Ingestion (Image/Audio)
Steps:
1. Send a message with a public image URL (simulating Twilio's MediaUrl0):
```bash
curl -X POST "$BASE_URL/api/webhook" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=+1TESTNUMBER&Body=see image&MediaUrl0=https://via.placeholder.com/300.png&NumMedia=1&MediaContentType0=image/jpeg"
```
2. Query messages:
```sql
select direction, body, media_url, created_at
from messages
where user_id = '<USER_ID>'
order by created_at desc
limit 5;
```
Expect: the latest incoming message has media_url populated with the URL.
Note: Current implementation stores first media URL in `messages.media_url` field, not separate `media` table.

### 5) Idempotency / Duplicate Prevention
Goal: Same Twilio event should not produce duplicate rows (best-effort check).
Steps:
1. Send the exact same POST twice within 2 seconds.
2. Query message count within a narrow time window:
```sql
select count(*)
from messages
where user_id = '<USER_ID>'
  and created_at > now() - interval '1 minute'
  and body = 'hello from db test';
```
Expect: Count reasonably small (ideally 1 per unique event). If duplicates appear, note in issues.

### 6) Retrieval: History by Phone
Service method `get_message_history_by_phone` should return latest N items.
Steps:
1. Hit (temporary) local function or run unit/integration tests:
   - Integration: `pytest -k history` (if test exists), or
   - Manual SQL below matches expected:
```sql
select direction, body, created_at
from messages
where user_id = (
  select id from users where phone_number = '+1TESTNUMBER'
)
order by created_at desc
limit 10;
```
Expect: Matches app responses order (most recent first).

### 6.5) Chat Endpoints Database Integration (NEW)
Goal: Validate chat endpoints store messages in database with proper user management.

Steps:
1. Test regular chat endpoint:
```bash
curl -X POST "$BASE_URL/chat/" \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello, I want to schedule an appointment", "media_urls": [], "audio_urls": []}'
```

2. Test streaming chat endpoint:
```bash
curl -X POST "$BASE_URL/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{"content": "I need help with my medical consultation", "media_urls": [], "audio_urls": []}'
```

3. Query chat user creation:
```sql
select id, phone_number, name, created_at
from users
where phone_number like 'chat_%';
```

4. Query chat messages:
```sql
select direction, body, created_at
from messages
where user_id = (
  select id from users where phone_number = 'chat_chat_user'
)
order by created_at desc
limit 10;
```

Expect: 
- Chat users stored as `chat_{user_id}` format
- Messages properly stored for both regular and streaming endpoints
- Both incoming and outgoing messages recorded

### 6.6) Service Method Testing (UPDATED)
Current implementation uses simplified service methods:
- `store_message()` - stores messages with phone_number
- `get_message_history_by_phone()` - retrieves by phone_number

Test these methods directly:
```python
# Test store_message
await history_service.store_message(
    phone_number="+1234567890",
    content="Test message",
    direction="incoming",
    media_urls=[]
)

# Test get_message_history_by_phone
history = await history_service.get_message_history_by_phone("+1234567890", 10)
```

### 7) Performance & Indexes
Checks to avoid table scans.
```sql
explain analyze
select * from messages
where user_id = '<USER_ID>'
order by created_at desc
limit 10;
```
Expect: Index scan on (user_id, created_at). If missing, add an index:
```sql
create index concurrently if not exists idx_messages_user_created
  on messages(user_id, created_at desc);
```

### 8) Data Integrity & Constraints
- Foreign key: `messages.user_id` -> `users.id` enforced (with SET NULL on delete)
- Non-null fields respected (direction, created_at, phone_number)
- Direction constraint: only 'incoming' or 'outgoing' allowed
- Long text handling (no truncation for larger bodies - String type, not Text)

### 9) Error Handling Paths
Simulate DB unavailable (temporarily block access) and confirm:
- Webhook returns friendly error XML (Twilio won’t retry forever)
- App logs a clear error (connection failure)

### 10) Privacy & Retention
- Verify PII stored: phone_number, message bodies
- Confirm data retention policy (how long to keep records)
- Right-to-erasure flow: ability to delete a user + cascade messages (if required)
```sql
-- Example manual delete (only if policy allows)
delete from messages where user_id = '<USER_ID>';
delete from users where id = '<USER_ID>';
```

### 11) Backup/Recovery (Optional)
- Confirm automated backups on DB provider
- Restore drill: ability to recover last 24h snapshot (not on prod unless scheduled)

### 12) Acceptance Checklist
- [ ] User auto-created on first inbound (WhatsApp)
- [ ] Incoming message row created (WhatsApp)
- [ ] Outgoing agent reply stored (WhatsApp)
- [ ] Media URL stored for image message (WhatsApp)
- [ ] Chat user auto-created on first chat request
- [ ] Chat messages stored (both regular and streaming)
- [ ] History retrieval returns latest N
- [ ] Indexes used on history queries
- [ ] No obvious duplicates for same event
- [ ] Graceful error when DB unavailable
- [ ] PII storage acceptable and documented

### 13) Quick Commands Reference
```bash
# Send WhatsApp test message
curl -X POST "$BASE_URL/api/webhook" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=+1TESTNUMBER&Body=hello from db test"

# Send WhatsApp with media
curl -X POST "$BASE_URL/api/webhook" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=+1TESTNUMBER&Body=see image&MediaUrl0=https://via.placeholder.com/300.png&NumMedia=1&MediaContentType0=image/jpeg"

# Test chat endpoint
curl -X POST "$BASE_URL/chat/" \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello, I want to schedule an appointment", "media_urls": [], "audio_urls": []}'

# Test chat streaming endpoint
curl -X POST "$BASE_URL/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{"content": "I need help with my medical consultation", "media_urls": [], "audio_urls": []}'
```

Notes:
- `$BASE_URL` is your deployment origin (e.g., `https://whats-app-agent-...vercel.app`).
- Replace `+1TESTNUMBER` and `<USER_ID>` with real values from your run.
- Current implementation uses simplified schema: direct user-message relationship (no conversations/connections tables)
- Chat users are stored as `chat_{user_id}` to distinguish from WhatsApp users
- Manager agent uses `run_manager_legacy()` with simplified context handling


