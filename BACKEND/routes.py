from flask import flash, redirect, render_template, request, session, url_for

import account


def register_routes(app, login_required):
    """Register dashboard, deposit, and withdraw routes on the Flask app."""

    # ----------------------------------------------------------------------- #
    #  Dashboard                                                                #
    # ----------------------------------------------------------------------- #

    @app.route('/dashboard')
    @login_required
    def dashboard():
        user_id = session['user_id']
        username = session['username']
        balance = account.get_balance(user_id)
        return render_template('dashboard.html', username=username, balance=balance)

    # ----------------------------------------------------------------------- #
    #  Deposit                                                                  #
    # ----------------------------------------------------------------------- #

    @app.route('/deposit', methods=['GET', 'POST'])
    @login_required
    def deposit():
        user_id = session['user_id']
        error = None
        balance = account.get_balance(user_id)

        if request.method == 'POST':
            raw = request.form.get('amount', '').strip()

            # Validate: non-empty and numeric
            try:
                amount = float(raw)
            except ValueError:
                error = 'Please enter a valid numeric amount.'
                return render_template('deposit.html', balance=balance, error=error)

            # Validate: must be positive
            if amount <= 0:
                error = 'Deposit amount must be greater than zero.'
                return render_template('deposit.html', balance=balance, error=error)

            new_balance = account.deposit(user_id, amount)
            flash(f'Deposit successful! New balance: ${new_balance:,.2f}', 'success')
            return redirect(url_for('dashboard'))

        return render_template('deposit.html', balance=balance, error=error)

    # ----------------------------------------------------------------------- #
    #  Withdraw                                                                 #
    # ----------------------------------------------------------------------- #

    @app.route('/withdraw', methods=['GET', 'POST'])
    @login_required
    def withdraw():
        user_id = session['user_id']
        error = None
        balance = account.get_balance(user_id)

        if request.method == 'POST':
            raw = request.form.get('amount', '').strip()

            # Validate: non-empty and numeric
            try:
                amount = float(raw)
            except ValueError:
                error = 'Please enter a valid numeric amount.'
                return render_template('withdraw.html', balance=balance, error=error)

            # Validate: must be positive
            if amount <= 0:
                error = 'Withdrawal amount must be greater than zero.'
                return render_template('withdraw.html', balance=balance, error=error)

            # Validate: must not exceed current balance (re-read from DB — never trust browser)
            try:
                new_balance = account.withdraw(user_id, amount)
            except ValueError as exc:
                error = str(exc)
                # Re-read balance after failed attempt (balance unchanged, but keep consistent)
                balance = account.get_balance(user_id)
                return render_template('withdraw.html', balance=balance, error=error)

            flash(f'Withdrawal successful! New balance: ${new_balance:,.2f}', 'success')
            return redirect(url_for('dashboard'))

        return render_template('withdraw.html', balance=balance, error=error)
