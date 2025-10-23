BEGIN;

ALTER TABLE clinics
    ADD COLUMN IF NOT EXISTS has_contract BOOLEAN NOT NULL DEFAULT false;

ALTER TABLE clinics
    ADD COLUMN IF NOT EXISTS package_ids UUID[] NOT NULL DEFAULT '{}'::uuid[];

CREATE TABLE IF NOT EXISTS packages (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    price NUMERIC(12, 2),
    currency TEXT NOT NULL DEFAULT 'USD',
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc', now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc', now())
);

CREATE TABLE IF NOT EXISTS clinic_packages (
    clinic_id UUID NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    package_id UUID NOT NULL REFERENCES packages(id) ON DELETE CASCADE,
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc', now()),
    PRIMARY KEY (clinic_id, package_id)
);

COMMIT;
