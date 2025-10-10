-- Phase 1 Performance Indexes Rollback

DROP INDEX IF EXISTS idx_leads_status;
DROP INDEX IF EXISTS idx_leads_assigned_to;
DROP INDEX IF EXISTS idx_leads_last_interaction_at;
DROP INDEX IF EXISTS idx_leads_country;
DROP INDEX IF EXISTS idx_leads_campaign;

DROP INDEX IF EXISTS idx_messages_user_id;
DROP INDEX IF EXISTS idx_messages_sent_at;

DROP INDEX IF EXISTS idx_bookings_patient;
DROP INDEX IF EXISTS idx_bookings_provider;
DROP INDEX IF EXISTS idx_bookings_procedure;
DROP INDEX IF EXISTS idx_bookings_date;

DROP INDEX IF EXISTS idx_conversations_user;
DROP INDEX IF EXISTS idx_conversations_status;


