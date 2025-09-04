#!/usr/bin/env python3
"""
Remove Duplicate Evaluations
Removes duplicate evaluation records and implements uniqueness constraints
"""

import sqlite3
from datetime import datetime

def remove_duplicate_evaluations():
    """Remove duplicate evaluations from database"""
    
    print("🔧 REMOVING DUPLICATE EVALUATIONS")
    print("="*40)
    
    conn = sqlite3.connect('doganai_compliance.db')
    cursor = conn.cursor()
    
    # Find duplicates
    cursor.execute('''
        SELECT mapping, vendor_id, COUNT(*) as duplicate_count, MIN(id) as keep_id
        FROM evaluation_results
        GROUP BY mapping, vendor_id
        HAVING COUNT(*) > 1
    ''')
    duplicates = cursor.fetchall()
    
    print(f"Found {len(duplicates)} sets of duplicates")
    
    total_removed = 0
    for mapping, vendor_id, count, keep_id in duplicates:
        # Delete all except the first one (keep_id)
        cursor.execute('''
            DELETE FROM evaluation_results 
            WHERE mapping = ? AND vendor_id = ? AND id != ?
        ''', (mapping, vendor_id, keep_id))
        
        removed = cursor.rowcount
        total_removed += removed
        print(f"   ✅ {mapping} + {vendor_id}: Removed {removed} duplicates, kept ID {keep_id}")
    
    # Create unique constraint to prevent future duplicates
    print("\n🔒 IMPLEMENTING UNIQUENESS CONSTRAINTS")
    
    try:
        # First, check if constraint already exists
        cursor.execute("PRAGMA table_info(evaluation_results)")
        columns = cursor.fetchall()
        
        # Create a new table with unique constraint
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evaluation_results_new (
                id TEXT PRIMARY KEY,
                mapping TEXT NOT NULL,
                vendor_id TEXT NOT NULL,
                compliance_percentage REAL,
                missing_items TEXT,
                remediation_status TEXT,
                last_evaluation DATE,
                evaluation_details TEXT,
                UNIQUE(mapping, vendor_id)
            )
        ''')
        
        # Copy data from old table
        cursor.execute('''
            INSERT OR IGNORE INTO evaluation_results_new 
            SELECT * FROM evaluation_results
        ''')
        
        # Drop old table and rename new one
        cursor.execute('DROP TABLE evaluation_results')
        cursor.execute('ALTER TABLE evaluation_results_new RENAME TO evaluation_results')
        
        print("   ✅ Uniqueness constraint implemented")
        
    except Exception as e:
        print(f"   ⚠️ Constraint implementation: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Removed {total_removed} duplicate evaluations")
    return total_removed

def verify_cleanup():
    """Verify that duplicates have been removed"""
    
    conn = sqlite3.connect('doganai_compliance.db')
    cursor = conn.cursor()
    
    # Check for remaining duplicates
    cursor.execute('''
        SELECT mapping, vendor_id, COUNT(*) as count
        FROM evaluation_results
        GROUP BY mapping, vendor_id
        HAVING COUNT(*) > 1
    ''')
    remaining_duplicates = cursor.fetchall()
    
    cursor.execute('SELECT COUNT(*) FROM evaluation_results')
    total_evaluations = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n📊 CLEANUP VERIFICATION:")
    print(f"   • Total evaluations: {total_evaluations}")
    print(f"   • Remaining duplicates: {len(remaining_duplicates)}")
    
    if len(remaining_duplicates) == 0:
        print("   ✅ All duplicates successfully removed")
    else:
        print("   ⚠️ Some duplicates still exist:")
        for mapping, vendor_id, count in remaining_duplicates:
            print(f"      • {mapping} + {vendor_id}: {count} records")
    
    return len(remaining_duplicates) == 0

def main():
    """Main function"""
    print("🚀 Database Duplicate Cleanup")
    print("="*35)
    print(f"Time: {datetime.now().isoformat()}")
    print()
    
    removed_count = remove_duplicate_evaluations()
    success = verify_cleanup()
    
    print(f"\n🎉 Cleanup {'completed successfully' if success else 'completed with issues'}!")
    print(f"📈 Removed {removed_count} duplicate records")
    
    return success

if __name__ == "__main__":
    main()
