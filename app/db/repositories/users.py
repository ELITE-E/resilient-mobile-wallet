import tigerbeetle as tb

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User

class DuplicatePhoneError(Exception):
    pass

async def create_user(session:AsyncSession,user_id:str,full_name:str,phone_number:str)->User:
    """
    Docstring for create_user
    
      # Generate TB-style time-based uint128 now (we persist it; TigerBeetle account creation happens later).
    """
    tb_account_id=tb.id()

    user=User(
        id=user_id,
        full_name=full_name,
        phone_number=phone_number,
        tb_account_id=tb_account_id,
        kycStatus="PENDING"
    )

    try:
        async with session.begin():
            session.add(user)
        return user
    except IntegrityError as e:
        raise DuplicatePhoneError("Phone number already exists") from e


