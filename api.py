'''
Main entrypoint file.  To run:

  $ python api.py

'''
from flask import Flask
from flask import request
from flask import jsonify
import importlib
import sys
import os
from urlresolve import UrlResolver
import logging
from logging import StreamHandler

# Set default FLASK_SETTINGS_MODULE for debug mode
if __name__ == "__main__":
    if not os.environ.get('FLASK_SETTINGS_MODULE', ''):
        os.environ['FLASK_SETTINGS_MODULE'] = 'core.settings.loc'

app = Flask(__name__)
app.logger.addHandler(StreamHandler())

# Import settings module for the inject_static_url context processor.
settings_module = os.environ.get('FLASK_SETTINGS_MODULE')

try:
    importlib.import_module(settings_module)
except ImportError, e:
    raise ImportError(
        "Could not import settings '%s' (Is it on sys.path?): %s" \
        % (settings_module, e))

settings = sys.modules[settings_module]


@app.route("/", methods=['GET'])
def index():
    url = request.args.get('url')
    if url:
        resolved = UrlResolver.resolve(url)
        return jsonify( resolved )
    else:
        return jsonify({})
    
        
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
