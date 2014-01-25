"""Production settings and globals."""
import sys
import os
from .base import *

# Import secrets
sys.path.append(
    os.path.normpath(os.path.join(PROJECT_ROOT, '../secrets/resolve-url/stg'))
)
from secrets import *

# Set static URL
STATIC_URL = 'http://media.knightlab.us/resolve-url/'

DATABASES = {
    'default': {
        'ENGINE': 'mongo',
        'NAME': 'resolve-url',
        'HOST': 'prd-mongo1.knilab.com',
        'PORT': 27017,
    }
}
