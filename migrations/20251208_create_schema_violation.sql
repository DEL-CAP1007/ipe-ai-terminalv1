CREATE TABLE IF NOT EXISTS schema_violation (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id    UUID NOT NULL REFERENCES entity(id) ON DELETE CASCADE,
    entity_type  TEXT NOT NULL,
    canonical_id TEXT NOT NULL,
    errors       JSONB NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at  TIMESTAMPTZ
);
