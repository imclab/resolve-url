A simple short URL resolver.

Attempts to resolve short URLs with as little network utilization as seems
reasonable.

* Resolved URLs are cached to Redis backend

* Multiple redirects are cached as final destination, rather than as
  intermediates, in order to reduce future cache hits

* 301 & 302 responses are assumed to have valid locations -- if the location
  header does not look like a short URL, it is taken to be a valid long
  URL for resolution

* Some shorteners return weird errors for missing User-Agent headers, whereas
  including the User-Agent is a problem in other cases. Thus, User-Agent
  is not included except as a fallback when a non-200, 301, or 302 is
  received.

* API response includes the history of requests made in resolving the URL,
  including cache requests. Thus, a request should not always return the
  same response (the requests history will differ, whereas the resolved URL
  should be the same)

* To make a web API request: <api-location>/?url=<short-url>

* Web API is optional. To call the library API directly, see usage in the
  web application (api.py)

* Redis is not currently optional -- but it should be easy enough to
  implement an alternative backend to plug into this.
