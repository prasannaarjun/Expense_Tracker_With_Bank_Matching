from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MatchCreate(BaseModel):
    transaction_id: int
    bank_transaction_id: int
    match_date: datetime
    match_amount: float

class MatchOut(MatchCreate):
    id: int
    owner_id: int
    is_confirmed: bool = False

    class Config:
        from_attributes = True 