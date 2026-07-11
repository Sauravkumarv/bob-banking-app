# Banking Web Application — Build Plan

> Reference documents: `IMPLEMENTATION_PLAN.md`, `STEP_BY_STEP_IMPLEMENTATION_GUIDE.md`
> All implementation follows the architecture and folder structure defined in those documents.

---

## Top-Level Overview

Build a full-stack banking web app using:
- **Frontend**: HTML + Bootstrap (Jinja2 templates) in `FRONTEND/`
- **Backend**: Python Flask in `BACKEND/`
- **Database**: SQLite (`banking.db`) stored in `BACKEND/`

Six features: Login, Dashboard, View Balance, Deposit, Withdraw, Logout.

Phases execute sequentially; each is independently reviewable.

---

## Sub-Task 1 — Project Scaffolding & Environment

**Intent:** Create the physical folder structure, `requirements.txt`, and confirm Flask starts.

**Expected Outcomes:**
- `FRONTEND/templates/`, `FRONTEND/static/css/`, `FRONTEND/static/images/` directories exist (with `.gitkeep` placeholders).
- `BACKEND/requirements.txt` exists with Flask listed.
- `BACKEND/app.py` exists as a minimal Flask app that returns "Flask is running" at `/`.
- Running `python BACKEND/app.py` starts the dev server without errors.

**Todo List:**
1. Create all required directories with placeholder files.
2. Write `BACKEND/requirements.txt` with `Flask` and `Werkzeug`.
3. Write minimal `BACKEND/app.py` (app factory, one placeholder route, `if __name__` guard).

**Relevant Context:**
- Folder layout: `IMPLEMENTATION_PLAN.md` Section 4
- Entry point: `STEP_BY_STEP_IMPLEMENTATION_GUIDE.md` Section 2.1

**Status:** [x] done

---

## Sub-Task 2 — Database Layer

**Intent:** Create `database.py` with connection helper, table creation, and seed data.

**Expected Outcomes:**
- `BACKEND/database.py` exists with `get_connection()` and `init_db()`.
- `init_db()` creates the `customers` table (id, username, hashed password, balance).
- Two seed customer accounts are inserted on first run (if table is empty).
- Passwords are hashed using Werkzeug's `generate_password_hash`.
- `init_db()` is called from `app.py` before the first request.

**Todo List:**
1. Write `database.py` with `get_connection()` using `sqlite3.Row` row factory.
2. Write `init_db()` with `CREATE TABLE IF NOT EXISTS` and conditional seed insert.
3. Hash seed passwords with Werkzeug before inserting.
4. Call `init_db()` inside `app.py` at startup.

**Relevant Context:**
- `STEP_BY_STEP_IMPLEMENTATION_GUIDE.md` Section 2.2
- DB file path must be absolute using `os.path` relative to `database.py`

**Status:** [x] done

---

## Sub-Task 3 — Authentication Module

**Intent:** Implement login/logout routes, password verification, and the `login_required` session guard.

**Expected Outcomes:**
- `BACKEND/auth.py` contains login handler, logout handler, and `login_required` decorator.
- `GET /login` renders `login.html`.
- `POST /login` with valid credentials creates session and redirects to `/dashboard`.
- `POST /login` with invalid credentials re-renders `login.html` with a generic error.
- `GET /logout` clears the session and redirects to `/login`.
- `login_required` redirects unauthenticated requests to `/login`.
- All protected routes decorated with `@login_required`.

**Todo List:**
1. Write `auth.py` with `login_required` decorator.
2. Write login GET/POST handler (credential lookup → hash check → session write).
3. Write logout handler (`session.clear()` → redirect).
4. Register auth Blueprint (or functions) in `app.py`.

**Relevant Context:**
- `STEP_BY_STEP_IMPLEMENTATION_GUIDE.md` Section 2.3
- Validation rules: Section 5.1 — always use generic "Invalid credentials" message

**Status:** [x] done

---

## Sub-Task 4 — Account Management Module

**Intent:** Implement `account.py` with pure business-logic functions for balance operations.

**Expected Outcomes:**
- `BACKEND/account.py` contains `get_balance(user_id)`, `deposit(user_id, amount)`, `withdraw(user_id, amount)`.
- `deposit` reads current balance, adds amount, writes back.
- `withdraw` reads current balance, enforces non-negative result, writes back or raises `ValueError`.
- No HTTP or session logic in this module — pure data logic only.

**Todo List:**
1. Write `get_balance(user_id)` — query and return balance.
2. Write `deposit(user_id, amount)` — read, add, write, return new balance.
3. Write `withdraw(user_id, amount)` — read, check, subtract, write, return new balance; raise `ValueError` on insufficient funds.

