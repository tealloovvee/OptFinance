"""
ASGI config for MainProject project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from registration.middleware import JWTAuthMiddleware
import registration.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MainProject.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddleware(
        URLRouter(
            registration.routing.websocket_urlpatterns
        )
    ),
})
