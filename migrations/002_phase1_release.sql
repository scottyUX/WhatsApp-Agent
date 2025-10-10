-- Phase 1 Release Migration
-- This migration aligns the DB with docs/DATABASE_SCHEMA_VISION.md updates.
-- Safe for PostgreSQL. Run inside a transaction.

BEGIN;

-- 1) bookings: remove duration_hours, set currency default EUR, update payment_status enum set
DO $$
DECLARE t_exists boolean;
BEGIN
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables WHERE table_name='bookings'
    ) INTO t_exists;
    IF t_exists THEN
        -- 1a) Remove duration_hours if it exists
        IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name='bookings' AND column_name='duration_hours'
        ) THEN
            ALTER TABLE bookings DROP COLUMN duration_hours;
        END IF;

        -- 1b) Set currency default to 'EUR'
        ALTER TABLE bookings ALTER COLUMN currency SET DEFAULT 'EUR';

        -- 1c) Update payment_status constraint: replace 'partial' with 'deposit'
        UPDATE bookings SET payment_status = 'deposit' WHERE payment_status = 'partial';

        -- Drop existing check constraint (name may vary) and recreate
        PERFORM 1; -- placeholder
        DECLARE cons_name text;
        SELECT conname INTO cons_name
        FROM pg_constraint
        WHERE conrelid = 'bookings'::regclass AND contype = 'c' AND conname LIKE 'bookings_payment_status_check%';
        IF cons_name IS NOT NULL THEN
            EXECUTE format('ALTER TABLE bookings DROP CONSTRAINT %I', cons_name);
        END IF;
        FOR cons_name IN
            SELECT conname FROM pg_constraint
            WHERE conrelid='bookings'::regclass AND contype='c' AND pg_get_constraintdef(oid) ILIKE '%payment_status%'
        LOOP
            EXECUTE format('ALTER TABLE bookings DROP CONSTRAINT %I', cons_name);
        END LOOP;

        ALTER TABLE bookings
            ADD CONSTRAINT bookings_payment_status_check
            CHECK (payment_status IN ('pending','deposit','paid','refunded'));
    END IF;
END $$;

-- 2) communication_channels: extend channel_type to include 'zoom'
DO $$
DECLARE t_exists boolean; cons_name text;
BEGIN
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables WHERE table_name='communication_channels'
    ) INTO t_exists;
    IF t_exists THEN
        SELECT conname INTO cons_name
        FROM pg_constraint
        WHERE conrelid = 'communication_channels'::regclass AND contype = 'c' AND conname LIKE 'communication_channels_channel_type_check%';
        IF cons_name IS NOT NULL THEN
            EXECUTE format('ALTER TABLE communication_channels DROP CONSTRAINT %I', cons_name);
        END IF;
        FOR cons_name IN
            SELECT conname FROM pg_constraint
            WHERE conrelid='communication_channels'::regclass AND contype='c' AND pg_get_constraintdef(oid) ILIKE '%channel_type%'
        LOOP
            EXECUTE format('ALTER TABLE communication_channels DROP CONSTRAINT %I', cons_name);
        END LOOP;

        ALTER TABLE communication_channels
            ADD CONSTRAINT communication_channels_channel_type_check
            CHECK (channel_type IN ('whatsapp','email','sms','phone','chat','zoom'));
    END IF;
END $$;

-- 3) consultations: extend consultation_type to include 'zoom'
DO $$
DECLARE t_exists boolean; cons_name text;
BEGIN
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables WHERE table_name='consultations'
    ) INTO t_exists;
    IF t_exists THEN
        SELECT conname INTO cons_name
        FROM pg_constraint
        WHERE conrelid = 'consultations'::regclass AND contype = 'c' AND conname LIKE 'consultations_consultation_type_check%';
        IF cons_name IS NOT NULL THEN
            EXECUTE format('ALTER TABLE consultations DROP CONSTRAINT %I', cons_name);
        END IF;
        FOR cons_name IN
            SELECT conname FROM pg_constraint
            WHERE conrelid='consultations'::regclass AND contype='c' AND pg_get_constraintdef(oid) ILIKE '%consultation_type%'
        LOOP
            EXECUTE format('ALTER TABLE consultations DROP CONSTRAINT %I', cons_name);
        END LOOP;

        ALTER TABLE consultations
            ADD CONSTRAINT consultations_consultation_type_check
            CHECK (consultation_type IN ('video','phone','in_person','zoom'));
    END IF;
END $$;

-- 4) leads: add enrichment fields if they do not exist (only if leads table exists)
DO $$
DECLARE t_exists boolean;
BEGIN
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables WHERE table_name='leads'
    ) INTO t_exists;
    IF t_exists THEN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns WHERE table_name='leads' AND column_name='last_interaction_at'
        ) THEN ALTER TABLE leads ADD COLUMN last_interaction_at TIMESTAMP WITH TIME ZONE; END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns WHERE table_name='leads' AND column_name='company'
        ) THEN ALTER TABLE leads ADD COLUMN company TEXT; END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns WHERE table_name='leads' AND column_name='job_title'
        ) THEN ALTER TABLE leads ADD COLUMN job_title TEXT; END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns WHERE table_name='leads' AND column_name='country'
        ) THEN ALTER TABLE leads ADD COLUMN country TEXT; END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns WHERE table_name='leads' AND column_name='city'
        ) THEN ALTER TABLE leads ADD COLUMN city TEXT; END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns WHERE table_name='leads' AND column_name='age_group'
        ) THEN ALTER TABLE leads ADD COLUMN age_group TEXT; END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns WHERE table_name='leads' AND column_name='income_group'
        ) THEN ALTER TABLE leads ADD COLUMN income_group TEXT; END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns WHERE table_name='leads' AND column_name='timezone'
        ) THEN ALTER TABLE leads ADD COLUMN timezone TEXT; END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns WHERE table_name='leads' AND column_name='deal_value'
        ) THEN ALTER TABLE leads ADD COLUMN deal_value DECIMAL(10,2); END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns WHERE table_name='leads' AND column_name='work_email'
        ) THEN ALTER TABLE leads ADD COLUMN work_email TEXT; END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns WHERE table_name='leads' AND column_name='employment_history'
        ) THEN ALTER TABLE leads ADD COLUMN employment_history JSONB DEFAULT '[]'; END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns WHERE table_name='leads' AND column_name='linkedin_url'
        ) THEN ALTER TABLE leads ADD COLUMN linkedin_url TEXT; END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns WHERE table_name='leads' AND column_name='reddit_handle'
        ) THEN ALTER TABLE leads ADD COLUMN reddit_handle TEXT; END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns WHERE table_name='leads' AND column_name='x_handle'
        ) THEN ALTER TABLE leads ADD COLUMN x_handle TEXT; END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns WHERE table_name='leads' AND column_name='facebook_profile'
        ) THEN ALTER TABLE leads ADD COLUMN facebook_profile TEXT; END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns WHERE table_name='leads' AND column_name='tiktok_profile'
        ) THEN ALTER TABLE leads ADD COLUMN tiktok_profile TEXT; END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns WHERE table_name='leads' AND column_name='instagram_profile'
        ) THEN ALTER TABLE leads ADD COLUMN instagram_profile TEXT; END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns WHERE table_name='leads' AND column_name='lead_summary'
        ) THEN ALTER TABLE leads ADD COLUMN lead_summary TEXT; END IF;
    END IF;
END $$;

COMMIT;


