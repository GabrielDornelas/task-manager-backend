import pymongo
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db
from bson.objectid import ObjectId

class User:
    def __init__(self, username, password=None, _id=None):
        self._id = _id
        self.username = username
        self.password = password

    @classmethod
    def get_by_id(cls, id):
        """Busca um usuário pelo nome de usuário"""
        db = get_db()
        user_data = db['users'].find_one({'_id': ObjectId(id)})
        if user_data:
            return cls(**user_data)
        return None
    
    @classmethod
    def get_by_username(cls, username):
        """Busca um usuário pelo nome de usuário"""
        db = get_db()
        user_data = db['users'].find_one({'username': username})
        if user_data:
            return cls(**user_data)
        return None

    @classmethod
    def create(cls, username, password):
        """Cria um novo usuário"""
        hashed_password = generate_password_hash(password)
        db = get_db()
        try:
            user_data = {
                "username": username,
                "password": hashed_password
            }
            result = db['users'].insert_one(user_data)
            return cls(username=username, password=hashed_password, _id=result.inserted_id)
        except pymongo.errors.DuplicateKeyError:
            return None

    def check_password(self, password):
        """Verifica se a senha fornecida é válida"""
        return check_password_hash(self.password, password)
