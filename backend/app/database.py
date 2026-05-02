from urllib.parse import urlparse, unquote
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import get_settings

settings = get_settings()


def _build_engine_url(raw: str) -> URL:
    """
    Parse the DATABASE_URL string and build a SQLAlchemy URL object.
    Using URL.create() means special characters in the password are
    handled safely — no string parsing issues.
    """
    parsed = urlparse(raw)

    # Normalise driver: force asyncpg dialect
    driver = "postgresql+asyncpg"

    return URL.create(
        drivername=driver,
        username=unquote(parsed.username or ""),
        password=unquote(parsed.password or ""),
        host=parsed.hostname,
        port=parsed.port or 5432,
        database=(parsed.path or "/postgres").lstrip("/"),
    )


engine = create_async_engine(
    _build_engine_url(settings.database_url),
    echo=settings.app_env == "development",
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args={"ssl": "require"},
)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
