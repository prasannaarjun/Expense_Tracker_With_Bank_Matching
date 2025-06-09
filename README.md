# Expense Tracker With Bank Matching

## Project Overview

This project is a personal finance application designed to help users manage their expenses and income, with a unique feature for matching manual transactions with bank statements. It provides a robust backend API for data management and a modern, responsive frontend for an intuitive user experience.

## Features

*   **User Authentication:** Secure user registration, login, and session management.
*   **Transaction Management:** Create, read, update, and delete personal income and expense transactions.
*   **Bank Transaction Management:** Import bank statements (CSV), view, edit, and delete bank transactions.
*   **Bank Transaction Matching:** A dedicated interface to manually match imported bank transactions with user-recorded transactions.
*   **Filtering and Reporting:** Filter transactions by date, month, week, and year. Generate downloadable reports of unmatched bank and regular transactions.
*   **Data Persistence:** Transactions and user data are stored in a PostgreSQL database.

## Tech Stack

### Backend

*   **Framework:** FastAPI (Python)
*   **Database:** PostgreSQL
*   **ORM:** SQLAlchemy 2.0
*   **Authentication:** JWT (JSON Web Tokens)
*   **Dependency Management:** Pipenv
*   **Data Processing:** Pandas (for CSV parsing and report generation)
*   **Migrations:** Alembic

### Frontend

*   **Framework:** React with Vite
*   **State Management/Data Fetching:** React Query (TanStack Query) v5
*   **Routing:** React Router DOM v6
*   **UI Library:** Material-UI (MUI v5)
*   **HTTP Client:** Axios
*   **Styling:** Custom theme with Material-UI

## Setup Instructions

Follow these steps to get the project up and running on your local machine.

### Prerequisites

Ensure you have the following installed:

*   **Python 3.9+**
*   **Node.js (LTS version)** and **npm**
*   **PostgreSQL** database server
*   **pipenv** (Python package manager): `pip install pipenv`

### 1. Backend Setup

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Install Python dependencies:**
    ```bash
    pipenv install
    ```

3.  **Set up Environment Variables:**
    Create a `.env` file in the `backend` directory with the following content:
    ```
    DATABASE_URL="postgresql://user:password@host:port/dbname"
    SECRET_KEY="your_super_secret_key_here"
    ALGORITHM="HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    ```
    *   Replace `user`, `password`, `host`, `port`, and `dbname` with your PostgreSQL database credentials.
    *   Generate a strong `SECRET_KEY` (e.g., using `openssl rand -hex 32`).

4.  **Run database migrations:**
    Activate the pipenv shell and then run alembic migrations:
    ```bash
    pipenv shell
    alembic upgrade head
    exit
    ```
    *If you encounter issues with alembic, ensure it's installed and configured correctly.*

5.  **Run the Backend Server:**
    ```bash
    pipenv run uvicorn main:app --reload
    ```
    The backend API will be running at `http://localhost:8000` (or your configured port).

### 2. Frontend Setup

1.  **Navigate to the frontend directory:**
    ```bash
    cd front
    ```

2.  **Install Node.js dependencies:**
    ```bash
    npm install
    ```

3.  **Set up Environment Variables:**
    Create a `.env` file in the `front` directory with the following content:
    ```
    VITE_API_URL="http://localhost:8000/api"
    ```
    *   Ensure this URL matches the address where your backend API is running.

4.  **Run the Frontend Development Server:**
    ```bash
    npm run dev
    ```
    The frontend application will be available at `http://localhost:5173` (or your configured port).

## Usage

1.  Ensure both the backend and frontend development servers are running.
2.  Open your web browser and navigate to `http://localhost:5173`.
3.  Register a new user or log in with existing credentials.
4.  Start managing your transactions and matching bank statements!

## Project Structure

```
.gitignore
README.md
requirements.txt

backend/
├── alembic/                  # Database migrations
├── routers/                  # API endpoints (auth, transactions, bank_transactions, matching)
├── schemas/                  # Pydantic models for data validation
├── utils/                    # Utility functions (e.g., bank_parser)
├── main.py                   # Main FastAPI application
├── models.py                 # SQLAlchemy models
├── database.py               # Database session management
├── auth.py                   # Authentication utilities
├── config.py                 # Configuration settings
├── reports/                  # Generated reports
├── uploads/                  # Uploaded files
└── Pipfile                   # Pipenv dependency file

front/
├── public/                   # Static assets
├── src/
│   ├── api/                  # API client setup
│   ├── components/           # Reusable UI components
│   ├── contexts/             # React Contexts (e.g., AuthContext)
│   ├── pages/                # Application pages (auth, transactions, bank-transactions, matching)
│   ├── styles/               # Global styles and theme configuration
│   ├── vite-env.d.ts
│   ├── App.tsx               # Main application component and routing
│   ├── main.tsx              # React entry point
│   └── theme.ts              # Material-UI theme definition
├── index.html                # Main HTML file
├── package.json              # Node.js dependencies and scripts
├── tsconfig.json             # TypeScript configuration
├── tsconfig.node.json        # TypeScript configuration for Node environment
└── vite.config.ts            # Vite configuration
``` 