from typing import List, Tuple, Dict
from datetime import datetime, timedelta
from ..models import Transaction, BankTransaction

def calculate_similarity_score(transaction: Transaction, bank_transaction: BankTransaction) -> float:
    """
    Calculate similarity score between a transaction and a bank transaction.
    Returns a score between 0 and 1.
    """
    score = 0.0
    total_factors = 0

    # Amount matching (exact match)
    if abs(transaction.amount - bank_transaction.amount) < 0.01:
        score += 1.0
    total_factors += 1

    # Date matching (within 3 days)
    date_diff = abs((transaction.date - bank_transaction.date).days)
    if date_diff <= 3:
        score += 1.0 - (date_diff / 3)
    total_factors += 1

    # Description matching (basic text similarity)
    trans_desc = transaction.description.lower()
    bank_desc = bank_transaction.description.lower()
    
    # Check if one description contains the other
    if trans_desc in bank_desc or bank_desc in trans_desc:
        score += 1.0
    total_factors += 1

    return score / total_factors

def find_potential_matches(transaction: Transaction, bank_transactions: List[BankTransaction], 
                         min_confidence: float = 0.6) -> List[Tuple[BankTransaction, float]]:
    """
    Find potential matches for a transaction from a list of bank transactions.
    Returns a list of tuples containing the bank transaction and its confidence score.
    """
    matches = []
    
    for bank_trans in bank_transactions:
        # Skip if bank transaction is already matched
        if bank_trans.is_matched:
            continue
            
        score = calculate_similarity_score(transaction, bank_trans)
        if score >= min_confidence:
            matches.append((bank_trans, score))
    
    # Sort by confidence score in descending order
    return sorted(matches, key=lambda x: x[1], reverse=True)

def find_best_match(transaction: Transaction, bank_transactions: List[BankTransaction], 
                   min_confidence: float = 0.6) -> Tuple[BankTransaction, float]:
    """
    Find the best matching bank transaction for a given transaction.
    Returns a tuple of (bank_transaction, confidence_score) or (None, 0.0) if no match found.
    """
    matches = find_potential_matches(transaction, bank_transactions, min_confidence)
    return matches[0] if matches else (None, 0.0)

def find_matches(transactions: List[Transaction], bank_transactions: List[BankTransaction], 
                min_confidence: float = 0.6) -> Dict[int, List[Tuple[BankTransaction, float]]]:
    """
    Find matches for multiple transactions against a list of bank transactions.
    Returns a dictionary mapping transaction IDs to their potential matches.
    """
    matches = {}
    
    # Sort transactions by date to process them in chronological order
    sorted_transactions = sorted(transactions, key=lambda x: x.date)
    
    for transaction in sorted_transactions:
        # Skip if transaction is already matched
        if transaction.matched:
            continue
            
        potential_matches = find_potential_matches(transaction, bank_transactions, min_confidence)
        if potential_matches:
            matches[transaction.id] = potential_matches
            
    return matches 