from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from core.constants import PermissionTypeEnum
from db.models import DrawingBoard, SharedDrawingBoard
from endpoints.api.v1.serializers.drawing_board import (
    DrawingBoardCreateSerializer,
    DrawingBoardDetailSerializer,
    DrawingBoardListSerializer,
)
from rest_framework.permissions import IsAuthenticated


class DrawingBoardCreateView(generics.CreateAPIView):
    serializer_class = DrawingBoardCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user_id = request.META.get("HTTP_USERID")
        try:
            owner = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST
            )

        permission_type = request.data.get("permission_type")
        shared_to = request.data.get("shared_to", [])

        if permission_type not in [
            PermissionTypeEnum.PUBLIC_READ.value,
            PermissionTypeEnum.PROTECTED_READ.value,
            PermissionTypeEnum.PROTECTED_READ_WRITE.value,
            PermissionTypeEnum.USER_READ.value,
            PermissionTypeEnum.USER_READ_WRITE.value,
        ]:
            return Response(
                {"error": "Invalid permission type"}, status=status.HTTP_400_BAD_REQUEST
            )

        if (
            permission_type
            in [
                PermissionTypeEnum.USER_READ.value,
                PermissionTypeEnum.USER_READ_WRITE.value,
            ]
            and not shared_to
        ):
            return Response(
                {"error": "shared_to field is required for the given permission type"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create DrawingBoard
        drawing_board = DrawingBoard.objects.create(
            owner_user=owner, permission_type=permission_type
        )

        # Create SharedDrawingBoard entries if needed
        if permission_type in [
            PermissionTypeEnum.USER_READ.value,
            PermissionTypeEnum.USER_READ_WRITE.value,
        ]:
            for shared_user_data in shared_to:
                shared_user = User.objects.get(id=shared_user_data["user_id"])
                SharedDrawingBoard.objects.create(
                    drawing_board=drawing_board,
                    shared_to=shared_user,
                    can_write=shared_user_data["can_write"],
                )

            if shared_to:
                return Response(
                    {
                        "error": "shared_to field must be empty for the given permission type"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        elif permission_type in [
            PermissionTypeEnum.USER_READ.value,
            PermissionTypeEnum.USER_READ_WRITE.value,
        ]:
            if not shared_to:
                return Response(
                    {
                        "error": "shared_to field is required for the given permission type"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"error": "Invalid permission type"}, status=status.HTTP_400_BAD_REQUEST
            )

        response_data = {
            "unique_id": drawing_board.unique_id,
            "permission_type": permission_type,
            "shared_to": shared_to,
        }

        return Response(response_data, status=status.HTTP_201_CREATED)


class DrawingBoardDetailView(APIView):
    def get(self, request, drawing_board_id, *args, **kwargs):
        drawing_board = get_object_or_404(DrawingBoard, unique_id=drawing_board_id)

        if drawing_board.permission_type == PermissionTypeEnum.PUBLIC_READ.value:
            # No authentication required for PUBLIC boards
            serializer = DrawingBoardDetailSerializer(drawing_board)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif drawing_board.permission_type in [
            PermissionTypeEnum.PROTECTED_READ.value,
            PermissionTypeEnum.PROTECTED_READ_WRITE.value,
        ]:
            # Token authentication required for PROTECTED boards
            if request.user.is_anonymous:
                return Response(
                    {"error": "Authentication required for this drawing board."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            serializer = DrawingBoardDetailSerializer(drawing_board)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif drawing_board.permission_type in [
            PermissionTypeEnum.USER_READ.value,
            PermissionTypeEnum.USER_READ_WRITE.value,
        ]:
            # Check if the requesting user is either the owner or has been shared with
            if (
                drawing_board.owner_user == request.user
                or SharedDrawingBoard.objects.filter(
                    drawing_board=drawing_board, shared_to=request.user
                ).exists()
            ):
                serializer = DrawingBoardDetailSerializer(drawing_board)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {
                        "error": "You do not have permission to access this drawing board."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        else:
            return Response(
                {"error": "Invalid permission type"}, status=status.HTTP_400_BAD_REQUEST
            )


class DrawingBoardAccessControlView(APIView):
    def get(self, request, drawing_board_id, *args, **kwargs):
        drawing_board = get_object_or_404(DrawingBoard, unique_id=drawing_board_id)

        if drawing_board.permission_type == PermissionTypeEnum.PUBLIC_READ.value:
            # No authentication required for PUBLIC boards
            serializer = DrawingBoardDetailSerializer(drawing_board)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif drawing_board.permission_type in [
            PermissionTypeEnum.PROTECTED_READ.value,
            PermissionTypeEnum.PROTECTED_READ_WRITE.value,
        ]:
            # Token authentication required for PROTECTED boards
            if request.user.is_anonymous:
                return Response(
                    {"error": "Authentication required for this drawing board."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            serializer = DrawingBoardDetailSerializer(drawing_board)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif drawing_board.permission_type in [
            PermissionTypeEnum.USER_READ.value,
            PermissionTypeEnum.USER_READ_WRITE.value,
        ]:
            # Check if the requesting user is either the owner or has been shared with
            if (
                drawing_board.owner_user == request.user
                or SharedDrawingBoard.objects.filter(
                    drawing_board=drawing_board, shared_to=request.user
                ).exists()
            ):
                serializer = DrawingBoardDetailSerializer(drawing_board)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {
                        "error": "You do not have permission to access this drawing board."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        else:
            return Response(
                {"error": "Invalid permission type"}, status=status.HTTP_400_BAD_REQUEST
            )


class DrawingBoardListView(generics.ListAPIView):
    serializer_class = DrawingBoardListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.META.get("HTTP_USERID")
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return []  # Or raise an appropriate error response

        owned_boards = DrawingBoard.objects.filter(owner_user=user)
        shared_boards = DrawingBoard.objects.filter(sharedrawingboard__shared_to=user)

        return owned_boards.union(shared_boards)
