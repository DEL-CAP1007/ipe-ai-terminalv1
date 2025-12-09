-- migrations/20251208_create_entity_index.sql

CREATE TABLE IF NOT EXISTS entity_index (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id     UUID NOT NULL REFERENCES entity(id) ON DELETE CASCADE,
    entity_type   TEXT NOT NULL,
    canonical_id  TEXT NOT NULL,
    title         TEXT,
    summary       TEXT,
    tags          TEXT[] DEFAULT '{}',
    status        TEXT,
    priority      TEXT,
    assignee      TEXT,
    owner         TEXT,
    due_date      TIMESTAMPTZ,
    updated_at    TIMESTAMPTZ NOT NULL,
    search_vector tsvector
);

CREATE INDEX IF NOT EXISTS idx_entity_index_entity_type
    ON entity_index (entity_type);
CREATE INDEX IF NOT EXISTS idx_entity_index_status
    ON entity_index (status);
CREATE INDEX IF NOT EXISTS idx_entity_index_priority
    ON entity_index (priority);
CREATE INDEX IF NOT EXISTS idx_entity_index_tags
    ON entity_index USING GIN (tags);
CREATE INDEX IF NOT EXISTS idx_entity_index_updated_at
    ON entity_index (updated_at);
CREATE INDEX IF NOT EXISTS idx_entity_index_search_vector
    ON entity_index USING GIN (search_vector);
CREATE UNIQUE INDEX IF NOT EXISTS uidx_entity_index_entity
    ON entity_index (entity_id);
