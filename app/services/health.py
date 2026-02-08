import asyncio
from dataclasses import dataclass

from sqlalchemy import text

from app.db.engine import engine
from app.settings.config import settings


@dataclass(frozen=True)
class Readiness:
    postgres_ok: bool
    tigerbeetle_ok: bool


async def check_postgres() -> bool:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


async def check_tigerbeetle_tcp() -> bool:
    # Phase 3: just check the port is reachable (no ledger semantics yet).
    try:
        host, port_str = settings.tb_address.split(":")
        port = int(port_str)
        reader, writer = await asyncio.open_connection(host, port)
        writer.close()
        await writer.wait_closed()
        return True
    except Exception:
        return False


async def readiness() -> Readiness:
    pg_ok, tb_ok = await asyncio.gather(check_postgres(), check_tigerbeetle_tcp())
    return Readiness(postgres_ok=pg_ok, tigerbeetle_ok=tb_ok)