import functools
import jwt
import datetime
from flask import jsonify, request, g, current_app
from ..models.user import User
from ..infra.redis_client import (
    store_jwt_token, invalidate_jwt_token, is_token_valid,
    store_reset_token
)
import os
from flask_mail import Mail, Message
from ..infra.metrics import metrics

# Chave secreta para assinar o token JWT
SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
JWT_EXPIRATION = 300  # 5 minutos em segundos

def login_required(view):
    """ Decorador para exigir autenticação via JWT """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        token = request.headers.get('Authorization')
        if token:
            try:
                user = get_user_from_jwt(token)
                g.user = user
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expired. Please log in again."}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token. Please provide a valid token."}), 401
            except Exception:
                g.user = None
                return jsonify({"error": "Invalid token. Please provide a valid token."}), 401
        else:
            g.user = None
            return jsonify({"error": "Token missing. Please provide an authentication token."}), 401
        return view(**kwargs)

    return wrapped_view

def get_logged_user_id():
    """ Retorna o ID do usuário logado a partir do JWT """
    if g.user:
        return g.user._id
    token = request.headers.get('Authorization')
    if token:
        try:
            user = get_user_from_jwt(token)
            g.user = user
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as error:
            g.user = None
            raise (error)
    else:
        g.user = None
    return g.user

def register():
    """ Rota para registrar um usuário """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password or not email:
        return jsonify({"error": "Username, password and email are required"}), 400

    # Verifica se o username já existe
    if User.get_by_username(username):
        return jsonify({"error": "Username already taken"}), 400

    # Verifica se o email já existe
    if User.get_by_email(email):
        return jsonify({"error": "Email already registered"}), 400

    new_user = User.create(username, password, email)
    if new_user:
        # Incrementar contador de registro
        if metrics:
            metrics.counter(
                'user_register_total',
                'Total number of user registrations',
                labels={'status': 'success'}
            ).inc()
        return jsonify({"message": "User registered successfully!"}), 201
    
    if metrics:
        metrics.counter(
            'user_register_total',
            'Total number of user registrations',
            labels={'status': 'failed'}
        ).inc()
    return jsonify({"error": "User registration failed"}), 400

def login():
    """Rota para autenticar um usuário e retornar um JWT"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        if metrics:
            metrics.counter(
                'user_login_total',
                'Total number of user logins',
                labels={'status': 'failed'}
            ).inc()
        return jsonify({"error": "Username and password are required."}), 400

    user = User.get_by_username(username)
    if user is None or not user.check_password(password):
        if metrics:
            metrics.counter(
                'user_login_total',
                'Total number of user logins',
                labels={'status': 'failed'}
            ).inc()
        return jsonify({"error": "Invalid username or password."}), 401

    # Incrementar contador de login
    if metrics:
        metrics.counter(
            'user_login_total',
            'Total number of user logins',
            labels={'status': 'success'}
        ).inc()

    # Gerar o JWT
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXPIRATION)
    token = jwt.encode(
        {'user_id': str(user._id), 'exp': expiration_time},
        SECRET_KEY,
        algorithm='HS256'
    )

    # Armazenar token no Redis
    store_jwt_token(str(user._id), token, JWT_EXPIRATION)

    return jsonify({
        "message": "Login successful",
        "token": token,
        "expires_in": JWT_EXPIRATION
    }), 200

@login_required
def logout():
    """Rota para logout"""
    # Invalidar token no Redis
    invalidate_jwt_token(str(g.user._id))
    return jsonify({"message": "Logout successful"}), 200

def get_user_from_jwt(token):
    """Extrai o usuário do JWT e verifica no Redis"""
    try:
        token = token.split(" ")[1] if " " in token else token
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
        
        # Verificar se o token está no Redis
        if not is_token_valid(user_id, token):
            raise jwt.InvalidTokenError("Token not found in Redis")
            
        user = User.get_by_id(user_id)
        return user
    except (IndexError, jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        raise Exception("Invalid or expired token")

def request_password_reset():
    """Rota para solicitar redefinição de senha"""
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({"error": "Email is required"}), 400

    user = User.get_by_email(email)
    if not user:
        return jsonify({"error": "Email not found"}), 404

    # Gerar token de reset
    reset_token = jwt.encode(
        {
            'user_id': str(user._id),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        },
        SECRET_KEY,
        algorithm='HS256'
    )

    # Armazenar token no Redis
    store_reset_token(str(user._id), reset_token)

    reset_link = f"Seu token de reset: {reset_token}"

    try:
        send_password_reset_email(user, reset_link)
        # Incrementar contador de reset de senha
        if metrics:
            metrics.counter(
                'password_reset_total',
                'Total number of password reset requests',
                labels={'status': 'success'}
            ).inc()
        return jsonify({
            "message": "Password reset instructions sent to your email",
            "token": reset_token
        }), 200
    except Exception as e:
        print(f"Erro ao enviar email: {e}")
        if metrics:
            metrics.counter(
                'password_reset_total',
                'Total number of password reset requests',
                labels={'status': 'failed'}
            ).inc()
        return jsonify({"error": "Failed to send reset email"}), 500

def reset_password():
    """Rota para resetar a senha usando o token"""
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('new_password')

    if not token or not new_password:
        return jsonify({"error": "Token and new password are required"}), 400

    try:
        # Verificar o token e obter o usuário
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user = User.get_by_id(payload['user_id'])
        
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Atualizar a senha
        if user.update_password(new_password):
            return jsonify({"message": "Password updated successfully"}), 200
        return jsonify({"error": "Failed to update password"}), 400

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

def send_password_reset_email(user, reset_link):
    """Envia email de recuperação de senha"""
    mail = Mail(current_app)
    msg = Message('Recuperação de Senha',
                 sender=current_app.config['MAIL_USERNAME'],
                 recipients=[user.email])
    
    msg.body = f'''Para resetar sua senha, acesse o link abaixo:
{reset_link}

Se você não solicitou a recuperação de senha, ignore este email.
'''
    mail.send(msg)
