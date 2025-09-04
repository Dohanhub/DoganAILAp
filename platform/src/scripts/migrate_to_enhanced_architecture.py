#!/usr/bin/env python3
"""
Data Migration Script for Enhanced Database Architecture
Migrates existing data from SQLite to PostgreSQL (TimescaleDB), Redis, and Elasticsearch
"""

import os
import sys
import json
import sqlite3
import psycopg2
import redis
from elasticsearch import Elasticsearch
from datetime import datetime
import logging
from typing import Dict, List

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedDatabaseMigrator:
    """Handles migration from SQLite to enhanced database architecture"""
    
    def __init__(self):
        self.sqlite_path = "doganai_compliance.db"
        self.migration_config = {
            'postgres': {
                'host': os.getenv('PGHOST', 'postgres-timescale'),
                'port': int(os.getenv('PGPORT', '5432')),
                'database': os.getenv('PGDATABASE', 'doganai_compliance'),
                'user': os.getenv('PGUSER', 'doganai'),
                'password': os.getenv('PGPASSWORD', 'DoganAI2024!')
            },
            'redis': {
                'host': os.getenv('REDIS_HOST', 'redis'),
                'port': int(os.getenv('REDIS_PORT', '6379')),
                'password': os.getenv('REDIS_PASSWORD'),
                'db': int(os.getenv('REDIS_DATABASE', '0'))
            },
            'elasticsearch': {
                'hosts': [f"{os.getenv('ELASTICSEARCH_HOST', 'elasticsearch')}:{os.getenv('ELASTICSEARCH_PORT', '9200')}"],
                'timeout': int(os.getenv('ELASTICSEARCH_TIMEOUT', '60')),
                'max_retries': int(os.getenv('ELASTICSEARCH_MAX_RETRIES', '5'))
            }
        }
        
        self.connections = {}
        self.migration_stats = {
            'tables_migrated': 0,
            'records_migrated': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }
    
    def connect_databases(self) -> bool:
        """Establish connections to all database systems"""
        try:
            logger.info("Connecting to database systems...")
            
            # Connect to PostgreSQL
            self.connections['postgres'] = psycopg2.connect(**self.migration_config['postgres'])
            logger.info("✓ Connected to PostgreSQL/TimescaleDB")
            
            # Connect to Redis
            redis_config = self.migration_config['redis'].copy()
            if not redis_config['password']:
                del redis_config['password']
            self.connections['redis'] = redis.Redis(**redis_config)
            self.connections['redis'].ping()
            logger.info("✓ Connected to Redis")
            
            # Connect to Elasticsearch
            self.connections['elasticsearch'] = Elasticsearch(**self.migration_config['elasticsearch'])
            if not self.connections['elasticsearch'].ping():
                raise Exception("Elasticsearch connection failed")
            logger.info("✓ Connected to Elasticsearch")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to databases: {e}")
            return False
    
    def get_sqlite_tables(self) -> List[str]:
        """Get list of tables from SQLite database"""
        try:
            conn = sqlite3.connect(self.sqlite_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall() if not row[0].startswith('sqlite_')]
            conn.close()
            return tables
        except Exception as e:
            logger.error(f"Failed to get SQLite tables: {e}")
            return []
    
    def create_postgres_tables(self) -> bool:
        """Create necessary tables in PostgreSQL"""
        try:
            cursor = self.connections['postgres'].cursor()
            
            # Create compliance data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS compliance_data (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    entity_id VARCHAR(255) NOT NULL,
                    compliance_type VARCHAR(100) NOT NULL,
                    status VARCHAR(50) NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    details JSONB DEFAULT '{}',
                    tags TEXT[],
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    modified_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    created_by VARCHAR(255),
                    modified_by VARCHAR(255)
                )
            """)
            
            # Create vendors table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vendors (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    vendor_id VARCHAR(255) UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    type VARCHAR(100),
                    status VARCHAR(50) DEFAULT 'active',
                    contact_info JSONB DEFAULT '{}',
                    compliance_info JSONB DEFAULT '{}',
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    modified_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create regulatory sources table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS regulatory_sources (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    source_id VARCHAR(255) UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    type VARCHAR(100),
                    url TEXT,
                    status VARCHAR(50) DEFAULT 'active',
                    last_updated TIMESTAMPTZ,
                    metadata JSONB DEFAULT '{}',
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    modified_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create audit logs table (if not exists from TimescaleDB init)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    table_name VARCHAR(255) NOT NULL,
                    operation VARCHAR(50) NOT NULL,
                    record_id UUID,
                    old_data JSONB,
                    new_data JSONB,
                    user_id VARCHAR(255),
                    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_compliance_entity_id ON compliance_data(entity_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_compliance_type ON compliance_data(compliance_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_compliance_status ON compliance_data(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_compliance_tags ON compliance_data USING GIN(tags)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_compliance_details ON compliance_data USING GIN(details)")
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_vendors_vendor_id ON vendors(vendor_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_vendors_status ON vendors(status)")
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_regulatory_sources_source_id ON regulatory_sources(source_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_regulatory_sources_status ON regulatory_sources(status)")
            
            self.connections['postgres'].commit()
            logger.info("✓ Created PostgreSQL tables and indexes")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create PostgreSQL tables: {e}")
            self.connections['postgres'].rollback()
            return False
    
    def setup_elasticsearch_indices(self) -> bool:
        """Set up Elasticsearch indices for search functionality"""
        try:
            es = self.connections['elasticsearch']
            
            # Compliance documents index
            compliance_mapping = {
                "mappings": {
                    "properties": {
                        "entity_id": {"type": "keyword"},
                        "compliance_type": {"type": "keyword"},
                        "status": {"type": "keyword"},
                        "title": {
                            "type": "text",
                            "analyzer": "standard",
                            "fields": {
                                "keyword": {"type": "keyword"}
                            }
                        },
                        "description": {
                            "type": "text",
                            "analyzer": "standard"
                        },
                        "details": {"type": "object"},
                        "tags": {"type": "keyword"},
                        "created_at": {"type": "date"},
                        "modified_at": {"type": "date"}
                    }
                },
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0,
                    "analysis": {
                        "analyzer": {
                            "compliance_analyzer": {
                                "type": "custom",
                                "tokenizer": "standard",
                                "filter": ["lowercase", "stop", "snowball"]
                            }
                        }
                    }
                }
            }
            
            if not es.indices.exists(index="compliance_documents"):
                es.indices.create(index="compliance_documents", body=compliance_mapping)
                logger.info("✓ Created compliance_documents index")
            
            # Vendors index
            vendors_mapping = {
                "mappings": {
                    "properties": {
                        "vendor_id": {"type": "keyword"},
                        "name": {
                            "type": "text",
                            "analyzer": "standard",
                            "fields": {
                                "keyword": {"type": "keyword"}
                            }
                        },
                        "type": {"type": "keyword"},
                        "status": {"type": "keyword"},
                        "contact_info": {"type": "object"},
                        "compliance_info": {"type": "object"},
                        "created_at": {"type": "date"},
                        "modified_at": {"type": "date"}
                    }
                },
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0
                }
            }
            
            if not es.indices.exists(index="vendors"):
                es.indices.create(index="vendors", body=vendors_mapping)
                logger.info("✓ Created vendors index")
            
            # Regulatory sources index
            sources_mapping = {
                "mappings": {
                    "properties": {
                        "source_id": {"type": "keyword"},
                        "name": {
                            "type": "text",
                            "analyzer": "standard",
                            "fields": {
                                "keyword": {"type": "keyword"}
                            }
                        },
                        "type": {"type": "keyword"},
                        "url": {"type": "keyword"},
                        "status": {"type": "keyword"},
                        "last_updated": {"type": "date"},
                        "metadata": {"type": "object"},
                        "created_at": {"type": "date"},
                        "modified_at": {"type": "date"}
                    }
                },
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0
                }
            }
            
            if not es.indices.exists(index="regulatory_sources"):
                es.indices.create(index="regulatory_sources", body=sources_mapping)
                logger.info("✓ Created regulatory_sources index")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup Elasticsearch indices: {e}")
            return False
    
    def migrate_table_data(self, table_name: str) -> bool:
        """Migrate data from SQLite table to enhanced databases"""
        try:
            logger.info(f"Migrating table: {table_name}")
            
            # Read data from SQLite
            sqlite_conn = sqlite3.connect(self.sqlite_path)
            sqlite_conn.row_factory = sqlite3.Row
            cursor = sqlite_conn.cursor()
            
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            if not rows:
                logger.info(f"No data found in table {table_name}")
                sqlite_conn.close()
                return True
            
            # Get column names
            columns = [description[0] for description in cursor.description]
            
            migrated_count = 0
            error_count = 0
            
            for row in rows:
                try:
                    row_dict = dict(row)
                    
                    # Migrate to PostgreSQL
                    if self.migrate_to_postgres(table_name, row_dict, columns):
                        # Migrate to Elasticsearch for searchable data
                        if table_name in ['compliance_data', 'vendors', 'regulatory_sources']:
                            self.migrate_to_elasticsearch(table_name, row_dict)
                        
                        # Cache frequently accessed data in Redis
                        if table_name in ['vendors', 'regulatory_sources']:
                            self.cache_in_redis(table_name, row_dict)
                        
                        migrated_count += 1
                    else:
                        error_count += 1
                        
                except Exception as e:
                    logger.error(f"Error migrating row in {table_name}: {e}")
                    error_count += 1
            
            sqlite_conn.close()
            
            logger.info(f"✓ Migrated {migrated_count} records from {table_name} (errors: {error_count})")
            self.migration_stats['records_migrated'] += migrated_count
            self.migration_stats['errors'] += error_count
            
            return error_count == 0
            
        except Exception as e:
            logger.error(f"Failed to migrate table {table_name}: {e}")
            return False
    
    def migrate_to_postgres(self, table_name: str, row_dict: Dict, columns: List[str]) -> bool:
        """Migrate a single row to PostgreSQL"""
        try:
            cursor = self.connections['postgres'].cursor()
            
            # Handle different table types
            if table_name == 'compliance_data':
                cursor.execute("""
                    INSERT INTO compliance_data (
                        entity_id, compliance_type, status, title, description, 
                        details, tags, created_at, modified_at, created_by, modified_by
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (
                    row_dict.get('entity_id'),
                    row_dict.get('compliance_type'),
                    row_dict.get('status'),
                    row_dict.get('title'),
                    row_dict.get('description'),
                    json.dumps(row_dict.get('details', {})),
                    row_dict.get('tags', []),
                    row_dict.get('created_at'),
                    row_dict.get('modified_at'),
                    row_dict.get('created_by'),
                    row_dict.get('modified_by')
                ))
            
            elif table_name == 'vendors':
                cursor.execute("""
                    INSERT INTO vendors (
                        vendor_id, name, type, status, contact_info, 
                        compliance_info, created_at, modified_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (vendor_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        type = EXCLUDED.type,
                        status = EXCLUDED.status,
                        contact_info = EXCLUDED.contact_info,
                        compliance_info = EXCLUDED.compliance_info,
                        modified_at = CURRENT_TIMESTAMP
                """, (
                    row_dict.get('vendor_id'),
                    row_dict.get('name'),
                    row_dict.get('type'),
                    row_dict.get('status'),
                    json.dumps(row_dict.get('contact_info', {})),
                    json.dumps(row_dict.get('compliance_info', {})),
                    row_dict.get('created_at'),
                    row_dict.get('modified_at')
                ))
            
            elif table_name == 'regulatory_sources':
                cursor.execute("""
                    INSERT INTO regulatory_sources (
                        source_id, name, type, url, status, 
                        last_updated, metadata, created_at, modified_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (source_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        type = EXCLUDED.type,
                        url = EXCLUDED.url,
                        status = EXCLUDED.status,
                        last_updated = EXCLUDED.last_updated,
                        metadata = EXCLUDED.metadata,
                        modified_at = CURRENT_TIMESTAMP
                """, (
                    row_dict.get('source_id'),
                    row_dict.get('name'),
                    row_dict.get('type'),
                    row_dict.get('url'),
                    row_dict.get('status'),
                    row_dict.get('last_updated'),
                    json.dumps(row_dict.get('metadata', {})),
                    row_dict.get('created_at'),
                    row_dict.get('modified_at')
                ))
            
            self.connections['postgres'].commit()
            return True
            
        except Exception as e:
            logger.error(f"Error migrating to PostgreSQL: {e}")
            self.connections['postgres'].rollback()
            return False
    
    def migrate_to_elasticsearch(self, table_name: str, row_dict: Dict) -> bool:
        """Migrate a single row to Elasticsearch"""
        try:
            es = self.connections['elasticsearch']
            
            # Prepare document for indexing
            doc = {
                'entity_id': row_dict.get('entity_id') or row_dict.get('vendor_id') or row_dict.get('source_id'),
                'title': row_dict.get('title') or row_dict.get('name'),
                'description': row_dict.get('description'),
                'status': row_dict.get('status'),
                'created_at': row_dict.get('created_at'),
                'modified_at': row_dict.get('modified_at')
            }
            
            # Add table-specific fields
            if table_name == 'compliance_data':
                doc.update({
                    'compliance_type': row_dict.get('compliance_type'),
                    'details': row_dict.get('details', {}),
                    'tags': row_dict.get('tags', [])
                })
                index_name = 'compliance_documents'
            
            elif table_name == 'vendors':
                doc.update({
                    'type': row_dict.get('type'),
                    'contact_info': row_dict.get('contact_info', {}),
                    'compliance_info': row_dict.get('compliance_info', {})
                })
                index_name = 'vendors'
            
            elif table_name == 'regulatory_sources':
                doc.update({
                    'type': row_dict.get('type'),
                    'url': row_dict.get('url'),
                    'last_updated': row_dict.get('last_updated'),
                    'metadata': row_dict.get('metadata', {})
                })
                index_name = 'regulatory_sources'
            
            # Index the document
            es.index(
                index=index_name,
                id=doc['entity_id'],
                body=doc
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error migrating to Elasticsearch: {e}")
            return False
    
    def cache_in_redis(self, table_name: str, row_dict: Dict) -> bool:
        """Cache frequently accessed data in Redis"""
        try:
            redis_conn = self.connections['redis']
            
            # Create cache key
            entity_id = row_dict.get('vendor_id') or row_dict.get('source_id')
            cache_key = f"{table_name}:{entity_id}"
            
            # Cache the data with TTL
            redis_conn.setex(
                cache_key,
                3600,  # 1 hour TTL
                json.dumps(row_dict)
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error caching in Redis: {e}")
            return False
    
    def run_migration(self) -> bool:
        """Run the complete migration process"""
        try:
            self.migration_stats['start_time'] = datetime.now()
            logger.info("Starting enhanced database migration...")
            
            # Step 1: Connect to databases
            if not self.connect_databases():
                return False
            
            # Step 2: Create PostgreSQL tables
            if not self.create_postgres_tables():
                return False
            
            # Step 3: Setup Elasticsearch indices
            if not self.setup_elasticsearch_indices():
                return False
            
            # Step 4: Get SQLite tables
            tables = self.get_sqlite_tables()
            if not tables:
                logger.warning("No tables found in SQLite database")
                return True
            
            # Step 5: Migrate each table
            for table in tables:
                if self.migrate_table_data(table):
                    self.migration_stats['tables_migrated'] += 1
                else:
                    logger.error(f"Failed to migrate table: {table}")
            
            # Step 6: Create migration summary
            self.migration_stats['end_time'] = datetime.now()
            self.create_migration_summary()
            
            logger.info("✓ Migration completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
        
        finally:
            # Close connections
            for conn_name, conn in self.connections.items():
                try:
                    if hasattr(conn, 'close'):
                        conn.close()
                except:
                    pass
    
    def create_migration_summary(self):
        """Create a summary of the migration process"""
        duration = self.migration_stats['end_time'] - self.migration_stats['start_time']
        
        summary = {
            'migration_date': self.migration_stats['end_time'].isoformat(),
            'duration_seconds': duration.total_seconds(),
            'tables_migrated': self.migration_stats['tables_migrated'],
            'records_migrated': self.migration_stats['records_migrated'],
            'errors': self.migration_stats['errors'],
            'success_rate': f"{((self.migration_stats['records_migrated'] - self.migration_stats['errors']) / max(1, self.migration_stats['records_migrated'])) * 100:.2f}%"
        }
        
        # Save summary to file
        with open('migration_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Migration Summary: {json.dumps(summary, indent=2)}")

def main():
    """Main migration function"""
    print("🚀 Enhanced Database Architecture Migration")
    print("=" * 50)
    
    migrator = EnhancedDatabaseMigrator()
    
    if migrator.run_migration():
        print("\n✅ Migration completed successfully!")
        print("📊 Check migration_summary.json for details")
        print("🔧 Next steps:")
        print("   1. Update your application configuration")
        print("   2. Test the new database connections")
        print("   3. Deploy the enhanced system")
        return 0
    else:
        print("\n❌ Migration failed!")
        print("📋 Check migration.log for details")
        return 1

if __name__ == "__main__":
    sys.exit(main())
