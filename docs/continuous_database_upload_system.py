#!/usr/bin/env python3
"""
DoganAI Compliance Kit - Continuous Database Upload System
Ministry of Interior Delivery - Urgent Priority

A robust, modular system that synchronizes actual data spaces to maintain
workflow connectivity and activity with operational technology principles.
"""

import asyncio
import aiohttp
import asyncpg
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import uuid
from contextlib import asynccontextmanager
import signal
import sys
from concurrent.futures import ThreadPoolExecutor
import threading
from queue import Queue, Empty
import psutil
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# =============================================================================
# OPERATIONAL TECHNOLOGY (OT) PRINCIPLES IMPLEMENTATION
# =============================================================================

class SystemState(Enum):
    """OT-inspired system states for operational reliability"""
    INITIALIZING = "initializing"
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    EMERGENCY_STOP = "emergency_stop"
    FAULT = "fault"

class Priority(Enum):
    """OT-style priority levels for data processing"""
    CRITICAL = 1    # Ministry critical data
    HIGH = 2        # Compliance data
    NORMAL = 3      # Regular operations
    LOW = 4         # Background tasks

@dataclass
class DataPacket:
    """OT-inspired data packet with integrity checks"""
    id: str
    source: str
    destination: str
    data: Dict[str, Any]
    priority: Priority
    timestamp: datetime
    checksum: str
    retry_count: int = 0
    max_retries: int = 3
    
    def __post_init__(self):
        if not self.checksum:
            self.checksum = self._calculate_checksum()
    
    def _calculate_checksum(self) -> str:
        """Calculate data integrity checksum"""
        data_str = json.dumps(self.data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def verify_integrity(self) -> bool:
        """Verify data packet integrity"""
        return self.checksum == self._calculate_checksum()

# =============================================================================
# METRICS AND MONITORING (OT SCADA-INSPIRED)
# =============================================================================

class SystemMetrics:
    """OT-style system metrics for operational monitoring"""
    
    def __init__(self):
        # Prometheus metrics
        self.upload_counter = Counter('db_uploads_total', 'Total database uploads', ['source', 'status'])
        self.upload_duration = Histogram('db_upload_duration_seconds', 'Upload duration', ['source'])
        self.queue_size = Gauge('upload_queue_size', 'Current upload queue size')
        self.system_health = Gauge('system_health_score', 'Overall system health (0-100)')
        self.connection_pool_size = Gauge('db_connection_pool_size', 'Database connection pool size')
        self.error_rate = Gauge('error_rate_percent', 'Error rate percentage')
        
        # OT-style operational metrics
        self.total_uploads = 0
        self.successful_uploads = 0
        self.failed_uploads = 0
        self.start_time = time.time()
        
    def record_upload(self, source: str, success: bool, duration: float):
        """Record upload metrics"""
        status = 'success' if success else 'failure'
        self.upload_counter.labels(source=source, status=status).inc()
        self.upload_duration.labels(source=source).observe(duration)
        
        self.total_uploads += 1
        if success:
            self.successful_uploads += 1
        else:
            self.failed_uploads += 1
    
    def get_health_score(self) -> float:
        """Calculate OT-style health score"""
        if self.total_uploads == 0:
            return 100.0
        
        success_rate = (self.successful_uploads / self.total_uploads) * 100
        uptime_hours = (time.time() - self.start_time) / 3600
        
        # OT-style health calculation
        health_score = min(100.0, success_rate * 0.7 + min(uptime_hours * 2, 30))
        self.system_health.set(health_score)
        return health_score

# =============================================================================
# INTELLIGENT COMPONENT INTEGRATION
# =============================================================================

class ComponentRegistry:
    """Registry for intelligent component integration"""
    
    def __init__(self):
        self.components: Dict[str, Any] = {}
        self.dependencies: Dict[str, List[str]] = {}
        self.health_checks: Dict[str, Callable] = {}
        
    def register_component(self, name: str, component: Any, 
                         dependencies: List[str] = None,
                         health_check: Callable = None):
        """Register a system component"""
        self.components[name] = component
        self.dependencies[name] = dependencies or []
        if health_check:
            self.health_checks[name] = health_check
    
    def get_startup_order(self) -> List[str]:
        """Calculate optimal component startup order based on dependencies"""
        visited = set()
        order = []
        
        def visit(component):
            if component in visited:
                return
            visited.add(component)
            for dep in self.dependencies.get(component, []):
                visit(dep)
            order.append(component)
        
        for component in self.components:
            visit(component)
        
        return order
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Run health checks on all components"""
        results = {}
        for name, check_func in self.health_checks.items():
            try:
                if asyncio.iscoroutinefunction(check_func):
                    results[name] = await check_func()
                else:
                    results[name] = check_func()
            except Exception as e:
                logging.error(f"Health check failed for {name}: {e}")
                results[name] = False
        return results

# =============================================================================
# DATABASE CONNECTION MANAGER
# =============================================================================

class DatabaseManager:
    """OT-inspired database manager with redundancy and failover"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.primary_pool: Optional[asyncpg.Pool] = None
        self.backup_pools: List[asyncpg.Pool] = []
        self.current_pool: Optional[asyncpg.Pool] = None
        self.connection_lock = asyncio.Lock()
        self.metrics = SystemMetrics()
        
    async def initialize(self):
        """Initialize database connections with failover support"""
        try:
            # Primary database connection
            self.primary_pool = await asyncpg.create_pool(
                self.config['primary_db_url'],
                min_size=5,
                max_size=20,
                command_timeout=30,
                server_settings={
                    'application_name': 'DoganAI_Continuous_Upload',
                    'timezone': 'Asia/Riyadh'
                }
            )
            self.current_pool = self.primary_pool
            
            # Initialize backup connections if configured
            for backup_url in self.config.get('backup_db_urls', []):
                backup_pool = await asyncpg.create_pool(
                    backup_url,
                    min_size=2,
                    max_size=10,
                    command_timeout=30
                )
                self.backup_pools.append(backup_pool)
            
            logging.info(f"Database manager initialized with {len(self.backup_pools)} backup connections")
            
        except Exception as e:
            logging.error(f"Failed to initialize database manager: {e}")
            raise
    
    async def get_connection(self):
        """Get database connection with automatic failover"""
        async with self.connection_lock:
            if self.current_pool:
                try:
                    conn = await self.current_pool.acquire()
                    # Test connection
                    await conn.execute('SELECT 1')
                    return conn
                except Exception as e:
                    logging.warning(f"Primary connection failed: {e}")
                    await self._failover_to_backup()
            
            # Try backup connections
            for i, backup_pool in enumerate(self.backup_pools):
                try:
                    conn = await backup_pool.acquire()
                    await conn.execute('SELECT 1')
                    self.current_pool = backup_pool
                    logging.info(f"Failed over to backup database {i+1}")
                    return conn
                except Exception as e:
                    logging.warning(f"Backup connection {i+1} failed: {e}")
            
            raise Exception("All database connections failed")
    
    async def _failover_to_backup(self):
        """Handle failover to backup database"""
        if self.backup_pools:
            self.current_pool = self.backup_pools[0]
            logging.warning("Failed over to backup database")
    
    async def release_connection(self, conn):
        """Release database connection back to pool"""
        if self.current_pool:
            await self.current_pool.release(conn)
    
    async def health_check(self) -> bool:
        """Database health check"""
        try:
            conn = await self.get_connection()
            await conn.execute('SELECT 1')
            await self.release_connection(conn)
            return True
        except Exception:
            return False
    
    async def close(self):
        """Close all database connections"""
        if self.primary_pool:
            await self.primary_pool.close()
        for backup_pool in self.backup_pools:
            await backup_pool.close()

# =============================================================================
# DATA SYNCHRONIZATION ENGINE
# =============================================================================

class DataSynchronizer:
    """Core data synchronization engine with OT reliability principles"""
    
    def __init__(self, db_manager: DatabaseManager, config: Dict[str, Any]):
        self.db_manager = db_manager
        self.config = config
        self.upload_queue = asyncio.Queue(maxsize=1000)
        self.processing_queue = Queue(maxsize=100)
        self.state = SystemState.INITIALIZING
        self.metrics = SystemMetrics()
        self.running = False
        self.workers = []
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # OT-style operational parameters
        self.cycle_time = config.get('cycle_time', 5.0)  # seconds
        self.batch_size = config.get('batch_size', 50)
        self.max_queue_size = config.get('max_queue_size', 1000)
        
    async def start(self):
        """Start the synchronization engine"""
        self.running = True
        self.state = SystemState.OPERATIONAL
        
        # Start worker tasks
        self.workers = [
            asyncio.create_task(self._upload_worker(f"worker_{i}"))
            for i in range(self.config.get('worker_count', 3))
        ]
        
        # Start monitoring task
        self.workers.append(asyncio.create_task(self._monitor_system()))
        
        logging.info(f"Data synchronizer started with {len(self.workers)} workers")
    
    async def stop(self):
        """Stop the synchronization engine"""
        self.running = False
        self.state = SystemState.MAINTENANCE
        
        # Cancel all workers
        for worker in self.workers:
            worker.cancel()
        
        # Wait for workers to finish
        await asyncio.gather(*self.workers, return_exceptions=True)
        
        # Close executor
        self.executor.shutdown(wait=True)
        
        logging.info("Data synchronizer stopped")
    
    async def queue_data(self, data_packet: DataPacket) -> bool:
        """Queue data for upload with priority handling"""
        try:
            # Verify data integrity
            if not data_packet.verify_integrity():
                logging.error(f"Data integrity check failed for packet {data_packet.id}")
                return False
            
            # Check queue capacity
            if self.upload_queue.qsize() >= self.max_queue_size:
                logging.warning("Upload queue at capacity, dropping low priority packets")
                await self._drop_low_priority_packets()
            
            await self.upload_queue.put(data_packet)
            self.metrics.queue_size.set(self.upload_queue.qsize())
            
            logging.debug(f"Queued data packet {data_packet.id} from {data_packet.source}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to queue data packet: {e}")
            return False
    
    async def _drop_low_priority_packets(self):
        """Drop low priority packets when queue is full"""
        temp_packets = []
        dropped_count = 0
        
        # Extract all packets
        while not self.upload_queue.empty():
            try:
                packet = self.upload_queue.get_nowait()
                if packet.priority in [Priority.CRITICAL, Priority.HIGH]:
                    temp_packets.append(packet)
                else:
                    dropped_count += 1
            except asyncio.QueueEmpty:
                break
        
        # Re-queue high priority packets
        for packet in temp_packets:
            await self.upload_queue.put(packet)
        
        logging.warning(f"Dropped {dropped_count} low priority packets")
    
    async def _upload_worker(self, worker_id: str):
        """Worker task for processing upload queue"""
        logging.info(f"Upload worker {worker_id} started")
        
        while self.running:
            try:
                # Get data packet with timeout
                data_packet = await asyncio.wait_for(
                    self.upload_queue.get(), 
                    timeout=self.cycle_time
                )
                
                # Process the data packet
                start_time = time.time()
                success = await self._process_data_packet(data_packet)
                duration = time.time() - start_time
                
                # Record metrics
                self.metrics.record_upload(data_packet.source, success, duration)
                
                # Handle retry logic
                if not success and data_packet.retry_count < data_packet.max_retries:
                    data_packet.retry_count += 1
                    await asyncio.sleep(2 ** data_packet.retry_count)  # Exponential backoff
                    await self.upload_queue.put(data_packet)
                    logging.info(f"Retrying packet {data_packet.id} (attempt {data_packet.retry_count})")
                
                self.upload_queue.task_done()
                self.metrics.queue_size.set(self.upload_queue.qsize())
                
            except asyncio.TimeoutError:
                # Normal timeout, continue
                continue
            except Exception as e:
                logging.error(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(1)
        
        logging.info(f"Upload worker {worker_id} stopped")
    
    async def _process_data_packet(self, data_packet: DataPacket) -> bool:
        """Process individual data packet"""
        try:
            conn = await self.db_manager.get_connection()
            
            try:
                # Start transaction
                async with conn.transaction():
                    # Insert data based on destination
                    if data_packet.destination == 'compliance_data':
                        await self._insert_compliance_data(conn, data_packet)
                    elif data_packet.destination == 'ministry_data':
                        await self._insert_ministry_data(conn, data_packet)
                    elif data_packet.destination == 'audit_logs':
                        await self._insert_audit_data(conn, data_packet)
                    else:
                        await self._insert_generic_data(conn, data_packet)
                    
                    # Log successful upload
                    await self._log_upload(conn, data_packet, 'success')
                
                logging.debug(f"Successfully processed packet {data_packet.id}")
                return True
                
            finally:
                await self.db_manager.release_connection(conn)
                
        except Exception as e:
            logging.error(f"Failed to process packet {data_packet.id}: {e}")
            
            # Log failed upload
            try:
                conn = await self.db_manager.get_connection()
                await self._log_upload(conn, data_packet, 'failed', str(e))
                await self.db_manager.release_connection(conn)
            except:
                pass
            
            return False
    
    async def _insert_compliance_data(self, conn, data_packet: DataPacket):
        """Insert compliance-specific data"""
        await conn.execute("""
            INSERT INTO compliance_uploads 
            (id, source, data, priority, timestamp, checksum)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (id) DO UPDATE SET
                data = EXCLUDED.data,
                timestamp = EXCLUDED.timestamp,
                updated_at = NOW()
        """, 
        data_packet.id, data_packet.source, json.dumps(data_packet.data),
        data_packet.priority.value, data_packet.timestamp, data_packet.checksum)
    
    async def _insert_ministry_data(self, conn, data_packet: DataPacket):
        """Insert Ministry of Interior specific data"""
        await conn.execute("""
            INSERT INTO ministry_data 
            (id, source, data, priority, timestamp, checksum, classification)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (id) DO UPDATE SET
                data = EXCLUDED.data,
                timestamp = EXCLUDED.timestamp,
                updated_at = NOW()
        """, 
        data_packet.id, data_packet.source, json.dumps(data_packet.data),
        data_packet.priority.value, data_packet.timestamp, data_packet.checksum,
        data_packet.data.get('classification', 'unclassified'))
    
    async def _insert_audit_data(self, conn, data_packet: DataPacket):
        """Insert audit log data"""
        await conn.execute("""
            INSERT INTO audit_logs 
            (id, source, action, details, timestamp, checksum)
            VALUES ($1, $2, $3, $4, $5, $6)
        """, 
        data_packet.id, data_packet.source, data_packet.data.get('action', 'unknown'),
        json.dumps(data_packet.data), data_packet.timestamp, data_packet.checksum)
    
    async def _insert_generic_data(self, conn, data_packet: DataPacket):
        """Insert generic data"""
        await conn.execute("""
            INSERT INTO data_uploads 
            (id, source, destination, data, priority, timestamp, checksum)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (id) DO UPDATE SET
                data = EXCLUDED.data,
                timestamp = EXCLUDED.timestamp,
                updated_at = NOW()
        """, 
        data_packet.id, data_packet.source, data_packet.destination,
        json.dumps(data_packet.data), data_packet.priority.value,
        data_packet.timestamp, data_packet.checksum)
    
    async def _log_upload(self, conn, data_packet: DataPacket, status: str, error: str = None):
        """Log upload attempt"""
        await conn.execute("""
            INSERT INTO upload_logs 
            (packet_id, source, destination, status, error_message, timestamp)
            VALUES ($1, $2, $3, $4, $5, $6)
        """, 
        data_packet.id, data_packet.source, data_packet.destination,
        status, error, datetime.now(timezone.utc))
    
    async def _monitor_system(self):
        """System monitoring task"""
        while self.running:
            try:
                # Update system health
                health_score = self.metrics.get_health_score()
                
                # Check system state
                if health_score < 50:
                    self.state = SystemState.DEGRADED
                    logging.warning(f"System degraded - health score: {health_score:.1f}%")
                elif health_score < 20:
                    self.state = SystemState.FAULT
                    logging.error(f"System fault - health score: {health_score:.1f}%")
                else:
                    self.state = SystemState.OPERATIONAL
                
                # Log system status
                logging.info(f"System status: {self.state.value}, Health: {health_score:.1f}%, Queue: {self.upload_queue.qsize()}")
                
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                logging.error(f"System monitor error: {e}")
                await asyncio.sleep(5)

# =============================================================================
# API DATA COLLECTOR
# =============================================================================

class APIDataCollector:
    """Collects data from various API endpoints or scraped data based on configuration"""
    
    def __init__(self, config: Dict[str, Any], synchronizer: DataSynchronizer):
        self.config = config
        self.synchronizer = synchronizer
        self.session: Optional[aiohttp.ClientSession] = None
        self.endpoints = self._load_endpoints_from_config()
        self.use_scraped_data = config.get('USE_SCRAPED_DATA', True)  # Default to scraped data
        
    def _load_endpoints_from_config(self) -> Dict[str, Dict[str, Any]]:
        """Load API endpoints from actual regulatory authorities"""
        return {
            'nca': {
                'url': self.config.get('NCA_API_URL', 'https://api.nca.gov.sa'),
                'endpoints': ['/api/v1/companies', '/api/v1/compliance', '/api/v1/violations'],
                'priority': Priority.CRITICAL,
                'auth_header': 'X-NCA-API-Key',
                'api_key': self.config.get('NCA_API_KEY')
            },
            'sama': {
                'url': self.config.get('SAMA_API_URL', 'https://api.sama.gov.sa'),
                'endpoints': ['/api/v1/indicators', '/api/v1/banking', '/api/v1/compliance'],
                'priority': Priority.CRITICAL,
                'auth_type': 'oauth2',
                'token_endpoint': self.config.get('SAMA_TOKEN_ENDPOINT')
            },
            'moh': {
                'url': self.config.get('MOH_API_URL', 'https://api.moh.gov.sa'),
                'endpoints': ['/api/v1/compliance', '/api/v1/facilities', '/api/v1/standards'],
                'priority': Priority.HIGH,
                'auth_header': 'X-MOH-API-Key',
                'api_key': self.config.get('MOH_API_KEY')
            },
            'citc': {
                'url': self.config.get('CITC_API_URL', 'https://api.citc.gov.sa'),
                'endpoints': ['/api/v1/telecom', '/api/v1/compliance', '/api/v1/licenses'],
                'priority': Priority.HIGH,
                'auth_header': 'X-CITC-API-Key',
                'api_key': self.config.get('CITC_API_KEY')
            },
            'cma': {
                'url': self.config.get('CMA_API_URL', 'https://api.cma.org.sa'),
                'endpoints': ['/api/v1/securities', '/api/v1/compliance', '/api/v1/violations'],
                'priority': Priority.HIGH,
                'auth_header': 'X-CMA-API-Key',
                'api_key': self.config.get('CMA_API_KEY')
            }
        }
    
    async def start_collection(self):
        """Start continuous data collection from APIs or scraped data"""
        
        if self.use_scraped_data:
            # Use scraped data instead of API calls
            logging.info("Using scraped regulatory data instead of API calls")
            return [asyncio.create_task(self._collect_from_scraped_data())]
        
        # Original API collection code
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=20,
            ttl_dns_cache=300,
            use_dns_cache=True
        )
        
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'DoganAI-Continuous-Upload/1.0',
                'Accept': 'application/json'
            }
        )
        
        # Start collection tasks for each service
        tasks = []
        for service_name, service_config in self.endpoints.items():
            task = asyncio.create_task(
                self._collect_from_service(service_name, service_config)
            )
            tasks.append(task)
        
        logging.info(f"Started data collection from {len(tasks)} services")
        return tasks
    
    async def _collect_from_service(self, service_name: str, service_config: Dict[str, Any]):
        """Collect data from a specific service"""
        base_url = service_config['url']
        endpoints = service_config['endpoints']
        priority = service_config['priority']
        
        while True:
            try:
                for endpoint in endpoints:
                    url = f"{base_url}{endpoint}"
                    
                    try:
                        # Prepare headers with authentication
                        headers = {}
                        service_info = service_config
                        
                        if 'auth_header' in service_info and 'api_key' in service_info:
                            headers[service_info['auth_header']] = service_info['api_key']
                        
                        # Add standard headers
                        headers.update({
                            "Accept": "application/json",
                            "Content-Type": "application/json",
                            "User-Agent": "DoganAI-Compliance-Kit/1.0"
                        })
                        
                        async with self.session.get(url, headers=headers) as response:
                            if response.status == 200:
                                data = await response.json()
                                
                                # Create data packet
                                packet = DataPacket(
                                    id=str(uuid.uuid4()),
                                    source=f"{service_name}{endpoint}",
                                    destination=self._determine_destination(service_name, endpoint),
                                    data=data,
                                    priority=priority,
                                    timestamp=datetime.now(timezone.utc),
                                    checksum=""  # Will be calculated in __post_init__
                                )
                                
                                # Queue for upload
                                await self.synchronizer.queue_data(packet)
                                
                                logging.info(f"Successfully collected data from {url} (Authority: {service_name.upper()})")
                            elif response.status == 401:
                                logging.error(f"Authentication failed for {url} - check API keys")
                            elif response.status == 429:
                                logging.warning(f"Rate limit exceeded for {url} - backing off")
                                await asyncio.sleep(60)  # Wait 1 minute on rate limit
                            else:
                                logging.warning(f"HTTP {response.status} from {url}")
                                
                    except Exception as e:
                        logging.error(f"Failed to collect from {url}: {e}")
                        # Log specific errors for regulatory authorities
                        if "api.nca.gov.sa" in url:
                            logging.error("NCA API connection failed - check network and credentials")
                        elif "api.sama.gov.sa" in url:
                            logging.error("SAMA API connection failed - check OAuth2 configuration") 
                        elif "api.moh.gov.sa" in url:
                            logging.error("MoH API connection failed - check API key")
                        elif "api.citc.gov.sa" in url:
                            logging.error("CITC API connection failed - check API key")
                        elif "api.cma.org.sa" in url:
                            logging.error("CMA API connection failed - check API key")
                
                # Wait before next collection cycle
                await asyncio.sleep(self.config.get('collection_interval', 60))
                
            except Exception as e:
                logging.error(f"Service collection error for {service_name}: {e}")
                await asyncio.sleep(30)
    
    def _determine_destination(self, service_name: str, endpoint: str) -> str:
        """Determine data destination based on service and endpoint"""
        if service_name == 'ministry':
            return 'ministry_data'
        elif service_name == 'compliance':
            return 'compliance_data'
        elif 'audit' in endpoint or 'log' in endpoint:
            return 'audit_logs'
        else:
            return 'data_uploads'
    
    async def _collect_from_scraped_data(self):
        """Collect data from scraped regulatory websites"""
        
        try:
            from scraped_data_adapter import get_scraped_data_adapter
            
            adapter = get_scraped_data_adapter()
            summary = adapter.get_summary()
            
            if summary['status'] != 'ready':
                logging.error(f"Scraped data not ready: {summary.get('message', 'Unknown error')}")
                return
            
            logging.info(f"Loading scraped data: {summary['total_records']} records from {len(summary['authorities'])} authorities")
            
            while True:
                try:
                    # Generate data packets from scraped data
                    data_packets = adapter.generate_data_packets()
                    
                    for packet_data in data_packets:
                        # Create data packet
                        packet = DataPacket(
                            id=packet_data['id'],
                            source=packet_data['source'],
                            destination=packet_data['destination'],
                            data=packet_data['data'],
                            priority=Priority(packet_data['priority']),
                            timestamp=datetime.fromisoformat(packet_data['timestamp'].replace('Z', '+00:00')),
                            checksum=""  # Will be calculated in __post_init__
                        )
                        
                        # Queue for upload
                        await self.synchronizer.queue_data(packet)
                        
                        logging.info(f"Queued scraped data from {packet.source} (Authority: {packet_data['data'].get('authority', 'Unknown')})")
                        
                        # Small delay between packets to avoid overwhelming the queue
                        await asyncio.sleep(0.1)
                    
                    # Wait before next collection cycle (longer for scraped data since it doesn't change as often)
                    collection_interval = self.config.get('scraped_data_interval', 300)  # 5 minutes default
                    logging.info(f"Scraped data collection cycle complete. Next cycle in {collection_interval} seconds.")
                    await asyncio.sleep(collection_interval)
                    
                except Exception as e:
                    logging.error(f"Error processing scraped data: {e}")
                    await asyncio.sleep(60)  # Wait before retrying
        
        except ImportError:
            logging.error("scraped_data_adapter not found. Please run the web scraper first.")
            await asyncio.sleep(300)
        except Exception as e:
            logging.error(f"Failed to collect scraped data: {e}")
            await asyncio.sleep(300)
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()

