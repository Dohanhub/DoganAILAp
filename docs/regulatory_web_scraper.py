#!/usr/bin/env python3
"""
Regulatory Website Auto-Connector & Data Scraper
Extracts public compliance data from regulatory authority websites
"""

import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from urllib.parse import urljoin, urlparse
import time

class RegulatoryWebScraper:
    """Auto-connect and scrape regulatory authority websites"""
    
    def __init__(self):
        self.session = None
        self.results = {}
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    async def initialize(self):
        """Initialize HTTP session"""
        timeout = aiohttp.ClientTimeout(total=30)
        connector = aiohttp.TCPConnector(limit=10)
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=timeout,
            connector=connector
        )
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
    
    async def ping_website(self, url: str, name: str) -> Dict[str, Any]:
        """Ping website and check accessibility"""
        try:
            start_time = time.time()
            async with self.session.get(url) as response:
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                
                return {
                    'name': name,
                    'url': url,
                    'status': 'online',
                    'status_code': response.status,
                    'response_time_ms': round(response_time, 2),
                    'content_type': response.headers.get('content-type', 'unknown'),
                    'server': response.headers.get('server', 'unknown'),
                    'accessible': response.status == 200
                }
        except Exception as e:
            return {
                'name': name,
                'url': url,
                'status': 'offline',
                'error': str(e),
                'accessible': False
            }
    
    async def scrape_nca_data(self) -> Dict[str, Any]:
        """Scrape NCA (National Commercial Authority) public data"""
        base_url = "https://nca.gov.sa"
        
        try:
            # Try different NCA endpoints
            endpoints = [
                "/en",  # English version
                "/ar",  # Arabic version
                "/services",
                "/companies",
                "/violations"
            ]
            
            scraped_data = {
                'authority': 'NCA',
                'base_url': base_url,
                'last_updated': datetime.now().isoformat(),
                'data_sources': [],
                'compliance_info': []
            }
            
            for endpoint in endpoints:
                url = urljoin(base_url, endpoint)
                try:
                    async with self.session.get(url) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, 'html.parser')
                            
                            # Extract relevant compliance information
                            data_source = {
                                'endpoint': endpoint,
                                'title': soup.title.string if soup.title else 'No title',
                                'extracted_data': self._extract_compliance_keywords(html)
                            }
                            scraped_data['data_sources'].append(data_source)
                            
                            # Look for specific compliance information
                            compliance_links = soup.find_all('a', href=True)
                            for link in compliance_links:
                                href = link.get('href', '')
                                text = link.get_text(strip=True)
                                if any(keyword in text.lower() for keyword in ['compliance', 'violation', 'license', 'registration']):
                                    scraped_data['compliance_info'].append({
                                        'text': text,
                                        'link': urljoin(base_url, href)
                                    })
                
                except Exception as e:
                    logging.warning(f"Failed to scrape NCA endpoint {endpoint}: {e}")
                
                # Rate limiting
                await asyncio.sleep(1)
            
            return scraped_data
            
        except Exception as e:
            return {
                'authority': 'NCA',
                'error': str(e),
                'status': 'failed'
            }
    
    async def scrape_sama_data(self) -> Dict[str, Any]:
        """Scrape SAMA (Saudi Arabian Monetary Authority) public data"""
        base_url = "https://sama.gov.sa"
        
        try:
            scraped_data = {
                'authority': 'SAMA',
                'base_url': base_url,
                'last_updated': datetime.now().isoformat(),
                'indicators': [],
                'regulations': [],
                'press_releases': []
            }
            
            # SAMA specific endpoints
            endpoints = [
                "/en-US",
                "/en-US/EconomicReports",
                "/en-US/News",
                "/en-US/BankingSupervision",
                "/en-US/Regulations"
            ]
            
            for endpoint in endpoints:
                url = urljoin(base_url, endpoint)
                try:
                    async with self.session.get(url) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, 'html.parser')
                            
                            # Extract financial indicators
                            indicators = self._extract_financial_indicators(html)
                            if indicators:
                                scraped_data['indicators'].extend(indicators)
                            
                            # Extract regulation information
                            regulations = self._extract_regulations(soup)
                            if regulations:
                                scraped_data['regulations'].extend(regulations)
                
                except Exception as e:
                    logging.warning(f"Failed to scrape SAMA endpoint {endpoint}: {e}")
                
                await asyncio.sleep(1)
            
            return scraped_data
            
        except Exception as e:
            return {
                'authority': 'SAMA',
                'error': str(e),
                'status': 'failed'
            }
    
    async def scrape_moh_data(self) -> Dict[str, Any]:
        """Scrape MoH (Ministry of Health) public data"""
        base_url = "https://moh.gov.sa"
        
        try:
            scraped_data = {
                'authority': 'MoH',
                'base_url': base_url,
                'last_updated': datetime.now().isoformat(),
                'facilities': [],
                'standards': [],
                'announcements': []
            }
            
            endpoints = [
                "/en",
                "/en/Ministry",
                "/en/HealthAwareness",
                "/en/Sectors"
            ]
            
            for endpoint in endpoints:
                url = urljoin(base_url, endpoint)
                try:
                    async with self.session.get(url) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, 'html.parser')
                            
                            # Extract healthcare standards
                            standards = self._extract_health_standards(soup)
                            if standards:
                                scraped_data['standards'].extend(standards)
                
                except Exception as e:
                    logging.warning(f"Failed to scrape MoH endpoint {endpoint}: {e}")
                
                await asyncio.sleep(1)
            
            return scraped_data
            
        except Exception as e:
            return {
                'authority': 'MoH',
                'error': str(e),
                'status': 'failed'
            }
    
    def _extract_compliance_keywords(self, html: str) -> List[str]:
        """Extract compliance-related keywords from HTML"""
        keywords = [
            'compliance', 'violation', 'license', 'registration', 'permit',
            'regulation', 'standard', 'requirement', 'audit', 'inspection'
        ]
        
        found_keywords = []
        html_lower = html.lower()
        
        for keyword in keywords:
            if keyword in html_lower:
                # Count occurrences
                count = html_lower.count(keyword)
                found_keywords.append(f"{keyword}({count})")
        
        return found_keywords
    
    def _extract_financial_indicators(self, html: str) -> List[Dict[str, Any]]:
        """Extract financial indicators from SAMA pages"""
        indicators = []
        
        # Look for percentage patterns (interest rates, inflation, etc.)
        percentage_pattern = r'(\d+\.?\d*)\s*%'
        percentages = re.findall(percentage_pattern, html)
        
        # Look for currency amounts
        currency_pattern = r'SAR\s*([\d,]+\.?\d*)|(\d+\.?\d*)\s*billion'
        currencies = re.findall(currency_pattern, html)
        
        for i, percentage in enumerate(percentages[:5]):  # Limit to 5
            indicators.append({
                'type': 'percentage',
                'value': percentage,
                'unit': '%',
                'context': f'indicator_{i+1}'
            })
        
        return indicators
    
    def _extract_regulations(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract regulation information from soup"""
        regulations = []
        
        # Look for regulation-related links
        links = soup.find_all('a', href=True)
        
        for link in links:
            text = link.get_text(strip=True)
            href = link.get('href', '')
            
            if any(keyword in text.lower() for keyword in ['regulation', 'circular', 'instruction', 'guideline']):
                regulations.append({
                    'title': text,
                    'link': href,
                    'type': 'regulation'
                })
        
        return regulations[:10]  # Limit to 10
    
    def _extract_health_standards(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract health standards from MoH pages"""
        standards = []
        
        # Look for standard-related content
        text_content = soup.get_text()
        
        standard_keywords = ['iso', 'standard', 'accreditation', 'certification', 'quality']
        
        for keyword in standard_keywords:
            if keyword.lower() in text_content.lower():
                standards.append({
                    'keyword': keyword,
                    'found': True,
                    'context': 'health_standards'
                })
        
        return standards
    
    async def auto_connect_all(self) -> Dict[str, Any]:
        """Auto-connect to all regulatory websites and extract data"""
        
        print("🌍 Auto-Connecting to Regulatory Websites...")
        print("=" * 50)
        
        # Define all regulatory websites
        regulatory_sites = {
            'NCA': 'https://nca.gov.sa',
            'SAMA': 'https://sama.gov.sa',
            'MoH': 'https://moh.gov.sa',
            'CITC': 'https://citc.gov.sa',
            'CMA': 'https://cma.org.sa'
        }
        
        results = {
            'scan_time': datetime.now().isoformat(),
            'total_sites': len(regulatory_sites),
            'accessible_sites': 0,
            'failed_sites': 0,
            'connectivity': {},
            'scraped_data': {}
        }
        
        # Test connectivity first
        print("\n🔍 Testing Connectivity...")
        for name, url in regulatory_sites.items():
            ping_result = await self.ping_website(url, name)
            results['connectivity'][name] = ping_result
            
            if ping_result.get('accessible', False):
                results['accessible_sites'] += 1
                print(f"✅ {name}: Online ({ping_result.get('response_time_ms', 0):.0f}ms)")
            else:
                results['failed_sites'] += 1
                print(f"❌ {name}: Offline - {ping_result.get('error', 'Unknown error')}")
        
        # Scrape data from accessible sites
        print(f"\n📊 Scraping Data from {results['accessible_sites']} Accessible Sites...")
        
        scraping_tasks = []
        
        if results['connectivity']['NCA'].get('accessible', False):
            scraping_tasks.append(('NCA', self.scrape_nca_data()))
        
        if results['connectivity']['SAMA'].get('accessible', False):
            scraping_tasks.append(('SAMA', self.scrape_sama_data()))
        
        if results['connectivity']['MoH'].get('accessible', False):
            scraping_tasks.append(('MoH', self.scrape_moh_data()))
        
        # Execute scraping tasks
        for authority_name, task in scraping_tasks:
            try:
                print(f"🔍 Scraping {authority_name}...")
                scraped_result = await task
                results['scraped_data'][authority_name] = scraped_result
                
                if 'error' not in scraped_result:
                    print(f"✅ {authority_name}: Data extracted successfully")
                else:
                    print(f"⚠️ {authority_name}: Partial data extracted")
                    
            except Exception as e:
                print(f"❌ {authority_name}: Scraping failed - {e}")
                results['scraped_data'][authority_name] = {
                    'authority': authority_name,
                    'error': str(e),
                    'status': 'failed'
                }
        
        return results
    
    def save_results(self, results: Dict[str, Any], filename: str = "regulatory_scraping_results.json"):
        """Save scraping results to file"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to: {filename}")
        
        # Generate summary
        print(f"\n📋 Summary:")
        print(f"   Total Sites: {results['total_sites']}")
        print(f"   Accessible: {results['accessible_sites']}")
        print(f"   Data Sources: {len(results['scraped_data'])}")
        
        return filename

async def main():
    """Main scraping function"""
    
    print("🚀 DoganAI Regulatory Website Auto-Connector")
    print("Automatically pinging and scraping regulatory authority websites")
    print()
    
    scraper = RegulatoryWebScraper()
    
    try:
        await scraper.initialize()
        results = await scraper.auto_connect_all()
        filename = scraper.save_results(results)
        
        print(f"\n🎉 Auto-connection completed!")
        print(f"📊 Check {filename} for detailed results")
        print("\n💡 This provides fallback data while waiting for official API access")
        
    except Exception as e:
        print(f"❌ Auto-connection failed: {e}")
    finally:
        await scraper.close()

if __name__ == "__main__":
    asyncio.run(main())
