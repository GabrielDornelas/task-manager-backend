from flask import current_app, g
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pymongo

def get_db():
    """ Returns the connection to the MongoDB database """
    if 'db' not in g:
        uri = current_app.config['MONGO_URI']


        # Create a new client and connect to the server
        client = MongoClient(uri, server_api=ServerApi('1'))
        try:

            # Send a ping to confirm a successful connection
            client.admin.command('ping')
            g.db_client = client  # Store the client to close later
            g.db = client[current_app.config['MONGO_DBNAME']]
        except Exception as e:
            print(e)

    
    return g.db

def close_db(e=None):
    """ Closes the MongoDB connection """
    db_client = g.pop('db_client', None)
    if db_client is not None:

        db_client.close()

def init_app(app):
    """ Initializes the application with the connection closure configuration """
    app.teardown_appcontext(close_db)
    

    # Create unique indexes
    with app.app_context():
        db = get_db()

        db.users.create_index([("email", pymongo.ASCENDING)], unique=True)
        db.users.create_index([("username", pymongo.ASCENDING)], unique=True)
