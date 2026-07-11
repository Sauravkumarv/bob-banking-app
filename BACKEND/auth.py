from functools import wraps

from flask import redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from database import get_connection


# --------------------------------------------------------------------------- #
#  Session guard decorator                                                      #
# --------------------------------------------------------------------------- #

def login_required(f):
    """Redirect unauthenticated requests to the login page."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login_view'))
        return f(*args, **kwargs)
    return decorated


# --------------------------------------------------------------------------- #
#  Login                                                                        #
# --------------------------------------------------------------------------- #

def login_view():
    """Handle GET (render form) and POST (validate credentials)."""
    error = None

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # Server-side presence check
        if not username or not password:
            error = 'Please enter both username and password.'
            return render_template('login.html', error=error)

        conn = get_connection()
        customer = conn.execute(
            'SELECT * FROM customers WHERE username = ?', (username,)
        ).fetchone()
        conn.close()

        # Always use a generic message — never reveal which field was wrong
        if customer is None or not check_password_hash(customer['password'], password):
            error = 'Invalid credentials. Please try again.'
            return render_template('login.html', error=error)

        # Credentials valid — write minimal identity into the session
        session.clear()
        session['user_id'] = customer['id']
        session['username'] = customer['username']
        return redirect(url_for('dashboard'))

    return render_template('login.html', error=error)


# --------------------------------------------------------------------------- #
#  Logout                                                                       #
# --------------------------------------------------------------------------- #

def logout_view():
    """Clear the session and redirect to login."""
    session.clear()
    return redirect(url_for('login_view'))
