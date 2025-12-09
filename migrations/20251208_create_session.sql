CREATE TABLE IF NOT EXISTS session (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES "user"(id),
    service_id UUID REFERENCES service_account(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    last_active_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_agent TEXT,
    client_ip TEXT
);

CREATE INDEX IF NOT EXISTS idx_session_user ON session(user_id);
CREATE INDEX IF NOT EXISTS idx_session_service ON session(service_id);
