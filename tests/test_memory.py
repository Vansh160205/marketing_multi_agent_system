# tests/test_memory.py
import pytest
import uuid

# Import all memory classes
from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory
from memory.episodic import EpisodicMemory
from memory.semantic import SemanticMemory

@pytest.mark.skip(reason="Temporarily disabled due to race condition/event loop issue")
@pytest.mark.asyncio
async def test_short_term_memory():
    """Tests adding to and retrieving from short-term memory."""
    agent_id = "test_stm_agent"
    stm = ShortTermMemory(agent_id)
    
    test_item = {'id': str(uuid.uuid4()), 'content': 'Test message from STM', 'significant': True}
    
    # Test adding an item
    await stm.add(test_item)
    
    # Test retrieving the recent item
    recent_items = await stm.get_recent(n=1)
    assert len(recent_items) == 1
    assert recent_items[0]['content'] == 'Test message from STM'
    
    # Test retrieving important items
    important_items = await stm.get_important()
    assert len(important_items) >= 1
    assert important_items[0]['significant'] is True
    print("✅ Short-term memory test passed")

@pytest.mark.skip(reason="Temporarily disabled due to race condition/event loop issue")
@pytest.mark.asyncio
async def test_long_term_memory():
    """Tests adding to and querying from long-term memory."""
    agent_id = "test_ltm_agent"
    ltm = LongTermMemory(agent_id)
    
    entity_id = f"customer-{uuid.uuid4()}@example.com"
    test_data = {'preference': 'email', 'last_contact': '2025-10-04'}
    
    # Test adding a memory
    await ltm.add(entity_id, 'customer', test_data, importance=0.9)
    
    # Test querying for the memory
    memories = await ltm.query(entity_id, 'customer')
    assert len(memories) >= 1
    assert memories[0]['data']['preference'] == 'email'
    print("✅ Long-term memory test passed")

@pytest.mark.asyncio
async def test_episodic_memory():
    """Tests adding and finding episodes in episodic memory."""
    # Note: This test is async to be consistent, but the underlying neo4j driver is sync.
    # A full async refactor would use an async neo4j driver.
    agent_id = "test_em_agent"
    em = EpisodicMemory(agent_id)
    
    problem = "High bounce rate on landing page"
    solution = "A/B test new headline"
    
    # Test adding an episode
    episode_id = em.add_episode(problem=problem, solution=solution, outcome="success")
    assert episode_id is not None
    
    # Test finding a similar episode
    similar_episodes = em.find_similar_episodes("High bounce")
    assert len(similar_episodes) >= 1
    assert similar_episodes[0]['problem'] == problem
    print("✅ Episodic memory test passed")

@pytest.mark.asyncio
async def test_semantic_memory():
    """Tests adding and finding knowledge in semantic memory."""
    sm = SemanticMemory()
    
    entity = "SaaS Onboarding"
    target = "Welcome Email Series"
    
    # Test adding a knowledge relationship
    sm.add_knowledge(entity=entity, relationship="IMPROVED_BY", target=target)
    
    # Test finding the related entity
    related_items = sm.find_related(entity, relationship_type="IMPROVED_BY")
    # Note: The structure of 'related_items' is a list of dicts with keys like 'related', 'r'
    assert len(related_items) >= 1
    print("✅ Semantic memory test passed")