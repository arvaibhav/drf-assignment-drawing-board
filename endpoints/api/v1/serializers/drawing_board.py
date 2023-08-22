from core.constants import PermissionTypeEnum, ActionTypeEnum
from core.drawing_board_user_permission import DrawingBoardAuthorization
from db.models import DrawingBoard, SharedDrawingBoard, DrawingSession
from rest_framework import serializers


class SharedDrawingBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharedDrawingBoard
        fields = "__all__"


class DrawingBoardCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DrawingBoard
        fields = ["header", "description"]

    def create(self, validated_data):
        user_id = self.context["request"].auth_payload.get("user_id")
        drawing_board = DrawingBoard.objects.create(
            owner_user_id=user_id, **validated_data
        )
        return drawing_board


class DrawingSessionSerializer(serializers.ModelSerializer):
    action_type = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = DrawingSession
        fields = [
            "user_name",
            "drawing_board",
            "action_meta",
            "action_type",
            "started_at",
            "ended_at",
            "version",
        ]

    def get_action_type(self, obj):
        return ActionTypeEnum(obj.action_type).name

    def get_user_name(self, obj):
        return obj.user.username


class DrawingBoardDetailSerializer(serializers.ModelSerializer):
    created_on = serializers.DateTimeField()
    shared_to = serializers.SerializerMethodField()
    drawing_sessions = DrawingSessionSerializer(many=True, read_only=True)
    permission_type = serializers.SerializerMethodField()

    class Meta:
        model = DrawingBoard
        fields = [
            "unique_id",
            "permission_type",
            "shared_to",
            "created_on",
            "drawing_sessions",
        ]

    def get_permission_type(self, obj):
        return PermissionTypeEnum(obj.permission_type).name

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


class DrawingBoardListSerializer(serializers.ModelSerializer):
    shared_by_username = serializers.SerializerMethodField()
    can_write = serializers.SerializerMethodField()
    can_read = serializers.SerializerMethodField()
    permission_type = serializers.SerializerMethodField()
    owner_username = serializers.CharField(source="owner_user.username", read_only=True)

    class Meta:
        model = DrawingBoard
        fields = [
            "unique_id",
            "created_on",
            "permission_type",
            "shared_by_username",
            "can_read",
            "can_write",
            "owner_username",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = self.context.get("request").auth_payload.get("user_id")
        self.access_permission_mapping = {}
        drawing_board_ids = []

        for board in self.instance:
            drawing_board_ids.append(board.pk)
            can_read, can_write = DrawingBoardAuthorization(
                drawing_board=board, user_id=self.user_id
            ).get_user_read_and_write_permissions()
            self.access_permission_mapping[board.pk] = {
                "can_read": can_read,
                "can_write": can_write,
            }

        shared_boards = SharedDrawingBoard.objects.filter(
            drawing_board__pk__in=drawing_board_ids
        ).select_related("drawing_board")

        self.shared_boards_mapping = {
            shared_board.drawing_board_id: shared_board
            for shared_board in shared_boards
        }

    def get_permission_type(self, obj):
        return PermissionTypeEnum(obj.permission_type).name

    def get_shared_by_username(self, obj: DrawingBoard):
        shared_board = self.shared_boards_mapping.get(obj.pk)
        shared_by_username = (
            None if not shared_board else shared_board.shared_to.username
        )
        if shared_by_username is None:
            if self.user_id and obj.owner_user.pk == self.user_id:
                shared_by_username = obj.owner_user.username
        return shared_by_username

    def get_can_write(self, obj):
        return self.access_permission_mapping.get(obj.pk, {}).get("can_write", False)

    def get_can_read(self, obj):
        return self.access_permission_mapping.get(obj.pk, {}).get("can_read", False)


class DrawingBoardAccessControlSerializer(serializers.Serializer):
    user_ids = serializers.ListField(child=serializers.IntegerField())
    permission_type = serializers.ChoiceField(
        choices=[PermissionTypeEnum.USER_WRITE.name, PermissionTypeEnum.USER_READ.name]
    )
