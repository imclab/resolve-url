"""
WSGI config for resolve-url project.
"""
import os
import sys
import site

site.addsitedir('/home/apps/env/resolve-url/lib/python2.7/site-packages')
sys.path.append('/home/apps/sites/resolve-url')
sys.stdout = sys.stderr

os.environ.setdefault('FLASK_SETTINGS_MODULE', 'core.settings.prd')

from api import app as application
