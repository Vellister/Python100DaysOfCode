from flask import Blueprint

admin_bp = Blueprint('admin', __name__, template_folder='templates', url_prefix='/admin')

from app.admin import routes
