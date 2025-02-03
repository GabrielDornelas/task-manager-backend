from flask import current_app, g
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pymongo

def get_db():
    """ Retorna a conexão com o banco de dados MongoDB """
    if 'db' not in g:
        uri = current_app.config['MONGO_URI']

        # Criar um novo cliente e conectar ao servidor
        client = MongoClient(uri, server_api=ServerApi('1'))
        try:
            # Enviar um ping para confirmar uma conexão bem-sucedida
            client.admin.command('ping')
            g.db_client = client  # Armazena o cliente para fechar depois
            g.db = client[current_app.config['MONGO_DBNAME']]
        except Exception as e:
            print(e)
    
    return g.db

def close_db(e=None):
    """ Fecha a conexão com o MongoDB """
    db_client = g.pop('db_client', None)
    if db_client is not None:
        db_client.close()

def init_app(app):
    """ Inicializa a aplicação com a configuração de fechamento da conexão """
    app.teardown_appcontext(close_db)
    
    # Criar índices únicos
    with app.app_context():
        db = get_db()
        db.users.create_index([("email", pymongo.ASCENDING)], unique=True)
        db.users.create_index([("username", pymongo.ASCENDING)], unique=True)
