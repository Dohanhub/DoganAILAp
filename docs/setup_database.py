#!/usr/bin/env python3
"""
Database Setup Script for DoganAI Compliance Kit
Initializes PostgreSQL database with tables and sample data
"""

import os
import sys
import psycopg2
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
import random

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/doganai_compliance")

def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Connect to default postgres database
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="postgres",
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname='doganai_compliance'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute("CREATE DATABASE doganai_compliance")
            print("✅ Database 'doganai_compliance' created successfully")
        else:
            print("✅ Database 'doganai_compliance' already exists")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False
    
    return True

def create_tables():
    """Create all necessary tables"""
    try:
        engine = create_engine(DATABASE_URL)
        
        # Create tables
        tables = [
            """
            CREATE TABLE IF NOT EXISTS organizations (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                sector VARCHAR(100) NOT NULL,
                country VARCHAR(100) DEFAULT 'Saudi Arabia',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS compliance_assessments (
                id SERIAL PRIMARY KEY,
                organization_id INTEGER REFERENCES organizations(id),
                framework VARCHAR(100) NOT NULL,
                score FLOAT NOT NULL,
                status VARCHAR(50) NOT NULL,
                assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                assessor VARCHAR(255),
                notes TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS controls (
                id SERIAL PRIMARY KEY,
                framework VARCHAR(100) NOT NULL,
                control_id VARCHAR(100) UNIQUE NOT NULL,
                description TEXT NOT NULL,
                category VARCHAR(100) NOT NULL,
                priority VARCHAR(50) NOT NULL,
                is_implemented BOOLEAN DEFAULT FALSE,
                implementation_date TIMESTAMP,
                evidence TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS risks (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                severity VARCHAR(50) NOT NULL,
                likelihood VARCHAR(50) NOT NULL,
                mitigation_plan TEXT,
                owner VARCHAR(255),
                identified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_date TIMESTAMP,
                status VARCHAR(50) DEFAULT 'open'
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                full_name VARCHAR(255),
                role VARCHAR(50) DEFAULT 'user',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        ]
        
        with engine.connect() as conn:
            for table_sql in tables:
                conn.execute(text(table_sql))
                conn.commit()
        
        print("✅ All tables created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def insert_sample_data():
    """Insert sample data for testing"""
    try:
        engine = create_engine(DATABASE_URL)
        
        # Sample organizations
        organizations = [
            ("Saudi National Bank", "Banking"),
            ("King Faisal Specialist Hospital", "Healthcare"),
            ("Saudi Telecom Company", "Technology"),
            ("Saudi Aramco", "Energy"),
            ("Ministry of Health", "Government")
        ]
        
        # Sample compliance frameworks
        frameworks = ["NCA", "SAMA", "PDPL", "ISO 27001", "NIST CSF"]
        
        with engine.connect() as conn:
            # Insert organizations
            for org_name, sector in organizations:
                conn.execute(text("""
                    INSERT INTO organizations (name, sector) 
                    VALUES (:name, :sector)
                    ON CONFLICT DO NOTHING
                """), {"name": org_name, "sector": sector})
            
            # Insert sample compliance assessments
            for org_id in range(1, 6):
                for framework in frameworks:
                    score = random.uniform(70, 95)
                    status = "Compliant" if score > 80 else "Non-Compliant"
                    
                    conn.execute(text("""
                        INSERT INTO compliance_assessments 
                        (organization_id, framework, score, status, assessor)
                        VALUES (:org_id, :framework, :score, :status, :assessor)
                    """), {
                        "org_id": org_id,
                        "framework": framework,
                        "score": round(score, 2),
                        "status": status,
                        "assessor": "Dogan AI System"
                    })
            
            # Insert sample controls
            controls = [
                ("NCA", "NCA-001", "Access Control Policy", "Access Control", "High"),
                ("NCA", "NCA-002", "Data Encryption", "Data Protection", "High"),
                ("SAMA", "SAMA-001", "Financial Data Security", "Data Security", "High"),
                ("PDPL", "PDPL-001", "Personal Data Consent", "Privacy", "High"),
                ("ISO 27001", "ISO-001", "Information Security Policy", "Policy", "High")
            ]
            
            for framework, control_id, description, category, priority in controls:
                conn.execute(text("""
                    INSERT INTO controls (framework, control_id, description, category, priority)
                    VALUES (:framework, :control_id, :description, :category, :priority)
                    ON CONFLICT DO NOTHING
                """), {
                    "framework": framework,
                    "control_id": control_id,
                    "description": description,
                    "category": category,
                    "priority": priority
                })
            
            conn.commit()
        
        print("✅ Sample data inserted successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error inserting sample data: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up DoganAI Compliance Kit Database...")
    
    # Step 1: Create database
    if not create_database():
        sys.exit(1)
    
    # Step 2: Create tables
    if not create_tables():
        sys.exit(1)
    
    # Step 3: Insert sample data
    if not insert_sample_data():
        sys.exit(1)
    
    print("🎉 Database setup completed successfully!")
    print("📊 You can now run the application with:")
    print("   streamlit run app.py")
    print("   python backend/server_complete.py")

if __name__ == "__main__":
    main()
