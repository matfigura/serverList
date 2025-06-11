import os
from flask import Flask
from config.config import config_dict
from .db import db


from . import auth
from . import main_page

def create_app(config_name=None):
    app = Flask(__name__, instance_relative_config=True)

    # wybór środowiska (np. development / testing / production)
    env = config_name or os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config_dict[env])

    # ustawienia z pliku instance/config.py (opcjonalne)
    app.config.from_pyfile('config.py', silent=True)

    # utwórz folder instance, jeśli nie istnieje
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # inicjalizacja bazy danych
    db.init_app(app)

    # rejestracja blueprintów wewnętrznych
    app.register_blueprint(auth.bp)
    app.register_blueprint(main_page.bp)
    app.add_url_rule('/', endpoint='index')

    # rejestracja blueprintów z routes/
    from flaskr.routes.servers import servers_bp
    from flaskr.routes.votes import votes_bp
    from flaskr.routes.skins import skins_bp

    app.register_blueprint(servers_bp)
    app.register_blueprint(votes_bp)
    app.register_blueprint(skins_bp)

    # debugowy endpoint
    @app.route('/_debug')
    def debug_info():
        return f"ENV: {env}<br>DB: {app.config.get('SQLALCHEMY_DATABASE_URI')}"

    return app