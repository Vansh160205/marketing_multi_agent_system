# database/init_db.py
from database.connection import db_manager
from sqlalchemy import text

def init_postgres():
    """Initialize PostgreSQL schema"""
    with open('deployment/schema.sql', 'r') as f:
        schema = f.read()
    
    with db_manager.get_db_session() as session:
        session.execute(text(schema))
    print("✅ PostgreSQL initialized")

def init_neo4j():
    """Initialize Neo4j constraints and indexes"""
    with db_manager.get_neo4j_session() as session:
        # Create constraints
        session.run("""
            CREATE CONSTRAINT entity_id IF NOT EXISTS
            FOR (e:Entity) REQUIRE e.id IS UNIQUE
        """)
        
        session.run("""
            CREATE CONSTRAINT episode_id IF NOT EXISTS
            FOR (ep:Episode) REQUIRE ep.id IS UNIQUE
        """)
    print("✅ Neo4j initialized")

def init_redis():
    """Test Redis connection"""
    client = db_manager.get_redis()
    client.ping()
    print("✅ Redis connected")

if __name__ == "__main__":
    init_postgres()
    init_neo4j()
    init_redis()