from django.urls import re_path
from .consumer import DrawingBoardConsumer

websocket_urlpatterns = [
    re_path(r"drawing/", DrawingBoardConsumer.as_asgi()),
]
