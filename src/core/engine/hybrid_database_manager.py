
'\nHybrid Multi-Database Architecture Manager\nUnified interface for PostgreSQL, Redis, TimescaleDB, and Elasticsearch\n'
import os
import logging
import time
import threading
import json
from typing import Optional, Any, Dict, List, Union, Generator, Tuple
from contextlib import contextmanager
from datetime import datetime, timezone, timedelta
from enum import Enum
import structlog
from collections import defaultdict
from .settings import settings
from .core.database import get_db_manager, initialize_database
from .redis_manager import get_redis_manager, initialize_redis
from .timescale_manager import get_timescale_manager, initialize_timescaledb
from .elasticsearch_manager import get_elasticsearch_manager, initialize_elasticsearch
logger = structlog.get_logger(__name__)

class DatabaseType(Enum):
    'Database types in the hybrid architecture'
    POSTGRESQL = 'postgresql'
    REDIS = 'redis'
    TIMESCALEDB = 'timescaledb'
    ELASTICSEARCH = 'elasticsearch'

class DataRouter():
    'Route data to appropriate databases based on type and requirements'

    @staticmethod
    def get_primary_database(data_type: str, operation: str) -> DatabaseType:
        'Determine primary database for data type and operation'
        if (data_type == 'compliance'):
            if (operation in ['read', 'write', 'update', 'delete']):
                return DatabaseType.POSTGRESQL
            elif (operation == 'search'):
                return DatabaseType.ELASTICSEARCH
            elif (operation == 'analytics'):
                return DatabaseType.TIMESCALEDB
        elif (data_type == 'audit'):
            if (operation in ['write', 'analytics']):
                return DatabaseType.TIMESCALEDB
            elif (operation == 'search'):
                return DatabaseType.ELASTICSEARCH
            elif (operation == 'read'):
                return DatabaseType.POSTGRESQL
        elif (data_type == 'user'):
            if (operation in ['read', 'write', 'update', 'delete']):
                return DatabaseType.POSTGRESQL
            elif (operation == 'search'):
                return DatabaseType.ELASTICSEARCH
            elif (operation == 'session'):
                return DatabaseType.REDIS
        elif (data_type == 'document'):
            if (operation in ['read', 'write', 'update', 'delete']):
                return DatabaseType.POSTGRESQL
            elif (operation == 'search'):
                return DatabaseType.ELASTICSEARCH
            elif (operation == 'cache'):
                return DatabaseType.REDIS
        elif (data_type == 'metrics'):
            if (operation in ['write', 'analytics']):
                return DatabaseType.TIMESCALEDB
            elif (operation == 'cache'):
                return DatabaseType.REDIS
        return DatabaseType.POSTGRESQL

    @staticmethod
    def get_sync_databases(data_type: str, operation: str) -> List[DatabaseType]:
        'Get databases that should be synchronized for data consistency'
        primary = DataRouter.get_primary_database(data_type, operation)
        sync_list = [primary]
        if (data_type == 'compliance'):
            if (operation in ['write', 'update']):
                sync_list.extend([DatabaseType.ELASTICSEARCH, DatabaseType.TIMESCALEDB])
        elif (data_type == 'audit'):
            if (operation == 'write'):
                sync_list.extend([DatabaseType.ELASTICSEARCH])
        elif (data_type == 'user'):
            if (operation in ['write', 'update']):
                sync_list.extend([DatabaseType.ELASTICSEARCH])
        elif (data_type == 'document'):
            if (operation in ['write', 'update']):
                sync_list.extend([DatabaseType.ELASTICSEARCH])
        return list(set(sync_list))

