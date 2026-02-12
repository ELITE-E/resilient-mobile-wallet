import os

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool
from app.settings.config import settings

#Fix of error is coming from asyncpg trying to reuse a pooled connection after the loop is closed.
#Nullpool gives you a fresh connection every time, which avoids loop reuse issues.
_use_null_pool = os.getenv("PYTEST_CURRENT_TEST") is not None

engine = create_async_engine(
	settings.database_url,
	pool_pre_ping=True,
	echo=True,
	poolclass=NullPool if _use_null_pool else None,
)