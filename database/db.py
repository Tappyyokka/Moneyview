import os

# Detect environment
RUNNING_ON_EC2 = os.path.exists("/home/ubuntu")

# -----------------------------
# EC2 → Use AWS RDS (MySQL)
# -----------------------------
if RUNNING_ON_EC2:
    import mysql.connector

    def get_db_connection():
        conn = mysql.connector.connect(
            host="moneyview-db.cvs02umqsh39.ap-south-1.rds.amazonaws.com",
            user="admin",
            password="",
            database="moneyview"
        )
        return conn

# -----------------------------
# Local machine → Use SQLite
# -----------------------------
else:
    import sqlite3

    def get_db_connection():
        conn = sqlite3.connect("moneyview.db")
        conn.row_factory = sqlite3.Row
        return conn


def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    # Financial data table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS financial_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,

        monthly_income REAL DEFAULT 0,
        additional_income REAL DEFAULT 0,
        annual_income REAL DEFAULT 0,
        bonus_income REAL DEFAULT 0,

        housing REAL DEFAULT 0,
        food REAL DEFAULT 0,
        transportation REAL DEFAULT 0,
        utilities REAL DEFAULT 0,
        entertainment REAL DEFAULT 0,
        other_expenses REAL DEFAULT 0,

        current_savings REAL DEFAULT 0,
        monthly_savings REAL DEFAULT 0,
        stocks_investments REAL DEFAULT 0,
        crypto_value REAL DEFAULT 0,
        property_value REAL DEFAULT 0,

        total_loan REAL DEFAULT 0,
        monthly_emi REAL DEFAULT 0,
        cc_debt REAL DEFAULT 0,
        other_liabilities REAL DEFAULT 0,

        savings_goal REAL DEFAULT 0,
        major_purchase TEXT,
        priority TEXT,

        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    cursor.close()
    conn.close()