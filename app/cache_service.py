# file: cache_service.py
# Redis caching service for Aura - Improves prediction and dashboard performance

import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Any, Dict
from functools import wraps

# Try to import Redis, fall back to in-memory cache if not available
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("[Cache] Redis not installed. Using in-memory fallback cache.")

# Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CACHE_DEFAULT_TTL = 300  # 5 minutes default
PREDICTION_CACHE_TTL = 180  # 3 minutes for predictions
DASHBOARD_CACHE_TTL = 60  # 1 minute for dashboard data
ANALYTICS_CACHE_TTL = 600  # 10 minutes for analytics (computed infrequently)


class InMemoryCache:
    """Fallback in-memory cache when Redis is not available"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        print("[Cache] In-memory cache initialized.")
    
    def get(self, key: str) -> Optional[str]:
        if key in self._cache:
            entry = self._cache[key]
            if entry['expires_at'] > datetime.now():
                return entry['value']
            else:
                del self._cache[key]
        return None
    
    def set(self, key: str, value: str, ex: int = CACHE_DEFAULT_TTL) -> bool:
        self._cache[key] = {
            'value': value,
            'expires_at': datetime.now() + timedelta(seconds=ex)
        }
        return True
    
    def delete(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def exists(self, key: str) -> bool:
        return key in self._cache and self._cache[key]['expires_at'] > datetime.now()
    
    def flushdb(self):
        self._cache.clear()
    
    def keys(self, pattern: str = "*") -> list:
        """Simple pattern matching for keys"""
        import fnmatch
        return [k for k in self._cache.keys() if fnmatch.fnmatch(k, pattern)]
    
    def ping(self) -> bool:
        return True


class CacheService:
    """
    Unified caching service with Redis support and in-memory fallback.
    Provides caching for predictions, dashboard data, and analytics.
    """
    
    def __init__(self):
        self._client = None
        self._connected = False
        self._init_client()
    
    def _init_client(self):
        """Initialize Redis client or fallback to in-memory"""
        if REDIS_AVAILABLE:
            try:
                self._client = redis.from_url(
                    REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=2,
                    socket_timeout=2
                )
                # Test connection
                self._client.ping()
                self._connected = True
                print(f"[Cache] Redis connected successfully: {REDIS_URL}")
            except Exception as e:
                print(f"[Cache] Redis connection failed: {e}. Using in-memory cache.")
                self._client = InMemoryCache()
                self._connected = True
        else:
            self._client = InMemoryCache()
            self._connected = True
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a unique cache key from prefix and arguments"""
        key_data = f"{prefix}:{':'.join(str(a) for a in args)}"
        if kwargs:
            key_data += f":{json.dumps(kwargs, sort_keys=True)}"
        return f"aura:{key_data}"
    
    def _hash_key(self, data: Any) -> str:
        """Create a hash of complex data for cache keys"""
        return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()[:12]
    
    # ============================================================================
    # GENERIC GET/SET METHODS
    # ============================================================================
    
    def get(self, key: str) -> Optional[Any]:
        """Generic get method for any cached data"""
        try:
            cached = self._client.get(f"aura:{key}")
            if cached:
                return json.loads(cached)
            return None
        except Exception as e:
            print(f"[Cache] Error getting key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = CACHE_DEFAULT_TTL) -> bool:
        """Generic set method for any data"""
        try:
            self._client.set(f"aura:{key}", json.dumps(value), ex=ttl)
            return True
        except Exception as e:
            print(f"[Cache] Error setting key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete a specific key"""
        try:
            self._client.delete(f"aura:{key}")
            return True
        except Exception as e:
            print(f"[Cache] Error deleting key {key}: {e}")
            return False
    
    # ============================================================================
    # PREDICTION CACHING
    # ============================================================================
    
    def get_prediction(self, user_id: int, glucose_history: list) -> Optional[dict]:
        """Retrieve cached prediction if available"""
        try:
            history_hash = self._hash_key(glucose_history[-12:])  # Use last 12 readings for hash
            key = self._generate_key("prediction", user_id, history_hash)
            cached = self._client.get(key)
            if cached:
                print(f"[Cache] Prediction cache HIT for user {user_id}")
                return json.loads(cached)
            print(f"[Cache] Prediction cache MISS for user {user_id}")
            return None
        except Exception as e:
            print(f"[Cache] Error getting prediction: {e}")
            return None
    
    def set_prediction(self, user_id: int, glucose_history: list, prediction: dict) -> bool:
        """Cache a prediction result"""
        try:
            history_hash = self._hash_key(glucose_history[-12:])
            key = self._generate_key("prediction", user_id, history_hash)
            self._client.set(key, json.dumps(prediction), ex=PREDICTION_CACHE_TTL)
            print(f"[Cache] Prediction cached for user {user_id} (TTL: {PREDICTION_CACHE_TTL}s)")
            return True
        except Exception as e:
            print(f"[Cache] Error setting prediction: {e}")
            return False
    
    def invalidate_user_predictions(self, user_id: int) -> int:
        """Invalidate all cached predictions for a user"""
        try:
            pattern = f"aura:prediction:{user_id}:*"
            keys = self._client.keys(pattern)
            if keys:
                for key in keys:
                    self._client.delete(key)
                print(f"[Cache] Invalidated {len(keys)} predictions for user {user_id}")
            return len(keys) if keys else 0
        except Exception as e:
            print(f"[Cache] Error invalidating predictions: {e}")
            return 0
    
    # ============================================================================
    # DASHBOARD DATA CACHING
    # ============================================================================
    
    def get_dashboard_data(self, user_id: int) -> Optional[dict]:
        """Retrieve cached dashboard data"""
        try:
            key = self._generate_key("dashboard", user_id)
            cached = self._client.get(key)
            if cached:
                print(f"[Cache] Dashboard cache HIT for user {user_id}")
                return json.loads(cached)
            return None
        except Exception as e:
            print(f"[Cache] Error getting dashboard: {e}")
            return None
    
    def set_dashboard_data(self, user_id: int, data: dict) -> bool:
        """Cache dashboard data"""
        try:
            key = self._generate_key("dashboard", user_id)
            # Convert datetime objects to strings for JSON serialization
            serializable_data = self._make_serializable(data)
            self._client.set(key, json.dumps(serializable_data), ex=DASHBOARD_CACHE_TTL)
            print(f"[Cache] Dashboard cached for user {user_id}")
            return True
        except Exception as e:
            print(f"[Cache] Error setting dashboard: {e}")
            return False
    
    def invalidate_dashboard(self, user_id: int) -> bool:
        """Invalidate cached dashboard data for a user"""
        try:
            key = self._generate_key("dashboard", user_id)
            self._client.delete(key)
            print(f"[Cache] Dashboard invalidated for user {user_id}")
            return True
        except Exception as e:
            print(f"[Cache] Error invalidating dashboard: {e}")
            return False
    
    # ============================================================================
    # ANALYTICS CACHING
    # ============================================================================
    
    def get_analytics(self, user_id: int, analytics_type: str, days: int = 7) -> Optional[dict]:
        """Retrieve cached analytics data"""
        try:
            key = self._generate_key("analytics", user_id, analytics_type, days)
            cached = self._client.get(key)
            if cached:
                print(f"[Cache] Analytics cache HIT: {analytics_type} for user {user_id}")
                return json.loads(cached)
            return None
        except Exception as e:
            print(f"[Cache] Error getting analytics: {e}")
            return None
    
    def set_analytics(self, user_id: int, analytics_type: str, data: dict, days: int = 7) -> bool:
        """Cache analytics data"""
        try:
            key = self._generate_key("analytics", user_id, analytics_type, days)
            serializable_data = self._make_serializable(data)
            self._client.set(key, json.dumps(serializable_data), ex=ANALYTICS_CACHE_TTL)
            print(f"[Cache] Analytics cached: {analytics_type} for user {user_id}")
            return True
        except Exception as e:
            print(f"[Cache] Error setting analytics: {e}")
            return False
    
    def invalidate_user_analytics(self, user_id: int) -> int:
        """Invalidate all analytics cache for a user"""
        try:
            pattern = f"aura:analytics:{user_id}:*"
            keys = self._client.keys(pattern)
            if keys:
                for key in keys:
                    self._client.delete(key)
                print(f"[Cache] Invalidated {len(keys)} analytics entries for user {user_id}")
            return len(keys) if keys else 0
        except Exception as e:
            print(f"[Cache] Error invalidating analytics: {e}")
            return 0
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def _make_serializable(self, obj: Any) -> Any:
        """Convert objects to JSON-serializable format"""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):
            return self._make_serializable(obj.__dict__)
        return obj
    
    def invalidate_all_user_cache(self, user_id: int) -> dict:
        """Invalidate all cached data for a user"""
        predictions = self.invalidate_user_predictions(user_id)
        self.invalidate_dashboard(user_id)
        analytics = self.invalidate_user_analytics(user_id)
        return {
            "predictions_invalidated": predictions,
            "dashboard_invalidated": True,
            "analytics_invalidated": analytics
        }
    
    def health_check(self) -> dict:
        """Check cache service health"""
        try:
            is_connected = self._client.ping()
            cache_type = "Redis" if REDIS_AVAILABLE and not isinstance(self._client, InMemoryCache) else "InMemory"
            return {
                "status": "healthy" if is_connected else "degraded",
                "cache_type": cache_type,
                "connected": is_connected
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }


# Create a singleton cache instance
cache = CacheService()


# ============================================================================
# DECORATOR FOR AUTOMATIC CACHING
# ============================================================================

def cached_prediction(ttl: int = PREDICTION_CACHE_TTL):
    """Decorator to automatically cache prediction results"""
    def decorator(func):
        @wraps(func)
        def wrapper(user_id: int, glucose_history: list, *args, **kwargs):
            # Try to get from cache
            cached_result = cache.get_prediction(user_id, glucose_history)
            if cached_result is not None:
                return cached_result
            
            # Call the actual function
            result = func(user_id, glucose_history, *args, **kwargs)
            
            # Cache the result if successful
            if result and result.get("status") != "error":
                cache.set_prediction(user_id, glucose_history, result)
            
            return result
        return wrapper
    return decorator


def cached_analytics(analytics_type: str, ttl: int = ANALYTICS_CACHE_TTL):
    """Decorator to automatically cache analytics results"""
    def decorator(func):
        @wraps(func)
        def wrapper(user_id: int, *args, days: int = 7, **kwargs):
            # Try to get from cache
            cached_result = cache.get_analytics(user_id, analytics_type, days)
            if cached_result is not None:
                return cached_result
            
            # Call the actual function
            result = func(user_id, *args, days=days, **kwargs)
            
            # Cache the result
            if result:
                cache.set_analytics(user_id, analytics_type, result, days)
            
            return result
        return wrapper
    return decorator


# ============================================================================
# EVENT HOOKS FOR CACHE INVALIDATION
# ============================================================================

def on_new_glucose_reading(user_id: int):
    """Called when a new glucose reading is added"""
    cache.invalidate_user_predictions(user_id)
    cache.invalidate_dashboard(user_id)


def on_new_meal_log(user_id: int):
    """Called when a new meal is logged"""
    cache.invalidate_dashboard(user_id)
    cache.invalidate_user_analytics(user_id)


def on_model_calibration(user_id: int):
    """Called when a user's model is re-trained"""
    cache.invalidate_all_user_cache(user_id)
