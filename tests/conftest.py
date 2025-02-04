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
    """Creates an app instance for tests"""
    app = create_app({
        'TESTING': True,
        'MONGO_URI': 'mongodb://mongo:27017/test_db',
        'MONGO_DBNAME': 'test_db',
        'REDIS_URL': 'redis://redis:6379/1',  # Use Redis bank 1 for testing
        'MAIL_SUPPRESS_SEND': True,  # Do not send emails during tests
        'SECRET_KEY': 'test_secret_key'  # Fixed key for testing
    })

    # Create app context
    with app.app_context():
        # Clear database before tests
        db = get_db()
        db.users.delete_many({})
        db.tasks.delete_many({})

        # Clear Redis
        redis = get_redis()
        redis.flushdb()

        yield app

@pytest.fixture
def client(app: Flask):
    """Test client"""
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    """Fixture that creates a user and returns the authentication header"""
    # Register user

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

    # Ensure the token is in Redis
    redis = get_redis()
    user = User.get_by_username('task_user')
    token_key = f"token:{token}"
    if not redis.exists(token_key):

        redis.set(token_key, str(user._id), ex=300)

    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def runner(app: Flask):
    """CLI runner for tests"""
    return app.test_cli_runner()


@pytest.fixture
def sample_task():
    """Fixture that returns a sample task"""

    return {
        'title': 'Test Task',
        'description': 'Test Description',
        'status': 'pending',
        'expire_date': (datetime.utcnow() + timedelta(days=1)).isoformat()
    }
