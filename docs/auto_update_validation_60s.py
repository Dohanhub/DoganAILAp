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
    HIGH_PRIORITY = 30  # 30 seconds for critical authorities
    CRITICAL = 15      # 15 seconds for emergency updates

class DataSourceType(Enum):
    """Data source classifications"""
    REGULATORY = "regulatory"
    GOVERNMENT = "government" 
    VENDOR = "vendor"
    COMPLIANCE = "compliance"

@dataclass
class DataSource:
    """Unified data source configuration"""
    id: str
    name: str
    type: DataSourceType
    url: str
    endpoints: List[str]
    priority: str
    auth_config: Dict[str, Any]
    validation_rules: Dict[str, Any]
    last_update: Optional[datetime] = None
    update_frequency: int = 60
    status: str = "active"
    retry_count: int = 0
    max_retries: int = 3

# =============================================================================
# REAL-TIME DATA SOURCES REGISTRY
# =============================================================================

class DataSourceRegistry:
    """Centralized registry for all data sources"""
    
    def __init__(self):
        self.regulatory_sources = self._init_regulatory_sources()
        self.vendor_sources = self._init_vendor_sources()
        self.government_sources = self._init_government_sources()
        self.all_sources = {**self.regulatory_sources, **self.vendor_sources, **self.government_sources}
        
    def _init_regulatory_sources(self) -> Dict[str, DataSource]:
        """Initialize Saudi regulatory authority sources"""
        return {
            "NCA": DataSource(
                id="nca_sa",
                name="National Commercial Authority",
                type=DataSourceType.REGULATORY,
                url="https://api.nca.gov.sa",
                endpoints=["/api/v1/companies", "/api/v1/compliance", "/api/v1/violations", "/api/v1/reports"],
                priority="critical",
                auth_config={"type": "api_key", "header": "X-NCA-API-Key", "key": os.getenv("NCA_API_KEY")},
                validation_rules={"min_records": 1, "required_fields": ["company_id", "status", "compliance_score"]},
                update_frequency=60
            ),
            "SAMA": DataSource(
                id="sama_sa",
                name="Saudi Arabian Monetary Authority", 
                type=DataSourceType.REGULATORY,
                url="https://api.sama.gov.sa",
                endpoints=["/api/v1/indicators", "/api/v1/banking", "/api/v1/compliance", "/api/v1/sanctions"],
                priority="critical",
                auth_config={"type": "oauth2", "token_endpoint": "https://auth.sama.gov.sa/oauth/token"},
                validation_rules={"min_records": 1, "required_fields": ["bank_id", "status", "risk_score"]},
                update_frequency=60
            ),
            "MOH": DataSource(
                id="moh_sa",
                name="Ministry of Health",
                type=DataSourceType.GOVERNMENT,
                url="https://api.moh.gov.sa", 
                endpoints=["/api/v1/compliance", "/api/v1/facilities", "/api/v1/standards", "/api/v1/certifications"],
                priority="high",
                auth_config={"type": "api_key", "header": "X-MOH-API-Key", "key": os.getenv("MOH_API_KEY")},
                validation_rules={"min_records": 1, "required_fields": ["facility_id", "compliance_status"]},
                update_frequency=60
            ),
            "CITC": DataSource(
                id="citc_sa", 
                name="Communications & IT Commission",
                type=DataSourceType.REGULATORY,
                url="https://api.citc.gov.sa",
                endpoints=["/api/v1/telecom", "/api/v1/compliance", "/api/v1/licenses"],
                priority="high",
                auth_config={"type": "api_key", "header": "X-CITC-API-Key", "key": os.getenv("CITC_API_KEY")},
                validation_rules={"min_records": 1, "required_fields": ["license_id", "status"]},
                update_frequency=60
            ),
            "CMA": DataSource(
                id="cma_sa",
                name="Capital Market Authority",
                type=DataSourceType.REGULATORY, 
                url="https://api.cma.org.sa",
                endpoints=["/api/v1/securities", "/api/v1/compliance", "/api/v1/violations"],
                priority="high",
                auth_config={"type": "api_key", "header": "X-CMA-API-Key", "key": os.getenv("CMA_API_KEY")},
                validation_rules={"min_records": 1, "required_fields": ["security_id", "compliance_score"]},
                update_frequency=60
            )
        }
    
    def _init_vendor_sources(self) -> Dict[str, DataSource]:
        """Initialize vendor API sources"""
        return {
            "IBM_WATSON": DataSource(
                id="ibm_watson",
                name="IBM Watson AI Platform",
                type=DataSourceType.VENDOR,
                url="https://gateway.watsonplatform.net",
                endpoints=["/natural-language-understanding/api/v1/analyze", "/assistant/api/v2/sessions"],
                priority="high",
                auth_config={"type": "api_key", "header": "Authorization", "key": f"Bearer {os.getenv('IBM_WATSON_API_KEY')}"},
                validation_rules={"min_records": 1, "required_fields": ["analysis", "confidence"]},
                update_frequency=60
            ),
            "MICROSOFT_AZURE": DataSource(
                id="microsoft_azure",
                name="Microsoft Azure Cognitive Services",
                type=DataSourceType.VENDOR,
                url="https://api.cognitive.microsoft.com",
                endpoints=["/text/analytics/v3.1/sentiment", "/text/analytics/v3.1/entities"],
                priority="high", 
                auth_config={"type": "api_key", "header": "Ocp-Apim-Subscription-Key", "key": os.getenv("AZURE_API_KEY")},
                validation_rules={"min_records": 1, "required_fields": ["documents", "sentiment"]},
                update_frequency=60
            ),
            "AWS_COMPREHEND": DataSource(
                id="aws_comprehend",
                name="Amazon Comprehend",
                type=DataSourceType.VENDOR,
                url="https://comprehend.us-east-1.amazonaws.com",
                endpoints=["/", "/comprehend/"],
                priority="high",
                auth_config={"type": "aws_signature", "access_key": os.getenv("AWS_ACCESS_KEY"), "secret_key": os.getenv("AWS_SECRET_KEY")},
                validation_rules={"min_records": 1, "required_fields": ["sentiment", "confidence"]},
                update_frequency=60
            )
        }
        
    def _init_government_sources(self) -> Dict[str, DataSource]:
        """Initialize government data sources"""
        return {
            "MOI": DataSource(
                id="moi_sa",
                name="Ministry of Interior",
                type=DataSourceType.GOVERNMENT,
                url="https://api.moi.gov.sa",
                endpoints=["/api/v1/security", "/api/v1/compliance", "/api/v1/violations"],
                priority="critical",
                auth_config={"type": "api_key", "header": "X-MOI-API-Key", "key": os.getenv("MOI_API_KEY")},
                validation_rules={"min_records": 1, "required_fields": ["security_id", "status"]},
                update_frequency=60
            ),
            "SDAIA": DataSource(
                id="sdaia_sa",
                name="Saudi Data & AI Authority",
                type=DataSourceType.GOVERNMENT,
                url="https://api.sdaia.gov.sa",
                endpoints=["/api/v1/data-compliance", "/api/v1/ai-governance"],
                priority="critical",
                auth_config={"type": "api_key", "header": "X-SDAIA-API-Key", "key": os.getenv("SDAIA_API_KEY")},
                validation_rules={"min_records": 1, "required_fields": ["compliance_id", "ai_governance_score"]},
                update_frequency=60
            )
        }
    
    def get_sources_by_type(self, source_type: DataSourceType) -> Dict[str, DataSource]:
        """Get sources filtered by type"""
        return {k: v for k, v in self.all_sources.items() if v.type == source_type}
    
    def get_critical_sources(self) -> Dict[str, DataSource]:
        """Get critical priority sources"""
        return {k: v for k, v in self.all_sources.items() if v.priority == "critical"}

