import asyncio

from tigerbeetle.client import InitError

from app.ledger.bootstrap import ensure_system_accounts
from app.ledger.ledger_client import LedgerClient
from app.ledger.tb_client import get_tb_client_async

RETRY_ATTEMPTS = 10
RETRY_DELAY_SECONDS = 1.0

async def main() -> None:
    last_error: Exception | None = None
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            async with get_tb_client_async() as client:
                ledger = LedgerClient(client)
                await ensure_system_accounts(ledger)
                print("OK: system accounts ensured")
                return
        except InitError as exc:
            last_error = exc
            if attempt == RETRY_ATTEMPTS:
                break
            await asyncio.sleep(RETRY_DELAY_SECONDS)

    if last_error:
        raise last_error

if __name__ == "__main__":
    asyncio.run(main())