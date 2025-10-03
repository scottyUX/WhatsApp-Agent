"""
Async database configuration for serverless environments.
Uses asyncpg driver with NullPool for Vercel compatibility.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.config.settings import settings


# Convert sync DATABASE_URL to async
DATABASE_URL = settings.DATABASE_URL
if DATABASE_URL.startswith("postgresql://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
else:
    ASYNC_DATABASE_URL = DATABASE_URL

# Lazy initialization for serverless compatibility
async_engine = None
AsyncSessionLocal = None

def get_async_engine():
    """Get or create async engine (lazy initialization)."""
    global async_engine
    if async_engine is None:
        async_engine = create_async_engine(
            ASYNC_DATABASE_URL,
            poolclass=NullPool,  # No connection pooling for serverless
            pool_recycle=300,  # 5 minutes
            echo=False
        )
    return async_engine

def get_async_session_local():
    """Get or create async session factory (lazy initialization)."""
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        AsyncSessionLocal = sessionmaker(
            bind=get_async_engine(),
            class_=AsyncSession,
            expire_on_commit=False
        )
    return AsyncSessionLocal

# Dependency for FastAPI routes
async def get_async_db():
    """Get async database session for FastAPI routes."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
