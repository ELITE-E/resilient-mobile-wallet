from __future__ import annotations

from decimal import Decimal
from typing import Any

from sqlalchemy import Dialect
from sqlalchemy.types import Numeric, TypeDecorator


class UInt128Numeric(TypeDecorator):
    """
    Store uint128 in Postgres NUMERIC(39,0) but expose as Python int.
    """
    impl = Numeric(precision=39, scale=0)
    cache_ok=True

    def process_bind_param(self, value: Any | None, dialect: Dialect) -> Any:
        if value is None:
            return None
        return Decimal(int(value))
    
    def process_result_value(self, value: Any | None, dialect: Dialect) -> Any | None:
        if value is None:
            return None
        return int(value)