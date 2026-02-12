from sqlalchemy import select,update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.deposit import Deposit

class DuplicateCheckoutRequestIDError(Exception):
    pass

class DepositNotFoundError(Exception):
    pass

async def create_deposit_attempt(
        session:AsyncSession,
        deposit_id:str,
        user_id:str,
    amount:int,
        checkout_request_id:str,
        merchant_request_id:str | None,
        )->Deposit:
    dep=Deposit(
    id=deposit_id,
        user_id=user_id,
        amount=amount,
        status="PENDING_CALLBACK",
        checkout_request_id=checkout_request_id,
        merchant_request_id=merchant_request_id,
    )

    try:
        async with session.begin():
            session.add(dep)

        return dep
    except IntegrityError as e:
        raise DuplicateCheckoutRequestIDError("checkout_request_id already exists") from e
    

async def update_deposit_status(session:AsyncSession,
                                checkout_request_id:str,
                                status:str,
                                receipt:str | None=None,
                                 )->None:
    async with session.begin():
        result =await session.execute(
            update(Deposit)
            .where(Deposit.checkout_request_id==checkout_request_id)
            .values(status=status,receipt=receipt)
            .returning(Deposit.id)
        )
    row = result.first()
    if row is None:
            raise DepositNotFoundError(checkout_request_id)
    
async def store_callback_payload(
            session: AsyncSession, *, 
            checkout_request_id: str,
              payload: dict) -> None:
        
        async with session.begin():
            result = await session.execute(
            update(Deposit)
            .where(Deposit.checkout_request_id == checkout_request_id)
            .values(raw_callback_json=payload)
            .returning(Deposit.id)
        )
        if result.first() is None:
            raise DepositNotFoundError(checkout_request_id)