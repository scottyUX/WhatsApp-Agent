BEGIN;

DROP TABLE IF EXISTS clinic_packages;
DROP TABLE IF EXISTS packages;

ALTER TABLE clinics
    DROP COLUMN IF EXISTS package_ids;

ALTER TABLE clinics
    DROP COLUMN IF EXISTS has_contract;

COMMIT;
