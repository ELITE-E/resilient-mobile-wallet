from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import tigerbeetle as tb

from app.ledger.constants import (
    LEDGER_KES,
    ACCOUNT_CODE_SYSTEM,
    ACCOUNT_CODE_WALLET,
)


class LedgerError(Exception): ...
class LedgerNotFound(LedgerError): ...
class LedgerConflict(LedgerError): ...
class InsufficientFunds(LedgerError): ...


@dataclass(frozen=True)
class TransferSpec:
    id: int
    debit_account_id: int
    credit_account_id: int
    amount: int
    code: int
    flags: int = 0
    pending_id: int = 0
    timeout: int = 0
    user_data_128: int = 0
    user_data_64: int = 0
    user_data_32: int = 0
    ledger: int = LEDGER_KES


def _raise_unless_only(errors, allowed_results: set) -> None:
    """
    TigerBeetle returns an array of error objects (index + result).
    We treat EXISTS as success for idempotency/crash recovery. <!--citation:4-->
    """
    for e in errors:
        if e.result in allowed_results:
            continue
        # map common financial failure:
        if e.result == tb.CreateTransferResult.EXCEEDS_CREDITS:
            raise InsufficientFunds(str(e.result))
        raise LedgerConflict(str(e.result))


class LedgerClient:
    def __init__(self, client: tb.ClientAsync):
        self.client = client

    async def create_account(self, account_id: int, *, is_wallet: bool) -> None:
        flags = 0
        code = ACCOUNT_CODE_SYSTEM

        if is_wallet:
            code = ACCOUNT_CODE_WALLET
            # No overdraft: debits must not exceed credits. <!--citation:2-->
            flags = tb.AccountFlags.DEBITS_MUST_NOT_EXCEED_CREDITS

        account = tb.Account(
            id=account_id,
            debits_pending=0,
            debits_posted=0,
            credits_pending=0,
            credits_posted=0,
            user_data_128=0,
            user_data_64=0,
            user_data_32=0,
            ledger=LEDGER_KES,
            code=code,
            flags=flags,
            timestamp=0,
        )

        errors = await self.client.create_accounts([account])
        # exists should be treated like ok for crash-safe retries. <!--citation:4-->
        _raise_unless_only(errors, allowed_results={tb.CreateAccountResult.EXISTS})

    async def lookup_account(self, account_id: int) -> tb.Account | None:
        accounts = await self.client.lookup_accounts([account_id])
        if not accounts:
            return None
        # lookup returns matched accounts; order not guaranteed
        for a in accounts:
            if a.id == account_id:
                return a
        return None

    async def create_transfer(self, spec: TransferSpec) -> None:
        t = tb.Transfer(
            id=spec.id,
            debit_account_id=spec.debit_account_id,
            credit_account_id=spec.credit_account_id,
            amount=spec.amount,
            pending_id=spec.pending_id,
            user_data_128=spec.user_data_128,
            user_data_64=spec.user_data_64,
            user_data_32=spec.user_data_32,
            timeout=spec.timeout,
            ledger=spec.ledger,
            code=spec.code,
            flags=spec.flags,
            timestamp=0,
        )

        errors = await self.client.create_transfers([t])
        # exists should be treated like ok for crash-safe retries. <!--citation:6-->
        _raise_unless_only(errors, allowed_results={tb.CreateTransferResult.EXISTS})

    async def create_linked_transfers(self, specs: Sequence[TransferSpec]) -> None:
        """
        Linked chain rule: all except last must have LINKED flag; last must not. <!--citation:1-->
        """
        batch: list[tb.Transfer] = []
        for i, s in enumerate(specs):
            flags = s.flags
            if i < len(specs) - 1:
                flags |= tb.TransferFlags.LINKED
            else:
                flags &= ~tb.TransferFlags.LINKED

            batch.append(
                tb.Transfer(
                    id=s.id,
                    debit_account_id=s.debit_account_id,
                    credit_account_id=s.credit_account_id,
                    amount=s.amount,
                    pending_id=s.pending_id,
                    user_data_128=s.user_data_128,
                    user_data_64=s.user_data_64,
                    user_data_32=s.user_data_32,
                    timeout=s.timeout,
                    ledger=s.ledger,
                    code=s.code,
                    flags=flags,
                    timestamp=0,
                )
            )

        errors = await self.client.create_transfers(batch)
        _raise_unless_only(errors, allowed_results={tb.CreateTransferResult.EXISTS})

    async def two_phase_pending(self, *, transfer_id: int, debit: int, credit: int, amount: int, code: int) -> None:
        # Pending reserves debits_pending/credits_pending. <!--citation:3-->
        await self.create_transfer(
            TransferSpec(
                id=transfer_id,
                debit_account_id=debit,
                credit_account_id=credit,
                amount=amount,
                code=code,
                flags=tb.TransferFlags.PENDING,
            )
        )

    async def two_phase_post(self, *, post_id: int, pending_id: int, code: int) -> None:
        # Post resolves pending -> posted; amount_max posts full amount. <!--citation:3-->
        await self.create_transfer(
            TransferSpec(
                id=post_id,
                debit_account_id=0,
                credit_account_id=0,
                amount=tb.amount_max,
                pending_id=pending_id,
                code=code,
                flags=tb.TransferFlags.POST_PENDING_TRANSFER,
            )
        )

    async def two_phase_void(self, *, void_id: int, pending_id: int, code: int) -> None:
        await self.create_transfer(
            TransferSpec(
                id=void_id,
                debit_account_id=0,
                credit_account_id=0,
                amount=0,
                pending_id=pending_id,
                code=code,
                flags=tb.TransferFlags.VOID_PENDING_TRANSFER,
            )
        )