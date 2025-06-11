def test_user_can_vote_only_once_per_24h(test_client, test_db_session):
    from datetime import datetime, timezone
    from flaskr.models import User, Server, Vote
    from flaskr.routes.votes import can_vote

    user = User(id=1, username="testuser", email="t@t.pl")
    server = Server(id=1, name="Test Server", ip_address="1.1.1.1", user_id=1, owner=user)
    vote = Vote(server=server, voter_ip="123.123.123.123", user_id=1,  voted_at=datetime.now(timezone.utc))

    test_db_session.add_all([user, server, vote])
    test_db_session.commit()

    result = can_vote(server_id=1, user=user)
    assert result is False