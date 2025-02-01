import functools
import jwt
import datetime
from flask import jsonify, request, g
from ..models.user import User
import os

# Chave secreta para assinar o token JWT
SECRET_KEY = os.getenv('SECRET_KEY', 'dev')

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

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = User.get_by_username(username)
    if user:
        return jsonify({"error": "Username already taken"}), 400

    new_user = User.create(username, password)
    if new_user:
        return jsonify({"message": "User registered successfully!"}), 201
    return jsonify({"error": "User registration failed"}), 400

def login():
    """ Rota para autenticar um usuário e retornar um JWT """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    user = User.get_by_username(username)
    if user is None or not user.check_password(password):
        return jsonify({"error": "Invalid username or password."}), 401

    # Gerar o JWT
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token válido por 1 hora
    token = jwt.encode(
        {'user_id': str(user._id), 'exp': expiration_time},
        SECRET_KEY,
        algorithm='HS256'
    )

    return jsonify({"message": "Login successful", "token": token}), 200

@login_required
def logout():
    """ Rota para logout """
    return jsonify({"message": "Logout successful"}), 200

def get_user_from_jwt(token):
    """ Extrai o usuário do JWT """
    try:
        token = token.split(" ")[1] if " " in token else token
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user = User.get_by_id(payload['user_id'])
        return user
    except (IndexError, jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        raise Exception("Invalid or expired token")
