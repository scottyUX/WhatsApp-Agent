BEGIN;

DROP INDEX IF EXISTS idx_offers_package_ids;

ALTER TABLE offers
    DROP CONSTRAINT IF EXISTS check_offers_package_ids_length;

ALTER TABLE offers
    DROP COLUMN IF EXISTS package_ids;

COMMIT;

