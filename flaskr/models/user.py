from werkzeug.security import check_password_hash, generate_password_hash
from ..infra.db import get_db
from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError
from ..infra.redis_client import (
    cache_user, get_cached_user, invalidate_user_cache,
    cache_with_prefix, get_cached_with_prefix
)

class User:
    def __init__(self, username, password=None, email=None, _id=None):
        self._id = _id
        self.username = username
        self.password = password
        self.email = email

    @classmethod
    def get_by_id(cls, id):
        """Busca um usuário pelo ID, usando cache"""
        # Tentar recuperar do cache primeiro
        cached_data = get_cached_user(str(id))
        if cached_data:
            return cls(
                username=cached_data['username'],
                email=cached_data['email'],
                _id=ObjectId(cached_data['id'])
            )

        # Se não estiver em cache, buscar no banco
        db = get_db()
        user_data = db['users'].find_one({'_id': ObjectId(id)})
        if user_data:
            user = cls(**user_data)
            # Armazenar em cache
            cache_user(str(user._id), user.to_dict())
            return user
        return None
    
    @classmethod
    def get_by_username(cls, username):
        """Busca um usuário pelo username, usando cache"""
        # Tentar recuperar do cache
        cached_data = get_cached_with_prefix('username', username)
        if cached_data:
            return cls.get_by_id(cached_data['id'])

        # Se não estiver em cache, buscar no banco
        db = get_db()
        user_data = db['users'].find_one({'username': username})
        
        import sys
        print(f"DEBUG: Buscando usuário: {username}", file=sys.stderr)
        print(f"DEBUG: Dados encontrados: {user_data}", file=sys.stderr)
        
        if user_data:
            user = cls(
                username=user_data['username'],
                password=user_data['password'],
                email=user_data['email'],
                _id=user_data['_id']
            )
            # Armazenar em cache
            cache_with_prefix('username', username, {'id': str(user._id)})
            return user
        return None

    @classmethod
    def create(cls, username, password, email):
        """Cria um novo usuário"""
        hashed_password = generate_password_hash(password)
        db = get_db()
        try:
            user_data = {
                "username": username,
                "password": hashed_password,
                "email": email
            }
            result = db['users'].insert_one(user_data)
            return cls(username=username, password=hashed_password, email=email, _id=result.inserted_id)
        except DuplicateKeyError:
            return None

    @classmethod
    def get_by_email(cls, email):
        """Busca um usuário pelo email"""
        db = get_db()
        user_data = db['users'].find_one({'email': email})
        if user_data:
            return cls(**user_data)
        return None

    def check_password(self, password):
        """Verifica se a senha fornecida é válida"""
        return check_password_hash(self.password, password) # type: ignore

    def update_password(self, new_password):
        """Atualiza a senha do usuário e invalida cache"""
        db = get_db()
        hashed_password = generate_password_hash(new_password)
        result = db['users'].update_one(
            {'_id': self._id},
            {'$set': {'password': hashed_password}}
        )
        if result.modified_count > 0:
            self.password = hashed_password
            # Invalidar cache após atualização
            invalidate_user_cache(str(self._id))
            return True
        return False

    def to_dict(self):
        """Converte o usuário para dicionário"""
        return {
            'id': str(self._id),
            'username': self.username,
            'email': self.email
        }
