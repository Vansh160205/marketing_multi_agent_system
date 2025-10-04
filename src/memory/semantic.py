# memory/semantic.py
from typing import Dict, List
from database.connection import db_manager

class SemanticMemory:
    """Domain knowledge graph"""
    
    def __init__(self):
        pass
    
    def add_knowledge(self, entity: str, relationship: str, target: str, properties: Dict = None):
        """Add knowledge to semantic network"""
        with db_manager.get_neo4j_session() as session:
            query = """
            MERGE (a:Entity {name: $entity})
            MERGE (b:Entity {name: $target})
            MERGE (a)-[r:RELATES {
                type: $relationship,
                properties: $properties,
                created_at: datetime()
            }]->(b)
            RETURN a, r, b
            """
            session.run(query,
                entity=entity,
                target=target,
                relationship=relationship,
                properties=str(properties or {})
            )
    
    def find_related(self, entity: str, relationship_type: str = None, depth: int = 2) -> List[Dict]:
        """Find related entities"""
        with db_manager.get_neo4j_session() as session:
            if relationship_type:
                query = f"""
                    MATCH path = (e:Entity {{name: $entity}})-[r*1..{depth}]->(related)
                    WHERE ALL(rel in r WHERE rel.type = $rel_type)
                    RETURN related, r
                    LIMIT 20
                    """
                result = session.run(query, entity=entity, rel_type=relationship_type)
            else:
                query = f"""
                MATCH path = (e:Entity {{name: $entity}})-[r:RELATES*1..{depth}]->(related)
                RETURN related, r
                LIMIT 20
                """
                result = session.run(query, entity=entity)
            
            return [dict(record) for record in result]