# agents/campaign_optimization/agent.py
from agents.base_agent import BaseAgent
from typing import Dict, Any
import random

class CampaignOptimizationAgent(BaseAgent):
    """Monitors and optimizes campaign performance"""
    
    def __init__(self, mcp_client):
        super().__init__("campaign_optimization_agent", mcp_client)
        print("Campaign Optimization Agent ready")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze and optimize campaigns"""
        print(f"\n📊 Analyzing campaign performance...")
        
        campaign_id = input_data.get('campaign_id')
        issue = input_data.get('issue')
        
        # Get campaign metrics
        metrics = await self._get_campaign_metrics(campaign_id)
        
        # Analyze performance
        analysis = self._analyze_performance(metrics)
        
        # Generate optimization recommendations
        recommendations = self._generate_recommendations(analysis, issue)
        
        # Determine if human escalation needed
        needs_escalation = analysis['performance_score'] < 0.5
        
        result = {
            'campaign_id': campaign_id,
            'analysis': analysis,
            'recommendations': recommendations,
            'needs_escalation': needs_escalation,
            'escalation_reason': 'Complex optimization required' if needs_escalation else None
        }
        
        # Store learning
        await self.store_interaction({
            'entity_id': str(campaign_id),
            'entity_type': 'campaign',
            'problem': issue or 'performance_optimization',
            'solution': recommendations[0]['action'] if recommendations else 'N/A',
            'outcome': 'escalated' if needs_escalation else 'optimized',
            'significant': True,
            'importance': 0.9
        })
        
        # Add to semantic knowledge
        if recommendations:
            self.semantic_memory.add_knowledge(
                entity=issue or 'low_performance',
                relationship='solved_by',
                target=recommendations[0]['action'],
                properties={'effectiveness': analysis['performance_score']}
            )
        
        return result
    
    async def _get_campaign_metrics(self, campaign_id: int = None) -> Dict:
        """Get campaign performance metrics"""
        if campaign_id:
            metrics = await self.mcp_client.request('get_campaign_metrics', {
                'campaign_id': campaign_id
            })
        else:
            # Simulated metrics
            metrics = {
                'open_rate': random.uniform(0.15, 0.35),
                'click_rate': random.uniform(0.02, 0.08),
                'conversion_rate': random.uniform(0.01, 0.05),
                'unsubscribe_rate': random.uniform(0.001, 0.01),
                'total_sent': random.randint(1000, 10000)
            }
        
        return metrics
    
    def _analyze_performance(self, metrics: Dict) -> Dict:
        """Analyze campaign performance"""
        # Define benchmarks
        benchmarks = {
            'open_rate': 0.25,
            'click_rate': 0.05,
            'conversion_rate': 0.03,
            'unsubscribe_rate': 0.005
        }
        
        score = 0
        issues = []
        
        if metrics.get('open_rate', 0) < benchmarks['open_rate']:
            issues.append('low_open_rate')
        else:
            score += 0.25
        
        if metrics.get('click_rate', 0) < benchmarks['click_rate']:
            issues.append('low_click_rate')
        else:
            score += 0.25
        
        if metrics.get('conversion_rate', 0) < benchmarks['conversion_rate']:
            issues.append('low_conversion_rate')
        else:
            score += 0.25
        
        if metrics.get('unsubscribe_rate', 0) > benchmarks['unsubscribe_rate']:
            issues.append('high_unsubscribe_rate')
        else:
            score += 0.25
        
        return {
            'performance_score': score,
            'issues': issues,
            'metrics': metrics,
            'benchmarks': benchmarks
        }
    
    def _generate_recommendations(self, analysis: Dict, issue: str = None) -> list:
        """Generate optimization recommendations"""
        recommendations = []
        
        for detected_issue in analysis['issues']:
            if detected_issue == 'low_open_rate':
                recommendations.append({
                    'action': 'optimize_subject_lines',
                    'priority': 'high',
                    'description': 'A/B test subject lines with personalization',
                    'expected_impact': '+15% open rate'
                })
            
            elif detected_issue == 'low_click_rate':
                recommendations.append({
                    'action': 'improve_cta',
                    'priority': 'high',
                    'description': 'Make CTAs more prominent and action-oriented',
                    'expected_impact': '+10% click rate'
                })
            
            elif detected_issue == 'low_conversion_rate':
                recommendations.append({
                    'action': 'refine_targeting',
                    'priority': 'medium',
                    'description': 'Narrow audience to higher-intent leads',
                    'expected_impact': '+5% conversion rate'
                })
            
            elif detected_issue == 'high_unsubscribe_rate':
                recommendations.append({
                    'action': 'reduce_frequency',
                    'priority': 'high',
                    'description': 'Decrease email frequency and improve segmentation',
                    'expected_impact': '-50% unsubscribe rate'
                })
        
        return recommendations