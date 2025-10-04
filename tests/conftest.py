# tests/conftest.py
import asyncio
import sys
import pytest

@pytest.fixture(scope="session")
def event_loop_policy():
    """Set the asyncio event loop policy for the test session."""
    if sys.platform == "win32":
        return asyncio.WindowsSelectorEventLoopPolicy()
    return asyncio.DefaultEventLoopPolicy()


@pytest.fixture(autouse=True)
async def db_manager_fixture():
    """
    This special "autouse" fixture re-initializes the global db_manager
    for every test, ensuring it runs in the correct event loop.
    """
    from database import connection
    from database.connection import DatabaseManager
    
    # Re-create the manager inside the test's event loop
    connection.db_manager = DatabaseManager()
    
    yield
    
    # Teardown: ensure connections are closed after tests
    # This is a simplified cleanup; for production tests, you might need more.
    if connection.db_manager.redis_client:
        await connection.db_manager.redis_client.close()
    if connection.db_manager.pg_engine:
        await connection.db_manager.pg_engine.dispose()