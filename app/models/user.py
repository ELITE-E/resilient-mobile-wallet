from __future__ import annotations

from sqlalchemy import String,DateTime,func
from sqlalchemy.orm import Mapped,mapped_column
from app.db.base import Base
from app.db.types import UInt128Numeric

class User(Base):
    __tablename__="users"

    id:Mapped[str]=mapped_column(String,primary_key=True)
    full_name:Mapped[str]=mapped_column(String,nullable=False)

    phone_number:Mapped[str]=mapped_column(String,nullable=False,unique=True)
    kycStatus:Mapped[str]=mapped_column(String,nullable=False,default='PENDING')

    tb_account_id:Mapped[int]=mapped_column(UInt128Numeric,nullable=False,
                                            unique=True)
    
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), 
                                                server_default=func.now())
    
    updated_at: Mapped[object] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
