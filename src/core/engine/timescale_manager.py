
'\nTimescaleDB manager for time-series data optimization\nHypertables, retention policies, and time-series analytics\n'
import os
import logging
import time
import threading
from typing import Optional, Any, Dict, List, Union, Generator
from contextlib import contextmanager
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine, text, event, MetaData, Table, Column, DateTime, String, Integer, Float, JSON
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError, OperationalError
import structlog
from collections import defaultdict
from .settings import settings
from .core.database import get_db_manager
logger = structlog.get_logger(__name__)

class TimescaleDBManager():
    'TimescaleDB manager for time-series data optimization'

    def __init__(self):
        self.engine: Optional[Any] = None
        self.session_factory: Optional[sessionmaker] = None
        self._lock = threading.Lock()
        self._health_status = 'unknown'
        self._last_health_check = None
        self._health_check_interval = 60
        self._connection_errors = 0
        self._max_connection_errors = 5
        self._timeseries_metrics = defaultdict(int)
        self._last_metrics_reset = datetime.now(timezone.utc)
        self._metrics_reset_interval = 3600
        self._chunk_time_interval = '1 day'
        self._compression_enabled = True
        self._compression_after = '7 days'
        self._retention_policy = '90 days'

    def initialize(self) -> bool:
        'Initialize TimescaleDB with extensions and hypertables'
        try:
            with self._lock:
                if (self.engine is not None):
                    logger.info('TimescaleDB already initialized')
                    return True
                db_manager = get_db_manager()
                if (not db_manager.engine):
                    raise Exception('Primary database not initialized')
                self.engine = db_manager.engine
                self.session_factory = db_manager.session_factory
                if (not self._enable_timescaledb_extension()):
                    raise Exception('Failed to enable TimescaleDB extension')
                if (not self._create_timeseries_tables()):
                    raise Exception('Failed to create time-series tables')
                if (not self._setup_retention_policies()):
                    raise Exception('Failed to setup retention policies')
                if (not self._setup_compression_policies()):
                    raise Exception('Failed to setup compression policies')
                logger.info('TimescaleDB initialized successfully', chunk_interval=self._chunk_time_interval, compression_enabled=self._compression_enabled, retention_policy=self._retention_policy)
                return True
        except Exception as e:
            logger.error('Failed to initialize TimescaleDB', error=str(e), exc_info=True)
            return False

    def _enable_timescaledb_extension(self) -> bool:
        'Enable TimescaleDB extension'
        try:
            with self.session_factory() as session:
                result = session.execute(text("SELECT * FROM pg_extension WHERE extname = 'timescaledb'")).fetchone()
                if (not result):
                    session.execute(text('CREATE EXTENSION IF NOT EXISTS timescaledb'))
                    session.commit()
                    logger.info('TimescaleDB extension enabled')
                else:
                    logger.info('TimescaleDB extension already exists')
                return True
        except Exception as e:
            logger.error('Failed to enable TimescaleDB extension', error=str(e))
            return False

    def _create_timeseries_tables(self) -> bool:
        'Create time-series tables with hypertables'
        try:
            with self.session_factory() as session:
                session.execute(text('\n                    CREATE TABLE IF NOT EXISTS compliance_logs (\n                        time TIMESTAMPTZ NOT NULL,\n                        entity_id VARCHAR(255) NOT NULL,\n                        compliance_type VARCHAR(100) NOT NULL,\n                        status VARCHAR(50) NOT NULL,\n                        details JSONB,\n                        created_at TIMESTAMPTZ DEFAULT NOW()\n                    )\n                '))
                session.execute(text("\n                    SELECT create_hypertable('compliance_logs', 'time', \n                        chunk_time_interval => INTERVAL '1 day',\n                        if_not_exists => TRUE)\n                "))
                session.execute(text('\n                    CREATE TABLE IF NOT EXISTS audit_trail (\n                        time TIMESTAMPTZ NOT NULL,\n                        user_id VARCHAR(255) NOT NULL,\n                        action VARCHAR(100) NOT NULL,\n                        resource_type VARCHAR(100) NOT NULL,\n                        resource_id VARCHAR(255) NOT NULL,\n                        changes JSONB,\n                        ip_address INET,\n                        user_agent TEXT,\n                        created_at TIMESTAMPTZ DEFAULT NOW()\n                    )\n                '))
                session.execute(text("\n                    SELECT create_hypertable('audit_trail', 'time',\n                        chunk_time_interval => INTERVAL '1 day',\n                        if_not_exists => TRUE)\n                "))
                session.execute(text('\n                    CREATE TABLE IF NOT EXISTS performance_metrics (\n                        time TIMESTAMPTZ NOT NULL,\n                        metric_name VARCHAR(100) NOT NULL,\n                        metric_value DOUBLE PRECISION NOT NULL,\n                        tags JSONB,\n                        created_at TIMESTAMPTZ DEFAULT NOW()\n                    )\n                '))
                session.execute(text("\n                    SELECT create_hypertable('performance_metrics', 'time',\n                        chunk_time_interval => INTERVAL '1 hour',\n                        if_not_exists => TRUE)\n                "))
                session.commit()
                logger.info('Time-series tables created successfully')
                return True
        except Exception as e:
            logger.error('Failed to create time-series tables', error=str(e))
            return False

    def _setup_retention_policies(self) -> bool:
        'Setup data retention policies'
        try:
            with self.session_factory() as session:
                session.execute(text("\n                    SELECT add_retention_policy('compliance_logs', INTERVAL '90 days', if_not_exists => TRUE)\n                "))
                session.execute(text("\n                    SELECT add_retention_policy('audit_trail', INTERVAL '1 year', if_not_exists => TRUE)\n                "))
                session.execute(text("\n                    SELECT add_retention_policy('performance_metrics', INTERVAL '30 days', if_not_exists => TRUE)\n                "))
                session.commit()
                logger.info('Retention policies configured successfully')
                return True
        except Exception as e:
            logger.error('Failed to setup retention policies', error=str(e))
            return False

    def _setup_compression_policies(self) -> bool:
        'Setup data compression policies'
        try:
            with self.session_factory() as session:
                session.execute(text("\n                    ALTER TABLE compliance_logs SET (\n                        timescaledb.compress,\n                        timescaledb.compress_segmentby = 'entity_id,compliance_type',\n                        timescaledb.compress_orderby = 'time DESC'\n                    )\n                "))
                session.execute(text("\n                    SELECT add_compression_policy('compliance_logs', INTERVAL '7 days', if_not_exists => TRUE)\n                "))
                session.execute(text("\n                    ALTER TABLE audit_trail SET (\n                        timescaledb.compress,\n                        timescaledb.compress_segmentby = 'user_id,action',\n                        timescaledb.compress_orderby = 'time DESC'\n                    )\n                "))
                session.execute(text("\n                    SELECT add_compression_policy('audit_trail', INTERVAL '7 days', if_not_exists => TRUE)\n                "))
                session.execute(text("\n                    ALTER TABLE performance_metrics SET (\n                        timescaledb.compress,\n                        timescaledb.compress_segmentby = 'metric_name',\n                        timescaledb.compress_orderby = 'time DESC'\n                    )\n                "))
                session.execute(text("\n                    SELECT add_compression_policy('performance_metrics', INTERVAL '1 day', if_not_exists => TRUE)\n                "))
                session.commit()
                logger.info('Compression policies configured successfully')
                return True
        except Exception as e:
            logger.error('Failed to setup compression policies', error=str(e))
            return False

    def insert_compliance_log(self, entity_id: str, compliance_type: str, status: str, details: Dict[(str, Any)]) -> bool:
        'Insert compliance log entry'
        try:
            with self.session_factory() as session:
                session.execute(text('\n                    INSERT INTO compliance_logs (time, entity_id, compliance_type, status, details)\n                    VALUES (:time, :entity_id, :compliance_type, :status, :details)\n                '), {'time': datetime.now(timezone.utc), 'entity_id': entity_id, 'compliance_type': compliance_type, 'status': status, 'details': details})
                session.commit()
                self._timeseries_metrics['compliance_logs_inserted'] += 1
                return True
        except Exception as e:
            logger.error('Failed to insert compliance log', error=str(e))
            return False

    def insert_audit_trail(self, user_id: str, action: str, resource_type: str, resource_id: str, changes: Dict[(str, Any)], ip_address: str=None, user_agent: str=None) -> bool:
        'Insert audit trail entry'
        try:
            with self.session_factory() as session:
                session.execute(text('\n                    INSERT INTO audit_trail (time, user_id, action, resource_type, resource_id, changes, ip_address, user_agent)\n                    VALUES (:time, :user_id, :action, :resource_type, :resource_id, :changes, :ip_address, :user_agent)\n                '), {'time': datetime.now(timezone.utc), 'user_id': user_id, 'action': action, 'resource_type': resource_type, 'resource_id': resource_id, 'changes': changes, 'ip_address': ip_address, 'user_agent': user_agent})
                session.commit()
                self._timeseries_metrics['audit_trail_inserted'] += 1
                return True
        except Exception as e:
            logger.error('Failed to insert audit trail', error=str(e))
            return False

    def insert_performance_metric(self, metric_name: str, metric_value: float, tags: Dict[(str, Any)]=None) -> bool:
        'Insert performance metric'
        try:
            with self.session_factory() as session:
                session.execute(text('\n                    INSERT INTO performance_metrics (time, metric_name, metric_value, tags)\n                    VALUES (:time, :metric_name, :metric_value, :tags)\n                '), {'time': datetime.now(timezone.utc), 'metric_name': metric_name, 'metric_value': metric_value, 'tags': (tags or {})})
                session.commit()
                self._timeseries_metrics['performance_metrics_inserted'] += 1
                return True
        except Exception as e:
            logger.error('Failed to insert performance metric', error=str(e))
            return False

    def get_compliance_stats(self, start_time: datetime, end_time: datetime, entity_id: str=None, compliance_type: str=None) -> Dict[(str, Any)]:
        'Get compliance statistics for time range'
        try:
            with self.session_factory() as session:
                where_clause = 'WHERE time BETWEEN :start_time AND :end_time'
                params = {'start_time': start_time, 'end_time': end_time}
                if entity_id:
                    where_clause += ' AND entity_id = :entity_id'
                    params['entity_id'] = entity_id
                if compliance_type:
                    where_clause += ' AND compliance_type = :compliance_type'
                    params['compliance_type'] = compliance_type
                result = session.execute(text(f'''
                    SELECT status, COUNT(*) as count
                    FROM compliance_logs
                    {where_clause}
                    GROUP BY status
                    ORDER BY count DESC
                '''), params)
                status_counts = {row[0]: row[1] for row in result}
                trend_result = session.execute(text(f'''
                    SELECT time_bucket('1 day', time) as bucket, 
                           COUNT(*) as count,
                           COUNT(*) FILTER (WHERE status = 'passed') as passed,
                           COUNT(*) FILTER (WHERE status = 'failed') as failed
                    FROM compliance_logs
                    {where_clause}
                    GROUP BY bucket
                    ORDER BY bucket
                '''), params)
                trends = [{'bucket': row[0].isoformat(), 'total': row[1], 'passed': row[2], 'failed': row[3]} for row in trend_result]
                return {'status_counts': status_counts, 'trends': trends, 'total_records': sum(status_counts.values())}
        except Exception as e:
            logger.error('Failed to get compliance stats', error=str(e))
            return {'error': str(e)}

    def get_audit_trail(self, start_time: datetime, end_time: datetime, user_id: str=None, action: str=None, limit: int=1000) -> List[Dict[(str, Any)]]:
        'Get audit trail entries for time range'
        try:
            with self.session_factory() as session:
                where_clause = 'WHERE time BETWEEN :start_time AND :end_time'
                params = {'start_time': start_time, 'end_time': end_time}
                if user_id:
                    where_clause += ' AND user_id = :user_id'
                    params['user_id'] = user_id
                if action:
                    where_clause += ' AND action = :action'
                    params['action'] = action
                result = session.execute(text(f'''
                    SELECT time, user_id, action, resource_type, resource_id, changes, ip_address, user_agent
                    FROM audit_trail
                    {where_clause}
                    ORDER BY time DESC
                    LIMIT :limit
                '''), {**params, 'limit': limit})
                return [{'time': row[0].isoformat(), 'user_id': row[1], 'action': row[2], 'resource_type': row[3], 'resource_id': row[4], 'changes': row[5], 'ip_address': (str(row[6]) if row[6] else None), 'user_agent': row[7]} for row in result]
        except Exception as e:
            logger.error('Failed to get audit trail', error=str(e))
            return []

    def get_performance_metrics(self, metric_name: str, start_time: datetime, end_time: datetime, interval: str='1 hour') -> List[Dict[(str, Any)]]:
        'Get performance metrics with time bucketing'
        try:
            with self.session_factory() as session:
                result = session.execute(text('\n                    SELECT time_bucket(:interval, time) as bucket,\n                           AVG(metric_value) as avg_value,\n                           MIN(metric_value) as min_value,\n                           MAX(metric_value) as max_value,\n                           COUNT(*) as count\n                    FROM performance_metrics\n                    WHERE metric_name = :metric_name \n                      AND time BETWEEN :start_time AND :end_time\n                    GROUP BY bucket\n                    ORDER BY bucket\n                '), {'interval': interval, 'metric_name': metric_name, 'start_time': start_time, 'end_time': end_time})
                return [{'bucket': row[0].isoformat(), 'avg_value': float(row[1]), 'min_value': float(row[2]), 'max_value': float(row[3]), 'count': row[4]} for row in result]
        except Exception as e:
            logger.error('Failed to get performance metrics', error=str(e))
            return []

    def run_maintenance(self) -> Dict[(str, Any)]:
        'Run TimescaleDB maintenance operations'
        try:
            with self.session_factory() as session:
                session.execute(text('SELECT compress_chunk(chunk_name) FROM timescaledb_information.chunks WHERE is_compressed = FALSE'))
                session.execute(text("SELECT drop_chunks('compliance_logs', older_than => INTERVAL '90 days')"))
                session.execute(text("SELECT drop_chunks('audit_trail', older_than => INTERVAL '1 year')"))
                session.execute(text("SELECT drop_chunks('performance_metrics', older_than => INTERVAL '30 days')"))
                session.execute(text('ANALYZE compliance_logs'))
                session.execute(text('ANALYZE audit_trail'))
                session.execute(text('ANALYZE performance_metrics'))
                session.commit()
                logger.info('TimescaleDB maintenance completed successfully')
                return {'status': 'success', 'message': 'Maintenance completed'}
        except Exception as e:
            logger.error('TimescaleDB maintenance failed', error=str(e))
            return {'status': 'error', 'message': str(e)}

    def get_hypertable_info(self) -> Dict[(str, Any)]:
        'Get information about hypertables'
        try:
            with self.session_factory() as session:
                result = session.execute(text('\n                    SELECT hypertable_name, num_chunks, compressed_chunks, uncompressed_chunks\n                    FROM timescaledb_information.hypertables\n                    ORDER BY hypertable_name\n                '))
                hypertables = [{'name': row[0], 'total_chunks': row[1], 'compressed_chunks': row[2], 'uncompressed_chunks': row[3]} for row in result]
                return {'hypertables': hypertables}
        except Exception as e:
            logger.error('Failed to get hypertable info', error=str(e))
            return {'error': str(e)}

    def health_check(self) -> Dict[(str, Any)]:
        'Perform TimescaleDB health check'
        current_time = time.time()
        if (self._last_health_check and ((current_time - self._last_health_check) < self._health_check_interval)):
            return {'status': self._health_status, 'last_check': self._last_health_check, 'message': 'Using cached health status'}
        try:
            with self.session_factory() as session:
                session.execute(text('SELECT 1'))
                result = session.execute(text("SELECT extversion FROM pg_extension WHERE extname = 'timescaledb'")).fetchone()
                if result:
                    self._health_status = 'healthy'
                    self._connection_errors = 0
                    message = 'TimescaleDB is healthy'
                else:
                    self._health_status = 'unhealthy'
                    self._connection_errors += 1
                    message = f'TimescaleDB extension not found ({self._connection_errors} consecutive failures)'
                hypertable_info = self.get_hypertable_info()
                timeseries_metrics = self._get_timeseries_metrics()
                self._last_health_check = current_time
                return {'status': self._health_status, 'last_check': current_time, 'message': message, 'connection_errors': self._connection_errors, 'extension_version': (result[0] if result else None), 'hypertable_info': hypertable_info, 'timeseries_metrics': timeseries_metrics}
        except Exception as e:
            self._health_status = 'error'
            self._connection_errors += 1
            logger.error('TimescaleDB health check failed', error=str(e), exc_info=True)
            return {'status': 'error', 'last_check': current_time, 'message': f'Health check error: {str(e)}', 'connection_errors': self._connection_errors}

    def _get_timeseries_metrics(self) -> Dict[(str, Any)]:
        'Get timeseries metrics'
        current_time = datetime.now(timezone.utc)
        if ((current_time - self._last_metrics_reset).total_seconds() > self._metrics_reset_interval):
            self._timeseries_metrics.clear()
            self._last_metrics_reset = current_time
        return dict(self._timeseries_metrics)
_timescale_manager: Optional[TimescaleDBManager] = None

def get_timescale_manager() -> TimescaleDBManager:
    'Get the global TimescaleDB manager instance'
    global _timescale_manager
    if (_timescale_manager is None):
        _timescale_manager = TimescaleDBManager()
    return _timescale_manager

def initialize_timescaledb() -> bool:
    'Initialize the global TimescaleDB connection'
    return get_timescale_manager().initialize()
__all__ = ['TimescaleDBManager', 'get_timescale_manager', 'initialize_timescaledb']
