import redis
import json
from typing import Optional, Any
from datetime import timedelta

# Подключение к htlbce
redis_client = redis.Redis(host="localhost", port=6379, db=2, decode_responses=True)

DEFAULT_EXPIRE = timedelta(minutes=5)

def cache_get(key: str) -> Optional[Any]:
    """Получить данные из кэша"""
    try:
        data = redis_client.get(key)
        return json.loads(data) if data else None
    except (redis.RedisError, json.JSONDecodeError):
        return None

def cache_set(key: str, value: Any, expire: timedelta = DEFAULT_EXPIRE) -> bool:
    """Сохранить данные в кэш"""
    try:
        redis_client.setex(key, int(expire.total_seconds()), json.dumps(value, default=str))
        return True
    except (redis.RedisError, TypeError):
        return False

def cache_delete(pattern: str) -> int:
    """Удалить ключи по паттерну (для инвалидации)"""
    try:
        keys = redis_client.keys(pattern)
        return redis_client.delete(*keys) if keys else 0
    except redis.RedisError:
        return 0

def cached_response(key_prefix: str, expire: timedelta = DEFAULT_EXPIRE):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # уникальный ключ: prefix + имя функции + аргументы
            cache_key = f"{key_prefix}:{func.__name__}:{str(kwargs)}"
            
            # Пробуем вернуть из кэша
            cached = cache_get(cache_key)
            if cached is not None:
                return cached
            
            # Если нет
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            cache_set(cache_key, result, expire)
            return result
        return wrapper
    return decorator