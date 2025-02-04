import pytest
from flaskr import create_app
from flask import Flask
from typing import Generator
from flaskr.infra.db import get_db
from flaskr.infra.redis_client import get_redis
from datetime import datetime, timedelta
from bson import ObjectId
from flaskr.models.user import User


@pytest.fixture
def app() -> Flask:
    """Cria uma instância do app para testes"""
    app = create_app({
        'TESTING': True,
        'MONGO_URI': 'mongodb://mongo:27017/test_db',
        'MONGO_DBNAME': 'test_db',
        'REDIS_URL': 'redis://redis:6379/1',  # Usar banco 1 do Redis para testes
        'MAIL_SUPPRESS_SEND': True,  # Não enviar emails durante testes
        'SECRET_KEY': 'test_secret_key'  # Chave fixa para testes
    })
    
    # Criar contexto da aplicação
    with app.app_context():
        # Limpar banco de dados antes dos testes
        db = get_db()
        db.users.delete_many({})
        db.tasks.delete_many({})
        
        # Limpar Redis
        redis = get_redis()
        redis.flushdb()
        
        yield app

@pytest.fixture
def client(app: Flask):
    """Cliente de teste"""
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    """Fixture que cria um usuário e retorna o header de autenticação"""
    # Registrar usuário
    response = client.post('/auth/register', json={
        'username': 'task_user',
        'password': 'task_pass',
        'email': 'task@example.com'
    })
    assert response.status_code == 201

    # Login
    response = client.post('/auth/login', json={
        'username': 'task_user',
        'password': 'task_pass'
    })
    assert response.status_code == 200
    
    data = response.get_json()
    token = data['token']
    
    # Garantir que o token está no Redis
    redis = get_redis()
    user = User.get_by_username('task_user')
    token_key = f"token:{token}"
    if not redis.exists(token_key):
        redis.set(token_key, str(user._id), ex=300)
    
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def runner(app: Flask):
    """Runner de CLI para testes"""
    return app.test_cli_runner()

@pytest.fixture
def sample_task():
    """Fixture que retorna uma task de exemplo"""
    return {
        'title': 'Test Task',
        'description': 'Test Description',
        'status': 'pending',
        'expire_date': (datetime.utcnow() + timedelta(days=1)).isoformat()
    } 