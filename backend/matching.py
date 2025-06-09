from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from . import models
from typing import List, Tuple

def find_potential_matches(db: Session, transaction: models.Transaction, time_window_days: int = 1, amount_tolerance: float = 0.01) -> List[models.BankTransaction]:
    """
    Find potential bank transaction matches for a given transaction based on date and amount.
    
    Args:
        db: Database session
        transaction: The transaction to find matches for
        time_window_days: Number of days to look before and after the transaction date
        amount_tolerance: Tolerance for amount matching (e.01 means 1% difference allowed)
    
    Returns:
        List of potential matching bank transactions
    """
    # Calculate date range
    start_date = transaction.date - timedelta(days=time_window_days)
    end_date = transaction.date + timedelta(days=time_window_days)
    
    # Calculate amount range
    min_amount = transaction.amount * (1 - amount_tolerance)
    max_amount = transaction.amount * (1 + amount_tolerance)
    
    # Query for potential matches
    potential_matches = db.query(models.BankTransaction).filter(
        models.BankTransaction.date.between(start_date, end_date),
        models.BankTransaction.amount.between(min_amount, max_amount),
        models.BankTransaction.is_matched == False,
        models.BankTransaction.owner_id == transaction.owner_id
    ).all()
    
    return potential_matches

def find_matches(transactions: List[models.Transaction], bank_transactions: List[models.BankTransaction]) -> List[Tuple[models.Transaction, models.BankTransaction]]:
    """
    Find matches between transactions and bank transactions based on date and amount.
    This function operates on already fetched lists of transactions.
    """
    matches = []
    for transaction in transactions:
        for bank_transaction in bank_transactions:
            # Match if date and amount are exactly the same
            if (transaction.date == bank_transaction.date and 
                transaction.amount == bank_transaction.amount):
                matches.append((transaction, bank_transaction))
                break  # Move to next transaction once we find a match
    
    return matches

def create_match(db: Session, transaction_id: int, bank_transaction_id: int, owner_id: int) -> Tuple[models.Transaction, models.BankTransaction]:
    """
    Create a match between a transaction and a bank transaction.
    
    Args:
        db: Database session
        transaction_id: ID of the transaction
        bank_transaction_id: ID of the bank transaction
        owner_id: ID of the owner
    
    Returns:
        Tuple of (updated transaction, updated bank transaction)
    """
    # Get the records
    transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id,
        models.Transaction.owner_id == owner_id
    ).first()
    
    bank_transaction = db.query(models.BankTransaction).filter(
        models.BankTransaction.id == bank_transaction_id,
        models.BankTransaction.owner_id == owner_id
    ).first()
    
    if not transaction or not bank_transaction:
        raise ValueError("Transaction or bank transaction not found")
    
    # Update the records
    transaction.matched = True
    transaction.bank_transaction_id = bank_transaction_id
    
    bank_transaction.is_matched = True
    bank_transaction.transaction_id = transaction_id
    
    # Save changes
    db.commit()
    db.refresh(transaction)
    db.refresh(bank_transaction)
    
    return transaction, bank_transaction 