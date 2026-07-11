import os
import sqlite3

from werkzeug.security import generate_password_hash

# Absolute path to the database file — reliable regardless of working directory
DB_PATH = os.path.join(os.path.dirname(__file__), 'banking.db')


def get_connection():
    """Return an open SQLite connection with dict-like row access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables and seed demo accounts if the database is empty."""
    conn = get_connection()
    cursor = conn.cursor()

    # Create customers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    NOT NULL UNIQUE,
            password TEXT    NOT NULL,
            balance  REAL    NOT NULL DEFAULT 0.0
        )
    ''')
    conn.commit()

    # Seed demo accounts only when the table is empty
    cursor.execute('SELECT COUNT(*) AS cnt FROM customers')
    if cursor.fetchone()['cnt'] == 0:
        seed_accounts = [
            ('alice', 'password123', 5000.00),
            ('bob',   'password456', 2500.00),
        ]
        for username, plain_password, balance in seed_accounts:
            hashed = generate_password_hash(plain_password)
            cursor.execute(
                'INSERT INTO customers (username, password, balance) VALUES (?, ?, ?)',
                (username, hashed, balance)
            )
        conn.commit()

    conn.close()
