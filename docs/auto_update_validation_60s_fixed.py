#!/usr/bin/env python3
"""
DoganAI Compliance Kit - 60-Second Auto-Update & Validation System
Real-time regulatory, government, and vendor data synchronization
"""

import asyncio
import aiohttp
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import uuid
from concurrent.futures import ThreadPoolExecutor
import sqlite3
import threading
from queue import Queue, Empty
import os
import signal
import sys

# =============================================================================
# RAPID CYCLE CONFIGURATION
# =============================================================================

class UpdateFrequency(Enum):
    """Update frequency settings"""
    REAL_TIME = 60     # 60 seconds for all sources
    HIGH_PRIORITY = 30 # 30 seconds for critical sources
    CRITICAL = 15      # 15 seconds for emergency updates

class DataSourceType(Enum):
    """Data source types"""
    REGULATORY = "regulatory"
    VENDOR = "vendor"
    GOVERNMENT = "government"

@dataclass
class DataSource:
    """Data source configuration"""
    id: str
    name: str
    type: DataSourceType
    url: str
    endpoints: List[str]
    auth_config: Dict[str, Any]
    validation_rules: Dict[str, Any]
    status: str = "active"
    retry_count: int = 0
    max_retries: int = 3
    last_update: Optional[datetime] = None
    priority: str = "normal"

# =============================================================================
# DATA SOURCE REGISTRY
# =============================================================================

class DataSourceRegistry:
    """Registry for all data sources"""
    
    def __init__(self):
        self.all_sources: Dict[str, DataSource] = {}
        self._load_default_sources()
    
    def _load_default_sources(self):
        """Load default data sources"""
        # Regulatory Authorities
        self.register_source(DataSource(
            id="nca",
            name="National Cybersecurity Authority",
            type=DataSourceType.REGULATORY,
            url="https://api.nca.gov.sa",
            endpoints=["/api/v1/companies", "/api/v1/compliance", "/api/v1/violations"],
            auth_config={"type": "api_key", "header": "X-API-Key", "key": ""},
            validation_rules={"min_records": 1, "required_fields": ["company_id", "status"]},
            priority="critical"
        ))
        
        self.register_source(DataSource(
            id="sama",
            name="Saudi Arabian Monetary Authority",
            type=DataSourceType.REGULATORY,
            url="https://api.sama.gov.sa",
            endpoints=["/api/v1/financial-institutions", "/api/v1/regulations"],
            auth_config={"type": "api_key", "header": "Authorization", "key": ""},
            validation_rules={"min_records": 1, "required_fields": ["institution_id", "compliance_status"]},
            priority="critical"
        ))
        
        # Vendor Sources
        self.register_source(DataSource(
            id="ibm_watson",
            name="IBM Watson",
            type=DataSourceType.VENDOR,
            url="https://api.ibm.com/watson",
            endpoints=["/api/v1/ai-models", "/api/v1/compliance-tools"],
            auth_config={"type": "oauth2", "client_id": "", "client_secret": ""},
            validation_rules={"min_records": 1, "required_fields": ["model_id", "version"]},
            priority="high"
        ))
        
        # Government Sources
        self.register_source(DataSource(
            id="moi",
            name="Ministry of Interior",
            type=DataSourceType.GOVERNMENT,
            url="https://api.moi.gov.sa",
            endpoints=["/api/v1/security-alerts", "/api/v1/compliance-reports"],
            auth_config={"type": "api_key", "header": "X-MOI-Key", "key": ""},
            validation_rules={"min_records": 1, "required_fields": ["alert_id", "severity"]},
            priority="critical"
        ))
    
    def register_source(self, source: DataSource):
        """Register a new data source"""
        self.all_sources[source.id] = source
    
    def get_sources_by_type(self, source_type: DataSourceType) -> Dict[str, DataSource]:
        """Get all sources of a specific type"""
        return {k: v for k, v in self.all_sources.items() if v.type == source_type}

# =============================================================================
# REAL-TIME VALIDATOR
# =============================================================================

