from __future__ import annotations

from sqlalchemy import String,DateTime,func,ForeignKey,BigInteger
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped,mapped_column

from app.db.base import Base

class Deposit(Base):
    __tablename__="deposits"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)

    amount:Mapped[int]=mapped_column(BigInteger,nullable=False)
    status:Mapped[str]=mapped_column(String,nullable=False,
                                     default='PENDING_CALLBACK')
    
    checkout_request_id:Mapped[str]=mapped_column(String,nullable=False,unique=True)
    merchant_request_id:Mapped[str | None]=mapped_column(String,nullable=True)

    receipt:Mapped[str |None]=mapped_column(String,nullable=True)
    raw_callback_json:Mapped[dict | None]=mapped_column(JSONB,nullable=True)

    created_at: Mapped[object] = mapped_column(DateTime(timezone=True),
                                                server_default=func.now())
    
    updated_at: Mapped[object] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )