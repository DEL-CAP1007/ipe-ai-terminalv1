CREATE TABLE IF NOT EXISTS trigger (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name           TEXT NOT NULL,
    description    TEXT,
    event_type     TEXT NOT NULL,
    conditions     JSONB NOT NULL,
    action         JSONB NOT NULL,
    is_enabled     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_trigger_event_type ON trigger(event_type);
CREATE INDEX idx_trigger_is_enabled ON trigger(is_enabled);
