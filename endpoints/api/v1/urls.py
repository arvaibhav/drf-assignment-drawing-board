from django.urls import path, re_path
from endpoints.api.v1.views import *
from endpoints.api.v1.views.drawing_board import (
    DrawingBoardListView,
    DrawingBoardCreateView,
    DrawingBoardDetailView,
)

urlpatterns = [
    path("signup/", UserSignupView.as_view(), name="signup"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("drawing_boards/", DrawingBoardListView.as_view(), name="drawing_board_list"),
    path(
        "drawing_boards/create/",
        DrawingBoardCreateView.as_view(),
        name="drawing_board_create",
    ),
    re_path(
        r"drawing_boards/(?P<unique_id>[0-9a-f-]+)/$",
        DrawingBoardDetailView.as_view(),
        name="drawing_board_detail",
    ),
    path(
        "api/v1/drawing_boards/<uuid:drawing_board_id>/permissions/",
        DrawingBoardAccessControlView.as_view(),
        name="drawing-board-permissions-update",
    ),
]
