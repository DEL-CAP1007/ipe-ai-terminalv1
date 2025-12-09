-- Migration for api_token table (Phase 15.4)
CREATE TABLE IF NOT EXISTS api_token (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    token_hash        TEXT NOT NULL,
    owner_user_id     UUID REFERENCES "user"(id),
    owner_service_id  UUID REFERENCES service_account(id),
    scopes            JSONB NOT NULL,
    description       TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at        TIMESTAMPTZ,
    last_used_at      TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_api_token_owner_user ON api_token(owner_user_id);
CREATE INDEX IF NOT EXISTS idx_api_token_owner_service ON api_token(owner_service_id);
