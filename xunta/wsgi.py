from __future__ import unicode_literals

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xunta.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