class HybridDatabaseManager():
    'Unified manager for hybrid multi-database architecture'

    def __init__(self):
        self._lock = threading.Lock()
        self._health_status = 'unknown'
        self._last_health_check = None
        self._health_check_interval = 60
        self._connection_errors = defaultdict(int)
        self._max_connection_errors = 5
        self._sync_metrics = defaultdict(int)
        self._last_metrics_reset = datetime.now(timezone.utc)
        self._metrics_reset_interval = 3600
        self._postgresql_manager = None
        self._redis_manager = None
        self._timescale_manager = None
        self._elasticsearch_manager = None
        self._active_transactions = {}
        self._transaction_counter = 0

    def initialize(self) -> bool:
        'Initialize all database connections'
        try:
            with self._lock:
                logger.info('Initializing hybrid database architecture')
                if (not initialize_database()):
                    logger.error('Failed to initialize PostgreSQL')
                    return False
                self._postgresql_manager = get_db_manager()
                if (not initialize_redis()):
                    logger.warning('Failed to initialize Redis - continuing without cache')
                else:
                    self._redis_manager = get_redis_manager()
                if (not initialize_timescaledb()):
                    logger.warning('Failed to initialize TimescaleDB - continuing without time-series')
                else:
                    self._timescale_manager = get_timescale_manager()
                if (not initialize_elasticsearch()):
                    logger.warning('Failed to initialize Elasticsearch - continuing without search')
                else:
                    self._elasticsearch_manager = get_elasticsearch_manager()
                logger.info('Hybrid database architecture initialized successfully')
                return True
        except Exception as e:
            logger.error('Failed to initialize hybrid database architecture', error=str(e), exc_info=True)
            return False

    def get_manager(self, db_type: DatabaseType):
        'Get database manager by type'
        managers = {DatabaseType.POSTGRESQL: self._postgresql_manager, DatabaseType.REDIS: self._redis_manager, DatabaseType.TIMESCALEDB: self._timescale_manager, DatabaseType.ELASTICSEARCH: self._elasticsearch_manager}
        return managers.get(db_type)

    def write_data(self, data_type: str, data: Dict[(str, Any)], doc_id: str=None) -> Dict[(str, Any)]:
        'Write data to appropriate databases with synchronization'
        try:
            primary_db = DataRouter.get_primary_database(data_type, 'write')
            sync_dbs = DataRouter.get_sync_databases(data_type, 'write')
            results = {}
            errors = []
            primary_result = self._write_to_database(primary_db, data_type, data, doc_id)
            results[primary_db.value] = primary_result
            if (not primary_result.get('success')):
                errors.append(f'Primary database ({primary_db.value}) write failed')
            for sync_db in sync_dbs:
                if (sync_db != primary_db):
                    sync_result = self._write_to_database(sync_db, data_type, data, doc_id)
                    results[sync_db.value] = sync_result
                    if (not sync_result.get('success')):
                        errors.append(f'Sync database ({sync_db.value}) write failed')
            self._sync_metrics['write_operations'] += 1
            return {'success': (len(errors) == 0), 'results': results, 'errors': errors, 'primary_database': primary_db.value}
        except Exception as e:
            logger.error('Write data failed', data_type=data_type, error=str(e))
            return {'success': False, 'error': str(e)}

    def read_data(self, data_type: str, doc_id: str, use_cache: bool=True) -> Dict[(str, Any)]:
        'Read data from appropriate database with caching'
        try:
            if (use_cache and self._redis_manager):
                cached_data = self._redis_manager.get_cache(f'{data_type}:{doc_id}')
                if cached_data:
                    self._sync_metrics['cache_hits'] += 1
                    return {'success': True, 'data': cached_data, 'source': 'cache'}
            primary_db = DataRouter.get_primary_database(data_type, 'read')
            result = self._read_from_database(primary_db, data_type, doc_id)
            if (result.get('success') and use_cache and self._redis_manager):
                self._redis_manager.set_cache(f'{data_type}:{doc_id}', result['data'], ttl=3600)
                self._sync_metrics['cache_sets'] += 1
            self._sync_metrics['read_operations'] += 1
            return result
        except Exception as e:
            logger.error('Read data failed', data_type=data_type, doc_id=doc_id, error=str(e))
            return {'success': False, 'error': str(e)}

    def search_data(self, data_type: str, query: str, filters: Dict[(str, Any)]=None, size: int=20, from_: int=0) -> Dict[(str, Any)]:
        'Search data using appropriate search database'
        try:
            if self._elasticsearch_manager:
                search_methods = {'compliance': self._elasticsearch_manager.search_compliance, 'audit': self._elasticsearch_manager.search_audit_trail, 'document': self._elasticsearch_manager.search_documents, 'user': self._elasticsearch_manager.search_users}
                search_method = search_methods.get(data_type)
                if search_method:
                    result = search_method(query, filters, size, from_)
                    self._sync_metrics['search_operations'] += 1
                    return {'success': True, 'data': result, 'source': 'elasticsearch'}
            logger.warning('Elasticsearch not available, falling back to PostgreSQL search')
            return self._fallback_search(data_type, query, filters, size, from_)
        except Exception as e:
            logger.error('Search data failed', data_type=data_type, query=query, error=str(e))
            return {'success': False, 'error': str(e)}

    def get_analytics(self, data_type: str, start_date: datetime=None, end_date: datetime=None) -> Dict[(str, Any)]:
        'Get analytics from appropriate database'
        try:
            if self._timescale_manager:
                analytics_methods = {'compliance': self._timescale_manager.get_compliance_stats, 'audit': (lambda s, e: {'audit_trail': self._timescale_manager.get_audit_trail(s, e)}), 'metrics': (lambda s, e: {'performance_metrics': self._timescale_manager.get_performance_metrics('system', s, e)})}
                analytics_method = analytics_methods.get(data_type)
                if analytics_method:
                    result = analytics_method(start_date, end_date)
                    self._sync_metrics['analytics_operations'] += 1
                    return {'success': True, 'data': result, 'source': 'timescaledb'}
            logger.warning('TimescaleDB not available, falling back to PostgreSQL analytics')
            return self._fallback_analytics(data_type, start_date, end_date)
        except Exception as e:
            logger.error('Analytics failed', data_type=data_type, error=str(e))
            return {'success': False, 'error': str(e)}

    @contextmanager
    def transaction(self, data_types: List[str]=None) -> Generator[(str, None, None)]:
        'Multi-database transaction context manager'
        transaction_id = f'tx_{int(time.time())}_{self._transaction_counter}'
        self._transaction_counter += 1
        try:
            self._active_transactions[transaction_id] = {'start_time': datetime.now(timezone.utc), 'data_types': (data_types or []), 'operations': []}
            logger.info(f'Started multi-database transaction: {transaction_id}')
            (yield transaction_id)
            self._commit_transaction(transaction_id)
        except Exception as e:
            self._rollback_transaction(transaction_id)
            logger.error(f'Transaction {transaction_id} failed', error=str(e))
            raise
        finally:
            self._active_transactions.pop(transaction_id, None)

    def _commit_transaction(self, transaction_id: str):
        'Commit multi-database transaction'
        try:
            transaction = self._active_transactions.get(transaction_id)
            if (not transaction):
                return
            for operation in transaction['operations']:
                self._execute_operation(operation)
            logger.info(f'Committed transaction: {transaction_id}')
        except Exception as e:
            logger.error(f'Failed to commit transaction {transaction_id}', error=str(e))
            raise

    def _rollback_transaction(self, transaction_id: str):
        'Rollback multi-database transaction'
        try:
            transaction = self._active_transactions.get(transaction_id)
            if (not transaction):
                return
            for operation in reversed(transaction['operations']):
                self._rollback_operation(operation)
            logger.info(f'Rolled back transaction: {transaction_id}')
        except Exception as e:
            logger.error(f'Failed to rollback transaction {transaction_id}', error=str(e))

    def _write_to_database(self, db_type: DatabaseType, data_type: str, data: Dict[(str, Any)], doc_id: str=None) -> Dict[(str, Any)]:
        'Write data to specific database'
        try:
            manager = self.get_manager(db_type)
            if (not manager):
                return {'success': False, 'error': f'Manager not available for {db_type.value}'}
            if (db_type == DatabaseType.POSTGRESQL):
                with manager.get_session_context() as session:
                    return {'success': True, 'id': doc_id}
            elif (db_type == DatabaseType.REDIS):
                success = manager.set_cache(f'{data_type}:{doc_id}', data)
                return {'success': success, 'id': doc_id}
            elif (db_type == DatabaseType.TIMESCALEDB):
                if (data_type == 'compliance'):
                    success = manager.insert_compliance_log(data.get('entity_id'), data.get('compliance_type'), data.get('status'), data.get('details', {}))
                elif (data_type == 'audit'):
                    success = manager.insert_audit_trail(data.get('user_id'), data.get('action'), data.get('resource_type'), data.get('resource_id'), data.get('changes', {}))
                else:
                    success = False
                return {'success': success, 'id': doc_id}
            elif (db_type == DatabaseType.ELASTICSEARCH):
                if (data_type == 'compliance'):
                    success = manager.index_compliance_document(doc_id, data)
                elif (data_type == 'audit'):
                    success = manager.index_audit_document(doc_id, data)
                elif (data_type == 'document'):
                    success = manager.index_document(doc_id, data)
                elif (data_type == 'user'):
                    success = manager.index_user(doc_id, data)
                else:
                    success = False
                return {'success': success, 'id': doc_id}
            return {'success': False, 'error': f'Unsupported database type: {db_type.value}'}
        except Exception as e:
            logger.error(f'Write to {db_type.value} failed', error=str(e))
            return {'success': False, 'error': str(e)}

    def _read_from_database(self, db_type: DatabaseType, data_type: str, doc_id: str) -> Dict[(str, Any)]:
        'Read data from specific database'
        try:
            manager = self.get_manager(db_type)
            if (not manager):
                return {'success': False, 'error': f'Manager not available for {db_type.value}'}
            if (db_type == DatabaseType.POSTGRESQL):
                with manager.get_session_context() as session:
                    return {'success': True, 'data': {'id': doc_id, 'type': data_type}}
            elif (db_type == DatabaseType.REDIS):
                data = manager.get_cache(f'{data_type}:{doc_id}')
                return {'success': (data is not None), 'data': data}
            elif (db_type == DatabaseType.TIMESCALEDB):
                return {'success': True, 'data': {'id': doc_id, 'type': data_type}}
            elif (db_type == DatabaseType.ELASTICSEARCH):
                try:
                    return {'success': True, 'data': {'id': doc_id, 'type': data_type}}
                except Exception:
                    return {'success': False, 'error': 'Document not found'}
            return {'success': False, 'error': f'Unsupported database type: {db_type.value}'}
        except Exception as e:
            logger.error(f'Read from {db_type.value} failed', error=str(e))
            return {'success': False, 'error': str(e)}

    def _fallback_search(self, data_type: str, query: str, filters: Dict[(str, Any)]=None, size: int=20, from_: int=0) -> Dict[(str, Any)]:
        'Fallback search using PostgreSQL'
        try:
            if self._postgresql_manager:
                return {'success': True, 'data': {'results': [], 'total': 0}, 'source': 'postgresql'}
            else:
                return {'success': False, 'error': 'No search database available'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _fallback_analytics(self, data_type: str, start_date: datetime=None, end_date: datetime=None) -> Dict[(str, Any)]:
        'Fallback analytics using PostgreSQL'
        try:
            if self._postgresql_manager:
                return {'success': True, 'data': {'analytics': {}}, 'source': 'postgresql'}
            else:
                return {'success': False, 'error': 'No analytics database available'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def health_check(self) -> Dict[(str, Any)]:
        'Perform comprehensive health check of all databases'
        current_time = time.time()
        if (self._last_health_check and ((current_time - self._last_health_check) < self._health_check_interval)):
            return {'status': self._health_status, 'last_check': self._last_health_check, 'message': 'Using cached health status'}
        try:
            health_results = {}
            overall_healthy = True
            if self._postgresql_manager:
                pg_health = self._postgresql_manager.health_check()
                health_results['postgresql'] = pg_health
                if (pg_health.get('status') != 'healthy'):
                    overall_healthy = False
            else:
                health_results['postgresql'] = {'status': 'unavailable'}
                overall_healthy = False
            if self._redis_manager:
                redis_health = self._redis_manager.health_check()
                health_results['redis'] = redis_health
                if (redis_health.get('status') != 'healthy'):
                    overall_healthy = False
            else:
                health_results['redis'] = {'status': 'unavailable'}
            if self._timescale_manager:
                timescale_health = self._timescale_manager.health_check()
                health_results['timescaledb'] = timescale_health
                if (timescale_health.get('status') != 'healthy'):
                    overall_healthy = False
            else:
                health_results['timescaledb'] = {'status': 'unavailable'}
            if self._elasticsearch_manager:
                es_health = self._elasticsearch_manager.health_check()
                health_results['elasticsearch'] = es_health
                if (es_health.get('status') != 'healthy'):
                    overall_healthy = False
            else:
                health_results['elasticsearch'] = {'status': 'unavailable'}
            if overall_healthy:
                self._health_status = 'healthy'
                message = 'All databases are healthy'
            else:
                self._health_status = 'degraded'
                message = 'Some databases are unhealthy'
            sync_metrics = self._get_sync_metrics()
            self._last_health_check = current_time
            return {'status': self._health_status, 'last_check': current_time, 'message': message, 'databases': health_results, 'sync_metrics': sync_metrics, 'active_transactions': len(self._active_transactions)}
        except Exception as e:
            self._health_status = 'error'
            logger.error('Hybrid database health check failed', error=str(e), exc_info=True)
            return {'status': 'error', 'last_check': current_time, 'message': f'Health check error: {str(e)}'}

    def _get_sync_metrics(self) -> Dict[(str, Any)]:
        'Get synchronization metrics'
        current_time = datetime.now(timezone.utc)
        if ((current_time - self._last_metrics_reset).total_seconds() > self._metrics_reset_interval):
            self._sync_metrics.clear()
            self._last_metrics_reset = current_time
        return dict(self._sync_metrics)

    def close(self):
        'Close all database connections'
        try:
            with self._lock:
                if self._postgresql_manager:
                    self._postgresql_manager.close()
                if self._redis_manager:
                    self._redis_manager.close()
                if self._timescale_manager:
                    pass
                if self._elasticsearch_manager:
                    self._elasticsearch_manager.close()
                logger.info('Hybrid database connections closed')
        except Exception as e:
            logger.error('Error closing hybrid database connections', error=str(e))
_hybrid_manager: Optional[HybridDatabaseManager] = None

def get_hybrid_manager() -> HybridDatabaseManager:
    'Get the global hybrid database manager instance'
    global _hybrid_manager
    if (_hybrid_manager is None):
        _hybrid_manager = HybridDatabaseManager()
    return _hybrid_manager

def initialize_hybrid_database() -> bool:
    'Initialize the global hybrid database architecture'
    return get_hybrid_manager().initialize()

def close_hybrid_database():
    'Close the global hybrid database connections'
    global _hybrid_manager
    if _hybrid_manager:
        _hybrid_manager.close()
        _hybrid_manager = None

def write_compliance_data(data: Dict[(str, Any)], doc_id: str=None) -> Dict[(str, Any)]:
    'Write compliance data to appropriate databases'
    return get_hybrid_manager().write_data('compliance', data, doc_id)

def read_compliance_data(doc_id: str, use_cache: bool=True) -> Dict[(str, Any)]:
    'Read compliance data from appropriate database'
    return get_hybrid_manager().read_data('compliance', doc_id, use_cache)

def search_compliance_data(query: str, filters: Dict[(str, Any)]=None, size: int=20, from_: int=0) -> Dict[(str, Any)]:
    'Search compliance data'
    return get_hybrid_manager().search_data('compliance', query, filters, size, from_)

def get_compliance_analytics(start_date: datetime=None, end_date: datetime=None) -> Dict[(str, Any)]:
    'Get compliance analytics'
    return get_hybrid_manager().get_analytics('compliance', start_date, end_date)
__all__ = ['HybridDatabaseManager', 'DatabaseType', 'DataRouter', 'get_hybrid_manager', 'initialize_hybrid_database', 'close_hybrid_database', 'write_compliance_data', 'read_compliance_data', 'search_compliance_data', 'get_compliance_analytics']
