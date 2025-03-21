from datetime import datetime, timedelta
from config import CACHE_EXPIRY

class Cache:
    """Simple in-memory cache with expiry."""
    
    def __init__(self, expiry_seconds=CACHE_EXPIRY):
        self._cache = {}  # key -> (timestamp, value)
        self.expiry_seconds = expiry_seconds
    
    def get(self, key):
        """Get a value from cache if it exists and hasn't expired."""
        if key in self._cache:
            timestamp, value = self._cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self.expiry_seconds):
                return value
            # Clean up expired entry
            del self._cache[key]
        return None
    
    def set(self, key, value):
        """Store a value in the cache."""
        self._cache[key] = (datetime.now(), value)
    
    def clear(self):
        """Clear all cache entries."""
        self._cache.clear()
    
    def prune(self):
        """Remove expired cache entries."""
        now = datetime.now()
        expired_keys = [
            key for key, (timestamp, _) in self._cache.items()
            if now - timestamp >= timedelta(seconds=self.expiry_seconds)
        ]
        for key in expired_keys:
            del self._cache[key]

# Initialize the cache
cache = Cache()