#!/usr/bin/env python3
"""
Start DoganAI with Scraped Data
Launch the continuous upload system using real scraped regulatory data
"""

import asyncio
import logging
import os
from datetime import datetime

# Set environment to use scraped data
os.environ['USE_SCRAPED_DATA'] = 'true'
os.environ['LOG_LEVEL'] = 'INFO'

async def main():
    """Start the system with scraped data"""
    
    print("🚀 Starting DoganAI with Real Scraped Regulatory Data")
    print("=" * 55)
    
    # Check if scraped data exists
    if not os.path.exists("regulatory_scraping_results.json"):
        print("❌ No scraped data found!")
        print("Run this first: python regulatory_web_scraper.py")
        return
    
    print("✅ Scraped data found")
    
    # Import and check scraped data
    try:
        from scraped_data_adapter import get_scraped_data_adapter
        
        adapter = get_scraped_data_adapter()
        summary = adapter.get_summary()
        
        if summary['status'] != 'ready':
            print(f"❌ Scraped data not ready: {summary.get('message')}")
            return
        
        print(f"📊 Data Summary:")
        print(f"   • Scan Time: {summary['scan_time']}")
        print(f"   • Total Records: {summary['total_records']}")
        print(f"   • Authorities: {list(summary['authorities'].keys())}")
        print(f"   • Data Packets: {summary['data_packets_available']}")
        
        for authority, count in summary['authorities'].items():
            print(f"     - {authority}: {count} records")
        
    except Exception as e:
        print(f"❌ Error checking scraped data: {e}")
        return
    
    print(f"\n🌍 Starting Continuous Upload System...")
    print("Using REAL regulatory data from scraped websites")
    print("No API keys required!")
    print()
    
    # Import and start the continuous upload system
    try:
        from continuous_database_upload_system import ContinuousUploadSystem
        
        # Create system with scraped data configuration
        config = {
            'USE_SCRAPED_DATA': True,
            'scraped_data_interval': 300,  # 5 minutes
            'log_level': 'INFO',
            'worker_count': 2,  # Fewer workers needed for scraped data
            'batch_size': 25,
            'max_queue_size': 500
        }
        
        system = ContinuousUploadSystem()
        
        # Override config to use scraped data
        system.config.update(config)
        
        # Initialize and start
        await system.initialize()
        
        print("✅ System initialized successfully")
        print("🔄 Starting data collection from scraped sources...")
        print("📊 Monitor metrics at: http://localhost:9091/metrics")
        print()
        print("Press Ctrl+C to stop")
        
        await system.start()
        
    except KeyboardInterrupt:
        print("\n⏹️ Stopping system...")
        await system.stop()
        print("✅ System stopped")
    except Exception as e:
        print(f"❌ System error: {e}")
        if 'system' in locals():
            await system.stop()

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    asyncio.run(main())