# =============================================================================
# 60-SECOND VALIDATION ENGINE
# =============================================================================

class RealTimeValidator:
    """Real-time data validation engine"""
    
    def __init__(self):
        self.validation_cache = {}
        self.error_threshold = 0.05  # 5% error rate threshold
        self.performance_metrics = {
            "total_validations": 0,
            "successful_validations": 0,
            "failed_validations": 0,
            "avg_validation_time": 0.0
        }
    
    def validate_data(self, source_id: str, data: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data against source-specific rules"""
        start_time = time.time()
        validation_result = {
            "source_id": source_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "record_count": 0,
            "validation_time": 0.0
        }
        
        try:
            # Record count validation
            if isinstance(data, list):
                validation_result["record_count"] = len(data)
                records = data
            elif isinstance(data, dict) and 'data' in data:
                records = data['data'] if isinstance(data['data'], list) else [data['data']]
                validation_result["record_count"] = len(records)
            else:
                records = [data]
                validation_result["record_count"] = 1
            
            # Minimum records check
            min_records = rules.get("min_records", 1)
            if validation_result["record_count"] < min_records:
                validation_result["errors"].append(f"Insufficient records: got {validation_result['record_count']}, expected >= {min_records}")
                validation_result["is_valid"] = False
            
            # Required fields validation
            required_fields = rules.get("required_fields", [])
            for record in records:
                if isinstance(record, dict):
                    for field in required_fields:
                        if field not in record or record[field] is None:
                            validation_result["warnings"].append(f"Missing required field '{field}' in record")
            
            # Data integrity checks
            for record in records:
                if isinstance(record, dict):
                    # Check for empty values in critical fields
                    critical_fields = ["id", "status", "timestamp"] 
                    for field in critical_fields:
                        if field in record and (record[field] == "" or record[field] is None):
                            validation_result["warnings"].append(f"Empty critical field '{field}'")
                    
                    # Timestamp validation
                    if "timestamp" in record:
                        try:
                            datetime.fromisoformat(record["timestamp"].replace('Z', '+00:00'))
                        except (ValueError, AttributeError):
                            validation_result["errors"].append(f"Invalid timestamp format: {record.get('timestamp')}")
                            validation_result["is_valid"] = False
            
            # Performance validation
            validation_time = time.time() - start_time
            validation_result["validation_time"] = validation_time
            
            if validation_time > 5.0:  # 5 second threshold
                validation_result["warnings"].append(f"Slow validation: {validation_time:.2f}s")
            
            # Update metrics
            self.performance_metrics["total_validations"] += 1
            if validation_result["is_valid"]:
                self.performance_metrics["successful_validations"] += 1
            else:
                self.performance_metrics["failed_validations"] += 1
            
            # Update average validation time
            total_time = (self.performance_metrics["avg_validation_time"] * 
                         (self.performance_metrics["total_validations"] - 1) + validation_time)
            self.performance_metrics["avg_validation_time"] = total_time / self.performance_metrics["total_validations"]
            
        except Exception as e:
            validation_result["is_valid"] = False
            validation_result["errors"].append(f"Validation exception: {str(e)}")
            self.performance_metrics["total_validations"] += 1
            self.performance_metrics["failed_validations"] += 1
        
        # Cache result for performance monitoring
        self.validation_cache[source_id] = validation_result
        
        return validation_result
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get overall validation performance summary"""
        error_rate = 0.0
        if self.performance_metrics["total_validations"] > 0:
            error_rate = self.performance_metrics["failed_validations"] / self.performance_metrics["total_validations"]
        
        return {
            "total_sources_validated": len(self.validation_cache),
            "performance_metrics": self.performance_metrics,
            "error_rate": error_rate,
            "health_status": "healthy" if error_rate < self.error_threshold else "degraded",
            "last_validation": datetime.now(timezone.utc).isoformat()
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
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
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

    async def _check_all_api_health(self):
        """Placeholder for API health checking logic"""
        self.logger.info("🔍 Checking API health for all sources...")
        # In a real scenario, you would iterate through all sources
        # and check their endpoints for availability and response times.
        # If a source becomes unhealthy, you might mark it as inactive
        # and trigger a retry mechanism.
        await asyncio.sleep(10) # Simulate a small check time
        self.logger.info("🔍 API health check complete.")
    
    async def _update_source(self, source: DataSource) -> bool:
        """Update individual data source"""
        start_time = time.time()
        
        try:
            # Check if source is active and not exceeding retry limit
            if source.status != "active" or source.retry_count >= source.max_retries:
                return False
            
            # Update source timestamp
            source.last_update = datetime.now(timezone.utc)
            
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
            
            if not all_data:
                self.logger.warning(f"📭 No data received from {source.name}")
                source.retry_count += 1
                return False
            
            # Validate data
            validation_result = self.validator.validate_data(source.id, all_data, source.validation_rules)
            
            # Store data if validation passes
            if validation_result["is_valid"]:
                await self._store_update_data(source, all_data, validation_result)
                source.retry_count = 0  # Reset retry count on success
                
                self.update_stats["successful_updates"] += 1
                self.logger.info(f"✅ {source.name}: Updated {validation_result['record_count']} records in {time.time() - start_time:.2f}s")
                
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
    
    async def _store_update_data(self, source: DataSource, data: List[Dict], validation_result: Dict):
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
                data_id, source, data_json, checksum, validation_result
            )
            
        except Exception as e:
            self.logger.error(f"💾 Failed to store data for {source.name}: {e}")
    
    def _sync_store_data(self, data_id: str, source: DataSource, data_json: str, 
                        checksum: str, validation_result: Dict):
        """Synchronous database storage operation"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Store realtime data
            cursor.execute("""
                INSERT OR REPLACE INTO realtime_data_updates 
                (id, source_id, source_type, data, checksum, validation_status, update_timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                data_id, source.id, source.type.value, data_json, checksum,
                "valid" if validation_result["is_valid"] else "invalid",
                datetime.now(timezone.utc).isoformat()
            ))
            
            # Log update
            cursor.execute("""
                INSERT INTO auto_update_log 
                (source_id, source_name, update_timestamp, status, records_updated, 
                 validation_result, update_duration)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                source.id, source.name, datetime.now(timezone.utc).isoformat(),
                "success", validation_result["record_count"],
                json.dumps(validation_result), validation_result["validation_time"]
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"💾 Database storage error: {e}")
    
    async def _data_processor(self):
        """Process queued data updates"""
        self.logger.info("📊 Starting data processor")
        
        while self.running:
            try:
                # Process any queued data updates
                # This could include additional processing, notifications, etc.
                await asyncio.sleep(10)  # Process every 10 seconds
                
            except Exception as e:
                self.logger.error(f"📊 Data processor error: {e}")
                await asyncio.sleep(30)
    
    async def _health_monitor(self):
        """Monitor system health and performance"""
        self.logger.info("🏥 Starting health monitor")
        
        while self.running:
            try:
                # Get validation summary
                validation_summary = self.validator.get_validation_summary()
                
                # Calculate update success rate
                success_rate = 0.0
                if self.update_stats["total_updates"] > 0:
                    success_rate = self.update_stats["successful_updates"] / self.update_stats["total_updates"]
                
                # Log health status
                if success_rate >= 0.8 and validation_summary["health_status"] == "healthy":
                    health_status = "🟢 HEALTHY"
                elif success_rate >= 0.6:
                    health_status = "🟡 DEGRADED"
                else:
                    health_status = "🔴 CRITICAL"
                
                self.logger.info(f"🏥 System Health: {health_status} | Success Rate: {success_rate:.1%} | Sources: {validation_summary['total_sources_validated']}")
                
                # Wait 2 minutes between health checks
                await asyncio.sleep(120)
                
            except Exception as e:
                self.logger.error(f"🏥 Health monitor error: {e}")
                await asyncio.sleep(60)
    
    def _report_stats(self):
        """Report system statistics"""
        uptime = time.time() - self.update_stats["start_time"]
        success_rate = 0.0
        if self.update_stats["total_updates"] > 0:
            success_rate = self.update_stats["successful_updates"] / self.update_stats["total_updates"]
        
        self.logger.info("📈 === AUTO-UPDATE STATISTICS ===")
        self.logger.info(f"📊 Total Updates: {self.update_stats['total_updates']}")
        self.logger.info(f"✅ Successful: {self.update_stats['successful_updates']}")
        self.logger.info(f"❌ Failed: {self.update_stats['failed_updates']}")
        self.logger.info(f"📈 Success Rate: {success_rate:.1%}")
        self.logger.info(f"⏰ Uptime: {uptime/3600:.1f} hours")
        self.logger.info("=" * 40)
    
    async def stop(self):
        """Stop the auto-update system"""
        self.logger.info("🛑 Stopping auto-update system...")
        self.running = False
        
        # Cancel all tasks
        for task in self.update_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.update_tasks, return_exceptions=True)
        
        # Close HTTP session
        if self.session:
            await self.session.close()
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        self.logger.info("✅ Auto-update system stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            "running": self.running,
            "total_sources": len(self.registry.all_sources),
            "update_stats": self.update_stats,
            "validation_summary": self.validator.get_validation_summary(),
            "uptime_hours": (time.time() - self.update_stats["start_time"]) / 3600
        }

# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

async def main():
    """Main entry point for 60-second auto-update system"""
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logging.info(f"Received signal {signum}, shutting down...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and start auto-update engine
    engine = AutoUpdateEngine()
    
    try:
        await engine.start()
    except KeyboardInterrupt:
        logging.info("Interrupted by user")
    except Exception as e:
        logging.error(f"System error: {e}")
    finally:
        await engine.stop()

if __name__ == "__main__":
    # Set event loop policy for Windows compatibility
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    asyncio.run(main())
