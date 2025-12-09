-- Migration for secret table (Phase 15.3)
CREATE TABLE IF NOT EXISTS secret (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT UNIQUE NOT NULL,
    value_encrypted BYTEA NOT NULL,
    scope           TEXT NOT NULL,
    owner_user_id   UUID REFERENCES "user"(id),
    owner_service_id UUID REFERENCES service_account(id),
    description     TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_secret_scope ON secret(scope);
