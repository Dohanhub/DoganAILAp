-- =============================================================================
-- TimescaleDB Initialization Script for DoganAI Compliance Kit
-- =============================================================================

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Enable additional useful extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Create custom functions for compliance data management
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create audit log function
CREATE OR REPLACE FUNCTION audit_log_trigger()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_logs (
            table_name, 
            operation, 
            record_id, 
            old_data, 
            new_data, 
            user_id, 
            timestamp
        ) VALUES (
            TG_TABLE_NAME,
            'INSERT',
            NEW.id,
            NULL,
            to_jsonb(NEW),
            COALESCE(NEW.created_by, 'system'),
            CURRENT_TIMESTAMP
        );
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_logs (
            table_name, 
            operation, 
            record_id, 
            old_data, 
            new_data, 
            user_id, 
            timestamp
        ) VALUES (
            TG_TABLE_NAME,
            'UPDATE',
            NEW.id,
            to_jsonb(OLD),
            to_jsonb(NEW),
            COALESCE(NEW.modified_by, 'system'),
            CURRENT_TIMESTAMP
        );
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_logs (
            table_name, 
            operation, 
            record_id, 
            old_data, 
            new_data, 
            user_id, 
            timestamp
        ) VALUES (
            TG_TABLE_NAME,
            'DELETE',
            OLD.id,
            to_jsonb(OLD),
            NULL,
            COALESCE(OLD.deleted_by, 'system'),
            CURRENT_TIMESTAMP
        );
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

-- Create performance metrics hypertable
CREATE TABLE IF NOT EXISTS performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(255) NOT NULL,
    metric_value DOUBLE PRECISION NOT NULL,
    metric_unit VARCHAR(50),
    tags JSONB DEFAULT '{}',
    timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Convert to hypertable for time-series optimization
