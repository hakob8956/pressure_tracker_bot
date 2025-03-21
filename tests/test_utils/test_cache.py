import pytest
from unittest.mock import patch
from utils.cache import Cache
from datetime import datetime, timedelta

@patch('utils.cache.datetime')
def test_cache_set_get(mock_datetime):
    """Test setting and getting values from the cache."""
    # Setup mock datetime
    now = datetime(2023, 1, 1, 12, 0)
    mock_datetime.now.return_value = now
    
    # Create a cache
    cache = Cache()
    
    # Set a value
    cache.set('test_key', 'test_value')
    
    # Verify the value was stored
    assert cache.get('test_key') == 'test_value'
    
    # Verify internal state
    assert 'test_key' in cache._cache
    assert cache._cache['test_key'][0] == now
    assert cache._cache['test_key'][1] == 'test_value'

@patch('utils.cache.datetime')
def test_cache_expiry(mock_datetime):
    """Test that cache entries expire correctly."""
    # Setup mock datetime for initial set
    now = datetime(2023, 1, 1, 12, 0)
    mock_datetime.now.return_value = now
    
    # Create a cache with a short expiry time
    cache = Cache(expiry_seconds=10)
    
    # Set a value
    cache.set('test_key', 'test_value')
    
    # Verify the value is available
    assert cache.get('test_key') == 'test_value'
    
    # Advance time by less than expiry
    later = now + timedelta(seconds=5)
    mock_datetime.now.return_value = later
    
    # Verify value is still available
    assert cache.get('test_key') == 'test_value'
    
    # Advance time beyond expiry
    expired = now + timedelta(seconds=15)
    mock_datetime.now.return_value = expired
    
    # Verify value is no longer available
    assert cache.get('test_key') is None
    
    # Verify internal state (entry should be removed)
    assert 'test_key' not in cache._cache

def test_cache_nonexistent_key():
    """Test getting a key that doesn't exist."""
    cache = Cache()
    assert cache.get('nonexistent_key') is None

@patch('utils.cache.datetime')
def test_cache_clear(mock_datetime):
    """Test clearing the cache."""
    # Setup mock datetime
    now = datetime(2023, 1, 1, 12, 0)
    mock_datetime.now.return_value = now
    
    # Create a cache
    cache = Cache()
    
    # Set multiple values
    cache.set('key1', 'value1')
    cache.set('key2', 'value2')
    
    # Verify values are available
    assert cache.get('key1') == 'value1'
    assert cache.get('key2') == 'value2'
    
    # Clear the cache
    cache.clear()
    
    # Verify values are no longer available
    assert cache.get('key1') is None
    assert cache.get('key2') is None
    
    # Verify internal state
    assert not cache._cache

@patch('utils.cache.datetime')
def test_cache_prune(mock_datetime):
    """Test pruning expired entries from the cache."""
    # Setup mock datetime for initial sets
    now = datetime(2023, 1, 1, 12, 0)
    mock_datetime.now.return_value = now
    
    # Create a cache with a short expiry time
    cache = Cache(expiry_seconds=10)
    
    # Set multiple values
    cache.set('key1', 'value1')
    cache.set('key2', 'value2')
    
    # Advance time for some entries to expire
    later = now + timedelta(seconds=15)
    mock_datetime.now.return_value = later
    
    # Set another value
    cache.set('key3', 'value3')
    
    # Prune the cache
    cache.prune()
    
    # Verify expired entries are removed
    assert cache.get('key1') is None
    assert cache.get('key2') is None
    assert cache.get('key3') == 'value3'
    
    # Verify internal state
    assert 'key1' not in cache._cache
    assert 'key2' not in cache._cache
    assert 'key3' in cache._cache