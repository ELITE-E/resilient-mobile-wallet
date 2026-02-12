import pytest

from app.db.repositories.deposits import (
    DuplicateCheckoutRequestIDError,
    create_deposit_attempt,
    store_callback_payload,
    update_deposit_status,
)
from app.db.repositories.users import DuplicatePhoneError, create_user
from app.db.session import SessionLocal


@pytest.mark.asyncio
async def test_create_user_unique_phone():
    async with SessionLocal() as session:
        await create_user(session, user_id="u1", full_name="A", phone_number="+254700000001")
        with pytest.raises(DuplicatePhoneError):
            await create_user(session, user_id="u2", full_name="B", phone_number="+254700000001")


@pytest.mark.asyncio
async def test_create_deposit_unique_checkout_request_id():
    async with SessionLocal() as session:
        # create user first (FK)
        await create_user(session, user_id="u3", full_name="A", phone_number="+254700000002")

        await create_deposit_attempt(
            session,
            deposit_id="d1",
            user_id="u3",
            amount=100,
            checkout_request_id="CR1",
            merchant_request_id="MR1",
        )

        with pytest.raises(DuplicateCheckoutRequestIDError):
            await create_deposit_attempt(
                session,
                deposit_id="d2",
                user_id="u3",
                amount=100,
                checkout_request_id="CR1",
                merchant_request_id="MR2",
            )


@pytest.mark.asyncio
async def test_update_deposit_status_and_store_callback():
    async with SessionLocal() as session:
        await create_user(session, user_id="u4", full_name="A", phone_number="+254700000003")
        await create_deposit_attempt(
            session,
            deposit_id="d3",
            user_id="u4",
            amount=250,
            checkout_request_id="CR2",
            merchant_request_id=None,
        )

        await store_callback_payload(session, checkout_request_id="CR2", payload={"ResultCode": 0})
        await update_deposit_status(session, checkout_request_id="CR2", status="SUCCESS", receipt="RCP123")