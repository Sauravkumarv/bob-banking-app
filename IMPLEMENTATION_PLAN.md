# Banking Web Application — Implementation Plan

> **Planning document only.**  
> No database schemas, SQL scripts, API contracts, or implementation code are included.

---

## 1. Solution Overview

### Objective
Build a simple, browser-based banking web application that allows registered customers to log in, view their account balance, and perform basic fund transactions (deposit and withdrawal), then securely log out.

### Scope

| In Scope | Out of Scope |
|---|---|
| Customer login / logout | User self-registration |
| View account balance | Multi-account support |
| Deposit funds | Transfers between accounts |
| Withdraw funds | Admin / bank-staff portal |
| Session management | Payment gateway integration |
| Client-side validation | Email / SMS notifications |

### Users
- **Customer** — an authenticated bank customer who interacts with the dashboard and performs transactions.

### Functional Requirements
1. A customer can log in using a username and password.
2. After successful login, the customer lands on a personal dashboard.
3. The dashboard displays the current account balance.
4. The customer can deposit a positive amount into their account.
5. The customer can withdraw an amount up to their current balance.
6. The customer can log out, terminating the session.
7. Unauthenticated users are redirected to the login page.

### Non-Functional Requirements
- **Security** — passwords are stored as hashed values; sessions are server-managed.
- **Usability** — responsive UI using Bootstrap; works on desktop and mobile browsers.
- **Simplicity** — minimal dependencies; the entire stack runs locally without external services.
- **Maintainability** — clear folder separation between frontend and backend concerns.

### Assumptions
- A small, fixed set of customer accounts is pre-seeded in the database.
- The application runs on `localhost` for development and workshop purposes.
- A single SQLite file serves as the database; no migration tooling is required.
- Python 3.x and a modern browser are available on the target machine.

---

## 2. High-Level Architecture

### Architecture Overview

```
┌─────────────────────────────┐
│         BROWSER             │
│  HTML + Bootstrap (static)  │
│  Forms / AJAX calls         │
└────────────┬────────────────┘
             │  HTTP (GET / POST)
             ▼
┌─────────────────────────────┐
│       FLASK BACKEND         │
│  Route handlers             │
│  Session management         │
│  Business logic layer       │
└────────────┬────────────────┘
             │  Python sqlite3
             ▼
┌─────────────────────────────┐
│       SQLITE DATABASE       │
│  Single .db file            │
│  Stores customers +         │
│  account balances           │
└─────────────────────────────┘
```

### Frontend → Backend → Database Interaction

| Trigger | Frontend Action | Backend Handler | Database Operation |
|---|---|---|---|
| Page load (login) | Render login form | Serve `login.html` | — |
| Submit credentials | POST form data | Validate credentials | Read customer record |
| Dashboard load | GET dashboard | Fetch balance | Read balance |
| Deposit | POST deposit form | Update balance | Write new balance |
| Withdraw | POST withdraw form | Validate & update | Write new balance |
| Logout | GET logout link | Clear session | — |

### Request Lifecycle
1. Browser sends an HTTP request (GET or POST) to Flask.
2. Flask checks the session cookie — unauthenticated requests are redirected to `/login`.
3. The relevant route handler executes business logic (validation, calculation).
4. The handler reads from or writes to SQLite via Python's built-in `sqlite3` module.
5. Flask renders an HTML template (with injected data) and returns it to the browser.
6. Bootstrap styles the response for a responsive presentation.

---

## 3. Component Design

### Frontend Responsibilities (`FRONTEND/`)
- Provide HTML pages (templates) for: Login, Dashboard, Deposit, Withdraw.
- Apply Bootstrap for layout, form styling, and responsive grid.
- Perform basic client-side input validation (non-empty fields, positive numbers).
- Display server-injected data (balance, messages) via Flask's Jinja2 template engine.
- Show contextual feedback messages (success, error) returned from the backend.

### Backend Responsibilities (`BACKEND/`)
- **Routing** — map URL paths to Python handler functions.
- **Authentication** — verify credentials, create/destroy Flask sessions.
- **Session guard** — protect all routes except `/login`; redirect if unauthenticated.
- **Business logic** — validate deposit/withdrawal amounts; enforce balance constraints.
- **Data access** — read and write customer and balance data using `sqlite3`.
- **Template rendering** — use Jinja2 to merge data into HTML templates and return responses.

### Database Responsibilities
- Persist customer credentials (username + hashed password).
- Persist account balance per customer.
- Provide reliable read/write for single-user concurrent access (SQLite default is sufficient).
- The `.db` file is stored inside the `BACKEND/` folder for locality.

---

## 4. Folder Structure