# =============================================================================
# MAIN SYSTEM ORCHESTRATOR
# =============================================================================

class ContinuousUploadSystem:
    """Main system orchestrator with OT principles"""
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.state = SystemState.INITIALIZING
        self.components = ComponentRegistry()
        self.db_manager: Optional[DatabaseManager] = None
        self.synchronizer: Optional[DataSynchronizer] = None
        self.collector: Optional[APIDataCollector] = None
        self.metrics_server_port = self.config.get('metrics_port', 9091)
        
        # Setup logging
        self._setup_logging()
        
        # Setup signal handlers
        self._setup_signal_handlers()
    
    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """Load system configuration"""
        default_config = {
            'primary_db_url': 'postgresql://doganai:secure_password@localhost:5432/ministry_db',
            'backup_db_urls': [],
            'worker_count': 3,
            'batch_size': 50,
            'cycle_time': 5.0,
            'collection_interval': 60,
            'max_queue_size': 1000,
            'metrics_port': 9091,
            'log_level': 'INFO',
            # Real Saudi Regulatory Authority APIs
            'NCA_API_URL': 'https://api.nca.gov.sa',
            'SAMA_API_URL': 'https://api.sama.gov.sa',
            'MOH_API_URL': 'https://api.moh.gov.sa',
            'CITC_API_URL': 'https://api.citc.gov.sa',
            'CMA_API_URL': 'https://api.cma.org.sa',
            # Data source configuration
            'USE_SCRAPED_DATA': True,  # Use scraped data by default
            'scraped_data_interval': 300,  # 5 minutes between scraped data cycles
            # GCC Regional APIs
            'UAE_CENTRAL_BANK_URL': 'https://api.centralbank.ae',
            'QATAR_CENTRAL_BANK_URL': 'https://api.qcb.gov.qa',
            'BAHRAIN_CENTRAL_BANK_URL': 'https://api.cbb.gov.bh',
            'KUWAIT_CENTRAL_BANK_URL': 'https://api.cbk.gov.kw',
            'OMAN_CENTRAL_BANK_URL': 'https://api.cbo.gov.om'
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def _setup_logging(self):
        """Setup system logging"""
        logging.basicConfig(
            level=getattr(logging, self.config.get('log_level', 'INFO')),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('continuous_upload_system.log')
            ]
        )
        
        # Reduce noise from external libraries
        logging.getLogger('aiohttp').setLevel(logging.WARNING)
        logging.getLogger('asyncpg').setLevel(logging.WARNING)
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logging.info(f"Received signal {signum}, initiating graceful shutdown")
            asyncio.create_task(self.stop())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def initialize(self):
        """Initialize all system components"""
        logging.info("Initializing Continuous Database Upload System")
        
        try:
            # Initialize database manager
            self.db_manager = DatabaseManager(self.config)
            await self.db_manager.initialize()
            self.components.register_component(
                'database', self.db_manager, 
                health_check=self.db_manager.health_check
            )
            
            # Initialize synchronizer
            self.synchronizer = DataSynchronizer(self.db_manager, self.config)
            self.components.register_component(
                'synchronizer', self.synchronizer,
                dependencies=['database']
            )
            
            # Initialize API collector
            self.collector = APIDataCollector(self.config, self.synchronizer)
            self.components.register_component(
                'collector', self.collector,
                dependencies=['synchronizer']
            )
            
            # Create database tables
            await self._create_database_tables()
            
            # Start metrics server
            start_http_server(self.metrics_server_port)
            logging.info(f"Metrics server started on port {self.metrics_server_port}")
            
            self.state = SystemState.OPERATIONAL
            logging.info("System initialization completed successfully")
            
        except Exception as e:
            self.state = SystemState.FAULT
            logging.error(f"System initialization failed: {e}")
            raise
    
    async def _create_database_tables(self):
        """Create necessary database tables"""
        conn = await self.db_manager.get_connection()
        
        try:
            # Create tables for different data types
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS compliance_uploads (
                    id VARCHAR(255) PRIMARY KEY,
                    source VARCHAR(255) NOT NULL,
                    data JSONB NOT NULL,
                    priority INTEGER NOT NULL,
                    timestamp TIMESTAMPTZ NOT NULL,
                    checksum VARCHAR(64) NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                );
                
                CREATE TABLE IF NOT EXISTS ministry_data (
                    id VARCHAR(255) PRIMARY KEY,
                    source VARCHAR(255) NOT NULL,
                    data JSONB NOT NULL,
                    priority INTEGER NOT NULL,
                    timestamp TIMESTAMPTZ NOT NULL,
                    checksum VARCHAR(64) NOT NULL,
                    classification VARCHAR(50) DEFAULT 'unclassified',
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                );
                
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id VARCHAR(255) PRIMARY KEY,
                    source VARCHAR(255) NOT NULL,
                    action VARCHAR(255) NOT NULL,
                    details JSONB NOT NULL,
                    timestamp TIMESTAMPTZ NOT NULL,
                    checksum VARCHAR(64) NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
                
                CREATE TABLE IF NOT EXISTS data_uploads (
                    id VARCHAR(255) PRIMARY KEY,
                    source VARCHAR(255) NOT NULL,
                    destination VARCHAR(255) NOT NULL,
                    data JSONB NOT NULL,
                    priority INTEGER NOT NULL,
                    timestamp TIMESTAMPTZ NOT NULL,
                    checksum VARCHAR(64) NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                );
                
                CREATE TABLE IF NOT EXISTS upload_logs (
                    id SERIAL PRIMARY KEY,
                    packet_id VARCHAR(255) NOT NULL,
                    source VARCHAR(255) NOT NULL,
                    destination VARCHAR(255) NOT NULL,
                    status VARCHAR(50) NOT NULL,
                    error_message TEXT,
                    timestamp TIMESTAMPTZ NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
                
                -- Create indexes for performance
                CREATE INDEX IF NOT EXISTS idx_compliance_uploads_timestamp ON compliance_uploads(timestamp);
                CREATE INDEX IF NOT EXISTS idx_ministry_data_timestamp ON ministry_data(timestamp);
                CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp);
                CREATE INDEX IF NOT EXISTS idx_data_uploads_timestamp ON data_uploads(timestamp);
                CREATE INDEX IF NOT EXISTS idx_upload_logs_timestamp ON upload_logs(timestamp);
                CREATE INDEX IF NOT EXISTS idx_ministry_data_classification ON ministry_data(classification);
            """)
            
            logging.info("Database tables created successfully")
            
        finally:
            await self.db_manager.release_connection(conn)
    
    async def start(self):
        """Start the continuous upload system"""
        logging.info("Starting Continuous Database Upload System")
        
        try:
            # Start components in dependency order
            startup_order = self.components.get_startup_order()
            
            for component_name in startup_order:
                component = self.components.components[component_name]
                if hasattr(component, 'start'):
                    await component.start()
                    logging.info(f"Started component: {component_name}")
            
            # Start API data collection
            collection_tasks = await self.collector.start_collection()
            
            logging.info("System started successfully - Ministry of Interior delivery ready")
            
            # Run health monitoring
            await self._run_health_monitoring()
            
        except Exception as e:
            logging.error(f"Failed to start system: {e}")
            await self.stop()
            raise
    
    async def _run_health_monitoring(self):
        """Run continuous health monitoring"""
        while self.state != SystemState.MAINTENANCE:
            try:
                health_results = await self.components.health_check_all()
                
                healthy_components = sum(1 for result in health_results.values() if result)
                total_components = len(health_results)
                
                if healthy_components < total_components:
                    logging.warning(f"Health check: {healthy_components}/{total_components} components healthy")
                    if healthy_components < total_components * 0.5:
                        self.state = SystemState.DEGRADED
                
                await asyncio.sleep(60)  # Health check every minute
                
            except Exception as e:
                logging.error(f"Health monitoring error: {e}")
                await asyncio.sleep(30)
    
    async def stop(self):
        """Stop the continuous upload system"""
        logging.info("Stopping Continuous Database Upload System")
        self.state = SystemState.MAINTENANCE
        
        try:
            # Stop components in reverse order
            if self.collector:
                await self.collector.close()
            
            if self.synchronizer:
                await self.synchronizer.stop()
            
            if self.db_manager:
                await self.db_manager.close()
            
            logging.info("System stopped successfully")
            
        except Exception as e:
            logging.error(f"Error during system shutdown: {e}")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        health_results = await self.components.health_check_all()
        
        return {
            'state': self.state.value,
            'components': health_results,
            'metrics': {
                'queue_size': self.synchronizer.upload_queue.qsize() if self.synchronizer else 0,
                'health_score': self.synchronizer.metrics.get_health_score() if self.synchronizer else 0,
                'total_uploads': self.synchronizer.metrics.total_uploads if self.synchronizer else 0,
                'successful_uploads': self.synchronizer.metrics.successful_uploads if self.synchronizer else 0,
                'failed_uploads': self.synchronizer.metrics.failed_uploads if self.synchronizer else 0
            },
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

async def main():
    """Main entry point for the continuous upload system"""
    system = ContinuousUploadSystem()
    
    try:
        await system.initialize()
        await system.start()
    except KeyboardInterrupt:
        logging.info("Received interrupt signal")
    except Exception as e:
        logging.error(f"System error: {e}")
    finally:
        await system.stop()

if __name__ == "__main__":
    asyncio.run(main())