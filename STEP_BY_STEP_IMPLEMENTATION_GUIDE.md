# Banking Web Application — Step-by-Step Implementation Guide

> **Plain-English instructions only.**  
> This guide explains *what* to build and *how the logic works* at each step — not the actual code.  
> Refer to [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) for architecture decisions and folder structure.

---

## Table of Contents

1. [Environment Setup](#1-environment-setup)
2. [Backend Implementation](#2-backend-implementation)
3. [Frontend Implementation](#3-frontend-implementation)
4. [Integration Steps](#4-integration-steps)
5. [Validation Rules](#5-validation-rules)
6. [Testing](#6-testing)
7. [Deployment](#7-deployment)

---

## 1. Environment Setup

### 1.1 Prerequisites Check

Before writing a single line, confirm the following are installed on your machine:

- **Python 3.8 or higher** — verify by running `python --version` in a terminal.
- **pip** — Python's package manager; usually bundled with Python.
- **A modern web browser** — Chrome, Firefox, or Edge.
- **A code editor** — VS Code is recommended.

---

### 1.2 Create the Project Folder Structure

Manually create the following directories inside the `banking_workshop/` workspace:

```
banking_workshop/
├── FRONTEND/
│   ├── templates/
│   └── static/
│       ├── css/
│       └── images/
└── BACKEND/
```

This mirrors the folder layout defined in the Implementation Plan. The `FRONTEND/templates/` folder is where Flask will look for HTML files. The `BACKEND/` folder will hold all Python files and the database.

---

### 1.3 Create and Activate a Virtual Environment

A virtual environment isolates your project's Python packages from the rest of your system so that different projects never conflict with each other.

**Steps:**
1. Open a terminal and navigate to the `BACKEND/` folder.
2. Create a virtual environment by running the `python -m venv` command and giving it a name — conventionally `venv`.
3. Activate the virtual environment:
   - On **Windows**: run the `activate` script inside `venv\Scripts\`.
   - On **Mac/Linux**: run `source venv/bin/activate`.
4. Once active, your terminal prompt will show the environment name in parentheses, e.g. `(venv)`.

Always activate the virtual environment before running or testing the application.

---

### 1.4 Create and Populate `requirements.txt`

Inside `BACKEND/`, create a plain text file named `requirements.txt`. List each dependency on its own line:

- **Flask** — the web framework that handles routing, templates, and sessions.
- **Werkzeug** — bundled with Flask; used for password hashing utilities.

No other external packages are needed. The `sqlite3` module is built into Python and requires no installation.

---

### 1.5 Install Dependencies

With the virtual environment active, run `pip install -r requirements.txt` from inside the `BACKEND/` folder. pip will download and install Flask and its dependencies. Confirm installation succeeded by importing Flask in a quick Python REPL check.

---

### 1.6 Verify Flask is Working

Create a temporary `app.py` with the absolute minimum: instantiate a Flask app and define one route at `/` that returns the text "Flask is running". Run it with `flask run` (or `python app.py`) and open `http://127.0.0.1:5000` in your browser. If you see the text, the environment is correctly set up. You can then delete or replace that placeholder route.

---

## 2. Backend Implementation

### 2.1 Application Entry Point — `app.py`

`app.py` is the heart of the backend. Its responsibilities are:

1. **Create the Flask app instance** — this object wires everything together.
2. **Set a secret key** — Flask needs a secret key to sign session cookies. Use any long, random string. Without this, sessions will not work.
3. **Tell Flask where to find templates** — point it to `FRONTEND/templates/` using the `template_folder` parameter when creating the app instance.
4. **Tell Flask where to find static files** — point it to `FRONTEND/static/` using `static_folder`.
5. **Register all routes** — import and attach routes from `auth.py` and the transaction handlers.
6. **Call `init_db()`** — invoke the database initialisation function on startup so the tables and seed data exist before any request arrives.
7. **Run the development server** — at the bottom, add the standard `if __name__ == "__main__"` guard and call `app.run(debug=True)`.

---

### 2.2 Database Layer — `database.py`

This module owns everything related to the SQLite connection and initial data. Its logic:

1. **Define the database file path** — build an absolute path to `banking.db` inside the `BACKEND/` folder. Using an absolute path prevents errors when Flask is started from a different working directory.
2. **`get_connection()` function** — opens and returns a connection to the SQLite file. Set `row_factory = sqlite3.Row` so that query results can be accessed by column name (like a dictionary) rather than by index number.
3. **`init_db()` function** — this runs once at startup:
   - Creates the `customers` table if it does not already exist. The table stores: a unique ID, a username, a hashed password, and a balance.
   - Checks whether any rows already exist. If the table is empty, it inserts seed accounts. Hash each seed password using Werkzeug's `generate_password_hash` before inserting — never store plain-text passwords.
4. **No migration logic needed** — the `CREATE TABLE IF NOT EXISTS` pattern is sufficient for this project.

---

### 2.3 Authentication — `auth.py`

This module handles all identity and session concerns.

#### Login Logic
1. When the browser sends a GET request to `/login`, simply render the login form.
2. When the browser sends a POST request to `/login` (form submitted):
   - Read the `username` and `password` fields from the form data.
   - Query the database for a customer record matching the submitted username.
   - If no record is found, send the user back to the login page with an "Invalid credentials" message.
   - If a record is found, use Werkzeug's `check_password_hash` to compare the submitted password against the stored hash.
   - If the hash check fails, send the user back with the same generic "Invalid credentials" message. (Do not reveal whether the username or password was wrong — this prevents user-enumeration attacks.)
   - If the hash check passes, store the customer's ID and username in `flask.session` and redirect to `/dashboard`.

#### Logout Logic
1. The logout route accepts a GET request at `/logout`.
2. It calls `session.clear()` to remove all session data.
3. It then redirects the user to `/login`.

#### Session Guard — `login_required` Decorator
1. Write a Python decorator function named `login_required`.
2. Inside it, check whether `'user_id'` exists in `flask.session`.
3. If not present, redirect the request to `/login` immediately, without executing the protected route.
4. If present, allow the request to continue normally.
5. Apply this decorator to every route except `/login` and `/logout`.

---

### 2.4 Account Management — `account.py`

This module is a pure logic layer — it does not handle HTTP requests directly. It provides reusable functions called by the route handlers.

#### `get_balance(user_id)`
- Opens a database connection.
- Queries the `customers` table for the row matching `user_id`.
- Returns the balance value as a number.

#### `deposit(user_id, amount)`
- Receives the customer's ID and the amount to add.
- Reads the current balance.
- Adds the amount to the current balance.
- Writes the new balance back to the database.
- Returns the updated balance so the caller can display it.

#### `withdraw(user_id, amount)`
- Receives the customer's ID and the amount to deduct.
- Reads the current balance.
- Checks that the requested amount does not exceed the current balance. If it does, raise a descriptive exception or return an error signal — do not modify the database.
- If the check passes, subtracts the amount and writes the new balance back.
- Returns the updated balance.

---

### 2.5 Route Handlers — Transaction Routes in `app.py`

#### Dashboard Route (`/dashboard`)
- Decorated with `@login_required`.
- Reads `user_id` from the session.
- Calls `account.get_balance(user_id)` to retrieve the current balance.
- Retrieves the customer's display name from the session or re-queries the database.
- Renders `dashboard.html`, passing the customer name and balance as template variables.

#### Deposit Route (`/deposit`)
- Decorated with `@login_required`.
- **GET request** — render `deposit.html` with the current balance pre-filled for context.
- **POST request**:
  1. Read the `amount` field from the form.
  2. Convert it to a float and validate (see Section 5).
  3. If valid, call `account.deposit(user_id, amount)`.
  4. Use Flask's `flash()` to set a success message like "Deposit successful. New balance: £X".
  5. Redirect to `/dashboard`.
  6. If invalid, re-render the deposit form with an inline error message.

#### Withdraw Route (`/withdraw`)
- Decorated with `@login_required`.
- **GET request** — render `withdraw.html` with the current balance shown.
- **POST request**:
  1. Read the `amount` field from the form.
  2. Convert it to a float and validate (see Section 5).
  3. Call `account.withdraw(user_id, amount)`.
  4. If withdrawal succeeds, flash a success message and redirect to `/dashboard`.
  5. If insufficient funds, re-render the withdraw form with an "Insufficient funds" error message.

---

### 2.6 Session Management

Flask sessions use a signed cookie stored in the browser. The server never stores session data — it stores the secret key used to sign (and verify) the cookie.

Key points:
- The `secret_key` on the Flask app must be set before sessions are used.
- Store only lightweight, non-sensitive data in the session: `user_id` and `username` are fine; never put the password or full account data there.
- When the user logs out, call `session.clear()` — this removes all keys. Do not just delete `user_id`; clear everything.
- Flask sessions persist as long as the browser tab/cookie is open. Closing the browser does not automatically clear the session unless you set `SESSION_PERMANENT = False` and the session is configured as non-permanent.

---

### 2.7 Error Handling

Keep error handling minimal and user-friendly:

- **Invalid form input** (non-numeric amount, empty field) — catch the conversion error (e.g., `ValueError` when casting to float), set an error message, and re-render the form. Do not let a raw exception reach the browser.
- **Insufficient funds** — this is a business rule violation, not a crash. Return an error message on the form page.
- **Unauthenticated access** — handled by the `login_required` decorator; no additional try/except needed.
- **Database errors** — for this project scope, let SQLite errors propagate to Flask's default error page (a 500 page). Adding full database error recovery is out of scope.
- Flask's `debug=True` mode will show a detailed error page in development. **Turn this off before any production use.**

---

## 3. Frontend Implementation

### 3.1 Shared Layout Principles

All pages share the same visual conventions:
- Load Bootstrap from a CDN link in the `<head>` of each HTML file. No local Bootstrap installation is needed.
- Use a Bootstrap `container` class to centre content and provide responsive margins.
- Use Bootstrap's grid system (`row` / `col`) for two-column or centred single-column layouts.
- Flash messages from Flask should be displayed in a Bootstrap `alert` component at the top of the page body (above the main content).
- Each page should have a consistent page title in the browser tab using the `<title>` tag.

---

### 3.2 Login Page — `login.html`

**Purpose:** Collect username and password, then POST them to `/login`.

Layout logic:
1. Centre a card or panel on the page — a `col-md-4 offset-md-4` grid or a flexbox-centred container works well.
2. Place the bank name / logo at the top of the card.
3. Add a Bootstrap `form` with two input fields: one for username (type `text`) and one for password (type `password`). Both must have `name` attributes matching what the backend reads from `request.form`.
4. Add a submit button styled as a Bootstrap `btn btn-primary`.
5. If the backend passes an error variable to the template, display it in a Bootstrap `alert-danger` above the form.
6. The form's `action` should point to `/login` and the `method` must be `POST`.

---

### 3.3 Dashboard Page — `dashboard.html`

**Purpose:** Show the customer's name, current balance, and navigation options.

Layout logic:
1. Add a top navigation bar using Bootstrap's `navbar` component. Include the bank name on the left and a "Logout" link on the right that links to `/logout`.
2. In the main body, greet the customer by name using the Jinja2 variable injected by Flask (e.g., `{{ username }}`).
3. Display the current balance prominently — use a large Bootstrap `card` or `jumbotron`-style block. Format the balance as currency (e.g., `$1,250.00`).
4. Below the balance, add two call-to-action buttons: "Deposit" linking to `/deposit` and "Withdraw" linking to `/withdraw`.
5. Display any flash messages (success/error from a previous transaction) at the top of the content area.

---

### 3.4 Deposit Page — `deposit.html`

**Purpose:** Accept a deposit amount from the customer.

Layout logic:
1. Show the current balance at the top so the customer has context before entering an amount.
2. Provide a single numeric input field for the deposit amount. Set `type="number"` with a `min` of `0.01` and a `step` of `0.01` for basic browser-level validation.
3. Add a submit button labelled "Deposit".
4. Add a "Back to Dashboard" link so the customer can cancel.
5. Display any validation error messages inline above or below the input field.
6. The form must POST to `/deposit`.

---

### 3.5 Withdraw Page — `withdraw.html`

**Purpose:** Accept a withdrawal amount from the customer.

Layout logic — nearly identical to the deposit page:
1. Show the current balance prominently so the customer knows the maximum they can withdraw.
2. Provide a single numeric input field for the withdrawal amount (`type="number"`, `min="0.01"`, `step="0.01"`).
3. Optionally, add an HTML5 `max` attribute equal to the current balance (injected via Jinja2) to catch over-withdrawals in the browser before the form is even submitted.
4. Add a submit button labelled "Withdraw".
5. Add a "Back to Dashboard" link.
6. Display "Insufficient funds" or other error messages inline if the backend returns them.
7. The form must POST to `/withdraw`.

---

### 3.6 Bootstrap Layout Best Practices

- Use `container` (fixed-width, centred) for page-level wrapping, not `container-fluid` (full-width), for a cleaner bank-style look.
- Use `mb-3` / `mt-3` (margin utility classes) to space form elements without writing custom CSS.
- Use `form-control` on all `<input>` elements so Bootstrap styles them uniformly.
- Use `form-label` on all `<label>` elements.
- Use `d-grid gap-2` on a button wrapper to make submit buttons full-width on small screens.
- For balance display, `display-4` or `display-5` heading classes make numbers stand out without extra CSS.

---

## 4. Integration Steps

### 4.1 Connect Flask to the Template Folder

When creating the Flask app instance, explicitly pass the path to `FRONTEND/templates/` as the `template_folder` argument. Similarly, pass `FRONTEND/static/` as the `static_folder`. This tells Flask to look outside its default folder for both templates and static assets.

To make these paths reliable regardless of where you run Flask from, construct them using Python's `os.path` module relative to the `__file__` location of `app.py`.

---

### 4.2 Connect Flask to SQLite

The connection between Flask and SQLite is managed entirely in `database.py`. The integration contract is:

1. Every route that needs data calls `get_connection()` to receive a live connection object.
2. The route runs its query, processes the result, then closes the connection.
3. Closing the connection after every request — rather than keeping one global connection — is the safest pattern for SQLite under Flask's single-threaded development server.
4. The `init_db()` call in `app.py` ensures the database file and tables exist before Flask begins accepting requests.

---

### 4.3 Connect HTML Forms to Flask Routes

The contract between frontend and backend is the HTML `<form>` element:

- The form's `action` attribute must exactly match the Flask route URL (e.g., `/login`, `/deposit`).
- The form's `method` must be `POST` for all data-submitting forms.
- Each `<input>` field's `name` attribute must exactly match the key that the Flask handler reads from `request.form`. A mismatch here is one of the most common integration bugs — double-check both sides.

---

### 4.4 Passing Data from Flask to Templates

Flask uses Jinja2 templating. When a route calls `render_template('dashboard.html', balance=1500, username='Alice')`, those keyword arguments become available inside the template as `{{ balance }}` and `{{ username }}`.

Key integration rules:
- Always pass the balance as a raw number from Flask; format it for display inside the template using Jinja2's `| round(2)` filter or a custom format.
- Pass flash messages using Flask's `flash()` system and retrieve them in the template using `get_flashed_messages()`.
- Never hardcode data in templates — all dynamic content must be injected by the Flask route.

---

### 4.5 Protecting Routes with the Session Guard

The `login_required` decorator ties the session to route access:

1. On every request to a protected route, the decorator checks `flask.session` for a `user_id` key.
2. If it is absent, the decorator short-circuits the route and returns a redirect to `/login`.
3. If it is present, the actual route function runs and reads `session['user_id']` to know which customer it is serving.

This means the integration of auth into every route is purely declarative — just add `@login_required` above the route definition.

---

## 5. Validation Rules

Validation happens at two levels: client-side (browser, HTML attributes) and server-side (Python, before any database write). **Server-side validation is mandatory** — client-side is a convenience only, since any user can bypass browser validation.

---

### 5.1 Login Validation

| Rule | Where Enforced | Response on Failure |
|---|---|---|
| Username field must not be empty | Client (HTML `required`) + Server | Re-render login with error |
| Password field must not be empty | Client (HTML `required`) + Server | Re-render login with error |
| Username must exist in the database | Server only | "Invalid credentials" (generic) |
| Password must match the stored hash | Server only | "Invalid credentials" (generic) |

**Important:** Always use the same generic error message ("Invalid credentials") for both a missing username and a wrong password. Specific messages like "Username not found" reveal which part was wrong and help attackers enumerate valid accounts.

---

### 5.2 Balance Validation

| Rule | Where Enforced | Response on Failure |
|---|---|---|
| Balance must always be ≥ 0 | Server (`account.py`) | Reject withdrawal, return error |
| Balance is read fresh from DB before every transaction | Server | N/A — architectural requirement |

Never trust a balance value passed from the browser (e.g., a hidden form field). Always re-read it from the database on the server side immediately before processing a transaction.

---

### 5.3 Deposit Validation

| Rule | Where Enforced | Response on Failure |
|---|---|---|
| Amount field must not be empty | Client (HTML `required`) + Server | Re-render form with error |
| Amount must be a valid number | Server (`try/except` float conversion) | "Please enter a valid amount" |
| Amount must be greater than zero | Server | "Deposit amount must be positive" |
| Amount must not exceed a reasonable maximum (optional) | Server | "Amount exceeds transaction limit" |

Logic flow: Convert the raw string from the form to a float. If conversion throws a `ValueError`, it is not a number. If conversion succeeds but the value is ≤ 0, it is not a valid deposit amount.

---

### 5.4 Withdrawal Validation

| Rule | Where Enforced | Response on Failure |
|---|---|---|
| Amount field must not be empty | Client (HTML `required`) + Server | Re-render form with error |
| Amount must be a valid number | Server | "Please enter a valid amount" |
| Amount must be greater than zero | Server | "Withdrawal amount must be positive" |
| Amount must not exceed current balance | Client (HTML `max` attribute) + Server | "Insufficient funds" |

The server-side insufficient-funds check is the most critical rule. Even if the browser enforces the `max` attribute, always re-check on the server by reading the balance fresh from the database and comparing before writing.

---

## 6. Testing

### 6.1 Unit Tests

Unit tests verify individual functions in isolation — no web server, no browser, no real database needed.

**What to test in `account.py`:**
- `get_balance` returns the correct balance for a known `user_id`.
- `deposit` increases the balance by the correct amount.
- `withdraw` decreases the balance by the correct amount.
- `withdraw` raises an error (or returns a failure signal) when the amount exceeds the balance.
- `withdraw` does not write to the database if the check fails.

**What to test in `auth.py`:**
- The login function returns a failure signal when the username does not exist.
- The login function returns a failure signal when the password is wrong.
- The login function returns a success signal (and populates the session) when credentials are correct.

**How to approach it:**
Use Python's built-in `unittest` module or `pytest`. For database-dependent tests, create an in-memory SQLite database (`":memory:"`) and use it instead of the real file — this keeps tests fast and side-effect-free.

---

### 6.2 Integration Tests

Integration tests verify that Flask routes, business logic, and the database work correctly together end-to-end.

**What to test:**
- `POST /login` with valid credentials creates a session and redirects to `/dashboard`.
- `POST /login` with invalid credentials stays on the login page and shows an error.
- `GET /dashboard` without a session redirects to `/login`.
- `GET /dashboard` with a valid session returns HTTP 200 and includes the balance in the response body.
- `POST /deposit` with a valid amount updates the balance and redirects to the dashboard.
- `POST /deposit` with a zero or negative amount re-renders the form with an error.
- `POST /withdraw` with an amount ≤ balance updates the balance correctly.
- `POST /withdraw` with an amount > balance does not change the balance and returns an error.
- `GET /logout` clears the session and redirects to `/login`.

**How to approach it:**
Use Flask's built-in test client (`app.test_client()`). Configure the test to use an in-memory or temporary SQLite database. Run the test client just like a real browser — send requests and assert on the response status code, redirect target, and response body text.

---

### 6.3 Manual Testing Checklist

Run through this checklist after each development phase to confirm the full user journey works:

#### Authentication
- [ ] Navigate to `http://127.0.0.1:5000/` — confirm redirect to `/login`.
- [ ] Submit the login form with an empty username — confirm an error appears.
- [ ] Submit the login form with a wrong password — confirm an error appears.
- [ ] Submit the login form with correct credentials — confirm redirect to `/dashboard`.
- [ ] While logged in, manually navigate to `/login` — confirm redirect to `/dashboard` (optional improvement).

#### Dashboard
- [ ] After login, the correct customer name is displayed.
- [ ] The balance shown matches the seeded/expected value.
- [ ] "Deposit" and "Withdraw" buttons are visible and link to the correct pages.
- [ ] "Logout" link is visible in the navigation.

#### Deposit
- [ ] Navigate to `/deposit` — confirm the current balance is shown.
- [ ] Submit the form with the amount field empty — confirm an error.
- [ ] Submit the form with a negative number — confirm an error.
- [ ] Submit a valid positive amount — confirm the success message and updated balance on the dashboard.
- [ ] Confirm the new balance in the database matches the expected value.

#### Withdraw
- [ ] Navigate to `/withdraw` — confirm the current balance is shown.
- [ ] Submit the form with the amount field empty — confirm an error.
- [ ] Submit an amount greater than the current balance — confirm "Insufficient funds" message and no balance change.
- [ ] Submit a valid amount ≤ balance — confirm success message and updated balance.
- [ ] Confirm the new balance in the database matches the expected value.

#### Logout
- [ ] Click "Logout" — confirm redirect to `/login`.
- [ ] After logout, press the browser Back button and try to access `/dashboard` — confirm redirect back to `/login`.

---

## 7. Deployment

### 7.1 Run Locally (Development)

Follow these steps each time you want to run the application:

1. Open a terminal and navigate to the `BACKEND/` folder.
2. Activate the virtual environment (`venv\Scripts\activate` on Windows, `source venv/bin/activate` on Mac/Linux).
3. Run the application using `python app.py` or `flask run`.
4. Flask will print the local URL — typically `http://127.0.0.1:5000`.
5. Open that URL in a browser.

The database file `banking.db` is created automatically the first time the app starts, courtesy of the `init_db()` call.

To stop the server, press `Ctrl + C` in the terminal.

---

### 7.2 Production Considerations

The Flask development server (used with `debug=True` and `flask run`) is **not suitable for real users**. For any deployment beyond a local workshop, the following changes are required:

| Concern | Development Setup | Production Requirement |
|---|---|---|
| Web server | Flask built-in (`flask run`) | Use a WSGI server: Gunicorn (Linux) or Waitress (Windows) |
| Debug mode | `debug=True` | **Must be `False`** — debug mode exposes the interactive debugger |
| Secret key | Any hardcoded string | A long, randomly generated string stored as an environment variable, never in source code |
| HTTPS | Not required locally | Required in production; use a reverse proxy (Nginx, Caddy) with an SSL certificate |
| Database | Single SQLite file | SQLite is acceptable for low-traffic single-server deployments; for higher load, migrate to PostgreSQL |
| Static files | Served by Flask | Served by the reverse proxy (Nginx) directly, bypassing Python entirely for performance |
| Environment config | Hardcoded in source | Use environment variables or a `.env` file (loaded with `python-dotenv`) for all secrets and paths |

#### Minimum Steps to Deploy on a Server

1. Copy the project to the server (via git clone or file transfer).
2. Create and activate a virtual environment on the server.
3. Install dependencies from `requirements.txt`.
4. Set the `SECRET_KEY` environment variable to a strong random value.
5. Set `DEBUG=False`.
6. Install and configure Gunicorn (Linux): `gunicorn -w 4 app:app`.
7. Place Nginx in front as a reverse proxy to forward traffic to Gunicorn.
8. Obtain and configure an SSL certificate (Let's Encrypt is free).

---

*End of Step-by-Step Implementation Guide*
