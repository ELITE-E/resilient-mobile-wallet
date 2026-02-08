from sqlalchemy.ext.asyncio import create_async_engine
from app.settings.config import settings

engine = create_async_engine(settings.database_url, pool_pre_ping=True, echo=True)