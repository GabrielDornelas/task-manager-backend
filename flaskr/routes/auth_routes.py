# auth_routes.py
from flask import Blueprint

from ..controllers.auth_controller import (
    login_required, register, login, logout, 
    request_password_reset, reset_password
)

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Registrando as rotas do Blueprint
auth_bp.route('/register', methods=['POST'])(register)
auth_bp.route('/login', methods=['POST'])(login)
auth_bp.route('/logout', methods=['POST'])(login_required(logout))
auth_bp.route('/reset-password', methods=['POST'])(request_password_reset)
auth_bp.route('/reset-password/confirm', methods=['POST'])(reset_password)
