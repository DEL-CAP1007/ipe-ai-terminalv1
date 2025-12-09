CREATE TABLE IF NOT EXISTS entity_relation (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_entity_id UUID NOT NULL REFERENCES entity(id) ON DELETE CASCADE,
    from_type      TEXT NOT NULL,
    from_canonical TEXT NOT NULL,
    to_entity_id   UUID NOT NULL REFERENCES entity(id) ON DELETE CASCADE,
    to_type        TEXT NOT NULL,
    to_canonical   TEXT NOT NULL,
    relation_type  TEXT NOT NULL,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_entity_relation_from ON entity_relation(from_entity_id);
CREATE INDEX idx_entity_relation_to ON entity_relation(to_entity_id);
CREATE INDEX idx_entity_relation_type ON entity_relation(relation_type);
