#!/usr/bin/env python3
"""
Timezone Diagnostic Tool for DoganAI Compliance Kit
This script helps diagnose and fix the 5-hour delay issue.
"""

import os
import sys
from datetime import datetime, timezone
import pytz
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from engine.settings import settings
    from engine.database import get_db_service
    IMPORT_SUCCESS = True
except ImportError as e:
    print(f"Warning: Could not import project modules: {e}")
    IMPORT_SUCCESS = False

def check_system_timezone():
    """Check system timezone configuration"""
    print("=" * 60)
    print("SYSTEM TIMEZONE INFORMATION")
    print("=" * 60)
    
    # System timezone
    try:
        import time
        print(f"System timezone: {time.tzname}")
        print(f"System timezone offset: {time.timezone} seconds")
        print(f"DST active: {time.daylight}")
    except Exception as e:
        print(f"Error getting system timezone: {e}")
    
    # Python timezone
    local_tz = datetime.now().astimezone().tzinfo
    print(f"Python local timezone: {local_tz}")
    
    # UTC time
    utc_now = datetime.now(timezone.utc)
    local_now = datetime.now()
    
    print(f"UTC time: {utc_now}")
    print(f"Local time: {local_now}")
    print(f"Time difference: {local_now - utc_now.replace(tzinfo=None)}")

def check_environment_variables():
    """Check timezone-related environment variables"""
    print("\n" + "=" * 60)
    print("ENVIRONMENT VARIABLES")
    print("=" * 60)
    
    timezone_vars = [
        'APP_TIMEZONE', 'DISPLAY_TIMEZONE', 'POSTGRES_TIMEZONE',
        'FORCE_UTC_TIMESTAMPS', 'LOG_USE_UTC', 'CACHE_TTL',
        'TZ'  # System timezone variable
    ]
    
    for var in timezone_vars:
        value = os.getenv(var, "NOT SET")
        print(f"{var}: {value}")

def check_application_config():
    """Check application timezone configuration"""
    if not IMPORT_SUCCESS:
        print("\n" + "=" * 60)
        print("APPLICATION CONFIG: SKIPPED (Import failed)")
        print("=" * 60)
        return
    
    print("\n" + "=" * 60)
    print("APPLICATION CONFIGURATION")
    print("=" * 60)
    
    try:
        print(f"App timezone: {settings.timezone.application_timezone}")
        print(f"Display timezone: {settings.timezone.display_timezone}")
        print(f"Force UTC: {settings.timezone.force_utc}")
        print(f"Cache TTL: {settings.cache_ttl} seconds")
        
        # Test timezone objects
        app_tz = settings.timezone.get_application_tz()
        display_tz = settings.timezone.get_display_tz()
        
        print(f"App timezone object: {app_tz}")
        print(f"Display timezone object: {display_tz}")
        
        # Test time functions
        utc_time = settings.timezone.now_utc()
        local_time = settings.timezone.now_local()
        display_time = settings.timezone.to_display_timezone(utc_time)
        
        print(f"UTC time: {utc_time}")
        print(f"Local time: {local_time}")
        print(f"Display time: {display_time}")
        
        # Calculate offsets
        utc_offset = local_time.utcoffset()
        display_offset = display_time.utcoffset()
        
        print(f"UTC offset: {utc_offset}")
        print(f"Display offset: {display_offset}")
        
        if utc_offset:
            offset_hours = utc_offset.total_seconds() / 3600
            print(f"UTC offset in hours: {offset_hours}")
            
            if abs(offset_hours) == 5:
                print("??  WARNING: 5-hour offset detected! This might be causing your delay issue.")
        
        if display_offset:
            display_hours = display_offset.total_seconds() / 3600
            print(f"Display offset in hours: {display_hours}")
        
    except Exception as e:
        print(f"Error checking application config: {e}")

def check_database_timezone():
    """Check database timezone configuration"""
    if not IMPORT_SUCCESS:
        print("\n" + "=" * 60)
        print("DATABASE TIMEZONE: SKIPPED (Import failed)")
        print("=" * 60)
        return
    
    print("\n" + "=" * 60)
    print("DATABASE TIMEZONE")
    print("=" * 60)
    
    try:
        db_service = get_db_service()
        with db_service.get_session() as session:
            result = session.execute("SELECT NOW(), CURRENT_SETTING('timezone')")
            db_time, db_timezone = result.fetchone()
            
            print(f"Database time: {db_time}")
            print(f"Database timezone: {db_timezone}")
            print(f"Configured timezone: {settings.database.timezone}")
            
            if db_timezone != settings.database.timezone:
                print(f"??  WARNING: Database timezone ({db_timezone}) differs from config ({settings.database.timezone})")
            
            # Compare with system time
            system_time = datetime.now(timezone.utc)
            if db_time.tzinfo is None:
                db_time = db_time.replace(tzinfo=timezone.utc)
            
            time_diff = abs((db_time - system_time).total_seconds())
            print(f"Time difference with system: {time_diff} seconds")
            
            if time_diff > 300:  # More than 5 minutes
                print(f"??  WARNING: Large time difference detected: {time_diff} seconds")
                
    except Exception as e:
        print(f"Error checking database timezone: {e}")

def check_cache_timestamps():
    """Check cache timestamp handling"""
    if not IMPORT_SUCCESS:
        print("\n" + "=" * 60)
        print("CACHE TIMESTAMPS: SKIPPED (Import failed)")
        print("=" * 60)
        return
    
    print("\n" + "=" * 60)
    print("CACHE TIMESTAMP CHECK")
    print("=" * 60)
    
    try:
        from datetime import timedelta
        
        # Simulate cache operations
        current_time = settings.get_current_time()
        cache_ttl_minutes = settings.cache_ttl // 60
        expires_at = current_time + timedelta(minutes=cache_ttl_minutes)
        
        print(f"Current time: {current_time}")
        print(f"Cache TTL: {settings.cache_ttl} seconds ({cache_ttl_minutes} minutes)")
        print(f"Cache expires at: {expires_at}")
        
        # Check if cache would be considered expired
        time_diff = (expires_at - current_time).total_seconds()
        print(f"Time until expiry: {time_diff} seconds")
        
        if time_diff != settings.cache_ttl:
            print(f"??  WARNING: Cache TTL calculation inconsistency!")
            
    except Exception as e:
        print(f"Error checking cache timestamps: {e}")

def suggest_fixes():
    """Suggest fixes for common timezone issues"""
    print("\n" + "=" * 60)
    print("SUGGESTED FIXES")
    print("=" * 60)
    
    print("1. Update your .env file with these settings:")
    print("   FORCE_UTC_TIMESTAMPS=true")
    print("   APP_TIMEZONE=UTC")
    print("   DISPLAY_TIMEZONE=Asia/Riyadh")
    print("   POSTGRES_TIMEZONE=UTC")
    print("   LOG_USE_UTC=true")
    print("")
    print("2. Restart your application after updating .env")
    print("")
    print("3. Verify the fix by running:")
    print("   curl http://localhost:8000/health/detailed")
    print("")
    print("4. Check the timezone section in the health response")
    print("")
    print("5. If using Docker, ensure timezone is set in container:")
    print("   TZ=UTC")
    print("")
    print("For more details, see: .env.timezone-fix")

def main():
    """Run all diagnostic checks"""
    print("TIMEZONE DIAGNOSTIC TOOL")
    print("Checking for 5-hour delay issue...\n")
    
    check_system_timezone()
    check_environment_variables()
    check_application_config()
    check_database_timezone()
    check_cache_timestamps()
    suggest_fixes()
    
    print("\n" + "=" * 60)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()