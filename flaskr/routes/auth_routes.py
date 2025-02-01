# auth_routes.py
from flask import Blueprint

from ..controllers.auth_controller import login_required, register, login, logout

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Registrando as rotas do Blueprint
auth_bp.route('/register', methods=['POST'])(register)
auth_bp.route('/login', methods=['POST'])(login)
auth_bp.route('/logout', methods=['POST'])(login_required(logout))  # Apenas no logout
