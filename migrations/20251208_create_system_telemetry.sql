CREATE TABLE IF NOT EXISTS system_telemetry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL,
    metric TEXT NOT NULL,
    value INTEGER NOT NULL,
    meta JSONB DEFAULT '{}'
);

CREATE INDEX idx_telemetry_metric_timestamp
    ON system_telemetry(metric, timestamp);
