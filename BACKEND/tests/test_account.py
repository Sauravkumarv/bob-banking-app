"""
test_account.py — Unit tests for BACKEND/account.py

All tests use an isolated in-memory SQLite database; no Flask app or
real banking.db is required.
"""
import os
import sys
import sqlite3

import pytest
from werkzeug.security import generate_password_hash

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import account
import database


# --------------------------------------------------------------------------- #
#  Helpers                                                                     #
# --------------------------------------------------------------------------- #

def _make_db(tmp_path):
    """Create a temp SQLite file with one seeded customer and return its path."""
    db_file = str(tmp_path / 'unit_test.db')
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    conn.execute('''
        CREATE TABLE customers (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    NOT NULL UNIQUE,
            password TEXT    NOT NULL,
            balance  REAL    NOT NULL DEFAULT 0.0
        )
    ''')
    conn.execute(
        'INSERT INTO customers (username, password, balance) VALUES (?, ?, ?)',
        ('unit_user', generate_password_hash('pass'), 500.00)
    )
    conn.commit()
    conn.close()
    return db_file


# --------------------------------------------------------------------------- #
#  Tests                                                                       #
# --------------------------------------------------------------------------- #

class TestGetBalance:
    def test_returns_seeded_balance(self, monkeypatch, tmp_path):
        monkeypatch.setattr(database, 'DB_PATH', _make_db(tmp_path))
        balance = account.get_balance(1)
        assert balance == pytest.approx(500.00)

    def test_returns_float(self, monkeypatch, tmp_path):
        monkeypatch.setattr(database, 'DB_PATH', _make_db(tmp_path))
        assert isinstance(account.get_balance(1), float)


class TestDeposit:
    def test_increases_balance(self, monkeypatch, tmp_path):
        monkeypatch.setattr(database, 'DB_PATH', _make_db(tmp_path))
        new_balance = account.deposit(1, 200.00)
        assert new_balance == pytest.approx(700.00)

    def test_persists_to_db(self, monkeypatch, tmp_path):
        monkeypatch.setattr(database, 'DB_PATH', _make_db(tmp_path))
        account.deposit(1, 100.00)
        assert account.get_balance(1) == pytest.approx(600.00)

    def test_zero_amount_raises(self, monkeypatch, tmp_path):
        monkeypatch.setattr(database, 'DB_PATH', _make_db(tmp_path))
        with pytest.raises(ValueError, match='greater than zero'):
            account.deposit(1, 0)

    def test_negative_amount_raises(self, monkeypatch, tmp_path):
        monkeypatch.setattr(database, 'DB_PATH', _make_db(tmp_path))
        with pytest.raises(ValueError):
            account.deposit(1, -50)


class TestWithdraw:
    def test_decreases_balance(self, monkeypatch, tmp_path):
        monkeypatch.setattr(database, 'DB_PATH', _make_db(tmp_path))
        new_balance = account.withdraw(1, 200.00)
        assert new_balance == pytest.approx(300.00)

    def test_persists_to_db(self, monkeypatch, tmp_path):
        monkeypatch.setattr(database, 'DB_PATH', _make_db(tmp_path))
        account.withdraw(1, 100.00)
        assert account.get_balance(1) == pytest.approx(400.00)

    def test_insufficient_funds_raises(self, monkeypatch, tmp_path):
        monkeypatch.setattr(database, 'DB_PATH', _make_db(tmp_path))
        with pytest.raises(ValueError, match='Insufficient funds'):
            account.withdraw(1, 999.00)

    def test_insufficient_funds_does_not_change_balance(self, monkeypatch, tmp_path):
        monkeypatch.setattr(database, 'DB_PATH', _make_db(tmp_path))
        try:
            account.withdraw(1, 999.00)
        except ValueError:
            pass
        assert account.get_balance(1) == pytest.approx(500.00)

    def test_zero_amount_raises(self, monkeypatch, tmp_path):
        monkeypatch.setattr(database, 'DB_PATH', _make_db(tmp_path))
        with pytest.raises(ValueError):
            account.withdraw(1, 0)

    def test_exact_balance_allowed(self, monkeypatch, tmp_path):
        monkeypatch.setattr(database, 'DB_PATH', _make_db(tmp_path))
        new_balance = account.withdraw(1, 500.00)
        assert new_balance == pytest.approx(0.00)
