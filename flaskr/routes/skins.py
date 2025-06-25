import math
from flask import Blueprint, request, jsonify, abort
from marshmallow import ValidationError
from flaskr.db import db
from flaskr.models.skin import Skin
from flaskr.schemas import SkinSchema

skins_bp = Blueprint('skins', __name__, url_prefix='/skins')
skin_schema        = SkinSchema()
skin_update_schema = SkinSchema(partial=True)

@skins_bp.route('/', methods=['GET'])
def list_skins():
    if not request.args:
        skins = db.session.query(Skin).all()
        return jsonify([{
            'id': s.id,
            'server_id': s.server_id,
            'name': s.name,
            'image_url': s.image_url,
            'description': getattr(s, 'description', None)
        } for s in skins])

    page     = request.args.get('page',     type=int)
    per_page = request.args.get('per_page', type=int)
    if not page or not per_page or page < 1 or per_page < 1 or per_page > 100:
        return jsonify({'message': 'Invalid pagination parameters'}), 400

    base_q = db.session.query(Skin)
    total  = base_q.count()
    skins  = base_q.offset((page-1)*per_page).limit(per_page).all()

    items = [{
        'id': s.id,
        'server_id': s.server_id,
        'name': s.name,
        'image_url': s.image_url,
        'description': getattr(s, 'description', None)
    } for s in skins]

    return jsonify({
        'items':       items,
        'total':       total,
        'page':        page,
        'per_page':    per_page,
        'total_pages': math.ceil(total / per_page)
    })

@skins_bp.route('/', methods=['POST'])
def add_skin():
    try:
        data = skin_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 400

    new_skin = Skin(**data)
    db.session.add(new_skin)
    db.session.commit()
    return jsonify({'message': 'Skin added', 'id': new_skin.id}), 201

@skins_bp.route('/<int:skin_id>', methods=['GET'])
def get_skin(skin_id):
    s = db.session.get(Skin, skin_id)
    if not s:
        abort(404)
    return jsonify({
        'id': s.id,
        'server_id': s.server_id,
        'name': s.name,
        'image_url': s.image_url,
        'description': getattr(s, 'description', None)
    })

@skins_bp.route('/<int:skin_id>', methods=['PUT'])
def update_skin(skin_id):
    s = db.session.get(Skin, skin_id)
    if not s:
        abort(404)

    try:
        data = skin_update_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 400

    for key, val in data.items():
        setattr(s, key, val)
    db.session.commit()
    return jsonify({'message': 'Skin updated'})

@skins_bp.route('/<int:skin_id>', methods=['DELETE'])
def delete_skin(skin_id):
    s = db.session.get(Skin, skin_id)
    if not s:
        abort(404)
    db.session.delete(s)
    db.session.commit()
    return jsonify({'message': 'Skin deleted'})