**Relevant Context:**
- `STEP_BY_STEP_IMPLEMENTATION_GUIDE.md` Section 2.4
- Validation rules: Section 5.2, 5.3, 5.4

**Status:** [x] done

---

## Sub-Task 5 — Dashboard & Transaction Routes

**Intent:** Wire up the dashboard, deposit, and withdraw routes in `app.py` using `account.py`.

**Expected Outcomes:**
- `GET /dashboard` (protected) renders `dashboard.html` with customer name and balance.
- `GET /deposit` (protected) renders `deposit.html` with current balance.
- `POST /deposit` validates amount, calls `account.deposit()`, flashes success, redirects to `/dashboard`.
- `GET /withdraw` (protected) renders `withdraw.html` with current balance.
- `POST /withdraw` validates amount, calls `account.withdraw()`, flashes success or error, redirects or re-renders.
- All validation rules from Section 5.3 and 5.4 applied server-side.

**Todo List:**
1. Add `/dashboard` route to `app.py`.
2. Add `/deposit` GET and POST routes with full validation.
3. Add `/withdraw` GET and POST routes with full validation.
4. Use Flask `flash()` for all user-facing feedback.

**Relevant Context:**
- `STEP_BY_STEP_IMPLEMENTATION_GUIDE.md` Section 2.5
- Amount validation pattern: try/except float cast → check > 0 → check ≤ balance

**Status:** [x] done

---

## Sub-Task 6 — Frontend Templates

**Intent:** Build all four HTML pages using Bootstrap via CDN and Jinja2 template variables.

**Expected Outcomes:**
- `FRONTEND/templates/login.html` — centred card, username/password form, error alert.
- `FRONTEND/templates/dashboard.html` — navbar with logout, balance display, deposit/withdraw buttons, flash messages.
- `FRONTEND/templates/deposit.html` — current balance shown, numeric input, submit, back link, error display.
- `FRONTEND/templates/withdraw.html` — current balance shown, numeric input with `max`, submit, back link, error display.
- All pages load Bootstrap from CDN and apply consistent utility classes.
- Flash messages displayed as Bootstrap `alert` components on all pages.

**Todo List:**
1. Write `login.html` with Bootstrap card layout and POST form.
2. Write `dashboard.html` with navbar, balance card, transaction buttons, flash alerts.
3. Write `deposit.html` with balance context, numeric form, validation feedback.
4. Write `withdraw.html` with balance context, numeric form with `max`, validation feedback.

**Relevant Context:**
- `STEP_BY_STEP_IMPLEMENTATION_GUIDE.md` Sections 3.1–3.6
- Jinja2 variables passed from routes: `username`, `balance`, `error`, `get_flashed_messages()`

**Status:** [x] done

---

## Sub-Task 7 — Tests

**Intent:** Add unit tests for `account.py` logic and integration tests for all Flask routes.

**Expected Outcomes:**
- `BACKEND/tests/test_account.py` — unit tests for `get_balance`, `deposit`, `withdraw` using in-memory SQLite.
- `BACKEND/tests/test_routes.py` — integration tests for every route using Flask's test client.
- All tests pass with `pytest` from the `BACKEND/` directory.

**Todo List:**
1. Create `BACKEND/tests/` directory with `__init__.py`.
2. Write `test_account.py` — test all three account functions including edge cases.
3. Write `test_routes.py` — test login success/failure, session guard, deposit/withdraw flows, logout.
4. Use in-memory SQLite and a test-specific app fixture to isolate tests from the real DB.

**Relevant Context:**
- `STEP_BY_STEP_IMPLEMENTATION_GUIDE.md` Sections 6.1, 6.2
- Use `pytest` fixtures for the Flask test client and in-memory DB setup

**Status:** [x] done

---

## Sub-Task 8 — Final Integration & Startup Instructions

**Intent:** Verify the full end-to-end flow works and produce a clear `README.md` with startup steps.

**Expected Outcomes:**
- All routes interconnect correctly (login → dashboard → deposit/withdraw → logout).
- Flash messages appear correctly after transactions.
- Accessing any protected route without a session redirects to `/login`.
- `README.md` created at project root with setup and run instructions.

**Todo List:**
1. Cross-check `app.py` route registration — ensure all blueprints/functions are wired.
2. Verify `template_folder` and `static_folder` paths are correct relative to `app.py`.
3. Write `README.md` with: prerequisites, virtual env setup, install, run, and test commands.

**Relevant Context:**
- `STEP_BY_STEP_IMPLEMENTATION_GUIDE.md` Section 4 (Integration), Section 7.1 (Local run)

**Status:** [x] done
