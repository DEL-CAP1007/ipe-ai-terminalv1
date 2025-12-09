-- Migration for audit_log table (Phase 15.5)
CREATE TABLE IF NOT EXISTS audit_log (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_type      TEXT NOT NULL,
    actor_id        TEXT NOT NULL,
    actor_label     TEXT,
    action          TEXT NOT NULL,
    target_type     TEXT,
    target_id       TEXT,
    target_label    TEXT,
    metadata        JSONB NOT NULL,
    status          TEXT NOT NULL,
    error_message   TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_actor ON audit_log(actor_type, actor_id);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_log(action);
CREATE INDEX IF NOT EXISTS idx_audit_target ON audit_log(target_type, target_id);
CREATE INDEX IF NOT EXISTS idx_audit_created_at ON audit_log(created_at);
