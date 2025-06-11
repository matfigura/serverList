from datetime import datetime, timedelta
from flaskr.models.vote import Vote

def can_vote(server_id, user=None, ip_address=None):
    """
    Sprawdza, czy użytkownik (lub IP anonimowego) może zagłosować na dany serwer.
    Głosowanie dozwolone raz na 24 godziny.
    """
    cutoff = datetime.utcnow() - timedelta(hours=24)

    query = Vote.query.filter(
        Vote.server_id == server_id,
        Vote.voted_at >= cutoff
    )

    if user:
        query = query.filter(Vote.user_id == user.id)
    else:
        query = query.filter(Vote.voter_ip == ip_address)

    return query.count() == 0