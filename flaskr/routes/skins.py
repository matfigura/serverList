from flask import Blueprint

skins_bp = Blueprint('skins', __name__, url_prefix='/skins')

@skins_bp.route('/')
def list_skins():
    return "Lista skinów"