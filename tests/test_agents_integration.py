# tests/test_agents_integration.py
import pytest
import asyncio

# Import client and all agent classes
from mcp.client import MCPClient
from agents.lead_triage.agent import LeadTriageAgent
from agents.engagement.agent import EngagementAgent
from agents.campaign_optimization.agent import CampaignOptimizationAgent
import uuid

@pytest.mark.asyncio
async def test_full_agent_workflow():
    """Tests the complete workflow from lead triage to potential optimization."""
    
    client = MCPClient()
    
    # Initialize all agents
    triage_agent = LeadTriageAgent(client)
    engagement_agent = EngagementAgent(client)
    campaign_agent = CampaignOptimizationAgent(client)
    
    # A high-value lead designed to trigger a handoff
    test_lead = {
        "id": 1,
        "email": f"ceo-{uuid.uuid4()}@bigcorp.com",
        "engagement_score": 90,
        "company_size": "5000+",
        "industry": "Finance",
        "source": "demo_request"
    }
    
    print("\n--- 1. EXECUTING LEAD TRIAGE ---")
    triage_result = await triage_agent.process(test_lead)
    print(f"Triage Result: {triage_result}")
    assert triage_result is not None
    assert 'category' in triage_result
    
    # Check if the handoff to the Engagement Agent occurred
    if triage_result.get('handoff'):
        print("\n--- 2. EXECUTING ENGAGEMENT (HANDOFF DETECTED) ---")
        # Construct the input for the engagement agent based on the handoff context
        engagement_input = triage_result['handoff']['context']
        engagement_result = await engagement_agent.process(engagement_input)
        print(f"Engagement Result: {engagement_result}")
        assert engagement_result is not None
        assert 'status' in engagement_result

        # Check if an escalation to the Campaign Optimization Agent occurred
        if engagement_result.get('escalation'):
            print("\n--- 3. EXECUTING CAMPAIGN OPTIMIZATION (ESCALATION DETECTED) ---")
            optimization_input = engagement_result['escalation']['context']
            optimization_result = await campaign_agent.process(optimization_input)
            print(f"Optimization Result: {optimization_result}")
            assert optimization_result is not None
            assert 'recommendations' in optimization_result
    
    else:
        print("\n--- SKIPPING ENGAGEMENT (NO HANDOFF TRIGGERED) ---")

    await client.close()
    print("\n✅ Agent integration test complete.")