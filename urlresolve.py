import logging
import os, re
import requests
import redis
from urlparse import urlparse


"""Not guaranteed to be a short URL, but looks like one:"""
SHORT_URL_PAT = re.compile('http://(?:[\w_-]+\.)?[\w_-]+\.\w{2,3}/\w+$')
MAX_SHORT_URL_LENGTH = 30
DNR_FILE = os.path.join(os.path.dirname(__file__), 'do_not_resolve.txt')
TTL = 60 * 60 * 24

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'

class InvalidUrl(Exception): pass


class UrlResolver(object):
    """Class instantiated on a particular input URL for resolving that
    URL to a non-redirected endpoint. In general, use the resolve
    classmethod instead of instantiating this class directly."""

    def __init__(self, backend, url):
        self.backend = backend
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

    def _handle_resolve(self, url, check_cache=True, send_user_agent=False):
        if check_cache and self.check_cache(url):
            return
        if not self.check_should_resolve(url):
            return
        if send_user_agent:
            r = requests.get(url, allow_redirects=False,
                headers={ 'User-Agent': USER_AGENT })
        else:
            r = requests.get(url, allow_redirects=False)
        self.requests.append({
            'type': 'NET',
            'request': url,
            'response': r.status_code
        })
        if r.status_code == 200:
            domain = urlparse(url).netloc
            self.backend.set(domain, '')
            self.info.append(
                'Added domain %s to do-not-resolve list' % domain
            )
            self.resolved = True
        elif r.status_code in (301, 302):
            loc = r.headers['Location']
            return self._handle_resolve(loc)
        elif not send_user_agent:
            return self._handle_resolve(url, check_cache=False,
                send_user_agent=True)
        else:
            self._error('http response status code: %s' % r.status_code)
        return

    def _resolve(self, url):
        try:
            self._handle_resolve(url)
        except requests.exceptions.ConnectionError, e:
            self._error('Connection error resolving URL: %s' % url)
        except InvalidUrl:
            self._error('Bad URL: %s' % url)
        self.cache_aliases()
        return self.data()

    @classmethod
    def resolve(cls, backend, url):
        """Resolve the URL to a non-shortened endpoint."""
        resolver = UrlResolver(backend, url)
        return resolver._resolve(url)

    def check_cache(self, url):
        """Check the redis db for previously resolved URL."""
        cached_url = self.backend.get(url)
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
        (i.e. listed in the backend), is not longer than the max short URL
        length, and otherwise looks like a short URL."""
        domain = urlparse(url).netloc
        if not domain:
            raise InvalidUrl
        if SHORT_URL_PAT.findall(url):
            return True
        if any([
                self.backend.exists(domain),
                len(url) > MAX_SHORT_URL_LENGTH ]):
            self.resolved_url=url
            if len(self.requests) > 1:
                self.resolved=True
            return False
        else:
            return True

    def cache_aliases(self):
        """Cache uncached URL aliases from the request history."""
        if self.resolved:
            for req in self.requests[:-1]:
                if req['type'] == 'CACHE' and req['response'] == None:
                    self.backend.set(req['request'], self.resolved_url)
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


class RedisUrlResolver(UrlResolver):

    from backends import RedisBackend
    backend = RedisBackend()

    @classmethod
    def resolve(cls, url):
        """Resolve the URL to a non-shortened endpoint."""
        resolver = UrlResolver(cls.backend, url)
        return resolver._resolve(url)
