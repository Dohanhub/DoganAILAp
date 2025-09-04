
'\nDeploy Real Sources\nStep 3: Deploy the system with real regulatory data sources\n'
import asyncio
import subprocess
import os
import json
import time
from datetime import datetime
from pathlib import Path

class RealSourcesDeployer():
    'Deploy system with real regulatory data sources'

    def __init__(self):
        self.deployment_status = {'deployment_time': datetime.now().isoformat(), 'web_scraping_deployed': False, 'database_deployed': False, 'hourly_maintenance_deployed': False, 'monitoring_deployed': False, 'data_sources_active': [], 'deployment_log': []}

    def log_step(self, step: str, status: str, details: str=''):
        'Log deployment step'
        log_entry = {'timestamp': datetime.now().isoformat(), 'step': step, 'status': status, 'details': details}
        self.deployment_status['deployment_log'].append(log_entry)
        status_icon = ('✅' if (status == 'success') else ('❌' if (status == 'failed') else '🔄'))
        print(f'{status_icon} {step}: {details}')

    async def deploy_web_scraping_system(self):
        'Deploy web scraping system for real data'
        print('\n🌐 Deploying Web Scraping System...')
        print(('-' * 40))
        try:
            if (not os.path.exists('regulatory_web_scraper.py')):
                self.log_step('Web Scraper Check', 'failed', 'regulatory_web_scraper.py not found')
                return False
            self.log_step('Web Scraping', 'running', 'Extracting fresh regulatory data...')
            from ingest.regulatory_web_scraper import RegulatoryWebScraper
            scraper = RegulatoryWebScraper()
            (await scraper.initialize())
            results = (await scraper.auto_connect_all())
            filename = scraper.save_results(results)
            (await scraper.close())
            if (results['accessible_sites'] > 0):
                self.log_step('Web Scraping', 'success', f"Scraped {results['accessible_sites']} authorities")
                self.deployment_status['web_scraping_deployed'] = True
                self.deployment_status['data_sources_active'].extend(list(results['scraped_data'].keys()))
                return True
            else:
                self.log_step('Web Scraping', 'failed', 'No accessible sites found')
                return False
        except Exception as e:
            self.log_step('Web Scraping', 'failed', f'Error: {str(e)}')
            return False

    async def deploy_database_system(self):
        'Deploy database system with real data'
        print('\n💾 Deploying Database System...')
        print(('-' * 35))
        try:
            self.log_step('Database Init', 'running', 'Initializing SQLite database...')
            from simple_database_start import main as init_database
            (await init_database())
            if os.path.exists('doganai_compliance.db'):
                import sqlite3
                conn = sqlite3.connect('doganai_compliance.db')
                compliance_count = conn.execute('SELECT COUNT(*) FROM compliance_uploads').fetchone()[0]
                ministry_count = conn.execute('SELECT COUNT(*) FROM ministry_data').fetchone()[0]
                total_records = (compliance_count + ministry_count)
                conn.close()
                if (total_records > 0):
                    self.log_step('Database Init', 'success', f'Database deployed with {total_records} records')
                    self.deployment_status['database_deployed'] = True
                    return True
                else:
                    self.log_step('Database Init', 'failed', 'Database empty after initialization')
                    return False
            else:
                self.log_step('Database Init', 'failed', 'Database file not created')
                return False
        except Exception as e:
            self.log_step('Database Init', 'failed', f'Error: {str(e)}')
            return False

    async def deploy_hourly_maintenance(self):
        'Deploy hourly maintenance system'
        print('\n⏰ Deploying Hourly Maintenance...')
        print(('-' * 35))
        try:
            if (not os.path.exists('hourly_data_maintenance.py')):
                self.log_step('Maintenance Check', 'failed', 'hourly_data_maintenance.py not found')
                return False
            self.log_step('Maintenance Test', 'running', 'Testing maintenance system...')
            from hourly_data_maintenance import HourlyDataMaintenance
            maintenance = HourlyDataMaintenance()
            if maintenance.init_database():
                status = maintenance.get_status()
                if (status['status'] != 'error'):
                    self.log_step('Maintenance Test', 'success', f'Maintenance system ready')
                    self.deployment_status['hourly_maintenance_deployed'] = True
                    return True
                else:
                    self.log_step('Maintenance Test', 'failed', f"Status error: {status.get('error', 'Unknown')}")
                    return False
            else:
                self.log_step('Maintenance Test', 'failed', 'Database initialization failed')
                return False
        except Exception as e:
            self.log_step('Maintenance Test', 'failed', f'Error: {str(e)}')
            return False

    def deploy_monitoring_system(self):
        'Deploy monitoring and health checks'
        print('\n📊 Deploying Monitoring System...')
        print(('-' * 35))
        try:
            self.log_step('Monitoring Setup', 'running', 'Creating monitoring scripts...')
            status_script = '#!/usr/bin/env python3\nimport sqlite3\nimport os\nimport json\nfrom datetime import datetime\n\ndef get_system_status():\n    status = {\n        "timestamp": datetime.now().isoformat(),\n        "database": {"status": "unknown", "records": 0},\n        "scraped_data": {"status": "unknown", "authorities": 0},\n        "maintenance": {"status": "unknown"}\n    }\n    \n    # Check database\n    if os.path.exists("doganai_compliance.db"):\n        try:\n            conn = sqlite3.connect("doganai_compliance.db")\n            compliance_count = conn.execute("SELECT COUNT(*) FROM compliance_uploads").fetchone()[0]\n            ministry_count = conn.execute("SELECT COUNT(*) FROM ministry_data").fetchone()[0]\n            total_records = compliance_count + ministry_count\n            conn.close()\n            \n            status["database"] = {"status": "operational", "records": total_records}\n        except Exception as e:\n            status["database"] = {"status": "error", "error": str(e)}\n    \n    # Check scraped data\n    if os.path.exists("regulatory_scraping_results.json"):\n        try:\n            with open("regulatory_scraping_results.json", \'r\') as f:\n                data = json.load(f)\n            \n            authorities = len(data.get("scraped_data", {}))\n            status["scraped_data"] = {"status": "available", "authorities": authorities}\n        except Exception as e:\n            status["scraped_data"] = {"status": "error", "error": str(e)}\n    \n    # Check maintenance system\n    if os.path.exists("hourly_data_maintenance.py"):\n        status["maintenance"] = {"status": "available"}\n    \n    return status\n\nif __name__ == "__main__":\n    status = get_system_status()\n    print("System Status:", status["timestamp"])\n    print(f"Database: {status[\'database\'][\'status\']} ({status[\'database\'].get(\'records\', 0)} records)")\n    print(f"Scraped Data: {status[\'scraped_data\'][\'status\']} ({status[\'scraped_data\'].get(\'authorities\', 0)} authorities)")\n    print(f"Maintenance: {status[\'maintenance\'][\'status\']}")\n'
            with open('check_system_status.py', 'w') as f:
                f.write(status_script)
            health_script = '#!/usr/bin/env python3\nimport subprocess\nimport sys\n\ndef quick_health_check():\n    checks = [\n        ("Database", "doganai_compliance.db"),\n        ("Scraped Data", "regulatory_scraping_results.json"),\n        ("Maintenance", "hourly_data_maintenance.py"),\n        ("Web Scraper", "regulatory_web_scraper.py")\n    ]\n    \n    print("Quick Health Check")\n    print("=" * 20)\n    \n    healthy = 0\n    for name, file in checks:\n        import os\n        if os.path.exists(file):\n            print(f"✅ {name}: OK")\n            healthy += 1\n        else:\n            print(f"❌ {name}: Missing")\n    \n    print(f"\\nHealth Score: {healthy}/{len(checks)} ({healthy/len(checks)*100:.0f}%)")\n    return healthy == len(checks)\n\nif __name__ == "__main__":\n    healthy = quick_health_check()\n    sys.exit(0 if healthy else 1)\n'
            with open('quick_health_check.py', 'w') as f:
                f.write(health_script)
            result = subprocess.run(['python', 'quick_health_check.py'], capture_output=True, text=True)
            if (result.returncode == 0):
                self.log_step('Monitoring Setup', 'success', 'Monitoring scripts created and tested')
                self.deployment_status['monitoring_deployed'] = True
                return True
            else:
                self.log_step('Monitoring Setup', 'failed', f'Health check failed: {result.stdout}')
                return False
        except Exception as e:
            self.log_step('Monitoring Setup', 'failed', f'Error: {str(e)}')
            return False

    def create_deployment_summary(self):
        'Create deployment summary'
        summary = {'deployment_time': self.deployment_status['deployment_time'], 'deployment_successful': all([self.deployment_status['web_scraping_deployed'], self.deployment_status['database_deployed'], self.deployment_status['hourly_maintenance_deployed'], self.deployment_status['monitoring_deployed']]), 'components_deployed': {'web_scraping': self.deployment_status['web_scraping_deployed'], 'database': self.deployment_status['database_deployed'], 'hourly_maintenance': self.deployment_status['hourly_maintenance_deployed'], 'monitoring': self.deployment_status['monitoring_deployed']}, 'data_sources_active': self.deployment_status['data_sources_active'], 'next_steps': ['Monitor system operation', 'Check hourly maintenance logs', 'Verify data updates', 'Set up alerting (optional)']}
        with open('deployment_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        return summary

    async def run_full_deployment(self):
        'Run complete deployment process'
        print('🚀 DoganAI Real Sources Deployment')
        print(('=' * 40))
        print('Deploying system with real regulatory data sources')
        print()
        web_scraping_success = (await self.deploy_web_scraping_system())
        database_success = (await self.deploy_database_system())
        maintenance_success = (await self.deploy_hourly_maintenance())
        monitoring_success = self.deploy_monitoring_system()
        summary = self.create_deployment_summary()
        print(f'''
📊 Deployment Summary''')
        print(('=' * 25))
        print(f"Deployment Time: {summary['deployment_time']}")
        print(f"Overall Success: {('✅ YES' if summary['deployment_successful'] else '❌ NO')}")
        print(f'''
Components Deployed:''')
        for (component, deployed) in summary['components_deployed'].items():
            status = ('✅' if deployed else '❌')
            print(f"  {status} {component.replace('_', ' ').title()}")
        if summary['data_sources_active']:
            print(f'''
Active Data Sources: {', '.join(summary['data_sources_active'])}''')
        print(f'''
💡 Next Steps:''')
        for step in summary['next_steps']:
            print(f'   • {step}')
        if summary['deployment_successful']:
            print(f'''
🎉 Deployment completed successfully!''')
            print('Real regulatory data sources are now active.')
            return True
        else:
            print(f'''
⚠️ Deployment completed with issues.''')
            print('Check the logs above for details.')
            return False

async def main():
    'Main deployment function'
    deployer = RealSourcesDeployer()
    success = (await deployer.run_full_deployment())
    if success:
        print(f'''
🚀 System is ready for Step 4: Monitor Operation''')
    else:
        print(f'''
🔧 Please resolve deployment issues before proceeding''')
if (__name__ == '__main__'):
    asyncio.run(main())
