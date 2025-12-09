CREATE TABLE IF NOT EXISTS trigger_run (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trigger_id     UUID NOT NULL REFERENCES trigger(id),
    event_type     TEXT NOT NULL,
    event_payload  JSONB NOT NULL,
    started_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at    TIMESTAMPTZ,
    status         TEXT NOT NULL,
    error_message  TEXT
);
CREATE INDEX idx_trigger_run_trigger ON trigger_run(trigger_id);
CREATE INDEX idx_trigger_run_status ON trigger_run(status);
