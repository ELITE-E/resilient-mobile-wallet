from app.ledger.constants import MPESA_CLEARING_ACCOUNT_ID, FEES_REVENUE_ACCOUNT_ID
from app.ledger.ledger_client import LedgerClient

async def ensure_system_accounts(ledger: LedgerClient) -> None:
    await ledger.create_account(MPESA_CLEARING_ACCOUNT_ID, is_wallet=False)
    await ledger.create_account(FEES_REVENUE_ACCOUNT_ID, is_wallet=False)