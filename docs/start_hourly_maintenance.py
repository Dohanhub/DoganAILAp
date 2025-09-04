
'\nStart Hourly Data Maintenance\nQuick start script for hourly data maintenance with integrity checks\n'
import asyncio
import os
from pathlib import Path

async def main():
    'Start hourly maintenance system'
    print('🔄 Starting Hourly Data Maintenance System')
    print(('=' * 45))
    Path('reports').mkdir(exist_ok=True)
    if (not os.path.exists('regulatory_scraping_results.json')):
        print('⚠️ No scraped data found. Running web scraper first...')
        try:
            from ingest.regulatory_web_scraper import RegulatoryWebScraper
            scraper = RegulatoryWebScraper()
            (await scraper.initialize())
            results = (await scraper.auto_connect_all())
            scraper.save_results(results)
            (await scraper.close())
            print('✅ Fresh regulatory data scraped')
        except Exception as e:
            print(f'❌ Failed to scrape data: {e}')
            return
    if (not os.path.exists('doganai_compliance.db')):
        print('⚠️ No database found. Initializing...')
        try:
            from simple_database_start import main as init_db
            (await init_db())
            print('✅ Database initialized with scraped data')
        except Exception as e:
            print(f'❌ Database initialization failed: {e}')
            return
    print(f'''
🚀 Starting hourly maintenance with:''')
    print('   • Hourly data updates')
    print('   • Data integrity verification')
    print('   • Official source validation')
    print('   • Automated cleanup')
    print('   • Detailed reporting')
    print()
    print('Press Ctrl+C to stop')
    print()
    try:
        from hourly_data_maintenance import HourlyDataMaintenance
        maintenance = HourlyDataMaintenance()
        (await maintenance.start_hourly_maintenance())
    except KeyboardInterrupt:
        print('\n⏹️ Hourly maintenance stopped')
    except Exception as e:
        print(f'❌ Maintenance system error: {e}')
if (__name__ == '__main__'):
    asyncio.run(main())
