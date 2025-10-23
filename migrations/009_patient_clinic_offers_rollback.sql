BEGIN;

ALTER TABLE patient_profiles
    DROP COLUMN IF EXISTS clinic_offer_ids;

ALTER TABLE clinics
    ADD COLUMN IF NOT EXISTS offer TEXT;

COMMIT;
