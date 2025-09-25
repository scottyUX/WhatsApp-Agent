-- Create enums
CREATE TYPE media_type AS ENUM ('image', 'audio');
CREATE TYPE scheduling_step AS ENUM ('initial_contact', 'basic_info', 'consultation_scheduling', 'additional_info', 'closure');
CREATE TYPE appointment_status AS ENUM ('scheduled', 'confirmed', 'cancelled', 'completed');
CREATE TYPE gender AS ENUM ('male', 'female', 'other', 'prefer_not_to_say');

-- Users table
CREATE TABLE users (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    auth_id text,
    name text,
    email text,
    phone_number text,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    deleted boolean DEFAULT false,
    
    -- Constraints
    CONSTRAINT uq_user_auth_id UNIQUE (auth_id),
    CONSTRAINT uq_user_phone_number UNIQUE (phone_number)
);

-- Connections table
CREATE TABLE connections (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    device_id uuid,
    ip_address text,
    channel text NOT NULL,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    deleted boolean DEFAULT false
);

-- Connection changes table
CREATE TABLE connection_changes (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    from_user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    to_user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    action text NOT NULL, -- 'merge' or 'unmerge'
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    deleted boolean DEFAULT false,
    
    -- Constraints
    CONSTRAINT check_action CHECK (action IN ('merge', 'unmerge'))
);

-- Conversations table
CREATE TABLE conversations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    connection_id uuid NOT NULL REFERENCES connections(id) ON DELETE CASCADE,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    deleted boolean DEFAULT false
);

-- Messages table
CREATE TABLE messages (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id uuid NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    sender text NOT NULL,
    content text NOT NULL,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    deleted boolean DEFAULT false
);

-- Media table
CREATE TABLE media (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id uuid NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    media_type media_type NOT NULL,
    media_url text NOT NULL,
    filename text,
    file_size integer,
    mime_type text,
    caption text,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    deleted boolean DEFAULT false
);

-- Patient profiles table
CREATE TABLE patient_profiles (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name text DEFAULT '',
    phone text DEFAULT '',
    email text DEFAULT '',
    location text DEFAULT '',
    age integer,
    gender gender,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    deleted boolean DEFAULT false,

    -- Constraints
    CONSTRAINT uq_patient_profile_user_id UNIQUE (user_id)
);

-- Medical backgrounds table
CREATE TABLE medical_backgrounds (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_profile_id uuid NOT NULL REFERENCES patient_profiles(id) ON DELETE CASCADE,
    medical_data jsonb DEFAULT '{}',
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    deleted boolean DEFAULT false,

    -- Constraints
    CONSTRAINT uq_medical_background_patient_profile_id UNIQUE (patient_profile_id)
);

-- Conversation states table
CREATE TABLE conversation_states (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_profile_id uuid NOT NULL REFERENCES patient_profiles(id) ON DELETE CASCADE,
    current_step scheduling_step NOT NULL,
    last_activity timestamptz DEFAULT now(),
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    deleted boolean DEFAULT false
);

-- Indexes for performance
CREATE INDEX idx_connections_user_id ON connections(user_id);
CREATE INDEX idx_conversations_connection_id ON conversations(connection_id);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_media_message_id ON media(message_id);
CREATE INDEX idx_users_phone_number ON users(phone_number);
CREATE INDEX idx_users_auth_id ON users(auth_id);
CREATE INDEX idx_patient_profiles_user_id ON patient_profiles(user_id);
CREATE INDEX idx_medical_backgrounds_patient_profile_id ON medical_backgrounds(patient_profile_id);
CREATE INDEX idx_conversation_states_patient_profile_id ON conversation_states(patient_profile_id);
CREATE INDEX idx_conversation_states_current_step ON conversation_states(current_step);
CREATE INDEX idx_conversation_states_last_activity ON conversation_states(last_activity);

-- Update triggers for updated_at columns
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_connections_updated_at BEFORE UPDATE ON connections
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_connection_changes_updated_at BEFORE UPDATE ON connection_changes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_messages_updated_at BEFORE UPDATE ON messages
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_media_updated_at BEFORE UPDATE ON media
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_patient_profiles_updated_at BEFORE UPDATE ON patient_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_medical_backgrounds_updated_at BEFORE UPDATE ON medical_backgrounds
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversation_states_updated_at BEFORE UPDATE ON conversation_states
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
