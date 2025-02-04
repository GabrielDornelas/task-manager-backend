import functools
import jwt
import datetime
from flask import jsonify, request, g, current_app
from ..models.user import User
from ..infra.redis_client import (
    store_jwt_token, invalidate_jwt_token, is_token_valid,
    store_reset_token, cache_user
)

import os
from flask_mail import Mail, Message
from datetime import datetime, timedelta
from ..infra.db import get_db

# Secret key to sign the JWT
SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
JWT_EXPIRATION = 300  # 5 minutes in seconds

def login_required(view):
    """ Decorator to require authentication via JWT """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({"error": "Token missing"}), 401
        try:
            # Extract token from Bearer header
            token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header

            # Check if token is in blacklist
            if not is_token_valid(token):
                return jsonify({"error": "Token invalidated"}), 401

            # Decode token
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = payload['user_id']

            # Search for user
            user = User.get_by_id(user_id)
            if not user:

                return jsonify({"error": "User not found"}), 401

            # Set user in context
            g.user = user
            return view(**kwargs)
        except jwt.ExpiredSignatureError:

            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        except Exception as e:
            return jsonify({"error": str(e)}), 401
    return wrapped_view

def get_logged_user_id():
    """ Returns the logged in user ID from the JWT """
    if hasattr(g, 'user') and g.user:
        return g.user._id

    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    try:
        # Extract token from Bearer header
        token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
        

        # Decodificar token
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']

        # Search for user
        user = User.get_by_id(user_id)
        if user:

            g.user = user
            return user._id
    except:
        pass
    return None

def register():
    data = request.get_json()
    if not data or not all(k in data for k in ['username', 'password', 'email']):
        return jsonify({'error': 'Username and password are required'}), 400
    
    # Check if user already exists
    if User.get_by_username(data['username']):
        return jsonify({'error': 'Username already taken'}), 400

    if User.get_by_email(data['email']):
        return jsonify({'error': 'Email already registered'}), 400

    # Create new user
    user = User(
        username=data['username'],
        password=data['password'],
        email=data['email']
    )

    # Try to save
    user_id = user.save()
    if not user_id:
        return jsonify({'error': 'User registration failed'}), 400

    return jsonify({'message': 'User registered successfully', 'id': user_id}), 201

def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = User.get_by_username(username)
    if user is None or not user.check_password(password):
        return jsonify({"error": "Invalid username or password"}), 401

    # Update last_login
    db = get_db()
    db.users.update_one(
        {'_id': user._id},
        {'$set': {'last_login': datetime.utcnow()}}
    )

    # Generate JWT token
    token = jwt.encode(
        {
            'user_id': str(user._id),

            'exp': datetime.utcnow() + timedelta(seconds=JWT_EXPIRATION)
        },
        SECRET_KEY,
        algorithm='HS256'
    )

    # Store token in Redis
    store_jwt_token(str(user._id), token)

    # Store user in cache
    cache_user(str(user._id), user.to_dict())

    return jsonify({
        "token": token,
        "expires_in": JWT_EXPIRATION
    }), 200

@login_required
def logout():
    """Route for logout"""
    # Invalidate token in Redis
    invalidate_jwt_token(str(g.user._id))
    return jsonify({"message": "Logout successful"}), 200


def get_user_from_jwt(token):
    """Extracts the user from the JWT and checks in Redis"""
    try:
        token = token.split(" ")[1] if " " in token else token
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']

        # Check if the token is in Redis
        if not is_token_valid(user_id, token):
            raise jwt.InvalidTokenError("Token not found in Redis")

        user = User.get_by_id(user_id)
        return user
    except (IndexError, jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        raise Exception("Invalid or expired token")

def request_password_reset():
    """Route for requesting password reset"""
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({"error": "Email is required"}), 400
    user = User.get_by_email(email)
    if not user:
        return jsonify({"error": "Email not found"}), 404

    # Generate reset token

    reset_token = jwt.encode(
        {
            'user_id': str(user._id),
            'exp': datetime.utcnow() + timedelta(hours=1)
        },
        SECRET_KEY,
        algorithm='HS256'
    )
    # Store token in Redis
    store_reset_token(str(user._id), reset_token)

    return jsonify({
        "message": "Password reset requested",
        "token": reset_token
    }), 200

def reset_password():
    """Route for resetting password using the token"""
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('new_password')


    if not token or not new_password:
        return jsonify({"error": "Token and new password are required"}), 400

    try:
        # Check the token and get the user
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user = User.get_by_id(payload['user_id'])

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Update the password
        if user.update_password(new_password):
            return jsonify({"message": "Password updated successfully"}), 200
        return jsonify({"error": "Failed to update password"}), 400


    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

def send_password_reset_email(user, reset_link):
    """Sends password reset email"""
    mail = Mail(current_app)
    msg = Message('Password Reset',
                 sender=current_app.config['MAIL_USERNAME'],
                 recipients=[user.email])

    msg.body = f'''Para resetar sua senha, acesse o link abaixo:
{reset_link}

Se você não solicitou a recuperação de senha, ignore este email.
'''
    mail.send(msg)
