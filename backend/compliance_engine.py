"""
Compliance Engine for Saudi Frameworks (NCA, SAMA, PDPL) and International Standards
"""
import asyncpg
from typing import Dict, List, Any
from datetime import datetime

class ComplianceEngine:
    def __init__(self, db_pool):
        self.db_pool = db_pool
        self.saudi_frameworks = ['NCA', 'SAMA', 'PDPL']
        self.international_frameworks = ['ISO27001', 'NIST']
        
    async def assess_compliance(self, organization_id: int, framework_code: str) -> Dict:
        """Perform automated compliance assessment"""
        async with self.db_pool.acquire() as conn:
            # Get framework details
            framework = await conn.fetchrow(
                'SELECT * FROM frameworks WHERE code = $1', framework_code
            )
            
            if not framework:
                raise ValueError(f"Framework {framework_code} not found")
            
            # Get all controls for framework
            controls = await conn.fetch(
                'SELECT * FROM controls WHERE framework_id = $1', framework['id']
            )
            
            # Calculate compliance score based on control implementation
            total_controls = len(controls)
            implemented_controls = 0
            control_scores = []
            
            for control in controls:
                # Check if control is implemented
                implementation = await self._check_control_implementation(
                    conn, organization_id, control['id']
                )
                if implementation['status'] == 'implemented':
                    implemented_controls += 1
                    score = 100
                elif implementation['status'] == 'partial':
                    implemented_controls += 0.5
                    score = 50
                else:
                    score = 0
                    
                control_scores.append({
                    'control_id': control['control_id'],
                    'title': control['title'],
                    'score': score,
                    'status': implementation['status'],
                    'evidence': implementation['evidence']
                })
            
            compliance_score = (implemented_controls / total_controls * 100) if total_controls > 0 else 0
            
            # Save assessment result
            assessment_id = await conn.fetchval('''
                INSERT INTO assessments (organization_id, framework_id, score, status, completed_at)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id
            ''', organization_id, framework['id'], compliance_score, 'completed', datetime.now())
            
            return {
                'assessment_id': assessment_id,
                'framework': framework_code,
                'score': round(compliance_score, 2),
                'total_controls': total_controls,
                'implemented_controls': int(implemented_controls),
                'control_scores': control_scores,
                'maturity_level': self._calculate_maturity_level(compliance_score),
                'recommendations': await self._generate_recommendations(control_scores)
            }
    
    async def _check_control_implementation(self, conn, org_id: int, control_id: int) -> Dict:
        """Check if a control is implemented for an organization"""
        # Check for evidence of control implementation
        evidence = await conn.fetchrow('''
            SELECT * FROM control_implementations 
            WHERE organization_id = $1 AND control_id = $2
        ''', org_id, control_id)
        
        if evidence:
            return {
                'status': evidence['status'],
                'evidence': evidence['evidence_path']
            }
        
        # Default to not implemented
        return {'status': 'not_implemented', 'evidence': None}
    
    def _calculate_maturity_level(self, score: float) -> int:
        """Calculate maturity level based on compliance score"""
        if score >= 90:
            return 5  # Optimized
        elif score >= 75:
            return 4  # Managed
        elif score >= 60:
            return 3  # Defined
        elif score >= 40:
            return 2  # Repeatable
        else:
            return 1  # Initial
    
    async def _generate_recommendations(self, control_scores: List[Dict]) -> List[str]:
        """Generate recommendations based on assessment results"""
        recommendations = []
        
        # Find controls with low scores
        low_score_controls = [c for c in control_scores if c['score'] < 50]
        
        if low_score_controls:
            recommendations.append(
                f"Focus on implementing {len(low_score_controls)} controls with low scores"
            )
            
        # Priority recommendations
        critical_controls = [c for c in low_score_controls if 'critical' in c['title'].lower()]
        if critical_controls:
            recommendations.append(
                f"Prioritize {len(critical_controls)} critical controls for immediate implementation"
            )
        
        return recommendations

    async def validate_saudi_framework(self, framework_code: str, data: Dict) -> Dict:
        """Validate compliance with specific Saudi framework requirements"""
        validators = {
            'NCA': self._validate_nca,
            'SAMA': self._validate_sama,
            'PDPL': self._validate_pdpl
        }
        
        if framework_code in validators:
            return await validators[framework_code](data)
        else:
            raise ValueError(f"Unknown Saudi framework: {framework_code}")
    
    async def _validate_nca(self, data: Dict) -> Dict:
        """Validate NCA (National Cybersecurity Authority) requirements"""
        requirements = {
            'cybersecurity_policy': 'Cybersecurity policy must be approved by board',
            'risk_assessment': 'Annual risk assessment is mandatory',
            'incident_response': '24-hour incident reporting to NCA required',
            'access_control': 'Multi-factor authentication for critical systems',
            'data_protection': 'Encryption for data at rest and in transit',
            'third_party_risk': 'Vendor security assessment required',
            'security_awareness': 'Annual security training for all employees',
            'business_continuity': 'BCP testing required twice yearly'
        }
        
        validation_results = {}
        for req, description in requirements.items():
            validation_results[req] = {
                'description': description,
                'status': data.get(req, False),
                'mandatory': True
            }
        
        return validation_results
    
    async def _validate_sama(self, data: Dict) -> Dict:
        """Validate SAMA (Saudi Central Bank) requirements"""
        requirements = {
            'cyber_resilience': 'Cyber resilience framework implementation',
            'fraud_management': 'Real-time fraud monitoring system',
            'data_localization': 'Customer data must be stored in Saudi Arabia',
            'api_security': 'Open banking API security standards',
            'payment_security': 'PCI-DSS compliance for payment systems',
            'audit_trail': 'Complete audit trail for all transactions',
            'customer_protection': 'Customer data protection measures',
            'regulatory_reporting': 'Monthly regulatory reporting to SAMA'
        }
        
        validation_results = {}
        for req, description in requirements.items():
            validation_results[req] = {
                'description': description,
                'status': data.get(req, False),
                'mandatory': True
            }
        
        return validation_results
    
    async def _validate_pdpl(self, data: Dict) -> Dict:
        """Validate PDPL (Personal Data Protection Law) requirements"""
        requirements = {
            'data_classification': 'Personal data classification system',
            'consent_management': 'Explicit consent for data processing',
            'data_subject_rights': 'System for handling data subject requests',
            'data_breach_notification': '72-hour breach notification requirement',
            'privacy_impact_assessment': 'PIA for high-risk processing',
            'data_retention': 'Data retention policy and implementation',
            'cross_border_transfer': 'Compliance with cross-border data transfer rules',
            'dpo_appointment': 'Data Protection Officer appointment'
        }
        
        validation_results = {}
        for req, description in requirements.items():
            validation_results[req] = {
                'description': description,
                'status': data.get(req, False),
                'mandatory': True
            }
        
        return validation_results