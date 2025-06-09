from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from datetime import datetime, date
import pandas as pd
from fastapi.responses import FileResponse
from .. import models, database, auth
from ..schemas.bank_transaction import BankTransactionBase, BankTransactionCreate, BankTransactionOut
from ..utils.bank_parser import parse_bank_csv, cleanup_upload
from sqlalchemy import extract

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=BankTransactionOut)
def create_bank_transaction(bank_transaction: BankTransactionCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_bank_transaction = models.BankTransaction(**bank_transaction.dict(), owner_id=current_user.id)
    db.add(db_bank_transaction)
    db.commit()
    db.refresh(db_bank_transaction)
    return db_bank_transaction

@router.post("/bulk/upload", response_model=List[BankTransactionOut])
async def bulk_upload_bank_transactions(
    file: UploadFile = File(...),
    bank_name: str = Form(...),
    account_number: str = Form(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    # The validation for bank_name and account_number will now be handled by FastAPI's Form(...) declaration
    
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
        
        # Convert to BankTransactionCreate objects
        bank_transactions = []
        for tx in bank_data:
            bank_transaction = BankTransactionCreate(
                date=tx['date'],
                description=tx['description'],
                amount=tx['amount'],
                bank_name=bank_name,
                account_number=account_number
            )
            bank_transactions.append(bank_transaction)
        
        # Create bank transactions in bulk
        db_bank_transactions = []
        for bank_transaction in bank_transactions:
            db_bank_transaction = models.BankTransaction(**bank_transaction.dict(), owner_id=current_user.id)
            db.add(db_bank_transaction)
            db_bank_transactions.append(db_bank_transaction)
        
        db.commit()
        for db_bank_transaction in db_bank_transactions:
            db.refresh(db_bank_transaction)
        
        return db_bank_transactions
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    finally:
        # Clean up the uploaded file
        cleanup_upload(file_path)

@router.post("/bulk", response_model=List[BankTransactionOut])
def create_bank_transactions(
    bank_transactions: List[BankTransactionCreate],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_bank_transactions = []
    for bank_transaction in bank_transactions:
        db_bank_transaction = models.BankTransaction(**bank_transaction.dict(), owner_id=current_user.id)
        db.add(db_bank_transaction)
        db_bank_transactions.append(db_bank_transaction)
    
    db.commit()
    for db_bank_transaction in db_bank_transactions:
        db.refresh(db_bank_transaction)
    
    return db_bank_transactions

@router.get("/", response_model=List[BankTransactionOut])
def read_bank_transactions(
    skip: int = 0,
    limit: int = 100,
    filter_type: Optional[str] = Query(None, description="Type of filter (date, month, week, year)"),
    filter_value: Optional[str] = Query(None, description="Value for the filter"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    query = db.query(models.BankTransaction).filter(models.BankTransaction.owner_id == current_user.id)

    if filter_type and filter_value:
        if filter_type == "date":
            try:
                filter_date = datetime.strptime(filter_value, "%Y-%m-%d").date()
                query = query.filter(models.BankTransaction.date == filter_date)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
        elif filter_type == "month":
            try:
                filter_month = datetime.strptime(filter_value, "%Y-%m").month
                filter_year = datetime.strptime(filter_value, "%Y-%m").year
                query = query.filter(
                    extract('month', models.BankTransaction.date) == filter_month,
                    extract('year', models.BankTransaction.date) == filter_year
                )
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid month format. Use YYYY-MM.")
        elif filter_type == "year":
            try:
                filter_year = int(filter_value)
                query = query.filter(extract('year', models.BankTransaction.date) == filter_year)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid year format. Use YYYY.")
        elif filter_type == "week":
            try:
                filter_year, filter_week = map(int, filter_value.split('-'))
                # This is a basic week filter, for more robust week filtering, consider ISO week dates or date ranges.
                # For simplicity, we'll check if the date falls within that week.
                # A more precise implementation would calculate the start and end of the week.
                start_of_week = date.fromisocalendar(filter_year, filter_week, 1)
                end_of_week = date.fromisocalendar(filter_year, filter_week, 7)
                query = query.filter(models.BankTransaction.date.between(start_of_week, end_of_week))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid week format. Use YYYY-WW (e.g., 2023-01).")
        else:
            raise HTTPException(status_code=400, detail="Invalid filter_type. Must be date, month, week, or year.")

    return query.offset(skip).limit(limit).all()

@router.get("/{bank_transaction_id}", response_model=BankTransactionOut)
def read_bank_transaction(bank_transaction_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    bank_transaction = db.query(models.BankTransaction).filter(models.BankTransaction.id == bank_transaction_id, models.BankTransaction.owner_id == current_user.id).first()
    if not bank_transaction:
        raise HTTPException(status_code=404, detail="Bank transaction not found")
    return bank_transaction

@router.put("/{bank_transaction_id}", response_model=BankTransactionOut)
def update_bank_transaction(bank_transaction_id: int, bank_transaction: BankTransactionCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_bank_transaction = db.query(models.BankTransaction).filter(models.BankTransaction.id == bank_transaction_id, models.BankTransaction.owner_id == current_user.id).first()
    if not db_bank_transaction:
        raise HTTPException(status_code=404, detail="Bank transaction not found")
    for key, value in bank_transaction.dict().items():
        setattr(db_bank_transaction, key, value)
    db.commit()
    db.refresh(db_bank_transaction)
    return db_bank_transaction

@router.delete("/{bank_transaction_id}")
def delete_bank_transaction(bank_transaction_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_bank_transaction = db.query(models.BankTransaction).filter(models.BankTransaction.id == bank_transaction_id, models.BankTransaction.owner_id == current_user.id).first()
    if not db_bank_transaction:
        raise HTTPException(status_code=404, detail="Bank transaction not found")
    db.delete(db_bank_transaction)
    db.commit()
    return {"ok": True}

@router.get("/unmatched/report")
async def generate_unmatched_report(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Get unmatched bank transactions
    unmatched_bank_transactions = db.query(models.BankTransaction).filter(
        models.BankTransaction.owner_id == current_user.id,
        models.BankTransaction.is_matched == False
    ).all()
    
    # Get unmatched regular transactions
    unmatched_transactions = db.query(models.Transaction).filter(
        models.Transaction.owner_id == current_user.id,
        models.Transaction.matched == False
    ).all()
    
    # Create DataFrames
    bank_df = pd.DataFrame([{
        'Date': tx.date,
        'Description': tx.description,
        'Amount': tx.amount,
        'Bank Name': tx.bank_name,
        'Account Number': tx.account_number,
        'Type': 'Bank Transaction'
    } for tx in unmatched_bank_transactions])
    
    transaction_df = pd.DataFrame([{
        'Date': tx.date,
        'Description': tx.note or tx.category,
        'Amount': tx.amount,
        'Category': tx.category,
        'Type': tx.type,
        'Type': 'User Transaction'
    } for tx in unmatched_transactions])
    
    # Create Excel writer
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"unmatched_transactions_{current_user.id}_{timestamp}.xlsx"
    filepath = os.path.join("backend", "reports", filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with pd.ExcelWriter(filepath) as writer:
        bank_df.to_excel(writer, sheet_name='Unmatched Bank Transactions', index=False)
        transaction_df.to_excel(writer, sheet_name='Unmatched User Transactions', index=False)
        
        # Add summary sheet
        summary_data = {
            'Metric': ['Total Unmatched Bank Transactions', 'Total Unmatched User Transactions'],
            'Count': [len(unmatched_bank_transactions), len(unmatched_transactions)]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
    
    return FileResponse(
        path=filepath,
        filename=filename,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ) 