# agents/base_agent.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import uuid
from datetime import datetime
from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory
from memory.episodic import EpisodicMemory
from memory.semantic import SemanticMemory
from mcp.client import MCPClient

class BaseAgent(ABC):
    """Base class for all marketing agents"""
    
    def __init__(self, agent_id: str, mcp_client: MCPClient):
        self.agent_id = agent_id
        self.mcp_client = mcp_client
        
        # Initialize memory systems
        self.short_term_memory = ShortTermMemory(agent_id)
        self.long_term_memory = LongTermMemory(agent_id)
        self.episodic_memory = EpisodicMemory(agent_id)
        self.semantic_memory = SemanticMemory()
        
        print(f"✅ {agent_id} initialized")
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return output - must be implemented by child classes"""
        pass
    
    async def handoff(self, target_agent: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handoff to another agent with context preservation"""
        handoff_context = {
            "from_agent": self.agent_id,
            "to_agent": target_agent,
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "conversation_history": await self.short_term_memory.get_recent(n=10),
            "handoff_id": str(uuid.uuid4())
        }
        
        # Store handoff in short-term memory
        await self.short_term_memory.add({
            'type': 'handoff',
            'target': target_agent,
            'context': context,
            'significant': True
        })
        
        # Call MCP server to register handoff
        result = await self.mcp_client.request("agent_handoff", handoff_context)
        
        return result
    
    async def store_interaction(self, interaction: Dict[str, Any]):
        """Store interaction in appropriate memory systems"""
        # Add timestamp
        interaction['timestamp'] = datetime.now().isoformat()
        interaction['agent_id'] = self.agent_id
        
        # Store in short-term memory
        await self.short_term_memory.add(interaction)
        
        # Store significant interactions in episodic memory
        if interaction.get('significant') or interaction.get('importance', 0) > 0.7:
            # Assuming episodic_memory methods are not async yet. If they were, they'd need await.
            self.episodic_memory.add_episode(
                problem=interaction.get('problem', 'N/A'),
                solution=interaction.get('solution', 'N/A'),
                outcome=interaction.get('outcome', 'pending'),
                metadata=interaction
            )
        
        # Consolidate if needed
        if await self.short_term_memory.should_consolidate():
            await self.consolidate_memory()
    
    async def consolidate_memory(self):
        """Move important short-term memories to long-term storage"""
        important_items = await self.short_term_memory.get_important()
        
        for item in important_items:
            await self.long_term_memory.add(
                entity_id=item.get('entity_id', 'unknown'),
                entity_type=item.get('entity_type', 'interaction'),
                data=item,
                importance=item.get('importance', 0.7)
            )
        
        print(f"✅ Consolidated {len(important_items)} memories for {self.agent_id}")