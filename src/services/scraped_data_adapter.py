#!/usr/bin/env python3
"""
Scraped Data Adapter
Converts web-scraped regulatory data into the format expected by the upload system
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any
import logging

class ScrapedDataAdapter:
    """Adapts scraped regulatory data for the continuous upload system"""
    
    def __init__(self, scraped_data_file: str = "regulatory_scraping_results.json"):
        self.scraped_data_file = scraped_data_file
        self.scraped_data = None
        self._load_scraped_data()
    
    def _load_scraped_data(self):
        """Load scraped data from file"""
        try:
            with open(self.scraped_data_file, 'r', encoding='utf-8') as f:
                self.scraped_data = json.load(f)
            logging.info(f"Loaded scraped data from {self.scraped_data_file}")
        except Exception as e:
            logging.error(f"Failed to load scraped data: {e}")
            self.scraped_data = None
    
    def get_nca_compliance_data(self) -> List[Dict[str, Any]]:
        """Extract NCA compliance data in API format"""
        
        if not self.scraped_data or 'NCA' not in self.scraped_data.get('scraped_data', {}):
            return []
        
        nca_data = self.scraped_data['scraped_data']['NCA']
        compliance_records = []
        
        # Process compliance keywords from scraped data
        for source in nca_data.get('data_sources', []):
            extracted_data = source.get('extracted_data', [])
            
            for keyword_data in extracted_data:
                keyword, count = keyword_data.split('(') if '(' in keyword_data else (keyword_data, '1')
                count = int(count.rstrip(')')) if count.rstrip(')').isdigit() else 1
                
                compliance_record = {
                    'id': str(uuid.uuid4()),
                    'authority': 'NCA',
                    'company_id': f'NCA-{keyword.upper()}-{datetime.now().strftime("%Y%m%d")}',
                    'compliance_type': keyword,
                    'status': 'active' if count > 5 else 'monitoring',
                    'score': min(95, 60 + count * 3),  # Convert count to score
                    'last_updated': datetime.now(timezone.utc).isoformat(),
                    'source': 'web_scraping',
                    'endpoint': source.get('endpoint', '/unknown'),
                    'raw_count': count,
                    'details': {
                        'keyword': keyword,
                        'occurrences': count,
                        'page_title': source.get('title', 'Unknown'),
                        'extraction_method': 'website_scraping'
                    }
                }
                compliance_records.append(compliance_record)
        
        # Add compliance links data
        for link_info in nca_data.get('compliance_info', []):
            compliance_record = {
                'id': str(uuid.uuid4()),
                'authority': 'NCA',
                'company_id': f'NCA-LINK-{datetime.now().strftime("%Y%m%d")}',
                'compliance_type': 'compliance_link',
                'status': 'available',
                'score': 85,
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'source': 'web_scraping',
                'details': {
                    'title': link_info.get('text', 'Compliance Link'),
                    'url': link_info.get('link', ''),
                    'type': 'compliance_resource'
                }
            }
            compliance_records.append(compliance_record)
        
        return compliance_records
    
    def get_sama_financial_data(self) -> List[Dict[str, Any]]:
        """Extract SAMA financial indicators in API format"""
        
        if not self.scraped_data or 'SAMA' not in self.scraped_data.get('scraped_data', {}):
            return []
        
        sama_data = self.scraped_data['scraped_data']['SAMA']
        financial_records = []
        
        # Process financial indicators
        for indicator in sama_data.get('indicators', []):
            financial_record = {
                'id': str(uuid.uuid4()),
                'authority': 'SAMA',
                'indicator_type': indicator.get('type', 'unknown'),
                'value': float(indicator.get('value', 0)),
                'unit': indicator.get('unit', ''),
                'context': indicator.get('context', 'financial_indicator'),
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'source': 'web_scraping',
                'compliance_impact': 'medium' if indicator.get('type') == 'percentage' else 'low',
                'details': indicator
            }
            financial_records.append(financial_record)
        
        # Process regulations
        for regulation in sama_data.get('regulations', []):
            regulation_record = {
                'id': str(uuid.uuid4()),
                'authority': 'SAMA',
                'regulation_title': regulation.get('title', 'Banking Regulation'),
                'regulation_type': regulation.get('type', 'regulation'),
                'link': regulation.get('link', ''),
                'status': 'active',
                'compliance_level': 'critical',
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'source': 'web_scraping',
                'details': regulation
            }
            financial_records.append(regulation_record)
        
        return financial_records
    
    def get_moh_health_data(self) -> List[Dict[str, Any]]:
        """Extract MoH health standards in API format"""
        
        if not self.scraped_data or 'MoH' not in self.scraped_data.get('scraped_data', {}):
            return []
        
        moh_data = self.scraped_data['scraped_data']['MoH']
        health_records = []
        
        # Process health standards
        for standard in moh_data.get('standards', []):
            health_record = {
                'id': str(uuid.uuid4()),
                'authority': 'MoH',
                'standard_keyword': standard.get('keyword', 'health_standard'),
                'found': standard.get('found', False),
                'context': standard.get('context', 'health_standards'),
                'compliance_level': 'high' if standard.get('found') else 'low',
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'source': 'web_scraping',
                'details': standard
            }
            health_records.append(health_record)
        
        return health_records
    
    def get_all_compliance_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all scraped compliance data organized by authority"""
        
        return {
            'nca_compliance': self.get_nca_compliance_data(),
            'sama_financial': self.get_sama_financial_data(),
            'moh_health': self.get_moh_health_data()
        }
    
    def generate_data_packets(self) -> List[Dict[str, Any]]:
        """Generate data packets compatible with the continuous upload system"""
        
        data_packets = []
        all_data = self.get_all_compliance_data()
        
        for authority_type, records in all_data.items():
            for record in records:
                # Create data packet in the format expected by DataSynchronizer
                packet = {
                    'id': str(uuid.uuid4()),
                    'source': f"scraped_{authority_type}",
                    'destination': self._determine_destination(authority_type),
                    'data': record,
                    'priority': self._determine_priority(record.get('authority', 'unknown')),
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'checksum': '',  # Will be calculated by DataPacket
                    'metadata': {
                        'source_type': 'web_scraping',
                        'authority': record.get('authority', 'unknown'),
                        'extraction_time': self.scraped_data.get('scan_time') if self.scraped_data else datetime.now().isoformat()
                    }
                }
                data_packets.append(packet)
        
        return data_packets
    
    def _determine_destination(self, authority_type: str) -> str:
        """Determine upload destination based on authority type"""
        destination_map = {
            'nca_compliance': 'compliance_data',
            'sama_financial': 'ministry_data',  # SAMA is critical government authority
            'moh_health': 'compliance_data'
        }
        return destination_map.get(authority_type, 'data_uploads')
    
    def _determine_priority(self, authority: str) -> int:
        """Determine priority level based on authority"""
        priority_map = {
            'NCA': 1,   # Critical
            'SAMA': 1,  # Critical  
            'MoH': 2,   # High
            'CITC': 2,  # High
            'CMA': 2    # High
        }
        return priority_map.get(authority, 3)  # Default to normal
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of available scraped data"""
        
        if not self.scraped_data:
            return {'status': 'no_data', 'message': 'No scraped data available'}
        
        all_data = self.get_all_compliance_data()
        
        summary = {
            'status': 'ready',
            'scan_time': self.scraped_data.get('scan_time'),
            'authorities': {
                'NCA': len(all_data.get('nca_compliance', [])),
                'SAMA': len(all_data.get('sama_financial', [])),
                'MoH': len(all_data.get('moh_health', []))
            },
            'total_records': sum(len(records) for records in all_data.values()),
            'data_packets_available': len(self.generate_data_packets())
        }
        
        return summary

# Global adapter instance
scraped_adapter = ScrapedDataAdapter()

def get_scraped_data_adapter() -> ScrapedDataAdapter:
    """Get the global scraped data adapter"""
    return scraped_adapter
