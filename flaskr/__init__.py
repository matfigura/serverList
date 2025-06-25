import os
from flask import Flask
from config.config import config_dict
from .db import db
from . import auth, main_page

def create_app(config_name=None):
    app = Flask(__name__, instance_relative_config=True)

    # 1) wybór środowiska
    env = config_name or os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config_dict[env])
    app.config.from_pyfile('config.py', silent=True)

    # 2) utworzenie folderu instance, jeśli nie istnieje
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # 3) inicjalizacja bazy
    db.init_app(app)

    if app.config.get("ENV") == "development":
        with app.app_context():
            db.create_all()

    # 4) inicjalizacja Flask-Login
    auth.login_manager.init_app(app)

    # ========================================
    # 5) Google OAuth (Flask-Dance) – dev-mode tweaks + blueprint
    # ========================================
    # pozwalamy na http i różne scope w devel
    os.environ.setdefault('OAUTHLIB_INSECURE_TRANSPORT', '1')
    os.environ.setdefault('OAUTHLIB_RELAX_TOKEN_SCOPE', '1')

    # blueprint stworzony w flaskr/auth.py jako auth.google_bp
    # (upewnij się, że w auth.py zrobiłeś roughly:)
    #
    #   from flask_dance.contrib.google import make_google_blueprint
    #   google_bp = make_google_blueprint(
    #       client_id=os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
    #       client_secret=os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"),
    #       scope=[
    #           "openid",
    #           "https://www.googleapis.com/auth/userinfo.email",
    #           "https://www.googleapis.com/auth/userinfo.profile",
    #       ],
    #       redirect_to="main_page.index",
    #   )
    #
    # i zaimportowałeś go w __init__.py modułu auth:
    #   from .auth import bp as auth_bp, google_bp

    app.register_blueprint(auth.google_bp, url_prefix='/auth')
    # ========================================

    # 6) rejestracja blueprintu naszego "tradycyjnego" auth
    app.register_blueprint(auth.bp)

    # 7) rejestracja głównej strony
    app.register_blueprint(main_page.bp)
    app.add_url_rule('/', endpoint='index')

    # 8) rejestracja REST API blueprintów
    from flaskr.routes.servers import servers_bp
    from flaskr.routes.votes  import votes_bp
    from flaskr.routes.skins  import skins_bp

    app.register_blueprint(servers_bp)
    app.register_blueprint(votes_bp)
    app.register_blueprint(skins_bp)

    # 9) debugowy endpoint
    @app.route('/_debug')
    def debug_info():
        return f"ENV: {env}<br>DB: {app.config.get('SQLALCHEMY_DATABASE_URI')}"

    return app