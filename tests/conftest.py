import pytest
from flaskr import create_app
from flask import Flask
from typing import Generator
from flaskr.infra.db import get_db
from flaskr.infra.redis_client import get_redis

# Ignorar warning específico do monkey-patch
@pytest.mark.filterwarnings("ignore::gevent.monkey.MonkeyPatchWarning")
def pytest_configure(config):
    pass

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
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def runner(app: Flask):
    """Runner de CLI para testes"""
    return app.test_cli_runner() 