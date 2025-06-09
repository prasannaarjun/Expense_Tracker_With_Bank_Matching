import pandas as pd
from typing import List, Dict
from datetime import datetime
import os

def parse_bank_csv(file_path: str) -> List[Dict]:
    """
    Parse a bank statement CSV file into a list of transactions.
    Handles common CSV formats and normalizes column names.
    """
    try:
        df = pd.read_csv(file_path)
        
        # Normalize column names
        df.columns = [col.strip().lower() for col in df.columns]
        
        # Map common column names to our standard format
        column_mapping = {
            'date': ['date', 'transaction date', 'transaction_date'],
            'description': ['description', 'details', 'transaction details', 'transaction_details', 'narration'],
            'amount': ['amount', 'transaction amount', 'transaction_amount', 'debit/credit']
        }
        
        # Find matching columns
        for standard_col, possible_names in column_mapping.items():
            for col in possible_names:
                if col in df.columns:
                    df[standard_col] = df[col]
                    break
        
        # Clean and convert amount
        df['amount'] = df['amount'].apply(lambda x: float(str(x).replace(',', '').replace('+', '').replace('-', '-')))
        
        # Convert date to standard format
        df['date'] = pd.to_datetime(df['date']).dt.date
        
        # Select and rename columns to standard format
        df = df[['date', 'description', 'amount']]
        
        return df.to_dict(orient='records')
    except Exception as e:
        raise ValueError(f"Error parsing CSV file: {str(e)}")

def cleanup_upload(file_path: str):
    """Remove the uploaded file after processing"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Error cleaning up file {file_path}: {str(e)}") 