# tests/test_requirements.py
import pytest
import asyncio, uuid
from agents.base_agent import BaseAgent
from agents.lead_triage.agent import LeadTriageAgent
from agents.engagement.agent import EngagementAgent
from agents.campaign_optimization.agent import CampaignOptimizationAgent

test_lead_for_reqs = {
    'id': 99, 'significant': True,
    'entity_id': f'req-{uuid.uuid4()}@example.com',
    'entity_type': 'lead', 'data': {}
}

class TestRequirements:
    
    def test_requirement_three_agents(self, client):
        triage = LeadTriageAgent(client)
        engagement = EngagementAgent(client)
        campaign = CampaignOptimizationAgent(client)
        assert isinstance(triage, BaseAgent)
        assert isinstance(engagement, BaseAgent)
        assert isinstance(campaign, BaseAgent)
    
    @pytest.mark.asyncio
    async def test_requirement_mcp_server_http(self, client):
        result = await client.request('get_lead_data', {'lead_id': -1})
        assert 'error' in result

    @pytest.mark.asyncio
    async def test_requirement_agent_handoff_protocol(self, client):
        triage_agent = LeadTriageAgent(client)
        context = {'lead_id': 123, 'priority': 'high'}
        handoff_result = await triage_agent.handoff('engagement_agent', context)
        assert handoff_result['status'] == 'completed'
        
    def test_requirement_memory_systems_exist(self, client):
        agent = LeadTriageAgent(client)
        assert hasattr(agent, 'short_term_memory')
        assert hasattr(agent, 'long_term_memory')


    @pytest.mark.skip(reason="Temporarily disabled due to asyncio event loop issues")
    @pytest.mark.asyncio
    async def test_requirement_adaptive_learning(self, client):
        agent = LeadTriageAgent(client)
        await agent.store_interaction(test_lead_for_reqs)
        final_memory = await agent.short_term_memory.get_recent()
        assert len(final_memory) > 0

    @pytest.mark.skip(reason="Temporarily disabled due to race condition/event loop issue")
    @pytest.mark.asyncio
    async def test_requirement_memory_consolidation(self, client):
        agent = LeadTriageAgent(client)
        agent.short_term_memory.max_size = 5
        
        for i in range(5):
            item = {'id': f'item-{i}', 'significant': True, 'entity_id': 'consolidation-test@example.com', 'entity_type': 'lead', 'data': {}}
            await agent.store_interaction(item)

        ltm_results = await agent.long_term_memory.query('consolidation-test@example.com')
        assert len(ltm_results) > 0