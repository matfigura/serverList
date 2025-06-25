import math
from flask import Blueprint, request, jsonify, abort
from marshmallow import ValidationError
from datetime import datetime, timedelta, timezone
from flaskr.db import db
from flaskr.models.server import Server
from flaskr.models.vote import Vote
from flaskr.schemas import ServerSchema

servers_bp = Blueprint('servers', __name__, url_prefix='/servers')
server_schema        = ServerSchema()
server_update_schema = ServerSchema(partial=True)

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

@servers_bp.route('/', methods=['GET'])
def list_servers():
    # jeśli brak query params – domyślnie zwracamy płaską listę
    if not request.args:
        servers = db.session.query(Server).all()
        return jsonify([{
            'id': s.id,
            'name': s.name,
            'ip_address': s.ip_address,
            'description': s.description,
            'user_id': s.user_id
        } for s in servers])

    # inaczej – paginacja
    page     = request.args.get('page',     type=int)
    per_page = request.args.get('per_page', type=int)
    if not page or not per_page or page < 1 or per_page < 1 or per_page > 100:
        return jsonify({'message': 'Invalid pagination parameters'}), 400

    base_q = db.session.query(Server)
    total  = base_q.count()
    servers = base_q.offset((page-1)*per_page).limit(per_page).all()

    items = [{
        'id': s.id,
        'name': s.name,
        'ip_address': s.ip_address,
        'description': s.description,
        'user_id': s.user_id
    } for s in servers]

    return jsonify({
        'items':       items,
        'total':       total,
        'page':        page,
        'per_page':    per_page,
        'total_pages': math.ceil(total / per_page)
    })

@servers_bp.route('/', methods=['POST'])
def add_server():
    try:
        data = server_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 400

    new_server = Server(**data)
    db.session.add(new_server)
    db.session.commit()
    return jsonify({'message': 'Server added', 'id': new_server.id}), 201

@servers_bp.route('/<int:server_id>', methods=['GET'])
def get_server(server_id):
    s = db.session.get(Server, server_id)
    if not s:
        abort(404)
    return jsonify({
        'id': s.id,
        'name': s.name,
        'ip_address': s.ip_address,
        'description': s.description,
        'user_id': s.user_id
    })

@servers_bp.route('/<int:server_id>', methods=['PUT'])
def update_server(server_id):
    s = db.session.get(Server, server_id)
    if not s:
        abort(404)

    try:
        data = server_update_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 400

    for key, val in data.items():
        setattr(s, key, val)
    db.session.commit()
    return jsonify({'message': 'Server updated'})

@servers_bp.route('/<int:server_id>', methods=['DELETE'])
def delete_server(server_id):
    s = db.session.get(Server, server_id)
    if not s:
        abort(404)
    db.session.delete(s)
    db.session.commit()
    return jsonify({'message': 'Server deleted'})