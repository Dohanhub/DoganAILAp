#!/usr/bin/env python3
"""
Database Data Validation Script
Checks current database state and validates transaction data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.database import get_db_service
from engine.models import *
from sqlalchemy import text
import traceback

def check_database_state():
    """Check current database state and validate data"""
    print("🔍 DoganAI Compliance Kit - Database Validation")
    print("=" * 50)
    
    try:
        # Get database service
        db = get_db_service()
        session = db.get_session()
        
        print("\n📊 Database Connection Status:")
        print("✅ Database connection established")
        
        # Check table existence and record counts
        models_to_check = [
            (EvaluationResult, "Evaluation Results"),
            (ComplianceReport, "Compliance Reports"),
            (Vendor, "Vendors"),
            (Policy, "Policies"),
            (Mapping, "Mappings"),
            (Benchmark, "Benchmarks"),
            (AuditLog, "Audit Logs"),
            (SystemMetrics, "System Metrics"),
            (UserSession, "User Sessions")
        ]
        
        print("\n📋 Table Record Counts:")
        total_records = 0
        
        for model, name in models_to_check:
            try:
                count = session.query(model).count()
                total_records += count
                status = "✅" if count > 0 else "⚠️"
                print(f"{status} {name}: {count} records")
            except Exception as e:
                print(f"❌ {name}: Error - {str(e)[:100]}...")
        
        print(f"\n📈 Total Records: {total_records}")
        
        # Check data integrity
        print("\n🔍 Data Integrity Checks:")
        
        # Check for evaluation results with valid compliance percentages
        try:
            invalid_compliance = session.query(EvaluationResult).filter(
                (EvaluationResult.compliance_percentage < 0) | 
                (EvaluationResult.compliance_percentage > 100)
            ).count()
            
            if invalid_compliance == 0:
                print("✅ All compliance percentages are valid (0-100%)")
            else:
                print(f"❌ Found {invalid_compliance} invalid compliance percentages")
        except Exception as e:
            print(f"⚠️ Could not check compliance percentages: {e}")
        
        # Check for evaluation results with negative evaluation times
        try:
            negative_times = session.query(EvaluationResult).filter(
                EvaluationResult.evaluation_time < 0
            ).count()
            
            if negative_times == 0:
                print("✅ All evaluation times are valid (>= 0)")
            else:
                print(f"❌ Found {negative_times} negative evaluation times")
        except Exception as e:
            print(f"⚠️ Could not check evaluation times: {e}")
        
        # Check for orphaned compliance reports
        try:
            orphaned_reports = session.query(ComplianceReport).filter(
                ~ComplianceReport.evaluation_id.in_(
                    session.query(EvaluationResult.id)
                )
            ).count()
            
            if orphaned_reports == 0:
                print("✅ No orphaned compliance reports found")
            else:
                print(f"❌ Found {orphaned_reports} orphaned compliance reports")
        except Exception as e:
            print(f"⚠️ Could not check orphaned reports: {e}")
        
        # Sample recent data
        print("\n📋 Recent Data Samples:")
        
        try:
            recent_evaluations = session.query(EvaluationResult).order_by(
                EvaluationResult.created_at.desc()
            ).limit(3).all()
            
            if recent_evaluations:
                print(f"\n🔍 Recent Evaluations ({len(recent_evaluations)}):")  
                for eval_result in recent_evaluations:
                    print(f"  • {eval_result.mapping} - {eval_result.compliance_percentage}% - {eval_result.status}")
            else:
                print("⚠️ No evaluation results found")
        except Exception as e:
            print(f"❌ Could not fetch recent evaluations: {e}")
        
        try:
            recent_reports = session.query(ComplianceReport).order_by(
                ComplianceReport.created_at.desc()
            ).limit(3).all()
            
            if recent_reports:
                print(f"\n📄 Recent Reports ({len(recent_reports)}):")  
                for report in recent_reports:
                    print(f"  • {report.format} - {report.status} - {report.created_at.strftime('%Y-%m-%d %H:%M')}")
            else:
                print("⚠️ No compliance reports found")
        except Exception as e:
            print(f"❌ Could not fetch recent reports: {e}")
        
        # Check database schema version
        print("\n🗄️ Database Schema Information:")
        try:
            # Check if tables exist
            result = session.execute(text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
            ))
            tables = [row[0] for row in result.fetchall()]
            print(f"✅ Found {len(tables)} tables in database")
            
            # List tables
            if tables:
                print("📋 Available tables:")
                for table in sorted(tables):
                    print(f"  • {table}")
        except Exception as e:
            print(f"❌ Could not check database schema: {e}")
        
        session.close()
        
        # Summary
        print("\n📊 Database Validation Summary:")
        if total_records > 0:
            print(f"✅ Database contains {total_records} total records")
            print("✅ Database is populated with transaction data")
        else:
            print("⚠️ Database appears to be empty or not properly seeded")
            print("💡 Consider running database seeding scripts")
        
        return total_records > 0
        
    except Exception as e:
        print(f"❌ Database validation failed: {e}")
        print(f"🔍 Error details: {traceback.format_exc()}")
        return False

def check_policy_data():
    """Check policy and compliance framework data"""
    print("\n🏛️ Policy and Compliance Framework Data:")
    
    try:
        db = get_db_service()
        session = db.get_session()
        
        # Check for policies
        policies = session.query(Policy).all()
        if policies:
            print(f"✅ Found {len(policies)} policies:")
            for policy in policies:
                print(f"  • {policy.name} ({policy.authority}) - v{policy.version}")
        else:
            print("⚠️ No policies found in database")
        
        # Check for vendors
        vendors = session.query(Vendor).all()
        if vendors:
            print(f"\n✅ Found {len(vendors)} vendors:")
            for vendor in vendors:
                print(f"  • {vendor.name} - Score: {vendor.overall_compliance_score or 'N/A'}")
        else:
            print("\n⚠️ No vendors found in database")
        
        # Check for benchmarks
        benchmarks = session.query(Benchmark).all()
        if benchmarks:
            print(f"\n✅ Found {len(benchmarks)} benchmarks:")
            for benchmark in benchmarks:
                print(f"  • {benchmark.name} ({benchmark.category})")
        else:
            print("\n⚠️ No benchmarks found in database")
        
        session.close()
        
    except Exception as e:
        print(f"❌ Policy data check failed: {e}")

def main():
    """Main validation function"""
    try:
        # Check database state
        has_data = check_database_state()
        
        # Check policy data
        check_policy_data()
        
        # Recommendations
        print("\n💡 Recommendations:")
        if not has_data:
            print("1. Run database initialization: python scripts/seed.sql")
            print("2. Execute data seeding: python scripts/seed_data.py")
            print("3. Verify API endpoints are working: curl http://localhost:8000/health")
        else:
            print("1. Database appears to be properly populated")
            print("2. Consider running data integrity tests regularly")
            print("3. Monitor transaction data for completeness")
        
        print("\n🎯 Next Steps:")
        print("• Verify all functional modules have complete data")
        print("• Run comprehensive data integrity tests")
        print("• Update seed scripts with verified data sources")
        print("• Document data validation procedures")
        
    except Exception as e:
        print(f"❌ Validation script failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()