-- Phase 1 Performance Indexes (create concurrently where allowed)
-- Note: CREATE INDEX CONCURRENTLY cannot run inside a transaction block.

-- Leads common queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_leads_assigned_to ON leads(assigned_to);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_leads_last_interaction_at ON leads(last_interaction_at DESC);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_leads_country ON leads(country);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_leads_campaign ON leads(campaign_id);

-- Messages: by user and time
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_user_id ON messages(user_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_sent_at ON messages(sent_at DESC);

-- Bookings: by foreign keys and date
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bookings_patient ON bookings(patient_profile_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bookings_provider ON bookings(provider_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bookings_procedure ON bookings(procedure_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bookings_date ON bookings(procedure_date);

-- Conversations: by user and status
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conversations_user ON conversation_sessions(user_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conversations_status ON conversation_sessions(status);


