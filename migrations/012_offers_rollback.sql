BEGIN;

-- Drop trigger and function
DROP TRIGGER IF EXISTS trigger_update_offers_updated_at ON offers;
DROP FUNCTION IF EXISTS update_offers_updated_at();

-- Drop indexes
DROP INDEX IF EXISTS idx_offers_clinic_ids;
DROP INDEX IF EXISTS idx_offers_created_at;
DROP INDEX IF EXISTS idx_offers_status;
DROP INDEX IF EXISTS idx_offers_patient_profile_id;

-- Drop offers table
DROP TABLE IF EXISTS offers;

COMMIT;

