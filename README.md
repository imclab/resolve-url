KnightLab resolve-url
=====================

A simple short URL resolver without a clever name.

Description
-----------

Attempts to resolve short URLs with as little network utilization as seems
reasonable. Designed primarily for the use case of resolving shortened URLs
occurring in Tweets, with some tolerance for things not getting resolved.
Due to this tolerance, the "should resolve" heuristics, and the lack of full
resolution to 200s, this might not be the right resolver for the most general
use cases.

License
-------
MIT License. See the included LICENSE.txt file.

Getting Started
---------------

* Create a backends.cfg file (see backends.cfg.example)

* Install the requirements (preferably in a virtual environment):

    pip install -r requirements

* Be sure redis is installed and running on the host specified in backends.cfg

* Run the Flask application:

    python api.py

* Hit the API with a shortened URL, e.g.

    http://localhost:8543/?url=http://bit.ly/1euQlFO

You should also be able to run api.py via wsgi. In the lab, we are using
Mozilla Circus (http://circus.readthedocs.org/) + Chaussette
(https://chaussette.readthedocs.org) with the following circus.ini:

    [circus]
    statsd=True
    httpd=False
    httpd_host=localhost
    httpd_port=<circus-port>

    [watcher:resolve_url]
    uid=apps
    copy_env=True
    virtualenv=<path-to-virtual-environment>
    cmd=chaussette --fd $(circus.sockets.resolve_url) --backend gevent api.app
    use_sockets=True
    numprocesses=1
    
    [socket:resolve_url]
    host=0.0.0.0
    port=<port-to-run-on>
    
    [env:resolve_url]
    PYTHONPATH=$PYTHONPATH:<path-to-repo>


Features
--------

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

Usage
-----

* To make a web API request: [api-location]/?url=[short-url]

    http://localhost:8543/?url=http://bit.ly/1euQlFO

  The web application will return a JSON payload with the resolved URL
  keyed as resolved\_url.

* Web API is optional. To call the library API directly, see usage in the
  web application (api.py)

* Redis is currently required -- but it should be easy enough to
  implement an alternative backend to plug into this.

