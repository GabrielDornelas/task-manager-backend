import pytest
from flaskr.models.user import User
from flaskr.infra.db import get_db
from flaskr.infra.redis_client import get_redis, get_cached_user
import json
from bson import ObjectId
from datetime import datetime

def test_register(client):
    """Teste de registro de usuário"""
    response = client.post('/auth/register', json={
        'username': 'test_user',
        'password': 'test_pass',
        'email': 'test@example.com'
    })
    assert response.status_code == 201
    assert b"User registered successfully" in response.data

def test_register_duplicate_username(client):
    """Teste de registro com username duplicado"""
    # Primeiro registro
    client.post('/auth/register', json={
        'username': 'test_user2',
        'password': 'test_pass',
        'email': 'test2@example.com'
    })
    
    # Tentativa de registro duplicado
    response = client.post('/auth/register', json={
        'username': 'test_user2',
        'password': 'other_pass',
        'email': 'other@example.com'
    })
    assert response.status_code == 400
    assert b"Username already taken" in response.data

def test_login_and_jwt_cache(client):
    """Teste de login e cache do JWT"""
    # Registrar usuário
    response = client.post('/auth/register', json={
        'username': 'test_user',
        'password': 'test_pass',
        'email': 'test@example.com'
    })
    assert response.status_code == 201

    # Login
    response = client.post('/auth/login', json={
        'username': 'test_user',
        'password': 'test_pass'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'token' in data
    
    # Verificar se last_login foi atualizado
    db = get_db()
    user = db.users.find_one({'username': 'test_user'})
    assert 'last_login' in user
    assert isinstance(user['last_login'], datetime)

def test_user_cache(client):
    """Teste do cache de usuário"""
    # Registrar usuário
    client.post('/auth/register', json={
        'username': 'cache_test',
        'password': 'test_pass',
        'email': 'cache@example.com'
    })
    
    # Login para criar cache
    response = client.post('/auth/login', json={
        'username': 'cache_test',
        'password': 'test_pass'
    })
    
    # Buscar usuário
    user = User.get_by_username('cache_test')
    assert user is not None  # Garantir que user não é None
    
    # Verificar cache
    cached_data = get_cached_user(str(user._id))
    assert cached_data is not None
    assert cached_data['username'] == 'cache_test'

def test_password_reset_flow(client):
    """Teste do fluxo de reset de senha"""
    # Registrar usuário
    client.post('/auth/register', json={
        'username': 'reset_test',
        'password': 'test_pass',
        'email': 'reset@example.com'
    })
    
    # Solicitar reset
    response = client.post('/auth/reset-password', json={
        'email': 'reset@example.com'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'token' in data
    
    # Reset senha
    response = client.post('/auth/reset-password/confirm', json={
        'token': data['token'],
        'new_password': 'new_pass123'
    })
    assert response.status_code == 200
    
    # Tentar login com nova senha
    response = client.post('/auth/login', json={
        'username': 'reset_test',
        'password': 'new_pass123'
    })
    assert response.status_code == 200 