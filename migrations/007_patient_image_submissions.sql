CREATE TABLE IF NOT EXISTS patient_image_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_profile_id UUID NOT NULL REFERENCES patient_profiles(id),
    image_urls TEXT[] NOT NULL,
    analysis_notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_patient_image_submissions_profile_id
    ON patient_image_submissions (patient_profile_id);
