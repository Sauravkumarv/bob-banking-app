# SecureBank — Banking Web Application

A simple, full-stack banking web app built with **Python Flask**, **Bootstrap 5**, and **SQLite**.  
Supports customer login, balance viewing, deposits, withdrawals, and logout.

---

## Project Structure

```
banking_workshop/
├── FRONTEND/
│   ├── templates/          # Jinja2 HTML pages (login, dashboard, deposit, withdraw)
│   └── static/             # CSS overrides and images
│       ├── css/
│       └── images/
├── BACKEND/
│   ├── app.py              # Flask app factory + route registration
│   ├── auth.py             # Login/logout handlers + login_required decorator
│   ├── account.py          # Business logic: get_balance, deposit, withdraw
│   ├── database.py         # SQLite connection, table creation, seed data
│   ├── routes.py           # Dashboard, deposit, withdraw route handlers
│   ├── requirements.txt    # Python dependencies
│   └── tests/
│       ├── conftest.py     # Pytest fixtures (test client + temp DB)
│       ├── test_account.py # Unit tests for account logic
│       └── test_routes.py  # Integration tests for all Flask routes
├── IMPLEMENTATION_PLAN.md
├── STEP_BY_STEP_IMPLEMENTATION_GUIDE.md
└── README.md               # This file
```

---

## Prerequisites

- Python 3.8 or higher
- pip (bundled with Python)
- A modern web browser

---

## Setup & Run

### 1. Create and activate a virtual environment

```bash
# From the BACKEND/ folder
cd BACKEND
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the Flask development server

```bash
python app.py
```

Flask will print:
```
 * Running on http://127.0.0.1:5000
```

### 4. Open the application

Navigate to **http://127.0.0.1:5000** in your browser.

---

## Demo Accounts

Two accounts are created automatically on the first run:

| Username | Password    | Starting Balance |
|----------|-------------|-----------------|
| alice    | password123 | $5,000.00        |
| bob      | password456 | $2,500.00        |

---

## Running Tests

With the virtual environment active, from the `BACKEND/` folder:

```bash
pytest tests/ -v
```

Expected output: **37 passed**

Tests cover:
- Unit tests for `get_balance`, `deposit`, and `withdraw` (12 tests)
- Integration tests for every Flask route — login, logout, session guard, dashboard, deposit, withdraw (25 tests)

---

## Features

| Feature          | Route         | Method    |
|------------------|---------------|-----------|
| Login            | `/login`      | GET, POST |
| Dashboard        | `/dashboard`  | GET       |
| View Balance     | `/dashboard`  | GET       |
| Deposit Funds    | `/deposit`    | GET, POST |
| Withdraw Funds   | `/withdraw`   | GET, POST |
| Logout           | `/logout`     | GET       |

---

## Security Notes

- Passwords are hashed using **Werkzeug's PBKDF2-SHA256** — never stored as plain text.
- Flask sessions are **server-signed cookies**; the secret key is required to forge them.
- All protected routes are guarded by the `@login_required` decorator.
- Balance is **always re-read from the database** before a transaction — never trusted from the browser.
- Generic error messages are used for login failures to prevent user enumeration.
- `debug=True` is set only for the development server; this **must be changed** before any real deployment.

---

## Production Checklist

Before deploying to a real server:

- [ ] Set `SECRET_KEY` to a long random value via an environment variable.
- [ ] Set `debug=False` (or remove the `debug` flag entirely).
- [ ] Replace the Flask dev server with **Gunicorn** (Linux) or **Waitress** (Windows).
- [ ] Put **Nginx** in front as a reverse proxy.
- [ ] Obtain an **SSL certificate** (Let's Encrypt).
- [ ] Move credentials to a `.env` file loaded with `python-dotenv`.
