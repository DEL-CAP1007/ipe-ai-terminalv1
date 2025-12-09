-- migrations/20251208_create_entity_embedding.sql

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS entity_embedding (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id   UUID NOT NULL REFERENCES entity(id) ON DELETE CASCADE,
    embedding   vector(1536),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (entity_id)
);

CREATE INDEX IF NOT EXISTS idx_entity_embedding_vector
    ON entity_embedding USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);
