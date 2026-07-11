"""
test_routes.py — Integration tests for all Flask routes.

Each test uses the `client` fixture from conftest.py which provides a
Flask test client backed by a fresh temporary SQLite database.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


# --------------------------------------------------------------------------- #
#  Helper                                                                      #
# --------------------------------------------------------------------------- #

def login(client, username='alice', password='password123'):
    """POST to /login and return the response."""
    return client.post('/login', data={'username': username, 'password': password},
                       follow_redirects=True)


# --------------------------------------------------------------------------- #
#  Authentication tests                                                        #
# --------------------------------------------------------------------------- #

class TestLogin:
    def test_get_login_page_returns_200(self, client):
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Sign In' in response.data

    def test_valid_credentials_redirect_to_dashboard(self, client):
        response = login(client)
        assert response.status_code == 200
        assert b'Current Balance' in response.data  # Dashboard content

    def test_invalid_password_stays_on_login(self, client):
        response = client.post('/login',
                               data={'username': 'alice', 'password': 'wrongpass'},
                               follow_redirects=True)
        assert b'Invalid credentials' in response.data

    def test_unknown_username_stays_on_login(self, client):
        response = client.post('/login',
                               data={'username': 'nobody', 'password': 'anything'},
                               follow_redirects=True)
        assert b'Invalid credentials' in response.data

    def test_empty_username_shows_error(self, client):
        response = client.post('/login',
                               data={'username': '', 'password': 'password123'},
                               follow_redirects=True)
        assert b'Please enter both' in response.data

    def test_empty_password_shows_error(self, client):
        response = client.post('/login',
                               data={'username': 'alice', 'password': ''},
                               follow_redirects=True)
        assert b'Please enter both' in response.data


class TestLogout:
    def test_logout_redirects_to_login(self, client):
        login(client)
        response = client.get('/logout', follow_redirects=True)
        assert b'Sign In' in response.data

    def test_after_logout_dashboard_redirects_to_login(self, client):
        login(client)
        client.get('/logout')
        response = client.get('/dashboard', follow_redirects=True)
        assert b'Sign In' in response.data


# --------------------------------------------------------------------------- #
#  Session guard tests                                                         #
# --------------------------------------------------------------------------- #

class TestSessionGuard:
    def test_dashboard_without_session_redirects(self, client):
        response = client.get('/dashboard', follow_redirects=True)
        assert b'Sign In' in response.data

    def test_deposit_without_session_redirects(self, client):
        response = client.get('/deposit', follow_redirects=True)
        assert b'Sign In' in response.data

    def test_withdraw_without_session_redirects(self, client):
        response = client.get('/withdraw', follow_redirects=True)
        assert b'Sign In' in response.data


# --------------------------------------------------------------------------- #
#  Dashboard tests                                                             #
# --------------------------------------------------------------------------- #

class TestDashboard:
    def test_dashboard_shows_balance(self, client):
        login(client)
        response = client.get('/dashboard')
        assert response.status_code == 200
        assert b'5000' in response.data  # Seed balance for alice

    def test_dashboard_shows_username(self, client):
        login(client)
        response = client.get('/dashboard')
        assert b'alice' in response.data


# --------------------------------------------------------------------------- #
#  Deposit tests                                                               #
# --------------------------------------------------------------------------- #

class TestDeposit:
    def test_get_deposit_page_returns_200(self, client):
        login(client)
        response = client.get('/deposit')
        assert response.status_code == 200
        assert b'Deposit' in response.data

    def test_valid_deposit_increases_balance(self, client):
        login(client)
        response = client.post('/deposit', data={'amount': '500'},
                               follow_redirects=True)
        assert b'Deposit successful' in response.data
        assert b'5500' in response.data

    def test_zero_amount_shows_error(self, client):
        login(client)
        response = client.post('/deposit', data={'amount': '0'},
                               follow_redirects=True)
        assert b'greater than zero' in response.data

    def test_negative_amount_shows_error(self, client):
        login(client)
        response = client.post('/deposit', data={'amount': '-100'},
                               follow_redirects=True)
        assert b'greater than zero' in response.data

    def test_non_numeric_amount_shows_error(self, client):
        login(client)
        response = client.post('/deposit', data={'amount': 'abc'},
                               follow_redirects=True)
        assert b'valid numeric' in response.data

    def test_empty_amount_shows_error(self, client):
        login(client)
        response = client.post('/deposit', data={'amount': ''},
                               follow_redirects=True)
        assert b'valid numeric' in response.data


# --------------------------------------------------------------------------- #
#  Withdraw tests                                                              #
# --------------------------------------------------------------------------- #

class TestWithdraw:
    def test_get_withdraw_page_returns_200(self, client):
        login(client)
        response = client.get('/withdraw')
        assert response.status_code == 200
        assert b'Withdraw' in response.data

    def test_valid_withdrawal_decreases_balance(self, client):
        login(client)
        response = client.post('/withdraw', data={'amount': '1000'},
                               follow_redirects=True)
        assert b'Withdrawal successful' in response.data
        assert b'4000' in response.data

    def test_insufficient_funds_shows_error(self, client):
        login(client)
        response = client.post('/withdraw', data={'amount': '99999'},
                               follow_redirects=True)
        assert b'Insufficient funds' in response.data

    def test_exact_balance_withdrawal_succeeds(self, client):
        login(client)
        response = client.post('/withdraw', data={'amount': '5000'},
                               follow_redirects=True)
        assert b'Withdrawal successful' in response.data

    def test_zero_amount_shows_error(self, client):
        login(client)
        response = client.post('/withdraw', data={'amount': '0'},
                               follow_redirects=True)
        assert b'greater than zero' in response.data

    def test_non_numeric_amount_shows_error(self, client):
        login(client)
        response = client.post('/withdraw', data={'amount': 'xyz'},
                               follow_redirects=True)
        assert b'valid numeric' in response.data
