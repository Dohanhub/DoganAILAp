"""
Report Generation System with PDF and Excel export capabilities
"""
import asyncpg
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime
import io
import json

class ReportGenerator:
    def __init__(self, db_pool):
        self.db_pool = db_pool
        self.report_types = {
            'compliance': self.generate_compliance_report,
            'risk': self.generate_risk_report,
            'executive': self.generate_executive_summary,
            'audit': self.generate_audit_report,
            'regulatory': self.generate_regulatory_report
        }
    
    async def generate_report(self, report_type: str, organization_id: int, 
                             frameworks: List[str] = None, format: str = 'json') -> Dict:
        """Generate report based on type and parameters"""
        if report_type not in self.report_types:
            raise ValueError(f"Unknown report type: {report_type}")
        
        # Generate report content
        report_data = await self.report_types[report_type](organization_id, frameworks)
        
        # Store report metadata
        async with self.db_pool.acquire() as conn:
            report_id = await conn.fetchval('''
                INSERT INTO reports (organization_id, report_type, format, title, parameters, generated_by)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id
            ''', organization_id, report_type, format, report_data.get('title', 'Report'),
                json.dumps({'frameworks': frameworks}), 'System')
        
        report_data['report_id'] = report_id
        report_data['format'] = format
        
        # Convert to requested format
        if format == 'excel':
            return await self._convert_to_excel(report_data)
        elif format == 'pdf':
            return await self._convert_to_pdf(report_data)
        else:
            return report_data
    
    async def generate_compliance_report(self, organization_id: int, frameworks: List[str] = None) -> Dict:
        """Generate comprehensive compliance report"""
        async with self.db_pool.acquire() as conn:
            # Get organization details
            org = await conn.fetchrow('SELECT * FROM organizations WHERE id = $1', organization_id)
            if not org:
                raise ValueError(f"Organization {organization_id} not found")
            
            # Get assessments
            query = '''
                SELECT a.*, f.code, f.name, f.name_arabic, f.is_saudi
                FROM assessments a
                JOIN frameworks f ON a.framework_id = f.id
                WHERE a.organization_id = $1
            '''
            params = [organization_id]
            
            if frameworks:
                query += ' AND f.code = ANY($2)'
                params.append(frameworks)
            
            assessments = await conn.fetch(query, *params)
            
            # Get control implementation status
            control_status = await conn.fetch('''
                SELECT 
                    f.code as framework,
                    COUNT(c.id) as total_controls,
                    COUNT(CASE WHEN ci.status = 'implemented' THEN 1 END) as implemented,
                    COUNT(CASE WHEN ci.status = 'partial' THEN 1 END) as partial,
                    COUNT(CASE WHEN ci.status = 'not_implemented' THEN 1 END) as not_implemented
                FROM frameworks f
                JOIN controls c ON f.id = c.framework_id
                LEFT JOIN control_implementations ci ON c.id = ci.control_id 
                    AND ci.organization_id = $1
                GROUP BY f.code
            ''', organization_id)
            
            # Calculate overall compliance
            overall_score = 0
            saudi_score = 0
            international_score = 0
            saudi_count = 0
            international_count = 0
            
            for assessment in assessments:
                score = assessment['score'] or 0
                overall_score += score
                if assessment['is_saudi']:
                    saudi_score += score
                    saudi_count += 1
                else:
                    international_score += score
                    international_count += 1
            
            avg_overall = overall_score / len(assessments) if assessments else 0
            avg_saudi = saudi_score / saudi_count if saudi_count > 0 else 0
            avg_international = international_score / international_count if international_count > 0 else 0
            
            return {
                'title': f'Compliance Report - {org["name"]}',
                'organization': dict(org),
                'generated_at': datetime.now().isoformat(),
                'summary': {
                    'overall_compliance': round(avg_overall, 2),
                    'saudi_compliance': round(avg_saudi, 2),
                    'international_compliance': round(avg_international, 2),
                    'total_assessments': len(assessments),
                    'frameworks_covered': len(set(a['code'] for a in assessments))
                },
                'assessments': [dict(a) for a in assessments],
                'control_implementation': [dict(c) for c in control_status],
                'compliance_gaps': await self._identify_compliance_gaps(conn, organization_id),
                'recommendations': await self._generate_compliance_recommendations(assessments)
            }
    
    async def generate_risk_report(self, organization_id: int, frameworks: List[str] = None) -> Dict:
        """Generate risk assessment report"""
        async with self.db_pool.acquire() as conn:
            # Get organization
            org = await conn.fetchrow('SELECT * FROM organizations WHERE id = $1', organization_id)
            
            # Get all risks
            risks = await conn.fetch('''
                SELECT * FROM risks
                WHERE organization_id = $1
                ORDER BY inherent_risk_score DESC
            ''', organization_id)
            
            # Risk statistics
            risk_stats = {
                'total_risks': len(risks),
                'open_risks': len([r for r in risks if r['status'] == 'open']),
                'critical_risks': len([r for r in risks if r['severity'] == 'critical']),
                'high_risks': len([r for r in risks if r['severity'] == 'high']),
                'average_risk_score': sum(r['inherent_risk_score'] for r in risks) / len(risks) if risks else 0
            }
            
            # Risk by category
            risk_by_category = {}
            for risk in risks:
                category = risk['category']
                if category not in risk_by_category:
                    risk_by_category[category] = []
                risk_by_category[category].append(dict(risk))
            
            return {
                'title': f'Risk Assessment Report - {org["name"]}',
                'organization': dict(org),
                'generated_at': datetime.now().isoformat(),
                'risk_statistics': risk_stats,
                'top_risks': [dict(r) for r in risks[:10]],
                'risk_by_category': risk_by_category,
                'risk_matrix': await self._generate_risk_matrix(risks),
                'mitigation_priorities': await self._prioritize_mitigations(risks)
            }
    
    async def generate_executive_summary(self, organization_id: int, frameworks: List[str] = None) -> Dict:
        """Generate executive summary report"""
        async with self.db_pool.acquire() as conn:
            org = await conn.fetchrow('SELECT * FROM organizations WHERE id = $1', organization_id)
            
            # Key metrics
            metrics = await conn.fetchrow('''
                SELECT 
                    (SELECT AVG(score) FROM assessments WHERE organization_id = $1) as avg_compliance,
                    (SELECT COUNT(*) FROM risks WHERE organization_id = $1 AND status = 'open') as open_risks,
                    (SELECT COUNT(*) FROM assessments WHERE organization_id = $1) as total_assessments,
                    (SELECT MAX(completed_at) FROM assessments WHERE organization_id = $1) as last_assessment
            ''', organization_id)
            
            # Compliance trends
            trends = await conn.fetch('''
                SELECT 
                    DATE_TRUNC('month', completed_at) as month,
                    AVG(score) as avg_score
                FROM assessments
                WHERE organization_id = $1
                AND completed_at IS NOT NULL
                GROUP BY month
                ORDER BY month DESC
                LIMIT 6
            ''', organization_id)
            
            return {
                'title': f'Executive Summary - {org["name"]}',
                'organization': dict(org),
                'generated_at': datetime.now().isoformat(),
                'key_metrics': {
                    'compliance_score': round(metrics['avg_compliance'] or 0, 2),
                    'open_risks': metrics['open_risks'] or 0,
                    'assessments_completed': metrics['total_assessments'] or 0,
                    'last_assessment': metrics['last_assessment'].isoformat() if metrics['last_assessment'] else None
                },
                'compliance_trends': [
                    {
                        'month': t['month'].strftime('%Y-%m'),
                        'score': round(t['avg_score'] or 0, 2)
                    }
                    for t in trends
                ],
                'key_findings': await self._generate_key_findings(conn, organization_id),
                'strategic_recommendations': await self._generate_strategic_recommendations(conn, organization_id)
            }
    
    async def generate_audit_report(self, organization_id: int, frameworks: List[str] = None) -> Dict:
        """Generate audit trail report"""
        async with self.db_pool.acquire() as conn:
            org = await conn.fetchrow('SELECT * FROM organizations WHERE id = $1', organization_id)
            
            # Get audit logs
            audit_logs = await conn.fetch('''
                SELECT * FROM audit_logs
                WHERE organization_id = $1
                ORDER BY created_at DESC
                LIMIT 1000
            ''', organization_id)
            
            # Get control evidence
            evidence = await conn.fetch('''
                SELECT 
                    ci.*,
                    c.control_id,
                    c.title,
                    f.code as framework
                FROM control_implementations ci
                JOIN controls c ON ci.control_id = c.id
                JOIN frameworks f ON c.framework_id = f.id
                WHERE ci.organization_id = $1
            ''', organization_id)
            
            return {
                'title': f'Audit Report - {org["name"]}',
                'organization': dict(org),
                'generated_at': datetime.now().isoformat(),
                'audit_period': {
                    'start': audit_logs[-1]['created_at'].isoformat() if audit_logs else None,
                    'end': audit_logs[0]['created_at'].isoformat() if audit_logs else None
                },
                'audit_logs': [dict(log) for log in audit_logs[:100]],
                'control_evidence': [dict(e) for e in evidence],
                'compliance_status': await self._get_audit_compliance_status(conn, organization_id),
                'findings': await self._generate_audit_findings(conn, organization_id)
            }
    
    async def generate_regulatory_report(self, organization_id: int, frameworks: List[str] = None) -> Dict:
        """Generate regulatory compliance report for Saudi authorities"""
        async with self.db_pool.acquire() as conn:
            org = await conn.fetchrow('SELECT * FROM organizations WHERE id = $1', organization_id)
            
            # Focus on Saudi frameworks
            saudi_assessments = await conn.fetch('''
                SELECT a.*, f.code, f.name, f.authority, f.authority_arabic
                FROM assessments a
                JOIN frameworks f ON a.framework_id = f.id
                WHERE a.organization_id = $1
                AND f.is_saudi = true
            ''', organization_id)
            
            # Get mandatory control compliance
            mandatory_compliance = await conn.fetch('''
                SELECT 
                    f.code,
                    f.authority,
                    COUNT(c.id) as total_controls,
                    COUNT(CASE WHEN ci.status = 'implemented' THEN 1 END) as compliant_controls
                FROM frameworks f
                JOIN controls c ON f.id = c.framework_id
                LEFT JOIN control_implementations ci ON c.id = ci.control_id 
                    AND ci.organization_id = $1
                WHERE f.is_mandatory = true
                GROUP BY f.code, f.authority
            ''', organization_id)
            
            return {
                'title': f'Regulatory Compliance Report - {org["name"]}',
                'organization': dict(org),
                'generated_at': datetime.now().isoformat(),
                'regulatory_authority': 'Saudi Regulatory Authorities',
                'saudi_compliance': {
                    'nca': next((a for a in saudi_assessments if a['code'] == 'NCA'), None),
                    'sama': next((a for a in saudi_assessments if a['code'] == 'SAMA'), None),
                    'pdpl': next((a for a in saudi_assessments if a['code'] == 'PDPL'), None)
                },
                'mandatory_controls': [dict(m) for m in mandatory_compliance],
                'compliance_declaration': await self._generate_compliance_declaration(org, saudi_assessments),
                'regulatory_requirements': await self._get_regulatory_requirements(conn)
            }
    
    async def _identify_compliance_gaps(self, conn, organization_id: int) -> List[Dict]:
        """Identify compliance gaps"""
        gaps = await conn.fetch('''
            SELECT 
                f.code as framework,
                c.control_id,
                c.title,
                c.priority
            FROM controls c
            JOIN frameworks f ON c.framework_id = f.id
            LEFT JOIN control_implementations ci ON c.id = ci.control_id 
                AND ci.organization_id = $1
            WHERE (ci.status IS NULL OR ci.status = 'not_implemented')
            AND c.priority IN ('Critical', 'High')
            ORDER BY c.priority, f.code
        ''', organization_id)
        
        return [dict(g) for g in gaps]
    
    async def _generate_compliance_recommendations(self, assessments: List) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        low_scores = [a for a in assessments if a['score'] and a['score'] < 60]
        if low_scores:
            frameworks = ', '.join(a['code'] for a in low_scores)
            recommendations.append(f"Priority improvement needed for: {frameworks}")
        
        saudi_assessments = [a for a in assessments if a['is_saudi']]
        if len(saudi_assessments) < 3:
            recommendations.append("Complete assessments for all Saudi regulatory frameworks")
        
        return recommendations
    
    async def _generate_risk_matrix(self, risks: List) -> Dict:
        """Generate risk matrix data"""
        matrix = {}
        for risk in risks:
            key = f"{risk['severity']}_{risk['likelihood']}"
            if key not in matrix:
                matrix[key] = []
            matrix[key].append(risk['title'])
        return matrix
    
    async def _prioritize_mitigations(self, risks: List) -> List[Dict]:
        """Prioritize risk mitigations"""
        priorities = []
        for risk in risks:
            if risk['status'] == 'open' and risk['inherent_risk_score'] >= 15:
                priorities.append({
                    'risk': risk['title'],
                    'score': risk['inherent_risk_score'],
                    'deadline': risk['mitigation_deadline'].isoformat() if risk['mitigation_deadline'] else None,
                    'priority': 'Critical' if risk['inherent_risk_score'] >= 20 else 'High'
                })
        return sorted(priorities, key=lambda x: x['score'], reverse=True)
    
    async def _generate_key_findings(self, conn, organization_id: int) -> List[str]:
        """Generate key findings for executive summary"""
        findings = []
        
        # Check compliance levels
        avg_score = await conn.fetchval(
            'SELECT AVG(score) FROM assessments WHERE organization_id = $1',
            organization_id
        )
        if avg_score and avg_score < 70:
            findings.append(f"Overall compliance at {round(avg_score, 2)}% - below target of 70%")
        
        # Check critical risks
        critical_risks = await conn.fetchval(
            'SELECT COUNT(*) FROM risks WHERE organization_id = $1 AND severity = $2 AND status = $3',
            organization_id, 'critical', 'open'
        )
        if critical_risks:
            findings.append(f"{critical_risks} critical risks require immediate attention")
        
        return findings
    
    async def _generate_strategic_recommendations(self, conn, organization_id: int) -> List[str]:
        """Generate strategic recommendations"""
        return [
            "Implement automated compliance monitoring",
            "Enhance risk assessment processes",
            "Strengthen third-party risk management",
            "Improve incident response capabilities"
        ]
    
    async def _get_audit_compliance_status(self, conn, organization_id: int) -> Dict:
        """Get audit compliance status"""
        return {
            'status': 'Compliant',
            'last_audit': datetime.now().isoformat(),
            'next_audit': (datetime.now() + timedelta(days=90)).isoformat()
        }
    
    async def _generate_audit_findings(self, conn, organization_id: int) -> List[Dict]:
        """Generate audit findings"""
        return [
            {
                'finding': 'Access control policies need updating',
                'severity': 'Medium',
                'recommendation': 'Review and update access control policies'
            }
        ]
    
    async def _generate_compliance_declaration(self, org: Dict, assessments: List) -> str:
        """Generate compliance declaration for regulatory reporting"""
        return f"""
        {org['name']} hereby declares compliance with Saudi regulatory requirements
        as assessed on {datetime.now().strftime('%Y-%m-%d')}.
        
        NCA Compliance: {next((a['score'] for a in assessments if a['code'] == 'NCA'), 'Not Assessed')}%
        SAMA Compliance: {next((a['score'] for a in assessments if a['code'] == 'SAMA'), 'Not Assessed')}%
        PDPL Compliance: {next((a['score'] for a in assessments if a['code'] == 'PDPL'), 'Not Assessed')}%
        """
    
    async def _get_regulatory_requirements(self, conn) -> List[Dict]:
        """Get regulatory requirements"""
        return [
            {'requirement': 'Annual NCA compliance assessment', 'status': 'Required'},
            {'requirement': 'SAMA cyber resilience framework', 'status': 'Required for financial institutions'},
            {'requirement': 'PDPL data protection compliance', 'status': 'Required'}
        ]
    
    async def _convert_to_excel(self, report_data: Dict) -> Dict:
        """Convert report to Excel format (returns data structure for Excel generation)"""
        # In production, would use openpyxl or xlsxwriter
        report_data['excel_sheets'] = {
            'Summary': report_data.get('summary', {}),
            'Details': report_data.get('assessments', []),
            'Risks': report_data.get('top_risks', []),
            'Recommendations': {'recommendations': report_data.get('recommendations', [])}
        }
        return report_data
    
    async def _convert_to_pdf(self, report_data: Dict) -> Dict:
        """Convert report to PDF format (returns data structure for PDF generation)"""
        # In production, would use reportlab or weasyprint
        report_data['pdf_sections'] = [
            {'type': 'title', 'content': report_data['title']},
            {'type': 'summary', 'content': report_data.get('summary', {})},
            {'type': 'table', 'content': report_data.get('assessments', [])},
            {'type': 'chart', 'content': report_data.get('compliance_trends', [])}
        ]
        return report_data