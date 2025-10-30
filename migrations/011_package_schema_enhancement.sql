BEGIN;

-- Drop deprecated columns
ALTER TABLE packages DROP COLUMN IF EXISTS grafts;
ALTER TABLE packages DROP COLUMN IF EXISTS airport_lounge_access_notes;
ALTER TABLE packages DROP COLUMN IF EXISTS aftercare_kit_duration;

-- Add clinic_id foreign key to packages table
ALTER TABLE packages 
    ADD COLUMN IF NOT EXISTS clinic_id UUID REFERENCES clinics(id);

-- Add currency enum constraint
ALTER TABLE packages 
    DROP CONSTRAINT IF EXISTS packages_currency_check;
ALTER TABLE packages 
    ADD CONSTRAINT packages_currency_check 
    CHECK (currency IN ('USD', 'EUR', 'GBP', 'TRY'));

-- Update default currency to EUR
ALTER TABLE packages 
    ALTER COLUMN currency SET DEFAULT 'EUR';

-- Add treatment specifics columns
ALTER TABLE packages 
    ADD COLUMN IF NOT EXISTS grafts_count TEXT CHECK (grafts_count IN ('1000', '1500', '2000', '2500', '3000', '3500', '4000', '4500', '5000', '5500', '6000', 'Unlimited'));
ALTER TABLE packages 
    ADD COLUMN IF NOT EXISTS hair_transplantation_method TEXT CHECK (hair_transplantation_method IN ('DHI Transplant Method', 'FUE Transplant Method', 'FUT Transplant Method', 'Sapphire FUE Method'));
ALTER TABLE packages 
    ADD COLUMN IF NOT EXISTS stem_cell_therapy_sessions INTEGER NOT NULL DEFAULT 0;

-- Add travel & accommodation columns
ALTER TABLE packages 
    ADD COLUMN IF NOT EXISTS airport_lounge_access_included BOOLEAN NOT NULL DEFAULT false;
ALTER TABLE packages 
    ADD COLUMN IF NOT EXISTS airport_lounge_access_details TEXT CHECK (airport_lounge_access_details IN ('IST only', 'Both ways'));
ALTER TABLE packages 
    ADD COLUMN IF NOT EXISTS breakfast_included BOOLEAN NOT NULL DEFAULT false;
ALTER TABLE packages 
    ADD COLUMN IF NOT EXISTS hotel_name TEXT;
ALTER TABLE packages 
    ADD COLUMN IF NOT EXISTS hotel_nights_included INTEGER NOT NULL DEFAULT 0;
ALTER TABLE packages 
    ADD COLUMN IF NOT EXISTS hotel_star_rating INTEGER NOT NULL DEFAULT 0;
ALTER TABLE packages 
    ADD COLUMN IF NOT EXISTS private_translator_included BOOLEAN NOT NULL DEFAULT false;
ALTER TABLE packages 
    ADD COLUMN IF NOT EXISTS vip_transfer_details TEXT CHECK (vip_transfer_details IN ('Hotel only', 'Airport only', 'Clinic only', 'Airport - hotel - clinic'));

-- Add aftercare columns
ALTER TABLE packages 
    ADD COLUMN IF NOT EXISTS aftercare_kit_supply_duration TEXT CHECK (aftercare_kit_supply_duration IN ('3 months', '6 months', '13 months'));
ALTER TABLE packages 
    ADD COLUMN IF NOT EXISTS laser_sessions INTEGER NOT NULL DEFAULT 0;
ALTER TABLE packages 
    ADD COLUMN IF NOT EXISTS online_follow_ups_duration TEXT CHECK (online_follow_ups_duration IN ('3 months', '6 months', '12 months', 'Lifetime'));
ALTER TABLE packages 
    ADD COLUMN IF NOT EXISTS oxygen_therapy_sessions INTEGER NOT NULL DEFAULT 0;
ALTER TABLE packages 
    ADD COLUMN IF NOT EXISTS post_operation_medication_included BOOLEAN NOT NULL DEFAULT false;
ALTER TABLE packages 
    ADD COLUMN IF NOT EXISTS prp_sessions_included BOOLEAN NOT NULL DEFAULT false;
ALTER TABLE packages 
    ADD COLUMN IF NOT EXISTS sedation_included BOOLEAN NOT NULL DEFAULT false;

COMMIT;
