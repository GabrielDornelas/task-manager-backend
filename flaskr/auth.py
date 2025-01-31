import functools
import os
from bson import ObjectId
import jwt
import datetime
from flask import Blueprint, jsonify, request, g
from werkzeug.security import check_password_hash, generate_password_hash
import pymongo.errors
from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

# Chave secreta para assinar o token JWT
SECRET_KEY = os.getenv('SECRET_KEY', 'dev')

@bp.route('/register', methods=['POST'])
def register():
    """ Rota para registrar um usuário """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    db = get_db()
    users_collection = db["users"]  # Acessa a collection correta

    try:
        # Insere o usuário na collection
        users_collection.insert_one({
            "username": username,
            "password": generate_password_hash(password)
        })
        return jsonify({"message": "User registered successfully!"}), 201
    except pymongo.errors.DuplicateKeyError:
        return jsonify({"error": f"User {username} already exists."}), 400


@bp.route('/login', methods=['POST'])
def login():
    """ Rota para autenticar um usuário e retornar um JWT """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    db = get_db()
    users_collection = db["users"]
    user = users_collection.find_one({"username": username})

    if user is None or not check_password_hash(user['password'], password):
        return jsonify({"error": "Invalid username or password."}), 401

    # Gerar o JWT
    expiration_time = datetime.datetime.now() + datetime.timedelta(hours=1)  # Token válido por 1 hora
    token = jwt.encode(
        {'user_id': str(user['_id']), 'exp': expiration_time},
        SECRET_KEY,
        algorithm='HS256'
    )

    return jsonify({"message": "Login successful", "token": token}), 200


def get_user_from_jwt(token):
    token = token.split(" ")[1]
    payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    db = get_db()
    users_collection = db["users"]
    user = users_collection.find_one({"_id": ObjectId(payload['user_id'])})
    return user


@bp.before_app_request
def load_logged_in_user():
    """ Carrega o usuário autenticado a partir do JWT """
    token = request.headers.get('Authorization')
    if token:
        try:
            user = get_user_from_jwt(token)
            g.user = user
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            g.user = None
    else:
        g.user = None


def login_required(view):
    """ Decorador para exigir autenticação via JWT """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return jsonify({"error": "Authentication required"}), 401
        return view(**kwargs)

    return wrapped_view


@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """ Rota para logout """
    return jsonify({"message": "Logout successful"}), 200
