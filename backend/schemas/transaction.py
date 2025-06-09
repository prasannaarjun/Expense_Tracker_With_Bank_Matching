from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional
from enum import Enum

class TransactionType(str, Enum):
    income = "income"
    expense = "expense"

class TransactionBase(BaseModel):
    date: date
    amount: float
    category: str
    type: TransactionType
    note: Optional[str] = None
    model_config = ConfigDict(extra='forbid', from_attributes=True)

class TransactionCreate(TransactionBase):
    pass

class TransactionOut(TransactionBase):
    id: int
    owner_id: int
    bank_transaction_id: Optional[int] = None
    matched: bool = False

    class Config:
        from_attributes = True 