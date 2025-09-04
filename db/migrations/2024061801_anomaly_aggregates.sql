CREATE MATERIALIZED VIEW anomaly_5min
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('5 minutes', event_time) as bucket,
    entity_id,
    avg(detection_score) as score_avg,
    stddev(detection_score) as score_std
FROM security_events
GROUP BY bucket, entity_id;

SELECT add_continuous_aggregate_policy('anomaly_5min',
    start_offset => INTERVAL '1 hour',
    end_offset => INTERVAL '5 minutes',
    schedule_interval => INTERVAL '5 minutes');