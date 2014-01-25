import logging
import os, re
import requests
import redis
from urlparse import urlparse


"""Not guaranteed to be a short URL, but looks like one:"""
SHORT_URL_PAT = re.compile('http://(?:[\w_-]+\.)?[\w_-]+\.\w{2,3}/\w+$')
#END_LINK_PAT = re.compile('\.\w{1,4}/?$')
MAX_SHORT_URL_LENGTH = 30
DNR_FILE = os.path.join(os.path.dirname(__file__), 'do_not_resolve.txt')
TTL = 60 * 60 * 24

class InvalidUrl(Exception): pass

def get_redis_db():
    return redis.StrictRedis(host='localhost', port=6379, db=0)

redisdb = get_redis_db()
def _get_redis(key):
    return redisdb.get(key)

def _set_redis(key, value, ttl=None):
    redisdb.set(key, value, ex=ttl) 

def _exists_redis(key):
    return redisdb.exists(key)


class UrlResolver(object):
    """Class instantiated on a particular input URL for resolving that
    URL to a non-redirected endpoint. In general, use the resolve
    classmethod instead of instantiating this class directly."""

    def __init__(self, url):
        self.url = url
        self.status = 'OK'
        self.requests = []
        self.resolved = False
        self.info = []
        self.resolved_url = None

    def _error(self, reason):
        logging.error(reason)
        self.status = 'ERR'
        self.reason = reason
        self.resolved = False

    def _resolve(self, url):
        if self.check_cache(url):
            return
        if not self.check_should_resolve(url):
            return
        r = requests.get(url, allow_redirects=False)
        self.requests.append({
            'type': 'NET',
            'request': url,
            'response': r.status_code
        })
        if r.status_code == 200:
            domain = urlparse(url).netloc
            _set_redis(domain, '')
            self.info.append(
                'Added domain %s to do-not-resolve list' % domain
            )
            self.resolved = True
        elif r.status_code in (301, 302):
            loc = r.headers['Location']
            return self._resolve(loc)
        else:
            self._error('http response status code: %s' % r.status_code)
        return

    @classmethod
    def resolve(cls, url):
        """Resolve the URL to a non-shortened endpoint."""
        resolver = UrlResolver(url)
        try:
            resolver._resolve(url)
        except requests.exceptions.ConnectionError, e:
            resolver._error('Connection error resolving URL: %s' % url)
        except InvalidUrl:
            resolver._error('Bad URL: %s' % url)
        resolver.cache_aliases()
        return resolver.data()

    def check_cache(self, url):
        """Check the redis db for previously resolved URL."""
        cached_url = _get_redis(url)
        self.requests.append({
            'type': 'CACHE',
            'request': url,
            'response': cached_url
        })
        if cached_url:
            self.resolved_url=cached_url
            self.resolved=True
            return True
        else:
            return False

    def check_should_resolve(self, url):
        """A URL should be resolved if its domain is not in the DNR list
        (i.e. listed in the redis db), is not longer than the max short URL
        length, and otherwise looks like a short URL."""
        domain = urlparse(url).netloc
        if not domain:
            raise InvalidUrl
        if SHORT_URL_PAT.findall(url):
            return True
        should = True
        if _exists_redis(domain):
            should = False
        if len(url) > MAX_SHORT_URL_LENGTH:
            should = False
        if not should:
            self.resolved_url=url
            if len(self.requests) > 1:
                self.resolved=True
        return False

    def cache_aliases(self):
        """Cache uncached URL aliases from the request history."""
        if self.resolved:
            for req in self.requests[:-1]:
                if req['type'] == 'CACHE' and req['response'] == None:
                    _set_redis(req['request'], self.resolved_url)
                    self.info.append(
                        'Cached URL %s as %s' % (
                            req['request'], self.resolved_url))

    def data(self):
        data = {
            'status': self.status,
            'url': self.url,
            'requests': self.requests,
            'resolved': self.resolved,
            'info': self.info,
            'resolved_url': self.resolved_url
        }
        if hasattr(self, 'reason'):
            data['reason'] = self.reason
        return data