SELECT create_hypertable('performance_metrics', 'timestamp', 
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_performance_metrics_name_time 
    ON performance_metrics (metric_name, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_tags 
    ON performance_metrics USING GIN (tags);

-- Enable compression on the hypertable
ALTER TABLE performance_metrics SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'metric_name',
    timescaledb.compress_orderby = 'timestamp DESC'
);

-- Create audit logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(255) NOT NULL,
    operation VARCHAR(50) NOT NULL,
    record_id UUID,
    old_data JSONB,
    new_data JSONB,
    user_id VARCHAR(255),
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Convert audit logs to hypertable
SELECT create_hypertable('audit_logs', 'timestamp', 
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- Create indexes for audit logs
CREATE INDEX IF NOT EXISTS idx_audit_logs_table_operation 
    ON audit_logs (table_name, operation);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_time 
    ON audit_logs (user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_record_id 
    ON audit_logs (record_id);

-- Enable compression on audit logs
ALTER TABLE audit_logs SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'table_name,operation',
    timescaledb.compress_orderby = 'timestamp DESC'
);

-- Create system health metrics table
CREATE TABLE IF NOT EXISTS system_health_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_name VARCHAR(255) NOT NULL,
    metric_type VARCHAR(100) NOT NULL,
    metric_value DOUBLE PRECISION NOT NULL,
    status VARCHAR(50) NOT NULL,
    details JSONB DEFAULT '{}',
    timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Convert to hypertable
SELECT create_hypertable('system_health_metrics', 'timestamp', 
    chunk_time_interval => INTERVAL '1 hour',
    if_not_exists => TRUE
);

-- Create indexes for health metrics
CREATE INDEX IF NOT EXISTS idx_health_metrics_service_type 
    ON system_health_metrics (service_name, metric_type);
CREATE INDEX IF NOT EXISTS idx_health_metrics_status 
    ON system_health_metrics (status, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_health_metrics_details 
    ON system_health_metrics USING GIN (details);

-- Enable compression on health metrics
ALTER TABLE system_health_metrics SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'service_name,metric_type',
    timescaledb.compress_orderby = 'timestamp DESC'
);

-- Create continuous aggregates for performance analytics
CREATE MATERIALIZED VIEW IF NOT EXISTS performance_metrics_hourly
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 hour', timestamp) AS bucket,
    metric_name,
    AVG(metric_value) AS avg_value,
    MIN(metric_value) AS min_value,
    MAX(metric_value) AS max_value,
    COUNT(*) AS count
FROM performance_metrics
GROUP BY bucket, metric_name;

CREATE MATERIALIZED VIEW IF NOT EXISTS performance_metrics_daily
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 day', timestamp) AS bucket,
    metric_name,
    AVG(metric_value) AS avg_value,
    MIN(metric_value) AS min_value,
    MAX(metric_value) AS max_value,
    COUNT(*) AS count
FROM performance_metrics
GROUP BY bucket, metric_name;

-- Create continuous aggregates for system health
CREATE MATERIALIZED VIEW IF NOT EXISTS system_health_hourly
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 hour', timestamp) AS bucket,
    service_name,
    metric_type,
    AVG(metric_value) AS avg_value,
    COUNT(*) AS count,
    COUNT(CASE WHEN status = 'healthy' THEN 1 END) AS healthy_count,
    COUNT(CASE WHEN status = 'warning' THEN 1 END) AS warning_count,
    COUNT(CASE WHEN status = 'error' THEN 1 END) AS error_count
FROM system_health_metrics
GROUP BY bucket, service_name, metric_type;

-- Set up retention policies
SELECT add_retention_policy('performance_metrics', INTERVAL '90 days');
SELECT add_retention_policy('audit_logs', INTERVAL '365 days');
SELECT add_retention_policy('system_health_metrics', INTERVAL '30 days');

-- Create database statistics view
CREATE OR REPLACE VIEW database_stats AS
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation,
    most_common_vals,
    most_common_freqs
FROM pg_stats 
WHERE schemaname NOT IN ('information_schema', 'pg_catalog');

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO doganai;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO doganai;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO doganai;

-- Create a function to get database health status
CREATE OR REPLACE FUNCTION get_database_health()
RETURNS TABLE (
    component VARCHAR(255),
    status VARCHAR(50),
    details JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        'postgresql'::VARCHAR(255) as component,
        'healthy'::VARCHAR(50) as status,
        jsonb_build_object(
            'version', version(),
            'uptime', extract(epoch from now() - pg_postmaster_start_time()),
            'active_connections', (SELECT count(*) FROM pg_stat_activity WHERE state = 'active'),
            'total_connections', (SELECT count(*) FROM pg_stat_activity)
        ) as details
    UNION ALL
    SELECT 
        'timescaledb'::VARCHAR(255) as component,
        'healthy'::VARCHAR(50) as status,
        jsonb_build_object(
            'version', (SELECT extversion FROM pg_extension WHERE extname = 'timescaledb'),
            'hypertables', (SELECT count(*) FROM timescaledb_information.hypertables),
            'compressed_chunks', (SELECT count(*) FROM timescaledb_information.compression_settings)
        ) as details;
END;
$$ LANGUAGE plpgsql;

-- Create a function to clean up old data
CREATE OR REPLACE FUNCTION cleanup_old_data()
RETURNS void AS $$
BEGIN
    -- Clean up old audit logs (older than 1 year)
    DELETE FROM audit_logs WHERE timestamp < NOW() - INTERVAL '1 year';
    
    -- Clean up old performance metrics (older than 90 days)
    DELETE FROM performance_metrics WHERE timestamp < NOW() - INTERVAL '90 days';
    
    -- Clean up old health metrics (older than 30 days)
    DELETE FROM system_health_metrics WHERE timestamp < NOW() - INTERVAL '30 days';
    
    -- Vacuum to reclaim space
    VACUUM ANALYZE;
END;
$$ LANGUAGE plpgsql;

-- Create a scheduled job to run cleanup (if pg_cron is available)
-- SELECT cron.schedule('cleanup-old-data', '0 2 * * *', 'SELECT cleanup_old_data();');

-- Log successful initialization
INSERT INTO system_health_metrics (service_name, metric_type, metric_value, status, details)
VALUES (
    'database',
    'initialization',
    1.0,
    'healthy',
    jsonb_build_object(
        'message', 'TimescaleDB initialization completed successfully',
        'timestamp', CURRENT_TIMESTAMP,
        'extensions', ARRAY['timescaledb', 'uuid-ossp', 'pg_stat_statements', 'btree_gin']
    )
);
