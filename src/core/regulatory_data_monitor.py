"""
Automated Regulatory Data Monitoring System
Keeps all regulators, auditors, and regulations updated from trusted sources
"""

import asyncio
import aiohttp
import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
from bs4 import BeautifulSoup
import pandas as pd
import feedparser
import schedule
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RegulatorInfo:
    """Regulator information structure"""
    id: str
    name: str
    type: str
    domain: str
    website: str
    api_endpoint: Optional[str]
    last_updated: str
    status: str
    regulations_count: int
    contact_info: Dict[str, Any]

@dataclass
class RegulationInfo:
    """Regulation information structure"""
    id: str
    regulator_id: str
    title: str
    type: str
    effective_date: str
    last_modified: str
    status: str
    sectors: List[str]
    compliance_deadline: Optional[str]
    source_url: str
    content_hash: str

@dataclass
class AuditFirmInfo:
    """Audit firm information structure"""
    id: str
    name: str
    type: str
    socpa_license: str
    staff_count: int
    offices: List[str]
    specializations: List[str]
    clients_count: int
    last_updated: str
    status: str

class RegulatoryDataMonitor:
    """Automated system for monitoring regulatory data updates"""
    
    def __init__(self, db_path: str = "regulatory_monitor.db"):
        self.db_path = db_path
        self.session = None
        self.trusted_sources = self._load_trusted_sources()
        self._init_database()
        
    def _load_trusted_sources(self) -> Dict[str, Dict[str, Any]]:
        """Load configuration of trusted government sources"""
        return {
            "sama": {
                "name": "Saudi Central Bank",
                "base_url": "https://www.sama.gov.sa",
                "rss_feed": "https://www.sama.gov.sa/en-US/News/Pages/default.aspx",
                "api_endpoints": {
                    "regulations": "/api/regulations",
                    "circulars": "/api/circulars"
                },
                "check_frequency": "daily",
                "selectors": {
                    "news": ".news-item",
                    "regulations": ".regulation-link",
                    "date": ".publish-date"
                }
            },
            "nca": {
                "name": "National Cybersecurity Authority",
                "base_url": "https://nca.gov.sa",
                "rss_feed": "https://nca.gov.sa/en/news/",
                "api_endpoints": {
                    "controls": "/api/controls",
                    "guidelines": "/api/guidelines"
                },
                "check_frequency": "daily",
                "selectors": {
                    "news": ".news-article",
                    "controls": ".control-item",
                    "date": ".news-date"
                }
            },
            "citc": {
                "name": "Communications & IT Commission",
                "base_url": "https://www.citc.gov.sa",
                "rss_feed": "https://www.citc.gov.sa/en/mediacenter/news/",
                "check_frequency": "daily"
            },
            "cma": {
                "name": "Capital Market Authority",
                "base_url": "https://cma.org.sa",
                "rss_feed": "https://cma.org.sa/en/MediaCenter/PR/",
                "check_frequency": "daily"
            },
            "zatca": {
                "name": "Zakat, Tax and Customs Authority",
                "base_url": "https://zatca.gov.sa",
                "api_endpoints": {
                    "einvoicing": "https://gw-fatoora.zatca.gov.sa/e-invoicing/developer-portal"
                },
                "check_frequency": "daily"
            },
            "sfda": {
                "name": "Saudi Food & Drug Authority",
                "base_url": "https://www.sfda.gov.sa",
                "api_endpoints": {
                    "products": "https://developer.sfda.gov.sa/api"
                },
                "check_frequency": "weekly"
            },
            "socpa": {
                "name": "Saudi Organization for CPAs",
                "base_url": "https://socpa.org.sa",
                "api_endpoints": {
                    "firms": "/api/licensed-firms",
                    "cpas": "/api/licensed-cpas"
                },
                "check_frequency": "weekly"
            }
        }
    
    def _init_database(self):
        """Initialize SQLite database for storing regulatory data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Regulators table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS regulators (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT,
                domain TEXT,
                website TEXT,
                api_endpoint TEXT,
                last_updated TEXT,
                status TEXT,
                regulations_count INTEGER,
                contact_info TEXT,
                data_hash TEXT
            )
        ''')
        
        # Regulations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS regulations (
                id TEXT PRIMARY KEY,
                regulator_id TEXT,
                title TEXT NOT NULL,
                type TEXT,
                effective_date TEXT,
                last_modified TEXT,
                status TEXT,
                sectors TEXT,
                compliance_deadline TEXT,
                source_url TEXT,
                content_hash TEXT,
                FOREIGN KEY (regulator_id) REFERENCES regulators (id)
            )
        ''')
        
        # Audit firms table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_firms (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT,
                socpa_license TEXT,
                staff_count INTEGER,
                offices TEXT,
                specializations TEXT,
                clients_count INTEGER,
                last_updated TEXT,
                status TEXT,
                data_hash TEXT
            )
        ''')
        
        # Monitoring log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monitoring_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                check_time TEXT,
                status TEXT,
                changes_detected INTEGER,
                error_message TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def start_monitoring(self):
        """Start the automated monitoring system"""
        logger.info("Starting regulatory data monitoring system...")
        
        # Create aiohttp session
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'DoganAI-Compliance-Monitor/1.0'
            }
        )
        
        # Schedule monitoring tasks
        schedule.every().day.at("06:00").do(self._run_daily_checks)
        schedule.every().week.at("06:00").do(self._run_weekly_checks)
        schedule.every().hour.do(self._check_critical_sources)
        
        # Run initial check
        await self._run_daily_checks()
        
        # Keep monitoring running
        while True:
            schedule.run_pending()
            await asyncio.sleep(60)  # Check every minute
    
    async def _run_daily_checks(self):
        """Run daily monitoring checks"""
        logger.info("Running daily regulatory checks...")
        
        daily_sources = [
            source for source, config in self.trusted_sources.items()
            if config.get("check_frequency") == "daily"
        ]
        
        for source in daily_sources:
            try:
                await self._monitor_source(source)
            except Exception as e:
                logger.error(f"Error monitoring {source}: {e}")
                await self._log_monitoring_error(source, str(e))
    
    async def _run_weekly_checks(self):
        """Run weekly monitoring checks"""
        logger.info("Running weekly regulatory checks...")
        
        weekly_sources = [
            source for source, config in self.trusted_sources.items()
            if config.get("check_frequency") == "weekly"
        ]
        
        for source in weekly_sources:
            try:
                await self._monitor_source(source)
            except Exception as e:
                logger.error(f"Error monitoring {source}: {e}")
                await self._log_monitoring_error(source, str(e))
    
    async def _check_critical_sources(self):
        """Check critical sources hourly"""
        critical_sources = ["sama", "nca", "zatca"]  # Most critical regulators
        
        for source in critical_sources:
            try:
                await self._quick_check_source(source)
            except Exception as e:
                logger.error(f"Critical check failed for {source}: {e}")
    
    async def _monitor_source(self, source_key: str):
        """Monitor a specific regulatory source"""
        config = self.trusted_sources[source_key]
        logger.info(f"Monitoring {config['name']}...")
        
        changes_detected = 0
        
        # Check RSS feed if available
        if "rss_feed" in config:
            changes = await self._check_rss_feed(source_key, config["rss_feed"])
            changes_detected += changes
        
        # Check API endpoints if available
        if "api_endpoints" in config:
            for endpoint_name, endpoint_url in config["api_endpoints"].items():
                changes = await self._check_api_endpoint(source_key, endpoint_name, endpoint_url)
                changes_detected += changes
        
        # Scrape website for updates
        changes = await self._scrape_website_updates(source_key, config)
        changes_detected += changes
        
        # Log monitoring result
        await self._log_monitoring_result(source_key, "success", changes_detected)
        
        if changes_detected > 0:
            logger.info(f"Detected {changes_detected} changes from {config['name']}")
            await self._notify_changes(source_key, changes_detected)
    
    async def _check_rss_feed(self, source_key: str, rss_url: str) -> int:
        """Check RSS feed for new updates"""
        try:
            async with self.session.get(rss_url) as response:
                if response.status == 200:
                    content = await response.text()
                    feed = feedparser.parse(content)
                    
                    changes = 0
                    for entry in feed.entries[:10]:  # Check last 10 entries
                        if await self._is_new_content(source_key, entry.link, entry.title):
                            await self._store_regulation_update(source_key, entry)
                            changes += 1
                    
                    return changes
        except Exception as e:
            logger.error(f"RSS check failed for {source_key}: {e}")
        
        return 0
    
    async def _check_api_endpoint(self, source_key: str, endpoint_name: str, endpoint_url: str) -> int:
        """Check API endpoint for updates"""
        try:
            async with self.session.get(endpoint_url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Process API response based on endpoint type
                    if endpoint_name == "regulations":
                        return await self._process_regulations_api(source_key, data)
                    elif endpoint_name == "firms":
                        return await self._process_audit_firms_api(source_key, data)
                    
        except Exception as e:
            logger.error(f"API check failed for {source_key}/{endpoint_name}: {e}")
        
        return 0
    
    async def _scrape_website_updates(self, source_key: str, config: Dict[str, Any]) -> int:
        """Scrape website for regulatory updates"""
        try:
            base_url = config["base_url"]
            async with self.session.get(f"{base_url}/en/news") as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    changes = 0
                    selectors = config.get("selectors", {})
                    
                    # Look for news items
                    news_selector = selectors.get("news", ".news-item")
                    news_items = soup.select(news_selector)
                    
                    for item in news_items[:5]:  # Check last 5 news items
                        title = item.get_text().strip()
                        link = item.get('href') or item.find('a')['href'] if item.find('a') else ""
                        
                        if link and await self._is_new_content(source_key, link, title):
                            await self._store_news_update(source_key, title, link)
                            changes += 1
                    
                    return changes
                    
        except Exception as e:
            logger.error(f"Website scraping failed for {source_key}: {e}")
        
        return 0
    
    async def _quick_check_source(self, source_key: str):
        """Quick health check for critical sources"""
        config = self.trusted_sources[source_key]
        
        try:
            async with self.session.get(config["base_url"], timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status != 200:
                    logger.warning(f"Critical source {source_key} returned status {response.status}")
                    await self._alert_critical_issue(source_key, f"HTTP {response.status}")
        except Exception as e:
            logger.error(f"Critical source {source_key} is unreachable: {e}")
            await self._alert_critical_issue(source_key, str(e))
    
    async def _is_new_content(self, source_key: str, url: str, title: str) -> bool:
        """Check if content is new based on URL and title hash"""
        content_hash = hashlib.md5(f"{url}:{title}".encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM regulations 
            WHERE regulator_id = ? AND content_hash = ?
        ''', (source_key, content_hash))
        
        exists = cursor.fetchone()[0] > 0
        conn.close()
        
        return not exists
    
    async def _store_regulation_update(self, source_key: str, entry):
        """Store new regulation update in database"""
        regulation = RegulationInfo(
            id=hashlib.md5(f"{source_key}:{entry.link}".encode()).hexdigest(),
            regulator_id=source_key,
            title=entry.title,
            type="news_update",
            effective_date=datetime.now().isoformat(),
            last_modified=datetime.now().isoformat(),
            status="active",
            sectors=[],
            compliance_deadline=None,
            source_url=entry.link,
            content_hash=hashlib.md5(f"{entry.link}:{entry.title}".encode()).hexdigest()
        )
        
        await self._save_regulation(regulation)
    
    async def _store_news_update(self, source_key: str, title: str, link: str):
        """Store news update in database"""
        regulation = RegulationInfo(
            id=hashlib.md5(f"{source_key}:{link}".encode()).hexdigest(),
            regulator_id=source_key,
            title=title,
            type="news_update",
            effective_date=datetime.now().isoformat(),
            last_modified=datetime.now().isoformat(),
            status="active",
            sectors=[],
            compliance_deadline=None,
            source_url=link,
            content_hash=hashlib.md5(f"{link}:{title}".encode()).hexdigest()
        )
        
        await self._save_regulation(regulation)
    
    async def _save_regulation(self, regulation: RegulationInfo):
        """Save regulation to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO regulations 
            (id, regulator_id, title, type, effective_date, last_modified, 
             status, sectors, compliance_deadline, source_url, content_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            regulation.id, regulation.regulator_id, regulation.title,
            regulation.type, regulation.effective_date, regulation.last_modified,
            regulation.status, json.dumps(regulation.sectors),
            regulation.compliance_deadline, regulation.source_url, regulation.content_hash
        ))
        
        conn.commit()
        conn.close()
    
    async def _process_regulations_api(self, source_key: str, data: Dict[str, Any]) -> int:
        """Process regulations from API response"""
        changes = 0
        
        if isinstance(data, dict) and "regulations" in data:
            for reg_data in data["regulations"]:
                if await self._is_new_regulation(source_key, reg_data):
                    await self._store_api_regulation(source_key, reg_data)
                    changes += 1
        
        return changes
    
    async def _process_audit_firms_api(self, source_key: str, data: Dict[str, Any]) -> int:
        """Process audit firms from API response"""
        changes = 0
        
        if isinstance(data, dict) and "firms" in data:
            for firm_data in data["firms"]:
                if await self._is_new_audit_firm(source_key, firm_data):
                    await self._store_api_audit_firm(source_key, firm_data)
                    changes += 1
        
        return changes
    
    async def _log_monitoring_result(self, source: str, status: str, changes: int):
        """Log monitoring result to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO monitoring_log 
            (source, check_time, status, changes_detected, error_message)
            VALUES (?, ?, ?, ?, ?)
        ''', (source, datetime.now().isoformat(), status, changes, None))
        
        conn.commit()
        conn.close()
    
    async def _log_monitoring_error(self, source: str, error: str):
        """Log monitoring error to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO monitoring_log 
            (source, check_time, status, changes_detected, error_message)
            VALUES (?, ?, ?, ?, ?)
        ''', (source, datetime.now().isoformat(), "error", 0, error))
        
        conn.commit()
        conn.close()
    
    async def _notify_changes(self, source_key: str, changes_count: int):
        """Notify about detected changes"""
        config = self.trusted_sources[source_key]
        logger.info(f"ALERT: {changes_count} new updates from {config['name']}")
        
        # Here you could integrate with notification systems:
        # - Send email alerts
        # - Post to Slack/Teams
        # - Update dashboard
        # - Trigger compliance engine updates
    
    async def _alert_critical_issue(self, source_key: str, issue: str):
        """Alert about critical issues with sources"""
        config = self.trusted_sources[source_key]
        logger.critical(f"CRITICAL: Issue with {config['name']}: {issue}")
        
        # Critical alerts could trigger:
        # - Immediate notifications
        # - Fallback data sources
        # - System health warnings
    
    def get_latest_updates(self, source_key: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get latest regulatory updates"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if source_key:
            cursor.execute('''
                SELECT * FROM regulations 
                WHERE regulator_id = ? 
                ORDER BY last_modified DESC 
                LIMIT ?
            ''', (source_key, limit))
        else:
            cursor.execute('''
                SELECT * FROM regulations 
                ORDER BY last_modified DESC 
                LIMIT ?
            ''', (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get monitoring system status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get last check times for each source
        cursor.execute('''
            SELECT source, MAX(check_time) as last_check, status, changes_detected
            FROM monitoring_log 
            GROUP BY source
            ORDER BY last_check DESC
        ''')
        
        status_data = {}
        for row in cursor.fetchall():
            source, last_check, status, changes = row
            status_data[source] = {
                "last_check": last_check,
                "status": status,
                "recent_changes": changes
            }
        
        # Get total counts
        cursor.execute('SELECT COUNT(*) FROM regulators')
        total_regulators = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM regulations')
        total_regulations = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM audit_firms')
        total_audit_firms = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "sources": status_data,
            "totals": {
                "regulators": total_regulators,
                "regulations": total_regulations,
                "audit_firms": total_audit_firms
            },
            "last_updated": datetime.now().isoformat()
        }
    
    async def force_update_all(self):
        """Force update all sources immediately"""
        logger.info("Force updating all regulatory sources...")
        
        for source_key in self.trusted_sources.keys():
            try:
                await self._monitor_source(source_key)
            except Exception as e:
                logger.error(f"Force update failed for {source_key}: {e}")
    
    async def close(self):
        """Close monitoring system"""
        if self.session:
            await self.session.close()
        logger.info("Regulatory monitoring system closed")

# Integration with existing compliance engine
class ComplianceEngineIntegration:
    """Integration with the live compliance engine"""
    
    def __init__(self, monitor: RegulatoryDataMonitor):
        self.monitor = monitor
    
    async def sync_regulatory_updates(self):
        """Sync latest regulatory updates with compliance engine"""
        updates = self.monitor.get_latest_updates(limit=100)
        
        # Update compliance rules based on new regulations
        for update in updates:
            await self._update_compliance_rules(update)
    
    async def _update_compliance_rules(self, regulation_update: Dict[str, Any]):
        """Update compliance rules based on regulatory changes"""
        # This would integrate with the existing compliance_validator.py
        # and live_compliance_engine.py to update rules automatically
        pass

# CLI interface for manual operations
async def main():
    """Main function for running the monitoring system"""
    monitor = RegulatoryDataMonitor()
    
    try:
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        logger.info("Shutting down monitoring system...")
    finally:
        await monitor.close()

if __name__ == "__main__":
    asyncio.run(main())
