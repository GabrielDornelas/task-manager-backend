from werkzeug.security import check_password_hash, generate_password_hash
from ..infra.db import get_db
from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError
from ..infra.redis_client import (
    cache_user, get_cached_user, invalidate_user_cache,
    cache_with_prefix, get_cached_with_prefix
)
from datetime import datetime, timedelta

class User:
    def __init__(self, username, password=None, email=None, _id=None, last_login=None):
        self._id = _id
        self.username = username
        self.email = email
        self.last_login = last_login
        
        # Se password for fornecido e não estiver hasheado, faz o hash
        if password and not (password.startswith('scrypt:') or password.startswith('pbkdf2:sha256:')):
            self.password = generate_password_hash(password)
        else:
            self.password = password


    @classmethod
    def get_by_id(cls, id):
        """Searches for a user by ID, using cache"""
        # Try to recover from the cache first
        cached_data = get_cached_user(str(id))
        if cached_data:
            return cls(
                username=cached_data['username'],
                email=cached_data['email'],
                _id=ObjectId(cached_data['id']),
                last_login=cached_data.get('last_login')
            )

        # If not cached, search the database
        db = get_db()
        user_data = db['users'].find_one({'_id': ObjectId(id)})
        if user_data:
            return cls(**user_data)
        return None


    @classmethod
    def get_by_username(cls, username):
        """Searches for a user by username, using cache"""
        db = get_db()
        user_data = db['users'].find_one({'username': username})
        
        if user_data:
            user = cls(
                username=user_data['username'],
                password=user_data['password'],
                email=user_data['email'],
                _id=user_data['_id'],
                last_login=user_data.get('last_login')
            )
            return user
        return None


    @classmethod
    def get_by_email(cls, email):
        """Search for a user by email"""
        db = get_db()
        user_data = db['users'].find_one({'email': email})
        if user_data:
            return cls(**user_data)
        return None


    def check_password(self, password):
        """Checks that the password provided is valid"""
        if not self.password:
            return False
        
        return check_password_hash(self.password, password)


    def update_password(self, new_password):
        """Updates user password and invalidates cache"""
        db = get_db()
        hashed_password = generate_password_hash(new_password)
        result = db['users'].update_one(
            {'_id': self._id},
            {'$set': {'password': hashed_password}}
        )
        if result.modified_count > 0:
            self.password = hashed_password
            # Invalidate cache after update
            invalidate_user_cache(str(self._id))
            return True
        return False


    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': str(self._id),
            'username': self.username,
            'email': self.email,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }


    def save(self):
        db = get_db()
        users_collection = db["users"]
        
        # Check if there is already a user with the same username or email address
        if not self._id:  # Only checks duplicates for new users
            existing_user = users_collection.find_one({
                "$or": [
                    {"username": self.username},
                    {"email": self.email}
                ]
            })
            if existing_user:
                return None
        
        # Ensure that the password is hashed before saving
        if self.password and not self.password.startswith('scrypt:'):
            self.password = generate_password_hash(self.password)
        
        user_data = {
            "username": self.username,
            "password": self.password,
            "email": self.email,
            "last_login": datetime.utcnow()
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
            return None


    @classmethod
    def count_active_users(cls, hours=24):
        """Count active users in the last X hours"""
        db = get_db()
        since = datetime.utcnow() - timedelta(hours=hours)
        
        # Search for users with a recent login
        count = db.users.count_documents({
            'last_login': {'$gte': since}
        })
        
        return count
