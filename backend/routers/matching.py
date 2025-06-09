from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, database, auth, matching
from ..schemas.matching import MatchCreate, MatchOut

router = APIRouter()

@router.post("/match", response_model=List[MatchOut])
def match_transactions(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    # Get all unmatched transactions
    transactions = db.query(models.Transaction).filter(
        models.Transaction.owner_id == current_user.id,
        models.Transaction.bank_transaction_id == None
    ).all()
    
    # Get all unmatched bank transactions
    bank_transactions = db.query(models.BankTransaction).filter(
        models.BankTransaction.owner_id == current_user.id,
        models.BankTransaction.transaction_id == None
    ).all()
    
    # Find matches
    matches = matching.find_matches(transactions, bank_transactions)
    
    # Create match records
    match_records = []
    for transaction, bank_transaction in matches:
        match_record = models.Match(
            transaction_id=transaction.id,
            bank_transaction_id=bank_transaction.id,
            match_date=bank_transaction.date,
            match_amount=bank_transaction.amount,
            owner_id=current_user.id
        )
        db.add(match_record)
        match_records.append(match_record)
    
    db.commit()
    for match_record in match_records:
        db.refresh(match_record)
    
    return match_records

@router.get("/matches", response_model=List[MatchOut])
def get_matches(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Match).filter(models.Match.owner_id == current_user.id).all()

@router.post("/matches/{match_id}/confirm")
def confirm_match(match_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    match = db.query(models.Match).filter(models.Match.id == match_id, models.Match.owner_id == current_user.id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Update transaction with bank transaction reference
    transaction = db.query(models.Transaction).filter(models.Transaction.id == match.transaction_id).first()
    transaction.bank_transaction_id = match.bank_transaction_id
    
    # Update bank transaction with transaction reference
    bank_transaction = db.query(models.BankTransaction).filter(models.BankTransaction.id == match.bank_transaction_id).first()
    bank_transaction.transaction_id = match.transaction_id
    
    # Delete the match record
    db.delete(match)
    
    db.commit()
    return {"ok": True}

@router.delete("/matches/{match_id}")
def delete_match(match_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    match = db.query(models.Match).filter(models.Match.id == match_id, models.Match.owner_id == current_user.id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    db.delete(match)
    db.commit()
    return {"ok": True}

@router.get("/potential/{transaction_id}", response_model=List[MatchOut])
def get_potential_matches(
    transaction_id: int,
    time_window_days: int = 1,
    amount_tolerance: float = 0.01,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Get the transaction
    transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id,
        models.Transaction.owner_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Find potential matches
    potential_matches = matching.find_potential_matches(
        db, 
        transaction, 
        time_window_days=time_window_days,
        amount_tolerance=amount_tolerance
    )
    
    # Convert to MatchOut format
    matches = []
    for bank_transaction in potential_matches:
        match = MatchOut(
            id=0,  # This is a potential match, not a confirmed one
            transaction_id=transaction.id,
            bank_transaction_id=bank_transaction.id,
            match_date=bank_transaction.date,
            match_amount=bank_transaction.amount,
            owner_id=current_user.id,
            is_confirmed=False
        )
        matches.append(match)
    
    return matches

@router.post("/confirm", response_model=MatchOut)
def confirm_match(
    match: MatchCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    try:
        transaction, bank_transaction = matching.create_match(
            db,
            match.transaction_id,
            match.bank_transaction_id,
            current_user.id
        )
        
        return MatchOut(
            id=0,  # This is a new match
            transaction_id=transaction.id,
            bank_transaction_id=bank_transaction.id,
            match_date=bank_transaction.date,
            match_amount=bank_transaction.amount,
            owner_id=current_user.id,
            is_confirmed=True
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) 