-- Rollback for core patient tables

BEGIN;

DROP TABLE IF EXISTS hair_loss_profiles;
DROP TABLE IF EXISTS medical_histories;
DROP TABLE IF EXISTS patient_profiles;
DROP TABLE IF EXISTS user_profiles;

COMMIT;