```
banking_workshop/
├── FRONTEND/
│   ├── templates/          # Jinja2 HTML templates served by Flask
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── deposit.html
│   │   └── withdraw.html
│   └── static/
│       ├── css/            # Custom CSS overrides (Bootstrap loaded via CDN)
│       └── images/         # Optional branding assets
│
├── BACKEND/
│   ├── app.py              # Flask application entry point; route definitions
│   ├── auth.py             # Login / logout logic and session helpers
│   ├── account.py          # Balance read, deposit, withdrawal business logic
│   ├── database.py         # SQLite connection helper and seed data loader
│   ├── banking.db          # SQLite database file (auto-created on first run)
│   └── requirements.txt    # Python dependencies (Flask, etc.)
│
├── docs/                   # Workshop and setup documentation (existing)
└── IMPLEMENTATION_PLAN.md  # This document
```

### Folder Responsibility Summary

| Path | Responsibility |
|---|---|
| `FRONTEND/templates/` | HTML pages rendered by Flask / Jinja2 |
| `FRONTEND/static/` | CSS overrides and static assets |
| `BACKEND/app.py` | App factory, route registration, startup |
| `BACKEND/auth.py` | Authentication and session management |
| `BACKEND/account.py` | Transaction business logic |
| `BACKEND/database.py` | DB connection, table creation, seed data |
| `BACKEND/banking.db` | Runtime SQLite data store |
| `BACKEND/requirements.txt` | Dependency list for `pip install` |

---

## 5. Module Breakdown

### 5.1 Authentication Module (`auth.py`)
**Purpose:** Control who can access the application.

- Handles the login form submission.
- Looks up the customer by username.
- Compares the submitted password against the stored hash.
- On success: writes customer identity into the Flask session.
- On failure: returns an error message to the login page.
- Provides a logout handler that clears the session.
- Provides a session-guard decorator applied to all protected routes.

### 5.2 Dashboard Module (`app.py` + `dashboard.html`)
**Purpose:** Central landing page after login.

- Reads the authenticated customer's name and current balance from the database.
- Passes that data to the dashboard template.
- Renders navigation links to Deposit, Withdraw, and Logout.

### 5.3 Account Management Module (`account.py`)
**Purpose:** Manage account state.

- Provides a function to retrieve the current balance for a given customer.
- Provides a function to update the balance (used by both deposit and withdrawal).
- Enforces that balance never goes below zero.

### 5.4 Transactions Module (deposit & withdraw routes in `app.py`)
**Purpose:** Handle fund movements.

- **Deposit flow:** Accept a positive amount → call `account.deposit()` → redirect to dashboard with confirmation.
- **Withdrawal flow:** Accept a positive amount ≤ current balance → call `account.withdraw()` → redirect to dashboard with confirmation or error.
- Both flows validate input server-side before touching the database.

---

## 6. Implementation Roadmap

### Phase 1 — Project Scaffolding
**Goal:** Establish folder structure and verify toolchain.

- Create `FRONTEND/` and `BACKEND/` directories with placeholder files.
- Set up `requirements.txt` and install Flask.
- Confirm Flask server starts with a placeholder route.

**Depends on:** Nothing  
**Effort:** Low

---

### Phase 2 — Database Layer
**Goal:** A working SQLite store with seed data.

- Implement `database.py` with connection helper and schema creation.
- Seed one or more test customer accounts with hashed passwords and starting balances.
- Verify data is readable via a simple Python script.

**Depends on:** Phase 1  
**Effort:** Low–Medium

---

### Phase 3 — Authentication
**Goal:** Customers can log in and log out.

- Build `login.html` with Bootstrap form.
- Implement login and logout routes in `auth.py`.
- Apply session guard to all non-login routes.
- Test: correct credentials → session created; wrong credentials → error displayed; accessing `/dashboard` without session → redirect to `/login`.

**Depends on:** Phase 2  
**Effort:** Medium

---

### Phase 4 — Dashboard & Balance View
**Goal:** Authenticated customers see their balance.

- Build `dashboard.html` with Bootstrap layout.
- Implement the dashboard route to query and display balance.
- Confirm balance reflects database value.

**Depends on:** Phase 3  
**Effort:** Low–Medium

---

### Phase 5 — Deposit & Withdrawal
**Goal:** Customers can move funds.

- Build `deposit.html` and `withdraw.html` with Bootstrap forms.
- Implement `account.py` with balance read and update logic.
- Wire deposit and withdrawal routes in `app.py`.
- Test: deposit increases balance; withdrawal decreases balance; over-withdrawal is rejected.

**Depends on:** Phase 4  
**Effort:** Medium

---

### Phase 6 — Integration & Polish
**Goal:** End-to-end flow is stable and presentable.

- Connect all pages with consistent navigation.
- Add user-facing feedback messages (flash messages or inline alerts).
- Apply Bootstrap styling consistently across all pages.
- Perform end-to-end walkthrough: login → view balance → deposit → withdraw → logout.

**Depends on:** Phase 5  
**Effort:** Low–Medium

---

### Dependency Chain

```
Phase 1 ──► Phase 2 ──► Phase 3 ──► Phase 4 ──► Phase 5 ──► Phase 6
Scaffold     DB Layer     Auth         Dashboard    Transactions  Polish
```

---

*End of Implementation Plan*
