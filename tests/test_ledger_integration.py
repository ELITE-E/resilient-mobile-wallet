import os
import pytest
import tigerbeetle as tb

from app.ledger.bootstrap import ensure_system_accounts
from app.ledger.constants import (
    MPESA_CLEARING_ACCOUNT_ID,
    FEES_REVENUE_ACCOUNT_ID,
    TRANSFER_CODE_MPESA_DEPOSIT,
    TRANSFER_CODE_P2P,
    TRANSFER_CODE_P2P_FEE,
)
from app.ledger.ledger_client import LedgerClient, TransferSpec, InsufficientFunds
from app.ledger.tb_client import get_tb_client_async


@pytest.mark.tb
@pytest.mark.asyncio
async def test_bootstrap_and_basic_transfer():
    async with get_tb_client_async() as client:
        ledger = LedgerClient(client)
        await ensure_system_accounts(ledger)

        alice = tb.id()
        bob = tb.id()
        await ledger.create_account(alice, is_wallet=True)
        await ledger.create_account(bob, is_wallet=True)

        # fund alice from clearing
        await ledger.create_transfer(
            TransferSpec(
                id=tb.id(),
                debit_account_id=MPESA_CLEARING_ACCOUNT_ID,
                credit_account_id=alice,
                amount=1000,
                code=TRANSFER_CODE_MPESA_DEPOSIT,
            )
        )

        # alice pays bob + fee atomically (linked events chain)
        main_id = tb.id()
        fee_id = tb.id()
        await ledger.create_linked_transfers(
            [
                TransferSpec(
                    id=main_id,
                    debit_account_id=alice,
                    credit_account_id=bob,
                    amount=100,
                    code=TRANSFER_CODE_P2P,
                ),
                TransferSpec(
                    id=fee_id,
                    debit_account_id=alice,
                    credit_account_id=FEES_REVENUE_ACCOUNT_ID,
                    amount=5,
                    code=TRANSFER_CODE_P2P_FEE,
                ),
            ]
        )

        a = await ledger.lookup_account(alice)
        b = await ledger.lookup_account(bob)
        assert a is not None and b is not None
        assert int(b.credits_posted) >= 100


@pytest.mark.tb
@pytest.mark.asyncio
async def test_overdraft_rejected_by_ledger():
    async with get_tb_client_async() as client:
        ledger = LedgerClient(client)
        await ensure_system_accounts(ledger)

        sender = tb.id()
        receiver = tb.id()
        await ledger.create_account(sender, is_wallet=True)
        await ledger.create_account(receiver, is_wallet=True)

        # No funding — should fail due to debits_must_not_exceed_credits.
        with pytest.raises(InsufficientFunds):
            await ledger.create_transfer(
                TransferSpec(
                    id=tb.id(),
                    debit_account_id=sender,
                    credit_account_id=receiver,
                    amount=50,
                    code=TRANSFER_CODE_P2P,
                )
            )


@pytest.mark.tb
@pytest.mark.asyncio
async def test_two_phase_pending_then_post():
    async with get_tb_client_async() as client:
        ledger = LedgerClient(client)
        await ensure_system_accounts(ledger)

        user = tb.id()
        await ledger.create_account(user, is_wallet=True)

        pending_id = tb.id()
        await ledger.two_phase_pending(
            transfer_id=pending_id,
            debit=MPESA_CLEARING_ACCOUNT_ID,
            credit=user,
            amount=200,
            code=TRANSFER_CODE_MPESA_DEPOSIT,
        )

        # After pending: credits_pending should reflect reservation. <!--citation:3-->
        u1 = await ledger.lookup_account(user)
        assert u1 is not None
        assert int(u1.credits_pending) >= 200

        post_id = tb.id()
        await ledger.two_phase_post(post_id=post_id, pending_id=pending_id, code=TRANSFER_CODE_MPESA_DEPOSIT)

        u2 = await ledger.lookup_account(user)
        assert u2 is not None
        assert int(u2.credits_pending) == 0
        assert int(u2.credits_posted) >= 200