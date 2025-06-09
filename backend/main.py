from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
from .routers import auth, transactions, bank_transactions, matching
from . import models, database
from .auth import create_access_token, authenticate_user, get_password_hash, get_current_user, verify_password

# Create database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="HomeBudget Guard API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React app and Vite dev server URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["transactions"])
app.include_router(bank_transactions.router, prefix="/api/bank-transactions", tags=["bank-transactions"])
app.include_router(matching.router, prefix="/api/matching", tags=["matching"])

@app.get("/")
def read_root():
    return {"message": "Welcome to HomeBudget Guard API"} 