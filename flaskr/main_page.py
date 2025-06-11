from flask import (
    Blueprint, render_template
)
from flaskr.models import Server  # model serwera

bp = Blueprint('main_page', __name__)


@bp.route('/')
def index():
    servers = Server.query.order_by(Server.created_at.desc()).all()
    return render_template('main_page/index.html', servers=servers)