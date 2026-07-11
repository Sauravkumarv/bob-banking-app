import os
from flask import Flask


def create_app():
    """Application factory."""
    template_dir = os.path.join(os.path.dirname(__file__), '..', 'FRONTEND', 'templates')
    static_dir = os.path.join(os.path.dirname(__file__), '..', 'FRONTEND', 'static')

    app = Flask(
        __name__,
        template_folder=os.path.abspath(template_dir),
        static_folder=os.path.abspath(static_dir),
    )

    app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # ------------------------------------------------------------------ #
    #  Database initialisation                                            #
    # ------------------------------------------------------------------ #
    from database import init_db
    init_db()

    # ------------------------------------------------------------------ #
    #  Route registration                                                 #
    # ------------------------------------------------------------------ #
    from auth import login_view, logout_view, login_required
    from routes import register_routes

    app.add_url_rule('/login',  view_func=login_view,  methods=['GET', 'POST'])
    app.add_url_rule('/logout', view_func=logout_view, methods=['GET'])
    register_routes(app, login_required)

    # Redirect bare root to login
    from flask import redirect, url_for

    @app.route('/')
    def index():
        return redirect(url_for('login_view'))

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
