from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.infrastructure.config.settings import get_settings

settings = get_settings()

# Create async engine
engine = create_async_engine(
    "postgresql+asyncpg://adrielmachado0111:Afwl6cC7hKUN@ep-aged-band-882777-pooler.us-east-2.aws.neon.tech/orders_db",
    echo=settings.DB_ECHO,
    future=True
)

# Create session factory
async_session_factory = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db_session() -> AsyncSession:
    """
    Dependency for getting async DB session
    """
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()