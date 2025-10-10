-- Consultations compatibility view over existing appointment table
-- Assumes column parity with docs/DATABASE_SCHEMA_VISION.md consultations schema

BEGIN;

-- Create or replace the view mapping consultations to appointment
CREATE OR REPLACE VIEW consultations AS
SELECT
  a.id,
  a.patient_profile_id,
  a.provider_id,
  a.procedure_id,
  a.consultation_type,
  a.status,
  a.scheduled_at,
  a.duration_minutes,
  a.meeting_url,
  a.meeting_id,
  a.notes,
  a.outcome,
  a.follow_up_required,
  a.created_at,
  a.updated_at,
  a.deleted
FROM appointment a;

-- Upsert helper: INSTEAD OF INSERT maps to appointment
CREATE OR REPLACE FUNCTION consultations_insert_fn()
RETURNS trigger AS $$
BEGIN
  INSERT INTO appointment (
    patient_profile_id,
    provider_id,
    procedure_id,
    consultation_type,
    status,
    scheduled_at,
    duration_minutes,
    meeting_url,
    meeting_id,
    notes,
    outcome,
    follow_up_required
  ) VALUES (
    NEW.patient_profile_id,
    NEW.provider_id,
    NEW.procedure_id,
    NEW.consultation_type,
    COALESCE(NEW.status, 'scheduled'),
    NEW.scheduled_at,
    COALESCE(NEW.duration_minutes, 30),
    NEW.meeting_url,
    NEW.meeting_id,
    NEW.notes,
    NEW.outcome,
    COALESCE(NEW.follow_up_required, FALSE)
  ) RETURNING * INTO NEW;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION consultations_update_fn()
RETURNS trigger AS $$
BEGIN
  UPDATE appointment SET
    patient_profile_id = NEW.patient_profile_id,
    provider_id = NEW.provider_id,
    procedure_id = NEW.procedure_id,
    consultation_type = NEW.consultation_type,
    status = NEW.status,
    scheduled_at = NEW.scheduled_at,
    duration_minutes = NEW.duration_minutes,
    meeting_url = NEW.meeting_url,
    meeting_id = NEW.meeting_id,
    notes = NEW.notes,
    outcome = NEW.outcome,
    follow_up_required = NEW.follow_up_required
  WHERE id = OLD.id
  RETURNING * INTO NEW;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION consultations_delete_fn()
RETURNS trigger AS $$
BEGIN
  -- Prefer soft delete if column exists; fallback to hard delete
  BEGIN
    UPDATE appointment SET deleted = TRUE WHERE id = OLD.id;
  EXCEPTION WHEN undefined_column THEN
    DELETE FROM appointment WHERE id = OLD.id;
  END;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS consultations_insert_tr ON consultations;
CREATE TRIGGER consultations_insert_tr
INSTEAD OF INSERT ON consultations
FOR EACH ROW EXECUTE FUNCTION consultations_insert_fn();

DROP TRIGGER IF EXISTS consultations_update_tr ON consultations;
CREATE TRIGGER consultations_update_tr
INSTEAD OF UPDATE ON consultations
FOR EACH ROW EXECUTE FUNCTION consultations_update_fn();

DROP TRIGGER IF EXISTS consultations_delete_tr ON consultations;
CREATE TRIGGER consultations_delete_tr
INSTEAD OF DELETE ON consultations
FOR EACH ROW EXECUTE FUNCTION consultations_delete_fn();

COMMIT;


