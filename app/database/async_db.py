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

# Create async engine with serverless-friendly settings
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    poolclass=NullPool,  # No connection pooling for serverless
    pool_recycle=300,  # 5 minutes
    echo=False
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency for FastAPI routes
async def get_async_db():
    """Get async database session for FastAPI routes."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
