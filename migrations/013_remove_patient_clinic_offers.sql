BEGIN;

-- Remove unused clinic offer cache from patient profiles
ALTER TABLE patient_profiles
    DROP COLUMN IF EXISTS clinic_offer_ids;

COMMIT;

