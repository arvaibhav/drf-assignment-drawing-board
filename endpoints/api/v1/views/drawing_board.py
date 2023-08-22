from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from core.constants import PermissionTypeEnum
from core.drawing_board_user_permission import (
    DrawingBoardAuthorization,
    remove_users_from_drawing_board_and_socket_channel,
    add_user_in_drawing_board,
)
from db.models import DrawingBoard
from endpoints.api.v1.serializers.drawing_board import (
    DrawingBoardCreateSerializer,
    DrawingBoardDetailSerializer,
    DrawingBoardListSerializer,
    DrawingBoardAccessControlSerializer,
)
from endpoints.middleware.authentication.auth import JwtAuthenticatedUser


class DrawingBoardCreateView(generics.CreateAPIView):
    serializer_class = DrawingBoardCreateSerializer
    permission_classes = [JwtAuthenticatedUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        drawing_board = serializer.save()
        response_data = {"unique_id": drawing_board.unique_id}
        return Response(response_data, status=status.HTTP_201_CREATED)


class DrawingBoardDetailView(APIView):
    permission_classes = [JwtAuthenticatedUser]

    def get(self, request, drawing_board_id, *args, **kwargs):
        drawing_board = get_object_or_404(DrawingBoard, unique_id=drawing_board_id)
        can_read, can_write = DrawingBoardAuthorization(
            drawing_board=drawing_board, user_id=request.auth_payload.get("user_id")
        ).get_user_read_and_write_permissions()
        if not can_read:
            return Response(
                {"error": "Authentication required for this drawing board."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = DrawingBoardDetailSerializer(drawing_board)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DrawingBoardAccessControlView(generics.CreateAPIView):
    permission_classes = [JwtAuthenticatedUser]
    serializer_class = DrawingBoardAccessControlSerializer

    def create(self, request, drawing_board_id, operation, *args, **kwargs):
        serializer = DrawingBoardAccessControlSerializer(data=request.data)

        if serializer.is_valid():
            user_ids = serializer.validated_data["user_ids"]
            permission_type = PermissionTypeEnum[
                serializer.validated_data["permission_type"]
            ].value
            if operation == "add":
                add_user_in_drawing_board(drawing_board_id, permission_type, user_ids)
            elif operation == "remove":
                remove_users_from_drawing_board_and_socket_channel(
                    drawing_board_id, permission_type, user_ids
                )
            else:
                return Response(
                    {"error": "Invalid operation"}, status=status.HTTP_400_BAD_REQUEST
                )
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DrawingBoardListView(generics.ListAPIView):
    serializer_class = DrawingBoardListSerializer
    permission_classes = [JwtAuthenticatedUser]

    def get_queryset(self):
        user_id = self.request.auth_payload.get("user_id")
        owned_boards = DrawingBoard.objects.filter(owner_user_id=user_id)
        shared_boards = DrawingBoard.objects.filter(
            shareddrawingboard__shared_to_id=user_id
        )
        return owned_boards.union(shared_boards)
