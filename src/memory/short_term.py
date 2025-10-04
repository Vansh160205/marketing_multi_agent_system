# memory/short_term.py
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import deque
import json
from database.connection import db_manager

class ShortTermMemory:
    """Working memory for current conversations"""
    
    def __init__(self, agent_id: str, max_size: int = 100, ttl_minutes: int = 60):
        self.agent_id = agent_id
        self.max_size = max_size
        self.ttl = timedelta(minutes=ttl_minutes)
        self.redis = None
        self.key_prefix = f"stm:{agent_id}"
    
    async def initialize(self):
        """Asynchronously initialize the Redis connection."""
        if self.redis is None:
            self.redis = await db_manager.get_redis()
    
    async def add(self, item: Dict):
        """Add item to short-term memory"""
        await self.initialize()
        item['timestamp'] = datetime.now().isoformat()
        item['agent_id'] = self.agent_id
        
        # Store in Redis with TTL
        key = f"{self.key_prefix}:{item.get('id', datetime.now().timestamp())}"
        await self.redis.setex(
            key,
            int(self.ttl.total_seconds()),
            json.dumps(item)
        )
        
        # Add to sorted set for ordering
        await self.redis.zadd(
            f"{self.key_prefix}:index",
            {key: datetime.now().timestamp()}
        )
        
        # Trim to max size
        await self._trim_to_size()
    
    # In memory/short_term.py

    async def get_recent(self, n: int = 10) -> List[Dict]:
        """Get n most recent items asynchronously and efficiently."""
        await self.initialize()
        keys = await self.redis.zrevrange(f"{self.key_prefix}:index", 0, n-1)
        if not keys:
            return []
        
        # Use mget to fetch all values in one network call
        items_json = await self.redis.mget(keys)
        
        # Filter out potential None values if a key expired between zrevrange and mget
        return [json.loads(item) for item in items_json if item]

    # After
    async def _trim_to_size(self):
        """Keep only max_size items asynchronously."""
        await self.initialize()
        count = await self.redis.zcard(f"{self.key_prefix}:index")
        if count > self.max_size:
            # Get the keys of the oldest items
            to_remove_keys = await self.redis.zrange(
                f"{self.key_prefix}:index", 0, count - self.max_size - 1
            )
            if to_remove_keys:
                # Use pipeline or transactions for atomicity in production
                # but for now, just await them.
                await self.redis.delete(*to_remove_keys)
                await self.redis.zrem(f"{self.key_prefix}:index", *to_remove_keys)
    
    async def should_consolidate(self) -> bool:
        """Check if consolidation is needed"""
        await self.initialize()
        count = await self.redis.zcard(f"{self.key_prefix}:index")
        return count > self.max_size * 0.8
    
    async def get_important(self) -> List[Dict]:
        """Get items marked as significant"""
        await self.initialize()
        all_items = await self.get_recent(n=self.max_size)
        return [item for item in all_items if item.get('significant', False)]