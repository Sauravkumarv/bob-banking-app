from database import get_connection


def get_balance(user_id: int) -> float:
    """Return the current balance for the given customer."""
    conn = get_connection()
    row = conn.execute(
        'SELECT balance FROM customers WHERE id = ?', (user_id,)
    ).fetchone()
    conn.close()
    return float(row['balance'])


def deposit(user_id: int, amount: float) -> float:
    """
    Add *amount* to the customer's balance.

    Returns the updated balance.
    Raises ValueError if amount is not positive.
    """
    if amount <= 0:
        raise ValueError('Deposit amount must be greater than zero.')

    conn = get_connection()
    current = float(conn.execute(
        'SELECT balance FROM customers WHERE id = ?', (user_id,)
    ).fetchone()['balance'])

    new_balance = current + amount
    conn.execute(
        'UPDATE customers SET balance = ? WHERE id = ?', (new_balance, user_id)
    )
    conn.commit()
    conn.close()
    return new_balance


def withdraw(user_id: int, amount: float) -> float:
    """
    Subtract *amount* from the customer's balance.

    Returns the updated balance.
    Raises ValueError if amount is not positive or exceeds the current balance.
    """
    if amount <= 0:
        raise ValueError('Withdrawal amount must be greater than zero.')

    conn = get_connection()
    current = float(conn.execute(
        'SELECT balance FROM customers WHERE id = ?', (user_id,)
    ).fetchone()['balance'])

    if amount > current:
        conn.close()
        raise ValueError('Insufficient funds.')

    new_balance = current - amount
    conn.execute(
        'UPDATE customers SET balance = ? WHERE id = ?', (new_balance, user_id)
    )
    conn.commit()
    conn.close()
    return new_balance
