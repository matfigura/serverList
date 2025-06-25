import math
from flask import Blueprint, request, jsonify, abort
from marshmallow import ValidationError
from datetime import datetime, timedelta, timezone
from flaskr.db import db
from flaskr.models.vote import Vote
from flaskr.schemas import VoteSchema

votes_bp    = Blueprint('votes', __name__, url_prefix='/votes')
vote_schema = VoteSchema()

def can_vote(server_id: int, user=None, ip_address=None) -> bool:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    q = db.session.query(Vote).filter(
        Vote.server_id == server_id,
        Vote.voted_at >= cutoff
    )
    if user:
        q = q.filter(Vote.user_id == user.id)
    elif ip_address:
        q = q.filter(Vote.voter_ip == ip_address)
    else:
        return False
    return q.first() is None

@votes_bp.route('/', methods=['GET'])
def list_votes():
    if not request.args:
        votes = db.session.query(Vote).all()
        return jsonify([{
            'id': v.id,
            'server_id': v.server_id,
            'voter_ip': v.voter_ip,
            'voted_at': v.voted_at.isoformat()
        } for v in votes])

    page     = request.args.get('page',     type=int)
    per_page = request.args.get('per_page', type=int)
    if not page or not per_page or page < 1 or per_page < 1 or per_page > 100:
        return jsonify({'message': 'Invalid pagination parameters'}), 400

    base_q = db.session.query(Vote)
    total  = base_q.count()
    votes  = base_q.offset((page-1)*per_page).limit(per_page).all()

    items = [{
        'id': v.id,
        'server_id': v.server_id,
        'voter_ip': v.voter_ip,
        'voted_at': v.voted_at.isoformat()
    } for v in votes]

    return jsonify({
        'items':       items,
        'total':       total,
        'page':        page,
        'per_page':    per_page,
        'total_pages': math.ceil(total / per_page)
    })

@votes_bp.route('/', methods=['POST'])
def add_vote():
    try:
        data = vote_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 400

    server_id  = data['server_id']
    ip_address = data['ip_address']
    user       = getattr(request, 'user', None)

    if not can_vote(server_id, user=user, ip_address=ip_address):
        return jsonify({'message': 'Głos został już oddany w ciągu ostatnich 24 godzin'}), 403

    vote = Vote(
        server_id=server_id,
        voter_ip=ip_address,
        voted_at=datetime.now(timezone.utc),
        user_id=getattr(user, 'id', None)
    )
    db.session.add(vote)
    db.session.commit()
    return jsonify({'message': 'Głos zapisany', 'id': vote.id}), 201