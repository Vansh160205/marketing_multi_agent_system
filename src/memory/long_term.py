# memory/long_term.py
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy import text
from database.connection import db_manager
import json

class LongTermMemory:
    """Persistent storage for customer history"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
    
    async def add(self, entity_id: str, entity_type: str, data: Dict, importance: float = 0.5):
        """Store item in long-term memory"""
        async with db_manager.get_db_session() as session:
            query = text("""
                INSERT INTO long_term_memory 
                (entity_id, entity_type, memory_type, data, importance_score, created_at, accessed_at)
                VALUES (:entity_id, :entity_type, :memory_type, :data, :importance, NOW(), NOW())
            """)
            await session.execute(query, {
                'entity_id': entity_id,
                'entity_type': entity_type,
                'memory_type': self.agent_id,
                'data': json.dumps(data),
                'importance': importance
            })
    
    async def query(self, entity_id: str, entity_type: str = None) -> List[Dict]:
        """Query long-term memory"""
        async with db_manager.get_db_session() as session:
            if entity_type:
                query = text("""
                    SELECT * FROM long_term_memory 
                    WHERE entity_id = :entity_id AND entity_type = :entity_type
                    ORDER BY importance_score DESC, created_at DESC
                    LIMIT 50
                """)
                result = await session.execute(query, {
                    'entity_id': entity_id,
                    'entity_type': entity_type
                })
            else:
                query = text("""
                    SELECT * FROM long_term_memory 
                    WHERE entity_id = :entity_id
                    ORDER BY importance_score DESC, created_at DESC
                    LIMIT 50
                """)
                result = await session.execute(query, {'entity_id': entity_id})
            
            return [dict(row._mapping) for row in result]
    
    # In src/memory/long_term.py
    async def bulk_add(self, items: List[Dict]):
        """Bulk insert items efficiently within a single session."""
        if not items:
            return

        async with db_manager.get_db_session() as session:
            # Prepare the data for a bulk insert
            insert_data = []
            for item in items:
                insert_data.append({
                    'entity_id': item.get('entity_id', 'unknown'),
                    'entity_type': item.get('entity_type', 'interaction'),
                    'memory_type': self.agent_id,
                    'data': json.dumps(item.get('data', item)), # Use item itself if 'data' key is missing
                    'importance': item.get('importance', 0.5)
                })

            query = text("""
                INSERT INTO long_term_memory 
                (entity_id, entity_type, memory_type, data, importance_score, created_at, accessed_at)
                VALUES (:entity_id, :entity_type, :memory_type, :data, :importance, NOW(), NOW())
            """)
            
            await session.execute(query, insert_data)