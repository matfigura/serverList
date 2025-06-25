import os
import functools

from flask import (
    Blueprint, flash, redirect, render_template,
    request, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import (
    LoginManager, login_user, logout_user,
    login_required as flask_login_required, current_user
)
from flask_dance.contrib.google import make_google_blueprint, google

from flaskr.db import db
from flaskr.models.user import User

# ----------------------------
# 1) Flask-Login setup
# ----------------------------
bp = Blueprint('auth', __name__, url_prefix='/auth')
login_manager = LoginManager()
login_manager.login_view = "auth.login"

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# ----------------------------
# 2) Flask-Dance (Google OAuth) dev-mode flags
# ----------------------------
# Zezwalamy na HTTP i akceptujemy różne formy scope w dev-owskim środowisku
os.environ.setdefault('OAUTHLIB_INSECURE_TRANSPORT', '1')
os.environ.setdefault('OAUTHLIB_RELAX_TOKEN_SCOPE', '1')

# ----------------------------
# 3) Blueprint Google OAuth
# ----------------------------
# Używamy redirect_url, żeby po wymianie kodu OAuth trafić na nasz własny callback:
google_bp = make_google_blueprint(
    client_id=lambda: current_app.config["GOOGLE_OAUTH_CLIENT_ID"],
    client_secret=lambda: current_app.config["GOOGLE_OAUTH_CLIENT_SECRET"],
    scope=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ],
    # po fetch_token blueprint zrobi redirect do /auth/google/callback
    redirect_url="/auth/google/callback"
)

# ----------------------------
# 4) Rejestracja blueprintów
#    zrobisz to w create_app:
#       app.register_blueprint(google_bp, url_prefix='/auth')
#       app.register_blueprint(bp)
# ----------------------------

# ----------------------------
# 5) Rejestracja / logowanie lokalne
# ----------------------------
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        error = None

        if not username:
            error = 'Username is required.'
        elif not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            if User.query.filter_by(username=username).first():
                error = f"User {username} is already registered."
            else:
                new_user = User(
                    username=username,
                    email=email,
                    password=generate_password_hash(password)
                )
                db.session.add(new_user)
                db.session.commit()
                flash("Rejestracja przebiegła pomyślnie. Zaloguj się.", "success")
                return redirect(url_for("auth.login"))

        flash(error, "error")

    return render_template(
        'auth/register.html',
        google_login=url_for("google.login")
    )


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        error = None

        user = User.query.filter_by(username=username).first()
        if user is None:
            error = 'Niepoprawna nazwa użytkownika.'
        elif not check_password_hash(user.password, password):
            error = 'Niepoprawne hasło.'

        if error is None:
            login_user(user)
            flash("Zalogowano pomyślnie.", "success")
            return redirect(url_for('main_page.index'))

        flash(error, "error")

    return render_template(
        'auth/login.html',
        google_login=url_for("google.login")
    )


@bp.route('/logout')
@flask_login_required
def logout():
    logout_user()
    flash("Wylogowano.", "info")
    return redirect(url_for('main_page.index'))


# ----------------------------
# 6) Google OAuth callback
# ----------------------------
@bp.route('/google/callback')
def google_authorized():
    # jeśli nie mamy tokena, wycofujemy się do logowania
    if not google.authorized:
        flash("Nie udało się uwierzytelnić przez Google.", "error")
        return redirect(url_for("auth.login"))

    # pobieramy profil z Google
    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        flash("Błąd podczas pobierania danych z Google.", "error")
        return redirect(url_for("auth.login"))

    info      = resp.json()
    google_id = info["id"]
    email     = info.get("email")

    # wyszukujemy albo zakładamy użytkownika
    user = User.query.filter(
        (User.google_id == google_id) | (User.email == email)
    ).first()

    if not user:
        user = User(
            username=info.get("name"),
            email=email,
            password="",         # brak lokalnego hasła
            google_id=google_id
        )
        db.session.add(user)
        db.session.commit()

    # logujemy i wracamy na główną
    login_user(user)
    flash("Zalogowano przez Google.", "success")
    return redirect(url_for("main_page.index"))


# ----------------------------
# 7) Decorator login_required
# ----------------------------
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view


# ----------------------------
# 8) before_app_request (opcjonalnie)
# ----------------------------
@bp.before_app_request
def _load_user():
    # Flask-Login trzyma current_user automagicznie
    pass