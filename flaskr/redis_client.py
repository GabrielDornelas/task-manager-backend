from redis import Redis
from flask import current_app, g
from typing import Optional, cast, Any, Union
import json

def get_redis() -> Redis:
    """Retorna uma conexão com o Redis"""
    if 'redis' not in g:
        g.redis = cast(Redis, Redis.from_url(current_app.config['REDIS_URL']))
    return g.redis

def close_redis(e=None):
    """Fecha a conexão com o Redis"""
    redis = g.pop('redis', None)
    if redis is not None:
        redis.close()

def init_redis(app):
    """Inicializa o Redis com a aplicação"""
    app.teardown_appcontext(close_redis)

def store_jwt_token(user_id: str, token: str, expires_in: int) -> None:
    """Armazena o token JWT no Redis"""
    redis = get_redis()
    key = f"jwt_token:{user_id}"
    redis.setex(key, expires_in, token)

def invalidate_jwt_token(user_id: str) -> None:
    """Invalida um token JWT no Redis"""
    redis = get_redis()
    key = f"jwt_token:{user_id}"
    redis.delete(key)

def is_token_valid(user_id: str, token: str) -> bool:
    """Verifica se um token JWT é válido no Redis"""
    redis = get_redis()
    key = f"jwt_token:{user_id}"
    stored_token = cast(Optional[bytes], redis.get(key))
    return bool(stored_token and stored_token.decode('utf-8') == token)

def store_reset_token(user_id: str, token: str) -> None:
    """Armazena o token de reset de senha no Redis"""
    redis = get_redis()
    key = f"reset_token:{user_id}"
    # Token de reset válido por 1 hora
    redis.setex(key, 3600, token)

def get_reset_token(user_id: str) -> Optional[str]:
    """Recupera o token de reset de senha do Redis"""
    redis = get_redis()
    key = f"reset_token:{user_id}"
    token = cast(Optional[bytes], redis.get(key))
    return token.decode('utf-8') if token else None

def cache_user(user_id: str, user_data: dict, expires_in: int = 300) -> None:
    """Armazena dados do usuário em cache"""
    redis = get_redis()
    key = f"user_cache:{user_id}"
    redis.setex(key, expires_in, json.dumps(user_data))

def get_cached_user(user_id: str) -> Optional[dict]:
    """Recupera dados do usuário do cache"""
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
    """Remove o cache do usuário"""
    redis = get_redis()
    key = f"user_cache:{user_id}"
    redis.delete(key)

def cache_with_prefix(prefix: str, key: str, data: Any, expires_in: int = 300) -> None:
    """Cache genérico com prefixo"""
    redis = get_redis()
    cache_key = f"{prefix}:{key}"
    redis.setex(cache_key, expires_in, json.dumps(data))

def get_cached_with_prefix(prefix: str, key: str) -> Optional[Any]:
    """Recupera dados do cache genérico"""
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
    """Armazena task em cache"""
    redis = get_redis()
    key = f"task_cache:{task_id}"
    redis.setex(key, expires_in, json.dumps(task_data))

def get_cached_task(task_id: str) -> Optional[dict]:
    """Recupera task do cache"""
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
    """Armazena lista de tasks em cache"""
    redis = get_redis()
    key = f"task_list:{user_id}"
    redis.setex(key, expires_in, json.dumps(tasks))

def get_cached_task_list(user_id: str) -> Optional[list]:
    """Recupera lista de tasks do cache"""
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
    """Remove task do cache"""
    redis = get_redis()
    key = f"task_cache:{task_id}"
    redis.delete(key)

def invalidate_user_task_list(user_id: str) -> None:
    """Remove lista de tasks do cache"""
    redis = get_redis()
    key = f"task_list:{user_id}"
    redis.delete(key) 