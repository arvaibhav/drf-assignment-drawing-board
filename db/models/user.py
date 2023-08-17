from django.db.models import *
from core.constants import PermissionTypeEnum, ActionTypeEnum
from db.models.base import BaseModel
from uuid import uuid4
from django.contrib.auth.models import User


class DrawingBoard(BaseModel):
    unique_id = UUIDField(primary_key=True, default=uuid4, editable=False)
    owner_user = ForeignKey(User, on_delete=CASCADE)

    PERMISSION_TYPE_CHOICES = [
        (choice.value, choice.name) for choice in PermissionTypeEnum
    ]
    permission_type = PositiveSmallIntegerField(
        choices=PERMISSION_TYPE_CHOICES,
        default=PermissionTypeEnum.PUBLIC_READ.value,
    )


class SharedDrawingBoard(BaseModel):
    # case where DrawingBoard permission_type is either USER_READ or USER_READ_WRITE
    drawing_board = ForeignKey(DrawingBoard, on_delete=CASCADE)
    shared_to = ForeignKey(User, on_delete=CASCADE)
    can_write = BooleanField(default=False)  # can read by default


class DrawingSession(BaseModel):
    user = ForeignKey(User, on_delete=CASCADE)
    drawing_board = ForeignKey(DrawingBoard, on_delete=CASCADE)

    action_meta = TextField()
    ACTION_TYPE_CHOICES = [(choice.value, choice.name) for choice in ActionTypeEnum]
    action_type = PositiveSmallIntegerField(
        choices=ACTION_TYPE_CHOICES, default=ActionTypeEnum.FREEHAND_DRAW
    )

    started_at = DateTimeField()
    ended_at = DateTimeField()

    version = PositiveSmallIntegerField(default=1)
