
# database/connection.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker,declarative_base
from neo4j import GraphDatabase
import redis.asyncio as redis # Import the asyncio version of redis
from config import settings
from contextlib import asynccontextmanager

Base = declarative_base()

class DatabaseManager:
    def __init__(self):
        # PostgreSQL
        self.pg_engine = create_async_engine(settings.POSTGRES_URL)
        self.SessionLocal = sessionmaker(bind=self.pg_engine,class_=AsyncSession,expire_on_commit=False,)
        
        # Neo4j
        self.neo4j_driver = GraphDatabase.driver(
            settings.NEO4J_URL,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
        
        # Asynchronous Redis Client
        self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

    @asynccontextmanager
    async def get_db_session(self) -> AsyncSession:
        """Get an asynchronous PostgreSQL session."""
        session = self.SessionLocal()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    def get_neo4j_session(self):
        """Get Neo4j session"""
        return self.neo4j_driver.session()
    
    async def get_redis(self):
        """Get the async Redis client."""
        return self.redis_client
    
    def close_all(self):
        """Close all connections"""
        self.neo4j_driver.close()
        self.redis_client.close()

db_manager = DatabaseManager()


