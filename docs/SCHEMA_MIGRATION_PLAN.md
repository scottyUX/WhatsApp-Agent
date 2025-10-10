# Database Schema Migration Plan

## Current State Analysis

The existing schema has these key tables:
- `users` - Basic user management
- `patient_profiles` - Patient information
- `medical_backgrounds` - Medical data (JSONB)
- `messages` - Communication history
- `conversations` - Chat sessions
- `Appoinment` - Basic appointment tracking

## Phase 1: Immediate Medical Questionnaire Support (Week 1-2)

### 1.1 Minimal Schema Updates
```sql
-- Add booking reference to patient profiles
ALTER TABLE patient_profiles 
ADD COLUMN booking_uid TEXT,
ADD COLUMN source_channel TEXT DEFAULT 'medical_questionnaire';

-- Create index for booking lookups
CREATE INDEX idx_patient_profiles_booking_uid ON patient_profiles(booking_uid);

-- Add user type to distinguish user sources
ALTER TABLE users 
ADD COLUMN user_type TEXT DEFAULT 'whatsapp' CHECK (user_type IN ('whatsapp', 'medical_questionnaire', 'chat'));

-- Make phone optional for medical questionnaire users
ALTER TABLE patient_profiles 
ALTER COLUMN phone DROP NOT NULL;
```

### 1.2 New Tables for Medical Questionnaire
```sql
-- Track medical questionnaire submissions
CREATE TABLE medical_questionnaire_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_uid TEXT UNIQUE NOT NULL,
    patient_profile_id UUID REFERENCES patient_profiles(id),
    submission_data JSONB NOT NULL,
    status TEXT NOT NULL DEFAULT 'submitted' CHECK (status IN ('submitted', 'processed', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted BOOLEAN DEFAULT FALSE
);

-- Index for quick lookups
CREATE INDEX idx_medical_submissions_booking_uid ON medical_questionnaire_submissions(booking_uid);
```

## Phase 2: Enhanced Patient Journey (Week 3-4)

### 2.1 Provider Management
```sql
-- Medical providers
CREATE TABLE providers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('clinic', 'hospital', 'doctor')),
    specialty TEXT[],
    location JSONB NOT NULL,
    contact_info JSONB NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted BOOLEAN DEFAULT FALSE
);

-- Procedures
CREATE TABLE procedures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_id UUID NOT NULL REFERENCES providers(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    price_range JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted BOOLEAN DEFAULT FALSE
);
```

### 2.2 Consultation Management
```sql
-- Consultations
CREATE TABLE consultations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_profile_id UUID NOT NULL REFERENCES patient_profiles(id) ON DELETE CASCADE,
    provider_id UUID NOT NULL REFERENCES providers(id) ON DELETE CASCADE,
    procedure_id UUID REFERENCES procedures(id) ON DELETE SET NULL,
    status TEXT NOT NULL DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'completed', 'cancelled', 'no_show')),
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
    meeting_url TEXT,
    notes TEXT,
    outcome TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted BOOLEAN DEFAULT FALSE
);
```

## Phase 3: Marketing & Analytics (Week 5-6)

### 3.1 Lead Management
```sql
-- Lead tracking
CREATE TABLE leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    email TEXT,
    phone TEXT,
    first_name TEXT,
    last_name TEXT,
    source TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'new' CHECK (status IN ('new', 'contacted', 'qualified', 'converted', 'lost')),
    lead_score INTEGER DEFAULT 0,
    assigned_to UUID REFERENCES users(id),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted BOOLEAN DEFAULT FALSE
);

-- Journey tracking
CREATE TABLE patient_journey_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_profile_id UUID NOT NULL REFERENCES patient_profiles(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    event_data JSONB,
    source TEXT,
    session_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted BOOLEAN DEFAULT FALSE
);
```

## Implementation Strategy

### Week 1: Medical Questionnaire Support
1. **Day 1-2**: Update existing tables with minimal changes
2. **Day 3-4**: Create medical questionnaire submission table
3. **Day 5**: Update backend services to use new schema
4. **Day 6-7**: Test and deploy medical questionnaire functionality

### Week 2: Enhanced Data Management
1. **Day 1-3**: Implement provider and procedure management
2. **Day 4-5**: Create consultation booking system
3. **Day 6-7**: Update frontend to use new booking system

### Week 3-4: Marketing Intelligence
1. **Day 1-5**: Implement lead tracking and journey analytics
2. **Day 6-10**: Create marketing dashboard and reporting
3. **Day 11-14**: A/B testing and optimization

## Migration Scripts

### Migration 1: Add Medical Questionnaire Support
```sql
-- migration_001_medical_questionnaire.sql
BEGIN;

-- Add new columns to existing tables
ALTER TABLE patient_profiles 
ADD COLUMN booking_uid TEXT,
ADD COLUMN source_channel TEXT DEFAULT 'medical_questionnaire';

ALTER TABLE users 
ADD COLUMN user_type TEXT DEFAULT 'whatsapp' CHECK (user_type IN ('whatsapp', 'medical_questionnaire', 'chat'));

-- Make phone optional
ALTER TABLE patient_profiles 
ALTER COLUMN phone DROP NOT NULL;

-- Create medical questionnaire submissions table
CREATE TABLE medical_questionnaire_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_uid TEXT UNIQUE NOT NULL,
    patient_profile_id UUID REFERENCES patient_profiles(id),
    submission_data JSONB NOT NULL,
    status TEXT NOT NULL DEFAULT 'submitted' CHECK (status IN ('submitted', 'processed', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted BOOLEAN DEFAULT FALSE
);

-- Create indexes
CREATE INDEX idx_patient_profiles_booking_uid ON patient_profiles(booking_uid);
CREATE INDEX idx_medical_submissions_booking_uid ON medical_questionnaire_submissions(booking_uid);

COMMIT;
```

## Rollback Plan

Each migration includes rollback scripts:

```sql
-- rollback_001_medical_questionnaire.sql
BEGIN;

-- Drop new tables
DROP TABLE IF EXISTS medical_questionnaire_submissions;

-- Remove new columns
ALTER TABLE patient_profiles 
DROP COLUMN IF EXISTS booking_uid,
DROP COLUMN IF EXISTS source_channel;

ALTER TABLE users 
DROP COLUMN IF EXISTS user_type;

-- Restore phone as required
ALTER TABLE patient_profiles 
ALTER COLUMN phone SET NOT NULL;

-- Drop indexes
DROP INDEX IF EXISTS idx_patient_profiles_booking_uid;
DROP INDEX IF EXISTS idx_medical_submissions_booking_uid;

COMMIT;
```

## Testing Strategy

### 1. Unit Tests
- Test all new database operations
- Validate data integrity constraints
- Test migration scripts

### 2. Integration Tests
- Test medical questionnaire submission flow
- Test booking creation and lookup
- Test user creation and profile management

### 3. Performance Tests
- Test query performance with new indexes
- Test concurrent user scenarios
- Test data migration performance

### 4. User Acceptance Tests
- Test complete patient journey
- Test admin functionality
- Test reporting and analytics

## Monitoring & Maintenance

### 1. Database Monitoring
- Query performance monitoring
- Index usage analysis
- Storage growth tracking

### 2. Data Quality
- Regular data validation
- Duplicate detection
- Data consistency checks

### 3. Backup & Recovery
- Automated daily backups
- Point-in-time recovery testing
- Disaster recovery procedures

This migration plan ensures a smooth transition from the current schema to a more robust system while maintaining backward compatibility and minimizing downtime.
