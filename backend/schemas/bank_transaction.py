from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BankTransactionBase(BaseModel):
    date: datetime
    description: str
    amount: float
    bank_name: str
    account_number: str

class BankTransactionCreate(BankTransactionBase):
    pass

class BankTransactionOut(BankTransactionBase):
    id: int
    owner_id: int
    transaction_id: Optional[int] = None
    is_matched: bool = False

    class Config:
        from_attributes = True 