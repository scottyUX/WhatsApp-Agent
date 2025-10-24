BEGIN;

-- Remove currency constraint and reset default
ALTER TABLE packages DROP CONSTRAINT IF EXISTS packages_currency_check;
ALTER TABLE packages ALTER COLUMN currency SET DEFAULT 'USD';

-- Remove all the new columns added in the enhancement
ALTER TABLE packages DROP COLUMN IF EXISTS clinic_id;
ALTER TABLE packages DROP COLUMN IF EXISTS grafts_count;
ALTER TABLE packages DROP COLUMN IF EXISTS hair_transplantation_method;
ALTER TABLE packages DROP COLUMN IF EXISTS stem_cell_therapy_sessions;
ALTER TABLE packages DROP COLUMN IF EXISTS airport_lounge_access_included;
ALTER TABLE packages DROP COLUMN IF EXISTS airport_lounge_access_details;
ALTER TABLE packages DROP COLUMN IF EXISTS breakfast_included;
ALTER TABLE packages DROP COLUMN IF EXISTS hotel_name;
ALTER TABLE packages DROP COLUMN IF EXISTS hotel_nights_included;
ALTER TABLE packages DROP COLUMN IF EXISTS hotel_star_rating;
ALTER TABLE packages DROP COLUMN IF EXISTS private_translator_included;
ALTER TABLE packages DROP COLUMN IF EXISTS vip_transfer_details;
ALTER TABLE packages DROP COLUMN IF EXISTS aftercare_kit_supply_duration;
ALTER TABLE packages DROP COLUMN IF EXISTS laser_sessions;
ALTER TABLE packages DROP COLUMN IF EXISTS online_follow_ups_duration;
ALTER TABLE packages DROP COLUMN IF EXISTS oxygen_therapy_sessions;
ALTER TABLE packages DROP COLUMN IF EXISTS post_operation_medication_included;
ALTER TABLE packages DROP COLUMN IF EXISTS prp_sessions_included;
ALTER TABLE packages DROP COLUMN IF EXISTS sedation_included;

COMMIT;
