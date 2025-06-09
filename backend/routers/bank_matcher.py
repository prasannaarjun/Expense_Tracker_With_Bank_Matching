from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import os
from datetime import datetime, timedelta
from .. import models, schemas, database, auth
from ..utils.bank_parser import parse_bank_csv, cleanup_upload
from ..schemas.bank import BankTransaction, BankMatchResult, BankMatchSummary

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def match_transactions(bank_tx: dict, db_transactions: List[models.Transaction], date_tolerance: int = 1) -> bool:
    """
    Match a bank transaction with user transactions.
    Uses date tolerance to account for slight date differences.
    """
    bank_date = bank_tx['date']
    bank_amount = bank_tx['amount']
    
    for tx in db_transactions:
        # Check if dates are within tolerance
        date_diff = abs((bank_date - tx.date).days)
        if date_diff <= date_tolerance and abs(tx.amount - bank_amount) < 0.01:
            return True
    return False

@router.post("/upload", response_model=BankMatchResult)
async def upload_bank_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    # Create uploads directory if it doesn't exist
    upload_dir = os.path.join("backend", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save uploaded file
    file_path = os.path.join(upload_dir, f"{current_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Parse CSV
        bank_data = parse_bank_csv(file_path)
        
        # Get user's transactions
        db_transactions = db.query(models.Transaction).filter(
            models.Transaction.owner_id == current_user.id
        ).all()
        
        # Match transactions
        matched = []
        unmatched = []
        
        for bank_tx in bank_data:
            if match_transactions(bank_tx, db_transactions):
                matched.append(BankTransaction(**bank_tx))
            else:
                unmatched.append(BankTransaction(**bank_tx))
        
        return BankMatchResult(matched=matched, unmatched=unmatched)
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    finally:
        # Clean up the uploaded file
        cleanup_upload(file_path)

@router.get("/summary", response_model=BankMatchSummary)
async def get_match_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Get a summary of matched vs unmatched transactions"""
    # Get all user transactions
    user_transactions = db.query(models.Transaction).filter(
        models.Transaction.owner_id == current_user.id
    ).all()
    
    total = len(user_transactions)
    if total == 0:
        return BankMatchSummary(
            total_transactions=0,
            matched_count=0,
            unmatched_count=0,
            match_percentage=0.0
        )
    
    # Count matched transactions (you might want to add a 'matched' flag to your Transaction model)
    matched_count = sum(1 for tx in user_transactions if hasattr(tx, 'matched') and tx.matched)
    unmatched_count = total - matched_count
    
    return BankMatchSummary(
        total_transactions=total,
        matched_count=matched_count,
        unmatched_count=unmatched_count,
        match_percentage=(matched_count / total) * 100
    ) 