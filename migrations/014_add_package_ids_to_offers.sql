BEGIN;

ALTER TABLE offers
    ADD COLUMN IF NOT EXISTS package_ids UUID[] NOT NULL DEFAULT '{}'::uuid[];

ALTER TABLE offers
    DROP CONSTRAINT IF EXISTS check_offers_package_ids_length;

ALTER TABLE offers
    ADD CONSTRAINT check_offers_package_ids_length
        CHECK (array_length(package_ids, 1) <= 3);

CREATE INDEX IF NOT EXISTS idx_offers_package_ids
    ON offers USING GIN(package_ids);

COMMIT;

