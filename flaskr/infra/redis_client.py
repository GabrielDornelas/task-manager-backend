from redis import Redis
from flask import current_app, g
from typing import Optional, cast, Any, Union
import json

def get_redis() -> Redis:
    """Returns a connection to Redis"""
    if 'redis' not in g:
        g.redis = cast(Redis, Redis.from_url(current_app.config['REDIS_URL']))
    return g.redis


def close_redis(e=None):
    """Closes the Redis connection"""
    redis = g.pop('redis', None)
    if redis is not None:
        redis.close()


def init_redis(app):
    """Initializes Redis with the application"""
    app.teardown_appcontext(close_redis)


def store_jwt_token(user_id, token, expiration=300):
    """Stores JWT token in Redis"""
    redis = get_redis()
    key = f"jwt_token:{user_id}"
    redis.set(key, token, ex=expiration)
    

    # Also store the reverse token for blacklist
    token_key = f"token:{token}"
    redis.set(token_key, user_id, ex=expiration)


def invalidate_jwt_token(user_id: str) -> None:
    """Invalidates a JWT token in Redis"""
    redis = get_redis()
    key = f"jwt_token:{user_id}"
    redis.delete(key)


def is_token_valid(token):
    """Checks if the token is valid in Redis"""
    redis = get_redis()
    token_key = f"token:{token}"
    return redis.exists(token_key)


def store_reset_token(user_id: str, token: str) -> None:
    """Stores the password reset token in Redis"""
    redis = get_redis()
    key = f"reset_token:{user_id}"
    # Valid reset token for 1 hour
    redis.setex(key, 3600, token)


def get_reset_token(user_id: str) -> Optional[str]:
    """Retrieves the password reset token from Redis"""
    redis = get_redis()
    key = f"reset_token:{user_id}"
    token = cast(Optional[bytes], redis.get(key))
    return token.decode('utf-8') if token else None


def cache_user(user_id: str, user_data: dict, expires_in: int = 300) -> None:
    """Caches user data"""
    redis = get_redis()
    key = f"user_cache:{user_id}"
    redis.setex(key, expires_in, json.dumps(user_data))


def get_cached_user(user_id: str) -> Optional[dict]:
    """Retrieves user data from cache"""
    redis = get_redis()
    key = f"user_cache:{user_id}"
    data = cast(Optional[bytes], redis.get(key))
    if data:

        try:
            return json.loads(data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None
    return None

def invalidate_user_cache(user_id: str) -> None:
    """Removes user cache"""
    redis = get_redis()
    key = f"user_cache:{user_id}"
    redis.delete(key)


def cache_with_prefix(prefix: str, key: str, data: Any, expires_in: int = 300) -> None:
    """Generic cache with prefix"""
    redis = get_redis()
    cache_key = f"{prefix}:{key}"
    redis.setex(cache_key, expires_in, json.dumps(data))


def get_cached_with_prefix(prefix: str, key: str) -> Optional[Any]:
    """Retrieves generic cache data"""
    redis = get_redis()
    cache_key = f"{prefix}:{key}"
    data = cast(Optional[bytes], redis.get(cache_key))
    if data:

        try:
            return json.loads(data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None
    return None

def cache_task(task_id: str, task_data: dict, expires_in: int = 300) -> None:
    """Caches task"""
    redis = get_redis()
    key = f"task_cache:{task_id}"
    redis.setex(key, expires_in, json.dumps(task_data))


def get_cached_task(task_id: str) -> Optional[dict]:
    """Retrieves task from cache"""
    redis = get_redis()
    key = f"task_cache:{task_id}"
    data = cast(Optional[bytes], redis.get(key))
    if data:

        try:
            return json.loads(data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None
    return None

def cache_task_list(user_id: str, tasks: list, expires_in: int = 60) -> None:
    """Caches task list"""
    redis = get_redis()
    key = f"task_list:{user_id}"
    redis.setex(key, expires_in, json.dumps(tasks))


def get_cached_task_list(user_id: str) -> Optional[list]:
    """Retrieves task list from cache"""
    redis = get_redis()
    key = f"task_list:{user_id}"
    data = cast(Optional[bytes], redis.get(key))
    if data:

        try:
            return json.loads(data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None
    return None

def invalidate_task_cache(task_id: str) -> None:
    """Removes task from cache"""
    redis = get_redis()
    key = f"task_cache:{task_id}"
    redis.delete(key)


def invalidate_user_task_list(user_id: str) -> None:
    """Removes task list from cache"""
    redis = get_redis()
    key = f"task_list:{user_id}"
    redis.delete(key)
