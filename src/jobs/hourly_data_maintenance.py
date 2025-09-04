
'\nHourly Data Maintenance System\nMaintains data updates on hourly basis with integrity checks and official source validation\n'
import asyncio
import sqlite3
import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, Any
import logging
import os
from pathlib import Path

class HourlyDataMaintenance():
    'Hourly data maintenance with integrity and official source validation'

    def __init__(self, db_path: str='doganai_compliance.db'):
        self.db_path = db_path
        self.running = False
        self.last_update = None
        self.integrity_log = []
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler('hourly_maintenance.log'), logging.StreamHandler()])
        self.logger = logging.getLogger(__name__)

    def init_database(self):
        'Initialize SQLite database for data maintenance'
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("\n                CREATE TABLE IF NOT EXISTS regulatory_data (\n                    id TEXT PRIMARY KEY,\n                    authority TEXT NOT NULL,\n                    data_type TEXT NOT NULL,\n                    content TEXT NOT NULL,\n                    source_url TEXT,\n                    hash_value TEXT NOT NULL,\n                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n                    verification_status TEXT DEFAULT 'pending',\n                    hourly_cycle INTEGER DEFAULT 0\n                )\n            ")
            conn.execute('\n                CREATE TABLE IF NOT EXISTS integrity_audit (\n                    id INTEGER PRIMARY KEY AUTOINCREMENT,\n                    check_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n                    authority TEXT NOT NULL,\n                    records_checked INTEGER,\n                    integrity_issues INTEGER,\n                    data_hash TEXT,\n                    status TEXT,\n                    details TEXT\n                )\n            ')
            conn.execute('\n                CREATE TABLE IF NOT EXISTS hourly_updates (\n                    id INTEGER PRIMARY KEY AUTOINCREMENT,\n                    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n                    hour_cycle INTEGER,\n                    authorities_updated TEXT,\n                    total_records INTEGER,\n                    new_records INTEGER,\n                    updated_records INTEGER,\n                    status TEXT,\n                    duration_seconds REAL\n                )\n            ')
            conn.commit()
            conn.close()
            self.logger.info('Database initialized successfully')
            return True
        except Exception as e:
            self.logger.error(f'Database initialization failed: {e}')
            return False

    async def hourly_maintenance_cycle(self):
        'Run hourly maintenance cycle'
        cycle_start = time.time()
        hour_cycle = datetime.now().hour
        self.logger.info(f'🔄 Starting hourly maintenance cycle {hour_cycle}')
        try:
            (await self._update_scraped_data())
            integrity_results = (await self._verify_data_integrity())
            source_validation = (await self._validate_official_sources())
            (await self._clean_and_optimize())
            report = (await self._generate_hourly_report(hour_cycle, integrity_results, source_validation))
            cycle_duration = (time.time() - cycle_start)
            self._log_hourly_update(hour_cycle, report, cycle_duration, 'success')
            self.logger.info(f'✅ Hourly cycle {hour_cycle} completed in {cycle_duration:.2f}s')
            return report
        except Exception as e:
            cycle_duration = (time.time() - cycle_start)
            self.logger.error(f'❌ Hourly cycle {hour_cycle} failed: {e}')
            self._log_hourly_update(hour_cycle, {}, cycle_duration, 'failed')
            raise

    async def _update_scraped_data(self):
        'Update scraped regulatory data'
        self.logger.info('📊 Updating scraped regulatory data...')
        if self._should_refresh_scraped_data():
            self.logger.info('🌐 Refreshing scraped data from websites...')
            try:
                from ingest.regulatory_web_scraper import RegulatoryWebScraper
                scraper = RegulatoryWebScraper()
                (await scraper.initialize())
                results = (await scraper.auto_connect_all())
                scraper.save_results(results, 'regulatory_scraping_results.json')
                (await scraper.close())
                self.logger.info(f"✅ Scraped data refreshed: {results['accessible_sites']}/{results['total_sites']} sites")
            except Exception as e:
                self.logger.warning(f'⚠️ Scraped data refresh failed: {e}')
        (await self._store_scraped_data())

    def _should_refresh_scraped_data(self) -> bool:
        'Check if scraped data should be refreshed'
        scrape_file = 'regulatory_scraping_results.json'
        if (not os.path.exists(scrape_file)):
            return True
        file_age = (time.time() - os.path.getmtime(scrape_file))
        return (file_age > (4 * 3600))

    async def _store_scraped_data(self):
        'Store scraped data in local database'
        try:
            with open('regulatory_scraping_results.json', 'r', encoding='utf-8') as f:
                scraped_data = json.load(f)
            conn = sqlite3.connect(self.db_path)
            stored_count = 0
            for (authority, data) in scraped_data.get('scraped_data', {}).items():
                if ('error' in data):
                    continue
                data_str = json.dumps(data, sort_keys=True)
                data_hash = hashlib.sha256(data_str.encode()).hexdigest()
                record_id = f"{authority}_{datetime.now().strftime('%Y%m%d_%H')}"
                conn.execute('\n                    INSERT OR REPLACE INTO regulatory_data \n                    (id, authority, data_type, content, source_url, hash_value, hourly_cycle)\n                    VALUES (?, ?, ?, ?, ?, ?, ?)\n                ', (record_id, authority, 'scraped_compliance', data_str, data.get('base_url', ''), data_hash, datetime.now().hour))
                stored_count += 1
            conn.commit()
            conn.close()
            self.logger.info(f'💾 Stored {stored_count} authority data records')
        except Exception as e:
            self.logger.error(f'Failed to store scraped data: {e}')

    async def _verify_data_integrity(self) -> Dict[(str, Any)]:
        'Verify data integrity across all sources'
        self.logger.info('🔍 Verifying data integrity...')
        integrity_results = {'check_time': datetime.now().isoformat(), 'authorities_checked': 0, 'total_records': 0, 'integrity_issues': 0, 'authorities': {}}
        try:
            conn = sqlite3.connect(self.db_path)
            authorities = conn.execute('SELECT DISTINCT authority FROM regulatory_data').fetchall()
            for (authority,) in authorities:
                authority_check = (await self._check_authority_integrity(conn, authority))
                integrity_results['authorities'][authority] = authority_check
                integrity_results['authorities_checked'] += 1
                integrity_results['total_records'] += authority_check['records_checked']
                integrity_results['integrity_issues'] += authority_check['issues_found']
            conn.execute('\n                INSERT INTO integrity_audit \n                (authority, records_checked, integrity_issues, status, details)\n                VALUES (?, ?, ?, ?, ?)\n            ', ('ALL', integrity_results['total_records'], integrity_results['integrity_issues'], ('passed' if (integrity_results['integrity_issues'] == 0) else 'issues_found'), json.dumps(integrity_results)))
            conn.commit()
            conn.close()
            status = ('✅' if (integrity_results['integrity_issues'] == 0) else '⚠️')
            self.logger.info(f"{status} Integrity check: {integrity_results['integrity_issues']} issues in {integrity_results['total_records']} records")
        except Exception as e:
            self.logger.error(f'Integrity verification failed: {e}')
            integrity_results['error'] = str(e)
        return integrity_results

    async def _check_authority_integrity(self, conn, authority: str) -> Dict[(str, Any)]:
        'Check integrity for specific authority'
        try:
            records = conn.execute('SELECT id, content, hash_value FROM regulatory_data WHERE authority = ?', (authority,)).fetchall()
            issues_found = 0
            records_checked = len(records)
            for (record_id, content, stored_hash) in records:
                calculated_hash = hashlib.sha256(content.encode()).hexdigest()
                if (calculated_hash != stored_hash):
                    issues_found += 1
                    self.logger.warning(f'🔴 Hash mismatch for {authority} record {record_id}')
            return {'records_checked': records_checked, 'issues_found': issues_found, 'status': ('clean' if (issues_found == 0) else 'corrupted')}
        except Exception as e:
            return {'records_checked': 0, 'issues_found': 1, 'status': 'error', 'error': str(e)}

    async def _validate_official_sources(self) -> Dict[(str, Any)]:
        'Validate that data comes from official government sources'
        self.logger.info('🏛️ Validating official sources...')
        official_domains = {'NCA': ['nca.gov.sa'], 'SAMA': ['sama.gov.sa'], 'MoH': ['moh.gov.sa'], 'CITC': ['citc.gov.sa'], 'CMA': ['cma.org.sa']}
        validation_results = {'check_time': datetime.now().isoformat(), 'authorities_validated': 0, 'official_sources': 0, 'unofficial_sources': 0, 'validation_details': {}}
        try:
            conn = sqlite3.connect(self.db_path)
            for (authority, official_urls) in official_domains.items():
                records = conn.execute('SELECT source_url FROM regulatory_data WHERE authority = ?', (authority,)).fetchall()
                official_count = 0
                unofficial_count = 0
                for (source_url,) in records:
                    if (source_url and any(((domain in source_url) for domain in official_urls))):
                        official_count += 1
                    else:
                        unofficial_count += 1
                validation_results['validation_details'][authority] = {'official_sources': official_count, 'unofficial_sources': unofficial_count, 'total_records': len(records), 'validation_score': (((official_count / len(records)) * 100) if records else 0)}
                validation_results['authorities_validated'] += 1
                validation_results['official_sources'] += official_count
                validation_results['unofficial_sources'] += unofficial_count
            conn.close()
            overall_score = ((validation_results['official_sources'] / (validation_results['official_sources'] + validation_results['unofficial_sources'])) * 100)
            validation_results['overall_validation_score'] = round(overall_score, 1)
            status = ('✅' if (overall_score >= 95) else ('⚠️' if (overall_score >= 80) else '❌'))
            self.logger.info(f'{status} Source validation: {overall_score:.1f}% official sources')
        except Exception as e:
            self.logger.error(f'Source validation failed: {e}')
            validation_results['error'] = str(e)
        return validation_results

    async def _clean_and_optimize(self):
        'Clean old data and optimize database'
        self.logger.info('🧹 Cleaning and optimizing data...')
        try:
            conn = sqlite3.connect(self.db_path)
            cutoff_date = (datetime.now() - timedelta(days=7))
            deleted_count = conn.execute('DELETE FROM regulatory_data WHERE last_updated < ?', (cutoff_date.isoformat(),)).rowcount
            audit_cutoff = (datetime.now() - timedelta(days=30))
            audit_deleted = conn.execute('DELETE FROM integrity_audit WHERE check_time < ?', (audit_cutoff.isoformat(),)).rowcount
            conn.execute('VACUUM')
            conn.commit()
            conn.close()
            self.logger.info(f'🗑️ Cleaned {deleted_count} old records, {audit_deleted} old audits')
        except Exception as e:
            self.logger.error(f'Cleanup failed: {e}')

    async def _generate_hourly_report(self, hour_cycle: int, integrity_results: Dict, source_validation: Dict) -> Dict[(str, Any)]:
        'Generate hourly maintenance report'
        report = {'hour_cycle': hour_cycle, 'timestamp': datetime.now().isoformat(), 'integrity_check': integrity_results, 'source_validation': source_validation, 'maintenance_actions': {'data_refreshed': True, 'integrity_verified': True, 'sources_validated': True, 'cleanup_performed': True}}
        report_file = f"hourly_report_{datetime.now().strftime('%Y%m%d_%H')}.json"
        with open(f'reports/{report_file}', 'w') as f:
            json.dump(report, f, indent=2)
        return report

    def _log_hourly_update(self, hour_cycle: int, report: Dict, duration: float, status: str):
        'Log hourly update to database'
        try:
            conn = sqlite3.connect(self.db_path)
            authorities_updated = list(report.get('integrity_check', {}).get('authorities', {}).keys())
            total_records = report.get('integrity_check', {}).get('total_records', 0)
            conn.execute('\n                INSERT INTO hourly_updates \n                (hour_cycle, authorities_updated, total_records, new_records, \n                 updated_records, status, duration_seconds)\n                VALUES (?, ?, ?, ?, ?, ?, ?)\n            ', (hour_cycle, json.dumps(authorities_updated), total_records, 0, 0, status, duration))
            conn.commit()
            conn.close()
        except Exception as e:
            self.logger.error(f'Failed to log hourly update: {e}')

    async def start_hourly_maintenance(self):
        'Start continuous hourly maintenance'
        self.logger.info('🚀 Starting hourly data maintenance system')
        if (not self.init_database()):
            raise Exception('Database initialization failed')
        Path('reports').mkdir(exist_ok=True)
        self.running = True
        while self.running:
            try:
                now = datetime.now()
                next_hour = (now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1))
                sleep_seconds = (next_hour - now).total_seconds()
                if (sleep_seconds > 0):
                    self.logger.info(f'⏰ Next maintenance cycle in {(sleep_seconds / 60):.1f} minutes')
                    (await asyncio.sleep(sleep_seconds))
                (await self.hourly_maintenance_cycle())
            except KeyboardInterrupt:
                self.logger.info('⏹️ Maintenance system stopped by user')
                break
            except Exception as e:
                self.logger.error(f'Maintenance cycle error: {e}')
                (await asyncio.sleep(300))
        self.running = False
        self.logger.info('✅ Hourly maintenance system stopped')

    def stop(self):
        'Stop the maintenance system'
        self.running = False

    def get_status(self) -> Dict[(str, Any)]:
        'Get current maintenance system status'
        try:
            conn = sqlite3.connect(self.db_path)
            latest_update = conn.execute('SELECT * FROM hourly_updates ORDER BY update_time DESC LIMIT 1').fetchone()
            latest_integrity = conn.execute('SELECT * FROM integrity_audit ORDER BY check_time DESC LIMIT 1').fetchone()
            stats = conn.execute('\n                SELECT \n                    COUNT(*) as total_records,\n                    COUNT(DISTINCT authority) as authorities,\n                    MIN(last_updated) as oldest_data,\n                    MAX(last_updated) as newest_data\n                FROM regulatory_data\n            ').fetchone()
            conn.close()
            return {'status': ('running' if self.running else 'stopped'), 'latest_update': latest_update, 'latest_integrity_check': latest_integrity, 'data_statistics': {'total_records': (stats[0] if stats else 0), 'authorities': (stats[1] if stats else 0), 'oldest_data': (stats[2] if stats else None), 'newest_data': (stats[3] if stats else None)}, 'next_cycle': (datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(hours=1))}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}

async def main():
    'Main function'
    print('🔄 DoganAI Hourly Data Maintenance System')
    print(('=' * 45))
    print('Maintains regulatory data integrity on hourly basis')
    print('Validates official sources and ensures data quality')
    print()
    maintenance = HourlyDataMaintenance()
    try:
        (await maintenance.start_hourly_maintenance())
    except KeyboardInterrupt:
        print('\n⏹️ Stopping maintenance system...')
        maintenance.stop()
if (__name__ == '__main__'):
    asyncio.run(main())
