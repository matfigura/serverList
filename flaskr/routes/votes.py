from flask import Blueprint
from datetime import datetime, timedelta, timezone
from flaskr.db import db
from flaskr.models.vote import Vote

votes_bp = Blueprint('votes', __name__, url_prefix='/votes')


@votes_bp.route('/')
def list_votes():
    return "Lista głosów"


def can_vote(server_id: int, user=None, ip_address=None) -> bool:
    """Sprawdza, czy użytkownik lub IP może zagłosować (1 raz na 24h)."""
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)

    query = db.session.query(Vote).filter(
        Vote.server_id == server_id,
        Vote.voted_at >= cutoff_time
    )

    if user:
        query = query.filter(Vote.user_id == user.id)
    elif ip_address:
        query = query.filter(Vote.voter_ip == ip_address)
    else:
        return False  # brak danych = brak zgody

    return not query.first()