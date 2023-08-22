from django.http import JsonResponse
from endpoints.middleware.base import BaseWebsocketMiddleware, BaseHttpMiddleware
from .auth import validate_access_token
from channels.exceptions import DenyConnection
import traceback


class HttpTokenMiddleware(BaseHttpMiddleware):
    def __call__(self, request):
        if self.skip_middleware(request):
            # continue with other middleware/ view
            return self.get_response(request)

        token = request.META.get("HTTP_AUTHORIZATION", "").split("Bearer ")[-1]
        try:
            payload = validate_access_token(token)
            request.auth_payload = payload
            return self.get_response(request)
        except Exception as e:
            return JsonResponse({"error": (e)}, status=401)


class WebsocketTokenMiddleware(BaseWebsocketMiddleware):
    async def __call__(self, scope, receive, send):
        if self.skip_middleware(scope):
            # continue with other middleware/ view
            return await super().__call__(scope, receive, send)

        headers = dict(scope["headers"])
        token_header = headers.get(b"authorization")

        if token_header:
            token = token_header.decode("utf-8").split("Bearer ")[-1]
            try:
                payload = validate_access_token(token)
                scope["auth_payload"] = payload
                return await super().__call__(scope, receive, send)
            except Exception as e:
                print(traceback.format_exc(), "ERROR in websocket auth")
                return DenyConnection(str(e))


HttpTokenMiddleware.SKIP_FOR_SUFFIX.append("signup/")
HttpTokenMiddleware.SKIP_FOR_SUFFIX.append("login/")
HttpTokenMiddleware.SKIP_FOR_SUFFIX.append("refresh-token/")
