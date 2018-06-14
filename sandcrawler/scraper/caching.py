from functools import wraps
import pickle
import logging # XXX TODO - work ok in celery?

import redis_cache
import redis

from redis_cache.rediscache import CacheMissException

# THis whole file is a bastardisation of redis-simple-cache
# https://github.com/vivekn/redis-simple-cache/blob/master/redis_cache/rediscache.py
# it doesn't quite fit with the patterns needed, largely an object method
# decorator, and a redis connection pooled connection.

# 1 week.
DEFAULT_EXPIRY = 60 * 60 * 168


# Make cache a global here.
# This needs to be instatiated as a RedisCache object *OUTSIDE* this module
# BEFORE importing any scrapers.
# Otherwise the cachable decorator falls back to just calling the function
global cache
cache = None

class FakeCache(dict):

    connection = None

    def get_pickle(self, key):
        if key not in self:
            raise redis_cache.CacheMissException('From fake cache.')
        return self.get(key)

    def store_pickle(self, key, value, expiry=None):
        self[key] = value
        return True

    def get_json(self, key):
        if key not in self:
            raise redis_cache.CacheMissException('From fake cache.')
        return self.get(key)

    def store_json(self, key, value, expiry=None):
        self[key] = value
        return True

    def invalidate(self, key):
        try:
            del self[key]
        except KeyError:
            pass


class RedisCache(redis_cache.SimpleCache):

    def __init__(self,
                 connection_pool,
                 limit=10000,
                 expire=DEFAULT_EXPIRY,
                 hashkeys=False,
                 namespace="RedisCache"):
        self.connection_pool = connection_pool

        self.limit = limit  # No of json encoded strings to cache
        self.expire = expire  # Time to keys to expire in seconds
        self.prefix = namespace
        # Should we hash keys? There is a very small risk of collision invloved.
        self.hashkeys = hashkeys

    @property
    def connection(self):
        if self.connection_pool:
            return redis.StrictRedis(connection_pool=self.connection_pool)
        return None

def cacheable(expire=DEFAULT_EXPIRY):
    """
    This is a bastardisation of redis_cache.cache_it.
     The base decorator will not work nicely with class based entries
     (ie it pickles self, which, if it works, means caching only works across
      a single instance.
     Also, removed some user options for simplicity; these will be handled by
     sandcrawler options files.

    """
    expire_ = expire
    cache_ = cache

    def decorator(function):
        cache, expire = cache_, expire_

        @wraps(function)
        def func(*args, **kwargs):
            ## Handle cases where caching is down or otherwise not available.
            if cache is None or cache.connection is None:
                result = function(*args, **kwargs)
                return result

            key_args = list(args[:])
            obj = key_args.pop(0)
            namespace = obj.__class__.__name__

            ## Key will be either a md5 hash or just pickle object,
            ## in the form of `function name`:`key`
            key = cache.get_hash(pickle.dumps([key_args, kwargs]))
            cache_key = '{namespace}:{func_name}:{key}'.format(
                namespace=namespace,
                func_name=function.__name__,
                key=key)

            try:
                return cache.get_pickle(cache_key)
            except (redis_cache.ExpiredKeyException,
                    redis_cache.CacheMissException) as e:
                ## Add some sort of cache miss handing here?
                pass
            except:
                logging.exception("Unknown redis-simple-cache error. Please check your Redis free space.")

            try:
                result = function(*args, **kwargs)
            except redis_cache.DoNotCache as e:
                result = e.result
            else:
                try:
                    cache.store_pickle(cache_key, result, expire)
                except redis_cache.redis.ConnectionError as e:
                    logging.exception(e)

            return result
        return func
    return decorator

