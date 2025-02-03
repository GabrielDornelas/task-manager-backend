import pytest
from flaskr import create_app
from flask import Flask
from typing import Generator

@pytest.fixture
def app() -> Flask:
    """Cria uma instância do app para testes"""
    app = create_app({
        'TESTING': True,
        'MONGO_URI': 'mongodb://mongo:27017/test_db',
        'MONGO_DBNAME': 'test_db',
        'REDIS_URL': 'redis://redis:6379/1',  # Usar banco 1 do Redis para testes
        'MAIL_SUPPRESS_SEND': True  # Não enviar emails durante testes
    })
    return app

@pytest.fixture
def client(app: Flask):
    """Cliente de teste"""
    return app.test_client()

@pytest.fixture
def runner(app: Flask):
    """Runner de CLI para testes"""
    return app.test_cli_runner() 