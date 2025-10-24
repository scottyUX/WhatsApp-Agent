ALTER TABLE patient_image_submissions
    ADD COLUMN IF NOT EXISTS analysis JSONB;
