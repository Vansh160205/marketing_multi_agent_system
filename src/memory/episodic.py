# memory/episodic.py
from typing import Dict, List
from datetime import datetime
import uuid
from database.connection import db_manager

class EpisodicMemory:
    """Stores problem-resolution episodes"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
    
    def add_episode(self, problem: str, solution: str, outcome: str, metadata: Dict = None):
        """Store a problem-solution episode"""
        with db_manager.get_neo4j_session() as session:
            episode_id = str(uuid.uuid4())
            query = """
            CREATE (e:Episode {
                id: $id,
                agent_id: $agent_id,
                problem: $problem,
                solution: $solution,
                outcome: $outcome,
                metadata: $metadata,
                timestamp: datetime()
            })
            RETURN e
            """
            session.run(query, 
                id=episode_id,
                agent_id=self.agent_id,
                problem=problem,
                solution=solution,
                outcome=outcome,
                metadata=str(metadata or {})
            )
            return episode_id
    
    def find_similar_episodes(self, problem_description: str, limit: int = 5) -> List[Dict]:
        """Find similar past episodes"""
        with db_manager.get_neo4j_session() as session:
            # Simple keyword matching (can be enhanced with embeddings)
            query = """
            MATCH (e:Episode)
            WHERE e.agent_id = $agent_id 
            AND e.problem CONTAINS $keyword
            RETURN e
            ORDER BY e.timestamp DESC
            LIMIT $limit
            """
            result = session.run(query,
                agent_id=self.agent_id,
                keyword=problem_description.split()[0],  # Simple matching
                limit=limit
            )
            return [dict(record['e']) for record in result]