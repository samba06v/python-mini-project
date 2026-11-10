"""Shared SQLite connection and database initialization helpers."""

import sqlite3
from pathlib import Path


DATABASE_PATH = Path(__file__).resolve().parent / "finance.db"


def get_connection():
    """Return a connection to the project's finance.db file."""
    return sqlite3.connect(DATABASE_PATH)


def initialize_database():
    """Create the required tables if they do not already exist."""
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT,
                amount REAL,
                category TEXT,
                description TEXT,
                date TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                amount REAL,
                month INTEGER,
                year INTEGER,
                UNIQUE(category, month, year)
            )
            """
        )
        connection.commit()
    finally:
        connection.close()
