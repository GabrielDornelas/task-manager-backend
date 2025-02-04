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
        self.email = email
        
        # Se password for fornecido e não estiver hasheado, faz o hash
        if password and not (password.startswith('scrypt:') or password.startswith('pbkdf2:sha256:')):
            self.password = generate_password_hash(password)
        else:
            self.password = password

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
    def get_by_email(cls, email):
        """Busca um usuário pelo email"""
        db = get_db()
        user_data = db['users'].find_one({'email': email})
        if user_data:
            return cls(**user_data)
        return None

    def check_password(self, password):
        """Verifica se a senha fornecida é válida"""
        import sys
        print(f"DEBUG: Verificando senha para usuário: {self.username}", file=sys.stderr)
        print(f"DEBUG: Hash armazenado: {self.password}", file=sys.stderr)
        print(f"DEBUG: Senha fornecida: {password}", file=sys.stderr)
        
        if not self.password:
            print("DEBUG: ERRO - Password está None!", file=sys.stderr)
            return False
        
        return check_password_hash(self.password, password)

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

    def save(self):
        db = get_db()
        users_collection = db["users"]
        
        # Verificar se já existe usuário com mesmo username ou email
        if not self._id:  # Apenas verifica duplicatas para novos usuários
            existing_user = users_collection.find_one({
                "$or": [
                    {"username": self.username},
                    {"email": self.email}
                ]
            })
            if existing_user:
                return None
        
        # Garantir que o password seja hasheado antes de salvar
        if self.password and not self.password.startswith('scrypt:'):
            self.password = generate_password_hash(self.password)
        
        user_data = {
            "username": self.username,
            "password": self.password,
            "email": self.email
        }
        
        try:
            if hasattr(self, '_id') and self._id:
                filter = {"_id": ObjectId(self._id)}
                result = users_collection.replace_one(filter, user_data, upsert=True)
            else:
                result = users_collection.insert_one(user_data)
                self._id = str(result.inserted_id)
            
            return self._id
        except Exception as e:
            print(f"DEBUG: Erro ao salvar usuário: {str(e)}", file=sys.stderr)
            return None
