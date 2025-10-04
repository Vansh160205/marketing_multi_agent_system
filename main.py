# main.py
import asyncio
from mcp.client import MCPClient
from agents.lead_triage.agent import LeadTriageAgent
from agents.engagement.agent import EngagementAgent
from agents.campaign_optimization.agent import CampaignOptimizationAgent

async def run_demo():
    client = MCPClient()
    
    # Initialize agents
    lead_agent = LeadTriageAgent(client)
    engagement_agent = EngagementAgent(client)
    campaign_agent = CampaignOptimizationAgent(client)

    # Sample lead
    lead = {
        "id": 1,
        "email": "demo@example.com",
        "engagement_score": 75,
        "company_size": "1000-5000",
        "industry": "SaaS",
        "source": "webinar"
    }

    # 1. Lead Triage
    triaged = await lead_agent.process(lead)
    print("\n🔍 Lead Triage Result:", triaged)

    # 2. Engagement
    engaged = await engagement_agent.process(triaged)
    print("\n📧 Engagement Result:", engaged)

    # 3. Campaign Optimization
    optimized = await campaign_agent.process({
        "campaign_id": 1,
        "issue": "low_click_rate"
    })
    print("\n📊 Campaign Optimization Result:", optimized)

    await client.close()

if __name__ == "__main__":
    asyncio.run(run_demo())
