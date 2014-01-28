import ConfigParser
import os
import redis

wd = os.path.dirname(os.path.realpath(__file__))
CONFIG_FN = os.path.join(wd, 'backends.cfg')

conf = ConfigParser.ConfigParser()
conf.readfp(open(CONFIG_FN))


def get_redis_db():
    return redis.StrictRedis(
        host=conf.get('redis', 'host'),
        port=conf.getint('redis', 'port'),
        db=conf.getint('redis', 'db'))


class RedisBackend(object):

    def __init__(self):
        self.redisdb = get_redis_db()

    def get(self, key):
        return self.redisdb.get(key)

    def set(self, key, value, ttl=None):
        self.redisdb.set(key, value, ex=ttl)

    def exists(self, key):
        return self.redisdb.exists(key)
