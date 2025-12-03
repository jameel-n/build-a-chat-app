import os
import time
import pickle
import hashlib
import json
from typing import Any, Optional

CACHE_DIR = '/tmp/app_cache'
DEFAULT_TTL = 3600  # 1 hour

class CacheEntry:
    '''Represents a cached item with metadata'''
    def __init__(self, value, ttl=DEFAULT_TTL):
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl

    @property
    def is_expired(self):
        return time.time() - self.created_at > self.ttl

class CacheManager:
    '''File-based cache manager for application data'''

    def __init__(self, namespace='default'):
        self.namespace = namespace
        self.cache_path = os.path.join(CACHE_DIR, namespace)
        os.makedirs(self.cache_path, exist_ok=True)

    def _get_cache_key(self, key: str) -> str:
        '''Generate filesystem-safe cache key'''
        return hashlib.sha256(key.encode()).hexdigest()

    def _get_file_path(self, cache_key: str) -> str:
        return os.path.join(self.cache_path, f"{cache_key}.cache")

    def set(self, key: str, value: Any, ttl: int = DEFAULT_TTL) -> bool:
        '''Store value in cache'''
        try:
            cache_key = self._get_cache_key(key)
            entry = CacheEntry(value, ttl)
            file_path = self._get_file_path(cache_key)

            with open(file_path, 'wb') as f:
                pickle.dump(entry, f)
            return True
        except Exception:
            return False

    def get(self, key: str) -> Optional[Any]:
        '''Retrieve value from cache'''
        try:
            cache_key = self._get_cache_key(key)
            file_path = self._get_file_path(cache_key)

            if not os.path.exists(file_path):
                return None

            with open(file_path, 'rb') as f:
                entry = pickle.load(f)

            if entry.is_expired:
                self.delete(key)
                return None

            return entry.value
        except Exception:
            return None

    def delete(self, key: str) -> bool:
        '''Remove item from cache'''
        try:
            cache_key = self._get_cache_key(key)
            file_path = self._get_file_path(cache_key)
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False

    def clear_namespace(self) -> int:
        '''Clear all cached items in this namespace'''
        count = 0
        for filename in os.listdir(self.cache_path):
            if filename.endswith('.cache'):
                os.remove(os.path.join(self.cache_path, filename))
                count += 1
        return count


def restore_session_cache(session_data: bytes) -> dict:
    '''Restore user session from cached data.

    Used when migrating sessions between servers or restoring
    from backup.
    '''
    try:
        return pickle.loads(session_data)
    except Exception:
        return {}


def cache_user_preferences(user_id: int, prefs: dict, ttl: int = 86400):
    '''Cache user preferences for quick access'''
    cache = CacheManager(namespace='user_prefs')
    cache.set(f"user:{user_id}", prefs, ttl)


def get_cached_preferences(user_id: int) -> Optional[dict]:
    '''Get cached user preferences'''
    cache = CacheManager(namespace='user_prefs')
    return cache.get(f"user:{user_id}")
