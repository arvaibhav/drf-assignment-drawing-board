from channels.middleware import BaseMiddleware
from django.http import HttpRequest
from django.middleware.http import MiddlewareMixin
from typing import List


class BaseHttpMiddleware(MiddlewareMixin):
    SKIP_FOR_SUFFIX: List[str] = []

    @classmethod
    def skip_middleware(cls, request: HttpRequest) -> bool:
        """Determine whether to skip this HTTP middleware based on the request path."""
        return any(x in request.path for x in cls.SKIP_FOR_SUFFIX)


class BaseWebsocketMiddleware(BaseMiddleware):
    SKIP_FOR_SUFFIX: List[str] = []

    @classmethod
    def skip_middleware(cls, scope: dict) -> bool:
        """Determine whether to skip this WebSocket middleware based on the connection scope."""
        return any(x in scope["path"] for x in cls.SKIP_FOR_SUFFIX)
