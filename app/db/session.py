from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import engine

SessionLocal=AsyncSession(bind=engine, expire_on_commit=False)

async def get_session()->AsyncGenerator[AsyncSession,None]:
    async with SessionLocal as session:
        yield session