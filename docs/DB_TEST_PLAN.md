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
- Tables exist (adjust schema/table names if prefixed):
```sql
select table_name from information_schema.tables where table_schema = 'public'
  and table_name in ('users','messages','media','patient_profiles','medical_backgrounds');
```
- Columns sanity (users, messages):
```sql
select column_name, data_type from information_schema.columns 
 where table_name = 'users';
select column_name, data_type from information_schema.columns 
 where table_name = 'messages';
```
- Note: `media` table exists but is separate from `messages.media_url` - both are valid storage patterns

### 3) Core Persistence: Inbound + Outbound Messages
Goal: When a WhatsApp message arrives, we store one incoming and one outgoing record and (optionally) media.

Steps:
1. Send a message via WhatsApp UI (or curl) to POST /api/webhook:
```bash
curl -X POST "$BASE_URL/api/webhook" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=whatsapp:+1TESTNUMBER&Body=hello from db test"
```
2. Query user auto-creation:
```sql
select id, phone_number, name, created_at
from users
where phone_number = 'whatsapp:+1TESTNUMBER';
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
  -d "From=whatsapp:+1TESTNUMBER&Body=see image&MediaUrl0=https://via.placeholder.com/300.png&NumMedia=1&MediaContentType0=image/jpeg"
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
Note: Implementation stores first media URL in `messages.media_url` field, not separate `media` table.

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
  select id from users where phone_number = 'whatsapp:+1TESTNUMBER'
)
order by created_at desc
limit 10;
```
Expect: Matches app responses order (most recent first).

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
- [ ] User auto-created on first inbound
- [ ] Incoming message row created
- [ ] Outgoing agent reply stored
- [ ] Media URL stored for image message
- [ ] History retrieval returns latest N
- [ ] Indexes used on history queries
- [ ] No obvious duplicates for same event
- [ ] Graceful error when DB unavailable
- [ ] PII storage acceptable and documented

### 13) Quick Commands Reference
```bash
# Send test message
curl -X POST "$BASE_URL/api/webhook" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=whatsapp:+1TESTNUMBER&Body=hello from db test"

# Send with media
curl -X POST "$BASE_URL/api/webhook" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=whatsapp:+1TESTNUMBER&Body=see image&MediaUrl0=https://via.placeholder.com/300.png&NumMedia=1&MediaContentType0=image/jpeg"
```

Notes:
- `$BASE_URL` is your deployment origin (e.g., `https://whats-app-agent-...vercel.app`).
- Replace `+1TESTNUMBER` and `<USER_ID>` with real values from your run.


