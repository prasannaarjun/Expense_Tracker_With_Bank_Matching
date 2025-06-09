from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional
from enum import Enum

class TransactionType(str, Enum):
    income = "income"
    expense = "expense"

class TransactionStatus(str, Enum):
    pending = "pending"
    matched = "matched"
    unmatched = "unmatched"

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    class Config:
        orm_mode = True

class TransactionBase(BaseModel):
    date: date
    amount: float
    category: str
    type: TransactionType
    note: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionOut(TransactionBase):
    id: int
    owner_id: int
    class Config:
        orm_mode = True

class BankTransactionBase(BaseModel):
    date: date
    amount: float
    description: str
    category: Optional[str] = None
    status: TransactionStatus = TransactionStatus.pending

class BankTransactionCreate(BankTransactionBase):
    pass

class BankTransactionOut(BankTransactionBase):
    id: int
    owner_id: int
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class MatchCreate(BaseModel):
    transaction_id: int
    bank_transaction_id: int

class MatchOut(BaseModel):
    id: int
    transaction_id: int
    bank_transaction_id: int
    match_date: date
    match_amount: float
    owner_id: int
    is_confirmed: bool
    class Config:
        orm_mode = True 