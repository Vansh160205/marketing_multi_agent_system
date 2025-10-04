# agents/lead_triage/agent.py
from agents.base_agent import BaseAgent
from typing import Dict, Any
import random  # Replace with actual ML model

class LeadTriageAgent(BaseAgent):
    """Categorizes and routes incoming leads"""
    
    CATEGORIES = {
        'campaign_qualified': 'Campaign Qualified Lead',
        'sales_qualified': 'Sales Qualified Lead',
        'cold_lead': 'Cold Lead',
        'general_inquiry': 'General Inquiry',
        'existing_customer': 'Existing Customer'
    }
    
    def __init__(self, mcp_client):
        super().__init__("lead_triage_agent", mcp_client)
        print("Lead Triage Agent ready")
    
    async def process(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Triage and categorize lead"""
        print(f"\n🔍 Triaging lead: {lead_data.get('email')}")
        
        # Extract features
        features = self._extract_features(lead_data)
        
        # Get historical context
        historical = await self._get_historical_context(lead_data.get('email'))
        
        # Classify lead
        category, confidence = self._classify_lead(features, historical)
        
        # Update lead in database
        if lead_data.get('id'):
            await self.mcp_client.request('update_lead_status', {
                'lead':lead_data,
                'lead_id': lead_data['id'],
                'status': 'triaged',
                'category': category
            })
        
        # Determine next action
        result = {
            'lead_id': lead_data.get('id'),
            'email': lead_data.get('email'),
            'category': category,
            'confidence': confidence,
            'historical_interactions': len(historical),
            'recommended_action': self._get_recommendation(category, confidence)
        }
        
        # Store interaction
        await self.store_interaction({
            'entity_id': lead_data.get('email'),
            'entity_type': 'lead',
            'problem': 'lead_categorization',
            'solution': category,
            'outcome': 'success',
            'confidence': confidence,
            'significant': confidence > 0.8,
            'importance': confidence
        })
        
        # Handoff to Engagement Agent if high priority
        if category == self.CATEGORIES['campaign_qualified'] and confidence > 0.8:
            print("🎯 High-value lead detected! Handing off to Engagement Agent...")
            handoff_result = await self.handoff('engagement_agent', {
                'lead': lead_data,
                'category': category,
                'confidence': confidence,
                'priority': 'high'
            })
            result['handoff'] = handoff_result
        
        return result
    
    def _extract_features(self, lead_data: Dict) -> Dict:
        """Extract classification features"""
        return {
            'source': lead_data.get('source', 'unknown'),
            'engagement_score': lead_data.get('engagement_score', 0),
            'company_size': lead_data.get('company_size', 'unknown'),
            'industry': lead_data.get('industry', 'unknown'),
            'has_company': bool(lead_data.get('company'))
        }
    
    async def _get_historical_context(self, email: str) -> list:
        """Get historical interactions"""
        if not email:
            return []
        
        # Check long-term memory
        historical = await self.long_term_memory.query(email, 'lead')
        
        # Add to semantic memory
        if historical:
            self.semantic_memory.add_knowledge(
                entity=email,
                relationship='has_history',
                target='interactions',
                properties={'count': len(historical)}
            )
        
        return historical
    
    def _classify_lead(self, features: Dict, historical: list) -> tuple:
        """Classify lead (simplified - replace with ML model)"""
        score = 0
        
        # Scoring logic
        if features['engagement_score'] > 70:
            score += 0.4
        if features['company_size'] in ['1000-5000', '5000+']:
            score += 0.3
        if len(historical) > 0:
            score += 0.2
        if features['source'] in ['webinar', 'demo_request']:
            score += 0.1
        
        # Determine category
        if score > 0.8:
            category = self.CATEGORIES['campaign_qualified']
        elif score > 0.6:
            category = self.CATEGORIES['sales_qualified']
        elif len(historical) > 0:
            category = self.CATEGORIES['existing_customer']
        elif score > 0.3:
            category = self.CATEGORIES['general_inquiry']
        else:
            category = self.CATEGORIES['cold_lead']
        
        confidence = min(score + random.uniform(0.1, 0.2), 1.0)
        
        return category, round(confidence, 2)
    
    def _get_recommendation(self, category: str, confidence: float) -> str:
        """Get next step recommendation"""
        recommendations = {
            self.CATEGORIES['campaign_qualified']: 'Immediate personalized outreach',
            self.CATEGORIES['sales_qualified']: 'Schedule sales call',
            self.CATEGORIES['cold_lead']: 'Add to nurture campaign',
            self.CATEGORIES['general_inquiry']: 'Send information packet',
            self.CATEGORIES['existing_customer']: 'Upsell opportunity'
        }
        return recommendations.get(category, 'Manual review required')