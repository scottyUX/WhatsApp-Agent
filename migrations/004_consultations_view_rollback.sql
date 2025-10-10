-- Rollback for consultations compatibility view

BEGIN;

DROP TRIGGER IF EXISTS consultations_insert_tr ON consultations;
DROP TRIGGER IF EXISTS consultations_update_tr ON consultations;
DROP TRIGGER IF EXISTS consultations_delete_tr ON consultations;

DROP FUNCTION IF EXISTS consultations_insert_fn();
DROP FUNCTION IF EXISTS consultations_update_fn();
DROP FUNCTION IF EXISTS consultations_delete_fn();

DROP VIEW IF EXISTS consultations;

COMMIT;


