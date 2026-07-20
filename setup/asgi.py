"""
ASGI config for setup project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""


from django.core.asgi import get_asgi_application
import os
import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")

django.setup()
application = get_asgi_application()
