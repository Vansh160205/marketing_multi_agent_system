# agents/engagement/agent.py
from agents.base_agent import BaseAgent
from typing import Dict, Any
from datetime import datetime
import json
class EngagementAgent(BaseAgent):
    """Manages personalized outreach and lead nurturing"""
    
    def __init__(self, mcp_client):
        super().__init__("engagement_agent", mcp_client)
        self.email_templates = self._load_templates()
        print("Engagement Agent ready")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process engagement request"""
        # In the process() method...
        print(f"\n📧 Processing engagement for lead: {input_data.get('email')}")
        
        lead = input_data.get('lead', {})
        category = input_data.get('category')
        priority = input_data.get('priority', 'normal')
        
        # Get lead preferences from memory
        preferences = await self._get_preferences(lead.get('email'))
        
        # Create personalized outreach
        outreach_plan = self._create_outreach_plan(lead, category, preferences)
        
        # Execute outreach (simulation)
        execution_result = await self._execute_outreach(outreach_plan)
        
        # Log interaction
        await self.mcp_client.request('log_interaction', {
            'lead_id': lead.get('id'),
            'agent_id': self.agent_id,
            'interaction_type': 'outreach',
            'content': outreach_plan['message_preview'],
            'outcome': execution_result['status'],
            'metadata': outreach_plan
        })
        
        # Store in memory
        await self.store_interaction({
            'entity_id': lead.get('email'),
            'entity_type': 'lead',
            'problem': 'lead_engagement',
            'solution': outreach_plan['strategy'],
            'outcome': execution_result['status'],
            'significant': priority == 'high',
            'importance': 0.8 if priority == 'high' else 0.5
        })
        
        # Check if needs escalation to Campaign Optimization
        if execution_result.get('performance_concern'):
            print("⚠️ Performance concern detected! Handing off to Campaign Optimization...")
            handoff_result = await self.handoff('campaign_optimization_agent', {
                'lead': lead,
                'outreach_plan': outreach_plan,
                'execution_result': execution_result,
                'issue': 'low_engagement_rate'
            })
            execution_result['escalation'] = handoff_result
        
        return execution_result
    
    async def _get_preferences(self, email: str) -> Dict:
        """Get customer preferences from memory"""
        if not email:
            return {}
        
        memories = await self.long_term_memory.query(email, 'lead')
        
        # Extract preferences
        preferences = {
            'channel': 'email',  # default
            'time_preference': 'morning',
            'content_type': 'detailed'
        }
        
        for memory in memories:
            if 'channel' in memory.get('data', {}):
                preferences['channel'] = memory['data']['channel']
        
        return preferences
    
    def _create_outreach_plan(self, lead: Dict, category: str, preferences: Dict) -> Dict:
        """Create personalized outreach plan"""
        template = self.email_templates.get(category, self.email_templates['default'])
        channel = preferences.get('channel', 'email')
        plan = {
            'strategy': f"{channel}_outreach",
            'channel': channel,
            'template_id': template['id'],
            'personalization': {
                'name': lead.get('company', 'there'),
                'industry': lead.get('industry', 'your industry'),
                'pain_point': template['pain_point']
            },
            'message_preview': template['preview'],
            'scheduled_time': datetime.now().isoformat(),
            'follow_up_sequence': template['follow_ups']
        }
        
        return plan
    
    async def _execute_outreach(self, plan: Dict) -> Dict:
        """Execute outreach plan (simulation)"""
        # In production, this would actually send emails, create social posts, etc.
        
        import random
        success = random.random() > 0.3  # 70% success rate
        
        result = {
            'status': 'sent' if success else 'failed',
            'channel': plan['channel'],
            'timestamp': datetime.now().isoformat(),
            'engagement_rate': random.uniform(0.1, 0.4),
            'performance_concern': random.random() < 0.2  # 20% chance of concern
        }
        
        return result
    
    def _load_templates(self) -> Dict:
        """Load email templates"""
        return {
            'Campaign Qualified Lead': {
                'id': 'cql_001',
                'preview': 'Exclusive offer for {company}...',
                'pain_point': 'scaling marketing',
                'follow_ups': ['day_3', 'day_7', 'day_14']
            },
            'Sales Qualified Lead': {
                'id': 'sql_001',
                'preview': 'Ready to discuss how we can help {company}...',
                'pain_point': 'improving conversion rates',
                'follow_ups': ['day_2', 'day_5']
            },
            'default': {
                'id': 'default_001',
                'preview': 'Thank you for your interest...',
                'pain_point': 'growing your business',
                'follow_ups': ['day_7']
            }
        }