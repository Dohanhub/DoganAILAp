"""
Audit Firm Tracking and Update System
Automated monitoring of SOCPA registry and audit firm changes
"""

import asyncio
import aiohttp
import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging
from bs4 import BeautifulSoup
import pandas as pd
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AuditFirmData:
    """Audit firm data structure"""
    id: str
    name: str
    socpa_license: str
    license_type: str
    status: str
    registration_date: str
    offices: List[str]
    partners: List[str]
    staff_count: int
    specializations: List[str]
    clients: List[str]
    revenue_range: str
    international_affiliation: str
    website: str
    contact_info: Dict[str, str]
    last_updated: str
    data_hash: str

class AuditFirmTracker:
    """Automated audit firm tracking system"""
    
    def __init__(self, db_path: str = "audit_firms.db"):
        self.db_path = db_path
        self.session = None
        self.socpa_sources = self._load_socpa_sources()
        self._init_database()
    
    def _load_socpa_sources(self) -> Dict[str, Any]:
        """Load SOCPA and audit firm data sources"""
        return {
            "socpa_registry": {
                "name": "SOCPA Licensed Firms Registry",
                "base_url": "https://socpa.org.sa",
                "endpoints": {
                    "firms_list": "/en/licensed-firms",
                    "firm_details": "/en/firm-details",
                    "search": "/en/search-firms"
                },
                "selectors": {
                    "firm_rows": ".firm-row, .license-row",
                    "firm_name": ".firm-name",
                    "license_number": ".license-number",
                    "status": ".status"
                }
            },
            "big4_sources": {
                "pwc": {
                    "name": "PricewaterhouseCoopers Saudi Arabia",
                    "website": "https://www.pwc.com/m1/en/about-us/office-locations-middle-east/saudi-arabia.html",
                    "careers_page": "/careers",
                    "news_page": "/news"
                },
                "ey": {
                    "name": "Ernst & Young Saudi Arabia",
                    "website": "https://www.ey.com/en_gl/locations/saudi-arabia",
                    "careers_page": "/careers",
                    "news_page": "/news"
                },
                "kpmg": {
                    "name": "KPMG Saudi Arabia",
                    "website": "https://kpmg.com/sa/en/home.html",
                    "careers_page": "/careers",
                    "news_page": "/insights"
                },
                "deloitte": {
                    "name": "Deloitte Saudi Arabia",
                    "website": "https://www.deloitte.com/middle-east/en/offices/middle-east-offices/riyadh.html",
                    "careers_page": "/careers",
                    "news_page": "/insights"
                }
            },
            "market_intelligence": {
                "linkedin": {
                    "company_search": "https://www.linkedin.com/company/search/",
                    "keywords": ["audit", "accounting", "saudi arabia", "riyadh", "jeddah"]
                },
                "business_directories": {
                    "saudi_business": "https://www.saudibusiness.directory/",
                    "yellow_pages": "https://www.yellowpages.com.sa/"
                }
            }
        }
    
    def _init_database(self):
        """Initialize database for audit firm tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Audit firms table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_firms (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                socpa_license TEXT,
                license_type TEXT,
                status TEXT,
                registration_date TEXT,
                offices TEXT,
                partners TEXT,
                staff_count INTEGER,
                specializations TEXT,
                clients TEXT,
                revenue_range TEXT,
                international_affiliation TEXT,
                website TEXT,
                contact_info TEXT,
                last_updated TEXT,
                data_hash TEXT
            )
        ''')
        
        # Firm changes tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS firm_changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                firm_id TEXT,
                change_type TEXT,
                old_value TEXT,
                new_value TEXT,
                change_date TEXT,
                source TEXT,
                FOREIGN KEY (firm_id) REFERENCES audit_firms (id)
            )
        ''')
        
        # Market intelligence
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_intelligence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                firm_id TEXT,
                data_type TEXT,
                data_source TEXT,
                content TEXT,
                collection_date TEXT,
                FOREIGN KEY (firm_id) REFERENCES audit_firms (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def start_tracking(self):
        """Start automated audit firm tracking"""
        logger.info("Starting audit firm tracking system...")
        
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'DoganAI-AuditTracker/1.0'}
        )
        
        # Initial data collection
        await self._collect_socpa_registry()
        await self._collect_big4_data()
        await self._collect_market_intelligence()
        
        # Schedule regular updates
        while True:
            try:
                # Daily SOCPA check
                await self._check_socpa_updates()
                
                # Weekly Big 4 updates
                if datetime.now().weekday() == 0:  # Monday
                    await self._collect_big4_data()
                
                # Monthly market intelligence
                if datetime.now().day == 1:  # First day of month
                    await self._collect_market_intelligence()
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"Tracking error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _collect_socpa_registry(self):
        """Collect data from SOCPA registry"""
        logger.info("Collecting SOCPA registry data...")
        
        try:
            socpa_config = self.socpa_sources["socpa_registry"]
            firms_url = f"{socpa_config['base_url']}{socpa_config['endpoints']['firms_list']}"
            
            async with self.session.get(firms_url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Parse firm listings
                    firm_rows = soup.select(socpa_config['selectors']['firm_rows'])
                    
                    for row in firm_rows:
                        firm_data = await self._parse_socpa_firm_row(row, socpa_config)
                        if firm_data:
                            await self._store_or_update_firm(firm_data)
                    
                    logger.info(f"Processed {len(firm_rows)} SOCPA firms")
        
        except Exception as e:
            logger.error(f"SOCPA collection error: {e}")
    
    async def _parse_socpa_firm_row(self, row, config: Dict[str, Any]) -> Optional[AuditFirmData]:
        """Parse individual SOCPA firm row"""
        try:
            name_elem = row.select_one(config['selectors']['firm_name'])
            license_elem = row.select_one(config['selectors']['license_number'])
            status_elem = row.select_one(config['selectors']['status'])
            
            if not name_elem:
                return None
            
            name = name_elem.get_text().strip()
            license_number = license_elem.get_text().strip() if license_elem else ""
            status = status_elem.get_text().strip() if status_elem else "active"
            
            # Generate unique ID
            firm_id = hashlib.md5(f"socpa:{name}:{license_number}".encode()).hexdigest()
            
            # Determine firm type and specializations
            firm_type, specializations = self._classify_firm(name)
            
            firm_data = AuditFirmData(
                id=firm_id,
                name=name,
                socpa_license=license_number,
                license_type=firm_type,
                status=status,
                registration_date="",
                offices=["Riyadh"],  # Default, will be updated with more data
                partners=[],
                staff_count=0,
                specializations=specializations,
                clients=[],
                revenue_range="",
                international_affiliation=self._detect_international_affiliation(name),
                website="",
                contact_info={},
                last_updated=datetime.now().isoformat(),
                data_hash=hashlib.md5(f"{name}:{license_number}:{status}".encode()).hexdigest()
            )
            
            return firm_data
            
        except Exception as e:
            logger.error(f"Error parsing SOCPA row: {e}")
            return None
    
    def _classify_firm(self, name: str) -> tuple[str, List[str]]:
        """Classify firm type and specializations based on name"""
        name_lower = name.lower()
        
        # Big 4 classification
        if any(big4 in name_lower for big4 in ['pwc', 'pricewaterhouse', 'ernst', 'young', 'kpmg', 'deloitte']):
            return "big4", ["audit", "tax", "advisory", "consulting"]
        
        # International networks
        international_networks = {
            'bdo': ["audit", "tax", "advisory"],
            'grant thornton': ["audit", "tax", "business advisory"],
            'rsm': ["audit", "tax", "consulting"],
            'crowe': ["audit", "tax", "risk advisory"],
            'baker tilly': ["audit", "tax", "advisory"],
            'nexia': ["audit", "tax", "business services"]
        }
        
        for network, specs in international_networks.items():
            if network in name_lower:
                return "international", specs
        
        # Local firms
        if any(keyword in name_lower for keyword in ['chartered', 'accountants', 'audit', 'cpa']):
            return "local", ["audit", "accounting"]
        
        return "local", ["general"]
    
    def _detect_international_affiliation(self, name: str) -> str:
        """Detect international network affiliation"""
        name_lower = name.lower()
        
        affiliations = {
            'pwc': 'PricewaterhouseCoopers International',
            'pricewaterhouse': 'PricewaterhouseCoopers International',
            'ernst': 'Ernst & Young Global',
            'young': 'Ernst & Young Global',
            'kpmg': 'KPMG International',
            'deloitte': 'Deloitte Touche Tohmatsu',
            'bdo': 'BDO International',
            'grant thornton': 'Grant Thornton International',
            'rsm': 'RSM International',
            'crowe': 'Crowe Global',
            'baker tilly': 'Baker Tilly International',
            'nexia': 'Nexia International'
        }
        
        for keyword, affiliation in affiliations.items():
            if keyword in name_lower:
                return affiliation
        
        return ""
    
    async def _collect_big4_data(self):
        """Collect detailed data from Big 4 firms"""
        logger.info("Collecting Big 4 firm data...")
        
        big4_config = self.socpa_sources["big4_sources"]
        
        for firm_key, firm_config in big4_config.items():
            try:
                await self._collect_firm_website_data(firm_key, firm_config)
            except Exception as e:
                logger.error(f"Error collecting {firm_key} data: {e}")
    
    async def _collect_firm_website_data(self, firm_key: str, config: Dict[str, Any]):
        """Collect data from individual firm website"""
        try:
            # Main website
            async with self.session.get(config["website"]) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract office information
                    offices = self._extract_offices(soup)
                    
                    # Extract staff information
                    staff_info = self._extract_staff_info(soup)
                    
                    # Extract services/specializations
                    services = self._extract_services(soup)
                    
                    # Update firm data
                    await self._update_big4_firm_data(firm_key, {
                        "offices": offices,
                        "staff_info": staff_info,
                        "services": services,
                        "website": config["website"]
                    })
            
            # Careers page for staff count estimates
            careers_url = f"{config['website']}{config['careers_page']}"
            await self._collect_careers_data(firm_key, careers_url)
            
        except Exception as e:
            logger.error(f"Website data collection error for {firm_key}: {e}")
    
    def _extract_offices(self, soup: BeautifulSoup) -> List[str]:
        """Extract office locations from website"""
        offices = []
        
        # Common selectors for office information
        office_selectors = [
            '.office-location', '.location', '.address',
            '[class*="office"]', '[class*="location"]'
        ]
        
        for selector in office_selectors:
            elements = soup.select(selector)
            for elem in elements:
                text = elem.get_text().strip()
                if any(city in text.lower() for city in ['riyadh', 'jeddah', 'khobar', 'dammam']):
                    offices.append(text)
        
        # Default Saudi offices if none found
        if not offices:
            offices = ["Riyadh", "Jeddah", "Al Khobar"]
        
        return list(set(offices))  # Remove duplicates
    
    def _extract_staff_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract staff information from website"""
        staff_info = {"estimated_count": 0, "hiring_indicators": []}
        
        # Look for staff count indicators
        text_content = soup.get_text().lower()
        
        # Search for numerical indicators
        import re
        numbers = re.findall(r'(\d+)\s*(?:employees|staff|professionals|people)', text_content)
        if numbers:
            staff_info["estimated_count"] = max(int(n) for n in numbers)
        
        # Look for hiring indicators
        hiring_keywords = ['hiring', 'careers', 'join us', 'opportunities', 'graduate program']
        for keyword in hiring_keywords:
            if keyword in text_content:
                staff_info["hiring_indicators"].append(keyword)
        
        return staff_info
    
    def _extract_services(self, soup: BeautifulSoup) -> List[str]:
        """Extract services/specializations from website"""
        services = []
        
        # Common service keywords
        service_keywords = [
            'audit', 'assurance', 'tax', 'advisory', 'consulting',
            'risk', 'compliance', 'forensic', 'valuation', 'deals',
            'digital', 'technology', 'cybersecurity', 'sustainability'
        ]
        
        text_content = soup.get_text().lower()
        
        for keyword in service_keywords:
            if keyword in text_content:
                services.append(keyword)
        
        return services
    
    async def _collect_careers_data(self, firm_key: str, careers_url: str):
        """Collect careers data for staff estimates"""
        try:
            async with self.session.get(careers_url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Count job postings as indicator of size/growth
                    job_postings = len(soup.select('.job-posting, .career-opportunity, .position'))
                    
                    # Store as market intelligence
                    await self._store_market_intelligence(firm_key, "careers_data", {
                        "job_postings_count": job_postings,
                        "collection_date": datetime.now().isoformat(),
                        "source_url": careers_url
                    })
        
        except Exception as e:
            logger.error(f"Careers data collection error for {firm_key}: {e}")
    
    async def _collect_market_intelligence(self):
        """Collect market intelligence from various sources"""
        logger.info("Collecting market intelligence...")
        
        # This would integrate with:
        # - LinkedIn company data
        # - Business directories
        # - News sources
        # - Financial reports
        
        # Placeholder for market intelligence collection
        pass
    
    async def _store_or_update_firm(self, firm_data: AuditFirmData):
        """Store or update firm data in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if firm exists
        cursor.execute('SELECT data_hash FROM audit_firms WHERE id = ?', (firm_data.id,))
        existing = cursor.fetchone()
        
        if existing:
            # Check if data has changed
            if existing[0] != firm_data.data_hash:
                # Update existing firm
                cursor.execute('''
                    UPDATE audit_firms SET
                    name=?, socpa_license=?, license_type=?, status=?,
                    registration_date=?, offices=?, partners=?, staff_count=?,
                    specializations=?, clients=?, revenue_range=?,
                    international_affiliation=?, website=?, contact_info=?,
                    last_updated=?, data_hash=?
                    WHERE id=?
                ''', (
                    firm_data.name, firm_data.socpa_license, firm_data.license_type,
                    firm_data.status, firm_data.registration_date,
                    json.dumps(firm_data.offices), json.dumps(firm_data.partners),
                    firm_data.staff_count, json.dumps(firm_data.specializations),
                    json.dumps(firm_data.clients), firm_data.revenue_range,
                    firm_data.international_affiliation, firm_data.website,
                    json.dumps(firm_data.contact_info), firm_data.last_updated,
                    firm_data.data_hash, firm_data.id
                ))
                
                # Log the change
                await self._log_firm_change(firm_data.id, "update", existing[0], firm_data.data_hash)
        else:
            # Insert new firm
            cursor.execute('''
                INSERT INTO audit_firms 
                (id, name, socpa_license, license_type, status, registration_date,
                 offices, partners, staff_count, specializations, clients,
                 revenue_range, international_affiliation, website, contact_info,
                 last_updated, data_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                firm_data.id, firm_data.name, firm_data.socpa_license,
                firm_data.license_type, firm_data.status, firm_data.registration_date,
                json.dumps(firm_data.offices), json.dumps(firm_data.partners),
                firm_data.staff_count, json.dumps(firm_data.specializations),
                json.dumps(firm_data.clients), firm_data.revenue_range,
                firm_data.international_affiliation, firm_data.website,
                json.dumps(firm_data.contact_info), firm_data.last_updated,
                firm_data.data_hash
            ))
            
            # Log as new firm
            await self._log_firm_change(firm_data.id, "new", "", firm_data.data_hash)
        
        conn.commit()
        conn.close()
    
    async def _log_firm_change(self, firm_id: str, change_type: str, old_value: str, new_value: str):
        """Log firm changes for tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO firm_changes 
            (firm_id, change_type, old_value, new_value, change_date, source)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (firm_id, change_type, old_value, new_value, datetime.now().isoformat(), "automated"))
        
        conn.commit()
        conn.close()
    
    async def _store_market_intelligence(self, firm_id: str, data_type: str, content: Dict[str, Any]):
        """Store market intelligence data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO market_intelligence 
            (firm_id, data_type, data_source, content, collection_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (firm_id, data_type, "website", json.dumps(content), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_all_firms(self) -> List[Dict[str, Any]]:
        """Get all tracked audit firms"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM audit_firms ORDER BY name')
        columns = [desc[0] for desc in cursor.description]
        firms = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return firms
    
    def get_firm_changes(self, firm_id: Optional[str] = None, days: int = 30) -> List[Dict[str, Any]]:
        """Get recent firm changes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        if firm_id:
            cursor.execute('''
                SELECT * FROM firm_changes 
                WHERE firm_id = ? AND change_date > ?
                ORDER BY change_date DESC
            ''', (firm_id, cutoff_date))
        else:
            cursor.execute('''
                SELECT * FROM firm_changes 
                WHERE change_date > ?
                ORDER BY change_date DESC
            ''', (cutoff_date,))
        
        columns = [desc[0] for desc in cursor.description]
        changes = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return changes
    
    async def close(self):
        """Close tracking system"""
        if self.session:
            await self.session.close()
        logger.info("Audit firm tracking system closed")

# CLI interface
async def main():
    """Main function for running audit firm tracker"""
    tracker = AuditFirmTracker()
    
    try:
        await tracker.start_tracking()
    except KeyboardInterrupt:
        logger.info("Shutting down audit firm tracker...")
    finally:
        await tracker.close()

if __name__ == "__main__":
    asyncio.run(main())
