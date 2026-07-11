"""
conftest.py — shared pytest fixtures for the banking application test suite.

Provides:
  - an in-memory SQLite database that is set up fresh for each test
  - a Flask test client wired to that in-memory database
"""
import os
import sys
import sqlite3

import pytest
from werkzeug.security import generate_password_hash

# Make BACKEND modules importable when pytest is run from BACKEND/
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


# --------------------------------------------------------------------------- #
#  In-memory DB fixture                                                        #
# --------------------------------------------------------------------------- #

def build_in_memory_db():
    """Return a fresh in-memory SQLite connection with seed data."""
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    conn.execute('''
        CREATE TABLE customers (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    NOT NULL UNIQUE,
            password TEXT    NOT NULL,
            balance  REAL    NOT NULL DEFAULT 0.0
        )
    ''')
    conn.commit()
    conn.execute(
        'INSERT INTO customers (username, password, balance) VALUES (?, ?, ?)',
        ('testuser', generate_password_hash('testpass'), 1000.00)
    )
    conn.commit()
    return conn


@pytest.fixture
def mem_conn():
    """Yield an in-memory connection; close after the test."""
    conn = build_in_memory_db()
    yield conn
    conn.close()


# --------------------------------------------------------------------------- #
#  Flask test-client fixture                                                   #
# --------------------------------------------------------------------------- #

@pytest.fixture
def client(monkeypatch, tmp_path):
    """
    Yield a Flask test client backed by a temporary SQLite file.
    monkeypatch replaces database.DB_PATH so no real banking.db is touched.
    """
    tmp_db = str(tmp_path / 'test_banking.db')

    # Patch DB_PATH before the app is created
    import database
    monkeypatch.setattr(database, 'DB_PATH', tmp_db)

    from app import create_app
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as c:
        yield c
