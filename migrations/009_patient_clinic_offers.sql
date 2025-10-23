BEGIN;

ALTER TABLE clinics
    DROP COLUMN IF EXISTS offer;

ALTER TABLE patient_profiles
    ADD COLUMN IF NOT EXISTS clinic_offer_ids UUID[] NOT NULL DEFAULT '{}'::uuid[];

COMMIT;
