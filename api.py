"""
Main entrypoint file.  To run:

  $ python api.py
"""
from flask import Flask
from flask import request
from flask import jsonify
from urlresolve import RedisUrlResolver
import logging
from logging import StreamHandler

app = Flask(__name__)
app.logger.addHandler(StreamHandler())

@app.route('/', methods=['GET'])
def index():
    url = request.args.get('url')
    if url:
        resolved = RedisUrlResolver.resolve(url)
        return jsonify( resolved )
    else:
        return jsonify({})
    
        
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