class RealTimeValidator:
    """Real-time data validation engine"""
    
    def __init__(self):
        self.validation_cache = {}
        self.validation_stats = {
            "total_validations": 0,
            "successful_validations": 0,
            "failed_validations": 0
        }
    
    def validate_data(self, source_id: str, data: List[Dict], rules: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data against rules"""
        start_time = time.time()
        
        try:
            # Basic validation
            if not isinstance(data, list):
                return self._create_validation_result(False, "Data must be a list", 0, time.time() - start_time)
            
            if len(data) < rules.get("min_records", 0):
                return self._create_validation_result(False, f"Insufficient records: {len(data)} < {rules.get('min_records', 0)}", len(data), time.time() - start_time)
            
            # Field validation
            required_fields = rules.get("required_fields", [])
            valid_records = 0
            
            for record in data:
                if isinstance(record, dict) and all(field in record for field in required_fields):
                    valid_records += 1
            
            if valid_records == 0:
                return self._create_validation_result(False, "No valid records found", len(data), time.time() - start_time)
            
            # Update stats
            self.validation_stats["total_validations"] += 1
            self.validation_stats["successful_validations"] += 1
            
            return self._create_validation_result(True, "Validation successful", valid_records, time.time() - start_time)
            
        except Exception as e:
            self.validation_stats["total_validations"] += 1
            self.validation_stats["failed_validations"] += 1
            return self._create_validation_result(False, str(e), 0, time.time() - start_time)
    
    def _create_validation_result(self, is_valid: bool, message: str, record_count: int, validation_time: float) -> Dict[str, Any]:
        """Create validation result dictionary"""
        return {
            "is_valid": is_valid,
            "message": message,
            "record_count": record_count,
            "validation_time": validation_time,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# =============================================================================
# AUTO-UPDATE ENGINE
# =============================================================================

class AutoUpdateEngine:
    """60-second auto-update engine for all data sources"""
    
    def __init__(self, db_path: str = "doganai_compliance.db"):
        self.db_path = db_path
        self.registry = DataSourceRegistry()
        self.validator = RealTimeValidator()
        self.session: Optional[aiohttp.ClientSession] = None
        self.running = False
        self.update_tasks = []
        self.executor = ThreadPoolExecutor(max_workers=8)
        self.update_stats = {
            "total_updates": 0,
            "successful_updates": 0,
            "failed_updates": 0,
            "start_time": time.time()
        }
        
        # Data source priority settings
        self.use_scraped_data_primary = True  # Start with scraped data
        self.api_health_check_interval = 300  # Check API health every 5 minutes
        self.last_api_health_check = 0
        self.api_health_status = {}  # Track API health per source
        
        # Non-blocking queues for different data types
        self.regulatory_queue = asyncio.Queue(maxsize=1000)
        self.vendor_queue = asyncio.Queue(maxsize=1000) 
        self.government_queue = asyncio.Queue(maxsize=1000)
        
        self._setup_logging()
        self._setup_database()
    
    def _setup_logging(self):
        """Setup logging for auto-update system"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - AUTO_UPDATE - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('auto_update_60s.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _setup_database(self):
        """Setup database tables for auto-update tracking"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create auto-update tracking table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auto_update_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_id TEXT NOT NULL,
                    source_name TEXT NOT NULL,
                    update_timestamp DATETIME NOT NULL,
                    status TEXT NOT NULL,
                    records_updated INTEGER DEFAULT 0,
                    validation_result TEXT,
                    update_duration REAL DEFAULT 0.0,
                    error_message TEXT,
                    data_source_type TEXT DEFAULT 'scraped',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create data updates table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS realtime_data_updates (
                    id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    data TEXT NOT NULL,
                    checksum TEXT NOT NULL,
                    validation_status TEXT NOT NULL,
                    update_timestamp DATETIME NOT NULL,
                    data_source_type TEXT DEFAULT 'scraped',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create API health tracking table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_health_status (
                    source_id TEXT PRIMARY KEY,
                    source_name TEXT NOT NULL,
                    last_check DATETIME NOT NULL,
                    status TEXT NOT NULL,
                    response_time REAL DEFAULT 0.0,
                    error_count INTEGER DEFAULT 0,
                    success_count INTEGER DEFAULT 0,
                    last_success DATETIME,
                    last_error DATETIME,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_auto_update_timestamp ON auto_update_log(update_timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_auto_update_source ON auto_update_log(source_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_realtime_data_source ON realtime_data_updates(source_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_realtime_data_timestamp ON realtime_data_updates(update_timestamp)")
            
            conn.commit()
            conn.close()
            
            self.logger.info("Auto-update database tables initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to setup database: {e}")
            raise
    
    async def start(self):
        """Start the 60-second auto-update system"""
        self.logger.info("🚀 Starting 60-Second Auto-Update & Validation System")
        self.logger.info("=" * 60)
        self.logger.info("📊 PRIMARY DATA SOURCE: Existing Scraped Data")
        self.logger.info("🔄 FALLBACK: Live APIs (when available)")
        self.logger.info("⏰ API Health Check: Every 5 minutes")
        
        self.running = True
        
        # Setup HTTP session with optimized settings
        connector = aiohttp.TCPConnector(
            limit=200,
            limit_per_host=50,
            ttl_dns_cache=300,
            use_dns_cache=True,
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        
        timeout = aiohttp.ClientTimeout(total=45, connect=15)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'DoganAI-AutoUpdate/1.0',
                'Accept': 'application/json',
                'Cache-Control': 'no-cache'
            }
        )
        
        # Start update tasks for different source types
        self.update_tasks = [
            asyncio.create_task(self._regulatory_update_cycle()),
            asyncio.create_task(self._vendor_update_cycle()),
            asyncio.create_task(self._government_update_cycle()),
            asyncio.create_task(self._data_processor()),
            asyncio.create_task(self._health_monitor()),
            asyncio.create_task(self._api_health_checker())
        ]
        
        self.logger.info(f"✅ Started {len(self.update_tasks)} update cycles")
        self.logger.info("📊 Update frequency: 60 seconds for all sources")
        self.logger.info("🔄 Non-blocking operations enabled")
        
        # Wait for tasks to complete
        try:
            await asyncio.gather(*self.update_tasks)
        except Exception as e:
            self.logger.error(f"Update cycle error: {e}")
        finally:
            await self.stop()
    
    async def _api_health_checker(self):
        """Periodically check API health and switch data sources"""
        self.logger.info("🔍 Starting API health checker")
        
        while self.running:
            try:
                current_time = time.time()
                
                # Check API health every 5 minutes
                if current_time - self.last_api_health_check >= self.api_health_check_interval:
                    await self._check_all_api_health()
                    self.last_api_health_check = current_time
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"🔍 API health checker error: {e}")
                await asyncio.sleep(60)
    
    async def _check_all_api_health(self):
        """Check health of all API endpoints"""
        self.logger.info("🔍 Checking API health status...")
        
        for source_id, source in self.registry.all_sources.items():
            try:
                health_status = await self._check_single_api_health(source)
                self.api_health_status[source_id] = health_status
                
                # Log health status
                if health_status['healthy']:
                    self.logger.info(f"✅ {source.name}: API Healthy ({health_status['response_time']:.2f}s)")
                else:
                    self.logger.warning(f"❌ {source.name}: API Unhealthy - {health_status['error']}")
                
                # Store in database
                await self._store_api_health_status(source_id, source.name, health_status)
                
            except Exception as e:
                self.logger.error(f"🔍 Health check failed for {source.name}: {e}")
                self.api_health_status[source_id] = {
                    'healthy': False,
                    'error': str(e),
                    'response_time': 0.0,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
    
    async def _check_single_api_health(self, source: DataSource) -> Dict[str, Any]:
        """Check health of a single API endpoint"""
        start_time = time.time()
        
        try:
            # Try to connect to the first endpoint
            if source.endpoints:
                test_endpoint = source.endpoints[0]
                url = f"{source.url}{test_endpoint}"
                
                # Prepare headers
                headers = {}
                auth_config = source.auth_config
                
                if auth_config.get("type") == "api_key" and auth_config.get("key"):
                    headers[auth_config["header"]] = auth_config["key"]
                
                headers.update({
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                })
                
                # Quick health check with shorter timeout
                async with self.session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        return {
                            'healthy': True,
                            'response_time': response_time,
                            'status_code': response.status,
                            'timestamp': datetime.now(timezone.utc).isoformat()
                        }
                    elif response.status == 401:
                        return {
                            'healthy': False,
                            'error': 'Authentication required',
                            'response_time': response_time,
                            'status_code': response.status,
                            'timestamp': datetime.now(timezone.utc).isoformat()
                        }
                    else:
                        return {
                            'healthy': False,
                            'error': f'HTTP {response.status}',
                            'response_time': response_time,
                            'status_code': response.status,
                            'timestamp': datetime.now(timezone.utc).isoformat()
                        }
            
            return {
                'healthy': False,
                'error': 'No endpoints configured',
                'response_time': time.time() - start_time,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except asyncio.TimeoutError:
            return {
                'healthy': False,
                'error': 'Timeout',
                'response_time': time.time() - start_time,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'response_time': time.time() - start_time,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def _store_api_health_status(self, source_id: str, source_name: str, health_status: Dict):
        """Store API health status in database"""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self.executor,
                self._sync_store_api_health,
                source_id, source_name, health_status
            )
        except Exception as e:
            self.logger.error(f"💾 Failed to store API health status: {e}")
    
    def _sync_store_api_health(self, source_id: str, source_name: str, health_status: Dict):
        """Synchronous API health status storage"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO api_health_status 
                (source_id, source_name, last_check, status, response_time, 
                 error_count, success_count, last_success, last_error, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                source_id, source_name, health_status['timestamp'],
                'healthy' if health_status['healthy'] else 'unhealthy',
                health_status['response_time'],
                0 if health_status['healthy'] else 1,  # error_count
                1 if health_status['healthy'] else 0,  # success_count
                health_status['timestamp'] if health_status['healthy'] else None,
                None if health_status['healthy'] else health_status['timestamp'],
                datetime.now(timezone.utc).isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"💾 Database storage error: {e}")
    
    async def _regulatory_update_cycle(self):
        """60-second update cycle for regulatory sources"""
        self.logger.info("🏛️ Starting regulatory sources update cycle")
        
        while self.running:
            try:
                regulatory_sources = self.registry.get_sources_by_type(DataSourceType.REGULATORY)
                
                # Create concurrent update tasks
                update_tasks = []
                for source_id, source in regulatory_sources.items():
                    task = asyncio.create_task(self._update_source(source))
                    update_tasks.append(task)
                
                # Wait for all updates to complete with timeout
                if update_tasks:
                    await asyncio.wait_for(
                        asyncio.gather(*update_tasks, return_exceptions=True),
                        timeout=55.0  # 55 seconds to allow 5 seconds buffer
                    )
                
                # Wait for next cycle
                await asyncio.sleep(60)
                
            except asyncio.TimeoutError:
                self.logger.warning("⏰ Regulatory update cycle timeout - continuing to next cycle")
                await asyncio.sleep(60)
            except Exception as e:
                self.logger.error(f"❌ Regulatory cycle error: {e}")
                await asyncio.sleep(30)  # Shorter wait on error
    
    async def _vendor_update_cycle(self):
        """60-second update cycle for vendor sources"""
        self.logger.info("🔧 Starting vendor sources update cycle")
        
        while self.running:
            try:
                vendor_sources = self.registry.get_sources_by_type(DataSourceType.VENDOR)
                
                # Create concurrent update tasks
                update_tasks = []
                for source_id, source in vendor_sources.items():
                    task = asyncio.create_task(self._update_source(source))
                    update_tasks.append(task)
                
                # Wait for all updates to complete with timeout
                if update_tasks:
                    await asyncio.wait_for(
                        asyncio.gather(*update_tasks, return_exceptions=True),
                        timeout=55.0
                    )
                
                # Wait for next cycle
                await asyncio.sleep(60)
                
            except asyncio.TimeoutError:
                self.logger.warning("⏰ Vendor update cycle timeout - continuing to next cycle")
                await asyncio.sleep(60)
            except Exception as e:
                self.logger.error(f"❌ Vendor cycle error: {e}")
                await asyncio.sleep(30)
    
    async def _government_update_cycle(self):
        """60-second update cycle for government sources"""
        self.logger.info("🏛️ Starting government sources update cycle")
        
        while self.running:
            try:
                government_sources = self.registry.get_sources_by_type(DataSourceType.GOVERNMENT)
                
                # Create concurrent update tasks
                update_tasks = []
                for source_id, source in government_sources.items():
                    task = asyncio.create_task(self._update_source(source))
                    update_tasks.append(task)
                
                # Wait for all updates to complete with timeout
                if update_tasks:
                    await asyncio.wait_for(
                        asyncio.gather(*update_tasks, return_exceptions=True),
                        timeout=55.0
                    )
                
                # Wait for next cycle
                await asyncio.sleep(60)
                
            except asyncio.TimeoutError:
                self.logger.warning("⏰ Government update cycle timeout - continuing to next cycle")
                await asyncio.sleep(60)
            except Exception as e:
                self.logger.error(f"❌ Government cycle error: {e}")
                await asyncio.sleep(30)
    
    async def _update_source(self, source: DataSource) -> bool:
        """Update individual data source with priority logic"""
        start_time = time.time()
        
        try:
            # Check if source is active and not exceeding retry limit
            if source.status != "active" or source.retry_count >= source.max_retries:
                return False
            
            # Update source timestamp
            source.last_update = datetime.now(timezone.utc)
            
            # Determine data source priority
            api_healthy = self.api_health_status.get(source.id, {}).get('healthy', False)
            
            if self.use_scraped_data_primary and not api_healthy:
                # Use scraped data as primary source
                data = await self._get_scraped_data(source)
                data_source_type = "scraped"
            else:
                # Try live API first, fallback to scraped data
                data = await self._get_live_api_data(source)
                if not data:
                    data = await self._get_scraped_data(source)
                    data_source_type = "scraped"
                else:
                    data_source_type = "api"
            
            if not data:
                self.logger.warning(f"📭 No data received from {source.name}")
                source.retry_count += 1
                return False
            
            # Validate data
            validation_result = self.validator.validate_data(source.id, data, source.validation_rules)
            
            # Store data if validation passes
            if validation_result["is_valid"]:
                await self._store_update_data(source, data, validation_result, data_source_type)
                source.retry_count = 0  # Reset retry count on success
                
                self.update_stats["successful_updates"] += 1
                self.logger.info(f"✅ {source.name}: Updated {validation_result['record_count']} records from {data_source_type} in {time.time() - start_time:.2f}s")
                
                return True
            else:
                self.logger.error(f"❌ {source.name}: Validation failed - {validation_result['errors']}")
                source.retry_count += 1
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Update failed for {source.name}: {e}")
            source.retry_count += 1
            return False
        finally:
            self.update_stats["total_updates"] += 1
            if not hasattr(self, '_last_stats_report') or time.time() - self._last_stats_report > 300:  # Report every 5 minutes
                self._report_stats()
                self._last_stats_report = time.time()
    
    async def _get_scraped_data(self, source: DataSource) -> Optional[List[Dict]]:
        """Get data from existing scraped data sources"""
        try:
            # Check for existing scraped data files
            scraped_files = [
                "regulatory_scraping_results.json",
                "scraped_data_adapter.py",
                "doganai_compliance.db"
            ]
            
            # Try to load from scraped data adapter
            try:
                from scraped_data_adapter import get_scraped_data_adapter
                adapter = get_scraped_data_adapter()
                
                # Get data for this specific source
                source_data = adapter.get_source_data(source.id)
                if source_data:
                    return source_data
                    
            except ImportError:
                self.logger.debug(f"Scraped data adapter not available for {source.name}")
            
            # Try to load from regulatory scraping results
            if os.path.exists("regulatory_scraping_results.json"):
                with open("regulatory_scraping_results.json", "r") as f:
                    scraped_results = json.load(f)
                
                # Extract data for this source
                if source.id in scraped_results.get("scraped_data", {}):
                    return scraped_results["scraped_data"][source.id]
            
            # Try to load from database
            return await self._get_data_from_database(source.id)
            
        except Exception as e:
            self.logger.warning(f"📭 Failed to get scraped data for {source.name}: {e}")
            return None
    
    async def _get_data_from_database(self, source_id: str) -> Optional[List[Dict]]:
        """Get data from existing database"""
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                self.executor,
                self._sync_get_database_data,
                source_id
            )
            return data
        except Exception as e:
            self.logger.warning(f"📭 Failed to get database data for {source_id}: {e}")
            return None
    
    def _sync_get_database_data(self, source_id: str) -> Optional[List[Dict]]:
        """Synchronous database data retrieval"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Try to get data from various tables
            tables = ["compliance_uploads", "ministry_data", "data_uploads"]
            
            for table in tables:
                cursor.execute(f"""
                    SELECT data FROM {table} 
                    WHERE source_id = ? OR source LIKE ? 
                    ORDER BY timestamp DESC LIMIT 10
                """, (source_id, f"%{source_id}%"))
                
                results = cursor.fetchall()
                if results:
                    data = []
                    for row in results:
                        try:
                            row_data = json.loads(row[0])
                            if isinstance(row_data, list):
                                data.extend(row_data)
                            else:
                                data.append(row_data)
                        except:
                            continue
                    
                    if data:
                        conn.close()
                        return data
            
            conn.close()
            return None
            
        except Exception as e:
            self.logger.error(f"💾 Database retrieval error: {e}")
            return None
    
    async def _get_live_api_data(self, source: DataSource) -> Optional[List[Dict]]:
        """Get data from live API endpoints"""
        try:
            # Check if API is healthy
            api_health = self.api_health_status.get(source.id, {})
            if not api_health.get('healthy', False):
                return None
            
            # Collect data from all endpoints
            all_data = []
            for endpoint in source.endpoints:
                try:
                    endpoint_data = await self._fetch_endpoint_data(source, endpoint)
                    if endpoint_data:
                        all_data.extend(endpoint_data if isinstance(endpoint_data, list) else [endpoint_data])
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to fetch from {source.name} {endpoint}: {e}")
                    continue
            
            return all_data if all_data else None
            
        except Exception as e:
            self.logger.warning(f"⚠️ Live API data fetch failed for {source.name}: {e}")
            return None
    
    async def _fetch_endpoint_data(self, source: DataSource, endpoint: str) -> Optional[List[Dict]]:
        """Fetch data from specific endpoint"""
        url = f"{source.url}{endpoint}"
        
        try:
            # Prepare authentication headers
            headers = {}
            auth_config = source.auth_config
            
            if auth_config.get("type") == "api_key" and auth_config.get("key"):
                headers[auth_config["header"]] = auth_config["key"]
            elif auth_config.get("type") == "oauth2":
                # For OAuth2, implement token refresh logic here
                pass
            
            # Add standard headers
            headers.update({
                "Accept": "application/json",
                "Content-Type": "application/json"
            })
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data if isinstance(data, list) else [data]
                elif response.status == 401:
                    self.logger.error(f"🔐 Authentication failed for {url}")
                elif response.status == 429:
                    self.logger.warning(f"🚦 Rate limit hit for {url}")
                    await asyncio.sleep(30)  # Back off for 30 seconds
                elif response.status == 404:
                    self.logger.warning(f"🔍 Endpoint not found: {url}")
                else:
                    self.logger.warning(f"⚠️ HTTP {response.status} from {url}")
                
                return None
                
        except asyncio.TimeoutError:
            self.logger.warning(f"⏰ Timeout fetching from {url}")
            return None
        except Exception as e:
            self.logger.error(f"❌ Error fetching from {url}: {e}")
            return None
    
    async def _store_update_data(self, source: DataSource, data: List[Dict], validation_result: Dict, data_source_type: str = "scraped"):
        """Store updated data in database"""
        try:
            # Prepare data for storage
            data_id = str(uuid.uuid4())
            data_json = json.dumps(data)
            checksum = hashlib.sha256(data_json.encode()).hexdigest()
            
            # Store in database using thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self.executor,
                self._sync_store_data,
                data_id, source, data_json, checksum, validation_result, data_source_type
            )
            
        except Exception as e:
            self.logger.error(f"💾 Failed to store data for {source.name}: {e}")
    
    def _sync_store_data(self, data_id: str, source: DataSource, data_json: str, 
                        checksum: str, validation_result: Dict, data_source_type: str):
        """Synchronous database storage operation"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Store realtime data
            cursor.execute("""
                INSERT OR REPLACE INTO realtime_data_updates 
                (id, source_id, source_type, data, checksum, validation_status, update_timestamp, data_source_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data_id, source.id, source.type.value, data_json, checksum,
                "valid" if validation_result["is_valid"] else "invalid",
                datetime.now(timezone.utc).isoformat(), data_source_type
            ))
            
            # Log update
            cursor.execute("""
                INSERT INTO auto_update_log 
                (source_id, source_name, update_timestamp, status, records_updated, 
                 validation_result, update_duration, data_source_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                source.id, source.name, datetime.now(timezone.utc).isoformat(),
                "success", validation_result["record_count"],
                json.dumps(validation_result), validation_result["validation_time"], data_source_type
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"💾 Database storage error: {e}")
    
    async def _data_processor(self):
        """Process queued data updates"""
        self.logger.info("🔄 Starting data processor")
        
        while self.running:
            try:
                # Process regulatory data
                try:
                    regulatory_data = await asyncio.wait_for(
                        self.regulatory_queue.get(), timeout=1.0
                    )
                    await self._process_data_update(regulatory_data)
                except asyncio.TimeoutError:
                    pass
                
                # Process vendor data
                try:
                    vendor_data = await asyncio.wait_for(
                        self.vendor_queue.get(), timeout=1.0
                    )
                    await self._process_data_update(vendor_data)
                except asyncio.TimeoutError:
                    pass
                
                # Process government data
                try:
                    government_data = await asyncio.wait_for(
                        self.government_queue.get(), timeout=1.0
                    )
                    await self._process_data_update(government_data)
                except asyncio.TimeoutError:
                    pass
                
                await asyncio.sleep(0.1)  # Small delay to prevent CPU spinning
                
            except Exception as e:
                self.logger.error(f"❌ Data processor error: {e}")
                await asyncio.sleep(1)
    
    async def _process_data_update(self, data_update: Dict):
        """Process individual data update"""
        try:
            # Validate and store the update
            source_id = data_update.get("source_id")
            data = data_update.get("data", [])
            
            if source_id in self.registry.all_sources:
                source = self.registry.all_sources[source_id]
                validation_result = self.validator.validate_data(source_id, data, source.validation_rules)
                
                if validation_result["is_valid"]:
                    await self._store_update_data(source, data, validation_result)
                    self.logger.info(f"✅ Processed update for {source.name}: {validation_result['record_count']} records")
                else:
                    self.logger.warning(f"⚠️ Invalid data update for {source.name}: {validation_result['message']}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to process data update: {e}")
    
    async def _health_monitor(self):
        """Monitor system health and performance"""
        self.logger.info("🏥 Starting health monitor")
        
        while self.running:
            try:
                # Check system resources
                uptime = time.time() - self.update_stats["start_time"]
                success_rate = (self.update_stats["successful_updates"] / max(self.update_stats["total_updates"], 1)) * 100
                
                # Log health status every 5 minutes
                if int(uptime) % 300 < 60:  # Every 5 minutes
                    self.logger.info("🏥 System Health Check:")
                    self.logger.info(f"   📊 Total Updates: {self.update_stats['total_updates']}")
                    self.logger.info(f"   ✅ Successful: {self.update_stats['successful_updates']}")
                    self.logger.info(f"   ❌ Failed: {self.update_stats['failed_updates']}")
                    self.logger.info(f"   📈 Success Rate: {success_rate:.1f}%")
                    self.logger.info(f"   ⏰ Uptime: {uptime/3600:.1f} hours")
                
                # Check for critical issues
                if success_rate < 50 and self.update_stats["total_updates"] > 10:
                    self.logger.warning("🚨 CRITICAL: Success rate below 50%")
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"❌ Health monitor error: {e}")
                await asyncio.sleep(60)
    
    def _report_stats(self):
        """Report current statistics"""
        try:
            uptime = time.time() - self.update_stats["start_time"]
            success_rate = (self.update_stats["successful_updates"] / max(self.update_stats["total_updates"], 1)) * 100
            
            self.logger.info("=" * 40)
            self.logger.info("📊 Total Updates: %d", self.update_stats["total_updates"])
            self.logger.info("✅ Successful: %d", self.update_stats["successful_updates"])
            self.logger.info("❌ Failed: %d", self.update_stats["failed_updates"])
            self.logger.info("📈 Success Rate: %.1f%%", success_rate)
            self.logger.info("⏰ Uptime: %.1f hours", uptime/3600)
            self.logger.info("=" * 40)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to report stats: {e}")
    
    async def stop(self):
        """Stop the auto-update system"""
        self.logger.info("🛑 Stopping auto-update system...")
        self.running = False
        
        # Cancel all tasks
        for task in self.update_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.update_tasks:
            await asyncio.gather(*self.update_tasks, return_exceptions=True)
        
        # Close HTTP session
        if self.session:
            await self.session.close()
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        self.logger.info("✅ Auto-update system stopped")

# =============================================================================
# MAIN EXECUTION
# =============================================================================

async def main():
    """Main execution function"""
    engine = AutoUpdateEngine()
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        asyncio.create_task(engine.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await engine.start()
    except KeyboardInterrupt:
        await engine.stop()
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        await engine.stop()

if __name__ == "__main__":
    asyncio.run(main())
