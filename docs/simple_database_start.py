#!/usr/bin/env python3
"""
Simple Database Start with SQLite
Start the system using SQLite instead of PostgreSQL for immediate operation
"""

import asyncio
import logging
import os
import sqlite3
from datetime import datetime

async def main():
    """Start system with SQLite database"""
    
    print("🚀 Starting DoganAI with SQLite Database")
    print("=" * 40)
    print("Using local SQLite instead of PostgreSQL for immediate operation")
    print()
    
    # Set environment to use SQLite
    os.environ['USE_SCRAPED_DATA'] = 'true'
    os.environ['USE_SQLITE'] = 'true'
    os.environ['DATABASE_URL'] = 'sqlite:///doganai_compliance.db'
    
    # Initialize SQLite database
    print("📊 Initializing SQLite database...")
    
    try:
        conn = sqlite3.connect('doganai_compliance.db')
        
        # Create essential tables
        conn.execute("""
            CREATE TABLE IF NOT EXISTS compliance_uploads (
                id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                data TEXT NOT NULL,
                priority INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                checksum TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ministry_data (
                id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                data TEXT NOT NULL,
                priority INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                checksum TEXT NOT NULL,
                classification TEXT DEFAULT 'unclassified',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS data_uploads (
                id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                destination TEXT NOT NULL,
                data TEXT NOT NULL,
                priority INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                checksum TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS upload_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                packet_id TEXT NOT NULL,
                source TEXT NOT NULL,
                destination TEXT NOT NULL,
                status TEXT NOT NULL,
                error_message TEXT,
                timestamp TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ SQLite database initialized")
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return
    
    # Check scraped data
    if not os.path.exists("regulatory_scraping_results.json"):
        print("❌ No scraped data found!")
        print("Run this first: python regulatory_web_scraper.py")
        return
    
    print("✅ Scraped data found")
    
    # Test scraped data adapter
    try:
        from scraped_data_adapter import get_scraped_data_adapter
        
        adapter = get_scraped_data_adapter()
        summary = adapter.get_summary()
        
        if summary['status'] != 'ready':
            print(f"❌ Scraped data not ready: {summary.get('message')}")
            return
        
        print(f"📊 Data Summary:")
        print(f"   • Total Records: {summary['total_records']}")
        print(f"   • Authorities: {list(summary['authorities'].keys())}")
        
        # Process and store scraped data in SQLite
        print("\n💾 Storing scraped data in SQLite...")
        
        data_packets = adapter.generate_data_packets()
        
        conn = sqlite3.connect('doganai_compliance.db')
        
        stored_count = 0
        for packet in data_packets:
            
            # Determine table based on destination
            if packet['destination'] == 'compliance_data':
                table = 'compliance_uploads'
            elif packet['destination'] == 'ministry_data':
                table = 'ministry_data'
            else:
                table = 'data_uploads'
            
            # Insert data
            if table == 'data_uploads':
                conn.execute(f"""
                    INSERT OR REPLACE INTO {table} 
                    (id, source, destination, data, priority, timestamp, checksum)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    packet['id'], packet['source'], packet['destination'],
                    str(packet['data']), packet['priority'], 
                    packet['timestamp'], 'scraped_data_hash'
                ))
            else:
                conn.execute(f"""
                    INSERT OR REPLACE INTO {table} 
                    (id, source, data, priority, timestamp, checksum)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    packet['id'], packet['source'], str(packet['data']),
                    packet['priority'], packet['timestamp'], 'scraped_data_hash'
                ))
            
            stored_count += 1
        
        conn.commit()
        conn.close()
        
        print(f"✅ Stored {stored_count} data packets in SQLite")
        
        # Show what's in the database
        print("\n📊 Database Contents:")
        conn = sqlite3.connect('doganai_compliance.db')
        
        for table in ['compliance_uploads', 'ministry_data', 'data_uploads']:
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"   • {table}: {count} records")
        
        conn.close()
        
        print(f"\n🎉 SUCCESS! DoganAI now has {summary['total_records']} real regulatory data records!")
        print("📊 Data is stored and ready for compliance monitoring")
        print("🌍 Real data from NCA, SAMA, and MoH authorities")
        
        # Show next steps
        print(f"\n💡 Next Steps:")
        print("• Query compliance data: python -c \"import sqlite3; conn=sqlite3.connect('doganai_compliance.db'); print('Records:', conn.execute('SELECT COUNT(*) FROM compliance_uploads').fetchone()[0])\"")
        print("• Start hourly maintenance: python hourly_data_maintenance.py")
        print("• Run compliance checks: python quick_demo.py")
        
    except Exception as e:
        print(f"❌ Error processing scraped data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
