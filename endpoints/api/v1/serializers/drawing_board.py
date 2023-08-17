from core.constants import PermissionTypeEnum
from db.models import DrawingBoard, SharedDrawingBoard
from rest_framework import serializers


class SharedDrawingBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharedDrawingBoard
        fields = "__all__"


class DrawingBoardCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DrawingBoard
        fields = ["permission_type"]

    def create(self, validated_data):
        user = self.context["request"].user
        drawing_board = DrawingBoard.objects.create(owner_user=user, **validated_data)
        return drawing_board


class DrawingBoardDetailSerializer(serializers.ModelSerializer):
    permission_type = serializers.ChoiceField(
        choices=[(choice.value, choice.name) for choice in PermissionTypeEnum]
    )
    created_on = serializers.DateTimeField()
    shared_to = serializers.SerializerMethodField()

    class Meta:
        model = DrawingBoard
        fields = ["unique_id", "permission_type", "shared_to", "created_on"]

    def get_shared_to(self, obj):
        shared_users = SharedDrawingBoard.objects.filter(drawing_board=obj)
        return [
            {
                "user_id": shared.shared_to.pk,
                "user_name": shared.shared_to.username,
                "can_write": shared.can_write,
            }
            for shared in shared_users
        ]


from rest_framework import serializers
from db.models import DrawingBoard, SharedDrawingBoard


class DrawingBoardListSerializer(serializers.ModelSerializer):
    shared_by = serializers.SerializerMethodField()
    can_write = serializers.SerializerMethodField()

    class Meta:
        model = DrawingBoard
        fields = [
            "unique_id",
            "created_on",
            "permission_type",
            "shared_by",
            "can_write",
        ]

    def get_shared_by(self, obj):
        shared_board = SharedDrawingBoard.objects.filter(drawing_board=obj).first()
        return None if not shared_board else shared_board.shared_to.id

    def get_can_write(self, obj):
        shared_board = SharedDrawingBoard.objects.filter(drawing_board=obj).first()
        return False if not shared_board else shared_board.can_write
