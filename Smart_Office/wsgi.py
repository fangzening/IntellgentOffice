"""
WSGI config for Smart_Office project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os
import sys
from django.core.wsgi import get_wsgi_application
from Smart_Office import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Smart_Office.settings')
sys.path.append(settings.MEDIA_ROOT)

application = get_wsgi_application()
