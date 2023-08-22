"""
ASGI config for drawing_board project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.middleware import BaseMiddleware
from channels.routing import ProtocolTypeRouter, URLRouter
from endpoints.middleware.authentication import WebsocketTokenMiddleware
from endpoints.middleware.error_logging_middleware import (
    WebsocketErrorLoggingMiddleware,
)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "drawing_board.settings")
django_asgi_app = get_asgi_application()
from endpoints.websockets import routing

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": BaseMiddleware(
            (
                WebsocketTokenMiddleware(
                    WebsocketErrorLoggingMiddleware(
                        URLRouter(routing.websocket_urlpatterns)
                    )
                )
            )
        ),
    }
)
