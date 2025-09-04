"""
Risk Management Engine with calculations and analytics
"""
import asyncpg
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

class RiskEngine:
    def __init__(self, db_pool):
        self.db_pool = db_pool
        self.severity_matrix = {
            'minimal': 1, 'low': 2, 'medium': 3, 'high': 4, 'critical': 5
        }
        self.likelihood_matrix = {
            'very_low': 1, 'low': 2, 'medium': 3, 'high': 4, 'very_high': 5
        }
        
    async def calculate_risk_score(self, severity: str, likelihood: str) -> Dict:
        """Calculate inherent and residual risk scores"""
        severity_score = self.severity_matrix.get(severity.lower(), 3)
        likelihood_score = self.likelihood_matrix.get(likelihood.lower(), 3)
        
        inherent_risk = severity_score * likelihood_score
        
        # Risk levels
        if inherent_risk >= 20:
            risk_level = 'Critical'
            color = 'red'
        elif inherent_risk >= 15:
            risk_level = 'High'
            color = 'orange'
        elif inherent_risk >= 10:
            risk_level = 'Medium'
            color = 'yellow'
        elif inherent_risk >= 5:
            risk_level = 'Low'
            color = 'green'
        else:
            risk_level = 'Minimal'
            color = 'blue'
        
        return {
            'inherent_risk_score': inherent_risk,
            'risk_level': risk_level,
            'risk_color': color,
            'severity_score': severity_score,
            'likelihood_score': likelihood_score
        }
    
    async def create_risk_assessment(self, org_id: int, risks: List[Dict]) -> Dict:
        """Create comprehensive risk assessment for organization"""
        async with self.db_pool.acquire() as conn:
            assessment_results = []
            total_risk_score = 0
            
            for risk in risks:
                # Calculate risk score
                risk_calc = await self.calculate_risk_score(
                    risk['severity'], risk['likelihood']
                )
                
                # Store risk in database
                risk_id = await conn.fetchval('''
                    INSERT INTO risks (
                        organization_id, title, description, category,
                        severity, likelihood, inherent_risk_score,
                        residual_risk_score, status, mitigation_status,
                        owner, mitigation_deadline
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                    RETURNING id
                ''', org_id, risk['title'], risk.get('description', ''),
                    risk['category'], risk['severity'], risk['likelihood'],
                    risk_calc['inherent_risk_score'], 
                    risk_calc['inherent_risk_score'],  # Initial residual = inherent
                    'open', 'not_started', risk.get('owner', 'Unassigned'),
                    datetime.now() + timedelta(days=risk.get('mitigation_days', 30))
                )
                
                assessment_results.append({
                    'risk_id': risk_id,
                    'title': risk['title'],
                    **risk_calc
                })
                
                total_risk_score += risk_calc['inherent_risk_score']
            
            # Calculate organization risk profile
            avg_risk_score = total_risk_score / len(risks) if risks else 0
            
            return {
                'organization_id': org_id,
                'assessment_date': datetime.now().isoformat(),
                'total_risks': len(risks),
                'average_risk_score': round(avg_risk_score, 2),
                'risk_distribution': await self._get_risk_distribution(assessment_results),
                'risk_details': assessment_results,
                'recommendations': await self._generate_risk_recommendations(assessment_results)
            }
    
    async def _get_risk_distribution(self, risks: List[Dict]) -> Dict:
        """Calculate risk distribution by severity"""
        distribution = {
            'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0, 'Minimal': 0
        }
        
        for risk in risks:
            distribution[risk['risk_level']] += 1
        
        return distribution
    
    async def _generate_risk_recommendations(self, risks: List[Dict]) -> List[str]:
        """Generate risk mitigation recommendations"""
        recommendations = []
        
        critical_risks = [r for r in risks if r['risk_level'] == 'Critical']
        high_risks = [r for r in risks if r['risk_level'] == 'High']
        
        if critical_risks:
            recommendations.append(
                f"Immediate action required for {len(critical_risks)} critical risks"
            )
        
        if high_risks:
            recommendations.append(
                f"Develop mitigation plans for {len(high_risks)} high-priority risks"
            )
        
        if len(risks) > 10:
            recommendations.append(
                "Consider implementing automated risk monitoring system"
            )
        
        return recommendations
    
    async def calculate_residual_risk(self, risk_id: int, controls: List[Dict]) -> Dict:
        """Calculate residual risk after applying controls"""
        async with self.db_pool.acquire() as conn:
            # Get original risk
            risk = await conn.fetchrow('SELECT * FROM risks WHERE id = $1', risk_id)
            if not risk:
                raise ValueError(f"Risk {risk_id} not found")
            
            # Calculate control effectiveness
            total_effectiveness = 0
            for control in controls:
                effectiveness = control.get('effectiveness', 50) / 100
                total_effectiveness += effectiveness
            
            # Average effectiveness
            avg_effectiveness = total_effectiveness / len(controls) if controls else 0
            
            # Calculate residual risk
            inherent_risk = risk['inherent_risk_score']
            residual_risk = inherent_risk * (1 - avg_effectiveness)
            
            # Update database
            await conn.execute('''
                UPDATE risks 
                SET residual_risk_score = $1, mitigation_status = $2
                WHERE id = $3
            ''', residual_risk, 'in_progress', risk_id)
            
            return {
                'risk_id': risk_id,
                'inherent_risk': inherent_risk,
                'residual_risk': round(residual_risk, 2),
                'risk_reduction': round((1 - residual_risk/inherent_risk) * 100, 2),
                'controls_applied': len(controls),
                'average_effectiveness': round(avg_effectiveness * 100, 2)
            }
    
    async def generate_risk_heatmap(self, org_id: int) -> Dict:
        """Generate risk heatmap data for visualization"""
        async with self.db_pool.acquire() as conn:
            risks = await conn.fetch(
                'SELECT * FROM risks WHERE organization_id = $1 AND status = $2',
                org_id, 'open'
            )
            
            # Initialize heatmap matrix
            heatmap = [[0 for _ in range(5)] for _ in range(5)]
            
            for risk in risks:
                severity_idx = self.severity_matrix.get(risk['severity'].lower(), 3) - 1
                likelihood_idx = self.likelihood_matrix.get(risk['likelihood'].lower(), 3) - 1
                heatmap[severity_idx][likelihood_idx] += 1
            
            return {
                'heatmap': heatmap,
                'severity_labels': list(self.severity_matrix.keys()),
                'likelihood_labels': list(self.likelihood_matrix.keys()),
                'total_risks': len(risks)
            }
    
    async def predict_risk_trends(self, org_id: int, days: int = 90) -> Dict:
        """Predict future risk trends using historical data"""
        async with self.db_pool.acquire() as conn:
            # Get historical risk data
            historical_risks = await conn.fetch('''
                SELECT DATE(created_at) as date, COUNT(*) as count,
                       AVG(inherent_risk_score) as avg_score
                FROM risks
                WHERE organization_id = $1 
                AND created_at >= CURRENT_DATE - INTERVAL '%s days'
                GROUP BY DATE(created_at)
                ORDER BY date
            ''', org_id, days)
            
            if not historical_risks:
                return {'message': 'Insufficient data for trend analysis'}
            
            # Simple linear regression for trend prediction
            dates = [i for i in range(len(historical_risks))]
            scores = [float(r['avg_score']) for r in historical_risks]
            
            if len(dates) > 1:
                # Calculate trend
                x_mean = sum(dates) / len(dates)
                y_mean = sum(scores) / len(scores)
                
                num = sum((x - x_mean) * (y - y_mean) for x, y in zip(dates, scores))
                den = sum((x - x_mean) ** 2 for x in dates)
                
                slope = num / den if den != 0 else 0
                intercept = y_mean - slope * x_mean
                
                # Predict next 30 days
                future_predictions = []
                for i in range(1, 31):
                    predicted_score = slope * (len(dates) + i) + intercept
                    future_predictions.append({
                        'day': i,
                        'predicted_score': max(0, round(predicted_score, 2))
                    })
                
                trend = 'increasing' if slope > 0.1 else 'decreasing' if slope < -0.1 else 'stable'
                
                return {
                    'trend': trend,
                    'current_avg_score': round(scores[-1], 2) if scores else 0,
                    'predicted_30_day_score': round(future_predictions[-1]['predicted_score'], 2),
                    'trend_strength': abs(round(slope, 3)),
                    'predictions': future_predictions[:7]  # Next week predictions
                }
            
            return {'message': 'Need more data points for trend analysis'}