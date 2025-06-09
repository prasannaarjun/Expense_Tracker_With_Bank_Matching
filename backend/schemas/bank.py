from pydantic import BaseModel
from typing import List
from datetime import date

class BankTransaction(BaseModel):
    date: date
    description: str
    amount: float

class BankMatchResult(BaseModel):
    matched: List[BankTransaction]
    unmatched: List[BankTransaction]

class BankMatchSummary(BaseModel):
    total_transactions: int
    matched_count: int
    unmatched_count: int
    match_percentage: float 