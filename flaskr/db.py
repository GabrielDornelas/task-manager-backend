from flask import current_app, g
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson import json_util

def get_db():
    if 'db' not in g:
        uri = current_app.config['MONGO_URI']

        # Create a new client and connect to the server
        client = MongoClient(uri, server_api=ServerApi('1'))
        try:
            # Send a ping to confirm a successful connection
            client.admin.command('ping')
            g.db_client = client  # Armazena o cliente para fechar depois
            g.db = client[current_app.config['MONGO_DBNAME']]
        except Exception as e:
            print(e)
    
    return g.db

def close_db(e=None):
    db_client = g.pop('db_client', None)
    if db_client is not None:
        db_client.close()

def init_app(app):
    app.teardown_appcontext(close_db)


def handle_collection_to_list(collection):
    cursor = json_util.dumps(collection)
    cursor = cursor.replace('{"$oid": ', '')
    cursor = cursor.replace('"},', '",')
    cursor = cursor.replace('{"$date": ', '')
    cursor = cursor.replace('Z"}', 'Z"')
    return json_util.loads(cursor)
