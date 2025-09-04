"""
Analytics Engine using DuckDB and Polars for high-performance data analysis
"""
import duckdb
import polars as pl
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import os

class AnalyticsEngine:
    def __init__(self, db_pool):
        self.db_pool = db_pool
        self.duckdb_conn = duckdb.connect(':memory:')
        self._setup_duckdb()
    
    def _setup_duckdb(self):
        """Setup DuckDB with PostgreSQL extension"""
        self.duckdb_conn.execute("INSTALL postgres")
        self.duckdb_conn.execute("LOAD postgres")
    
    async def sync_data_to_duckdb(self):
        """Sync data from PostgreSQL to DuckDB for analytics"""
        db_url = os.getenv("DATABASE_URL")
        
        # Extract connection parameters
        if db_url:
            # Parse PostgreSQL URL
            parts = db_url.replace("postgresql://", "").split("@")
            if len(parts) == 2:
                user_pass = parts[0].split(":")
                host_db = parts[1].split("/")
                
                # Create connection string for DuckDB
                conn_str = f"dbname={host_db[1]} user={user_pass[0]} password={user_pass[1]} host={host_db[0].split(':')[0]}"
                
                # Attach PostgreSQL database
                self.duckdb_conn.execute(f"""
                    ATTACH 'postgres:{conn_str}' AS pg (TYPE POSTGRES)
                """)
                
                # Create local copies of key tables for analytics
                tables = ['organizations', 'assessments', 'risks', 'frameworks', 'controls']
                for table in tables:
                    try:
                        self.duckdb_conn.execute(f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM pg.{table}")
                    except:
                        pass  # Table might not exist yet
    
    async def get_compliance_analytics(self, organization_id: Optional[int] = None) -> Dict:
        """Get comprehensive compliance analytics"""
        await self.sync_data_to_duckdb()
        
        # Overall compliance scores by framework
        framework_scores = self.duckdb_conn.execute("""
            SELECT 
                f.code,
                f.name,
                AVG(a.score) as avg_score,
                COUNT(a.id) as assessment_count,
                MAX(a.completed_at) as last_assessment
            FROM frameworks f
            LEFT JOIN assessments a ON f.id = a.framework_id
            WHERE a.score IS NOT NULL
            GROUP BY f.code, f.name
            ORDER BY avg_score DESC
        """).fetchall()
        
        # Compliance trends over time
        trends = self.duckdb_conn.execute("""
            SELECT 
                DATE_TRUNC('month', a.completed_at) as month,
                AVG(a.score) as avg_score,
                COUNT(*) as assessments
            FROM assessments a
            WHERE a.completed_at IS NOT NULL
            GROUP BY month
            ORDER BY month
        """).fetchall()
        
        # Risk analytics
        risk_stats = self.duckdb_conn.execute("""
            SELECT 
                category,
                severity,
                COUNT(*) as count,
                AVG(inherent_risk_score) as avg_risk_score
            FROM risks
            WHERE status = 'open'
            GROUP BY category, severity
            ORDER BY avg_risk_score DESC
        """).fetchall()
        
        return {
            'framework_scores': [
                {
                    'framework': row[0],
                    'name': row[1],
                    'average_score': float(row[2]) if row[2] else 0,
                    'assessments': row[3],
                    'last_assessment': row[4].isoformat() if row[4] else None
                }
                for row in framework_scores
            ],
            'compliance_trends': [
                {
                    'month': row[0].isoformat() if row[0] else None,
                    'average_score': float(row[1]) if row[1] else 0,
                    'assessment_count': row[2]
                }
                for row in trends
            ],
            'risk_distribution': [
                {
                    'category': row[0],
                    'severity': row[1],
                    'count': row[2],
                    'average_risk': float(row[3]) if row[3] else 0
                }
                for row in risk_stats
            ]
        }
    
    async def generate_compliance_matrix(self, organization_id: int) -> pl.DataFrame:
        """Generate compliance matrix using Polars"""
        async with self.db_pool.acquire() as conn:
            # Fetch assessment data
            assessments = await conn.fetch("""
                SELECT 
                    o.name as organization,
                    f.code as framework,
                    a.score,
                    a.completed_at
                FROM assessments a
                JOIN organizations o ON a.organization_id = o.id
                JOIN frameworks f ON a.framework_id = f.id
                WHERE o.id = $1
            """, organization_id)
            
            # Convert to Polars DataFrame
            if assessments:
                df = pl.DataFrame([dict(a) for a in assessments])
                
                # Pivot to create compliance matrix
                matrix = df.pivot(
                    values='score',
                    index='organization',
                    columns='framework',
                    aggregate_function='mean'
                )
                
                return matrix
            
            return pl.DataFrame()
    
    async def calculate_risk_exposure(self, organization_id: int) -> Dict:
        """Calculate total risk exposure for organization"""
        await self.sync_data_to_duckdb()
        
        # Calculate risk exposure by category
        exposure = self.duckdb_conn.execute("""
            SELECT 
                category,
                SUM(inherent_risk_score) as total_exposure,
                SUM(residual_risk_score) as residual_exposure,
                COUNT(*) as risk_count,
                AVG(inherent_risk_score - residual_risk_score) as avg_mitigation
            FROM risks
            WHERE organization_id = ?
            AND status = 'open'
            GROUP BY category
        """, [organization_id]).fetchall()
        
        # Calculate financial impact estimation
        financial_impact = self.duckdb_conn.execute("""
            SELECT 
                severity,
                COUNT(*) * 
                CASE 
                    WHEN severity = 'critical' THEN 1000000
                    WHEN severity = 'high' THEN 500000
                    WHEN severity = 'medium' THEN 100000
                    WHEN severity = 'low' THEN 10000
                    ELSE 1000
                END as estimated_impact
            FROM risks
            WHERE organization_id = ?
            AND status = 'open'
            GROUP BY severity
        """, [organization_id]).fetchall()
        
        total_exposure = sum(row[1] for row in exposure) if exposure else 0
        total_impact = sum(row[1] for row in financial_impact) if financial_impact else 0
        
        return {
            'total_risk_exposure': total_exposure,
            'estimated_financial_impact': total_impact,
            'risk_by_category': [
                {
                    'category': row[0],
                    'total_exposure': row[1],
                    'residual_exposure': row[2],
                    'risk_count': row[3],
                    'average_mitigation': float(row[4]) if row[4] else 0
                }
                for row in exposure
            ],
            'financial_impact_by_severity': [
                {
                    'severity': row[0],
                    'estimated_impact': row[1]
                }
                for row in financial_impact
            ]
        }
    
    async def get_maturity_assessment(self, organization_id: int) -> Dict:
        """Assess organization's compliance maturity"""
        await self.sync_data_to_duckdb()
        
        # Calculate maturity indicators
        maturity_data = self.duckdb_conn.execute("""
            SELECT 
                AVG(score) as avg_compliance_score,
                COUNT(DISTINCT framework_id) as frameworks_assessed,
                MAX(completed_at) as last_assessment_date
            FROM assessments
            WHERE organization_id = ?
            AND score IS NOT NULL
        """, [organization_id]).fetchone()
        
        if not maturity_data:
            return {'maturity_level': 1, 'message': 'No assessments found'}
        
        avg_score = maturity_data[0] or 0
        frameworks_count = maturity_data[1] or 0
        
        # Determine maturity level
        if avg_score >= 90 and frameworks_count >= 5:
            maturity_level = 5
            description = "Optimized - Continuous improvement culture"
        elif avg_score >= 75 and frameworks_count >= 4:
            maturity_level = 4
            description = "Managed - Proactive compliance management"
        elif avg_score >= 60 and frameworks_count >= 3:
            maturity_level = 3
            description = "Defined - Standardized processes"
        elif avg_score >= 40 and frameworks_count >= 2:
            maturity_level = 2
            description = "Repeatable - Basic processes established"
        else:
            maturity_level = 1
            description = "Initial - Ad-hoc compliance efforts"
        
        return {
            'maturity_level': maturity_level,
            'description': description,
            'average_compliance_score': round(avg_score, 2),
            'frameworks_assessed': frameworks_count,
            'last_assessment': maturity_data[2].isoformat() if maturity_data[2] else None,
            'recommendations': self._generate_maturity_recommendations(maturity_level)
        }
    
    def _generate_maturity_recommendations(self, level: int) -> List[str]:
        """Generate recommendations based on maturity level"""
        recommendations = {
            1: [
                "Establish formal compliance program",
                "Document compliance policies and procedures",
                "Conduct initial risk assessment"
            ],
            2: [
                "Standardize compliance processes",
                "Implement regular assessment schedule",
                "Develop metrics and KPIs"
            ],
            3: [
                "Automate compliance monitoring",
                "Integrate compliance into business processes",
                "Enhance risk management capabilities"
            ],
            4: [
                "Implement predictive analytics",
                "Optimize control effectiveness",
                "Develop advanced reporting capabilities"
            ],
            5: [
                "Focus on continuous improvement",
                "Share best practices across organization",
                "Lead industry compliance initiatives"
            ]
        }
        
        return recommendations.get(level, [])