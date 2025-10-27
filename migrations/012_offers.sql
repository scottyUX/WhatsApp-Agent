BEGIN;

-- Create offers table
CREATE TABLE IF NOT EXISTS offers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Core relationships
    patient_profile_id UUID NOT NULL REFERENCES patient_profiles(id) ON DELETE CASCADE,
    
    -- Clinic selection (up to 3 clinics)
    -- Will fetch packages via clinic_packages junction table
    clinic_ids UUID[] NOT NULL DEFAULT '{}'::uuid[],
    
    -- Pricing snapshot (captured when offer is created)
    total_price DECIMAL(12, 2),
    currency VARCHAR(10) DEFAULT 'USD',
    deposit_amount DECIMAL(12, 2),
    
    -- Payment options (multiple can be selected)
    payment_methods TEXT[] NOT NULL DEFAULT '{}'::text[]
        CHECK (payment_methods <@ ARRAY['credit_card', 'klarna', 'paypal']),
    
    -- Status lifecycle
    status VARCHAR(50) NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft', 'approved', 'sent', 'deposit_received', 'paid_in_full', 'refunded')),
    
    -- Notes
    notes TEXT,
    
    -- Status history (track all status changes with timestamps and notes)
    status_history JSONB DEFAULT '[]'::jsonb,
    
    -- Audit fields
    created_by UUID, -- consultant_id
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CHECK (array_length(clinic_ids, 1) <= 3) -- Max 3 clinics per offer
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_offers_patient_profile_id 
    ON offers(patient_profile_id);
    
CREATE INDEX IF NOT EXISTS idx_offers_status 
    ON offers(status);
    
CREATE INDEX IF NOT EXISTS idx_offers_created_at 
    ON offers(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_offers_clinic_ids 
    ON offers USING GIN(clinic_ids); -- GIN index for array queries

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_offers_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update updated_at
CREATE TRIGGER trigger_update_offers_updated_at
    BEFORE UPDATE ON offers
    FOR EACH ROW
    EXECUTE FUNCTION update_offers_updated_at();

COMMIT;

