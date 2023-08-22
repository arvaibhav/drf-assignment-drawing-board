from channels.db import database_sync_to_async

from core.constants import PermissionTypeEnum
from core.drawing_board_session import close_and_delete_drawing_board_channels_for_users
from db.models import DrawingBoard, SharedDrawingBoard


class DrawingBoardAuthorization:
    def __init__(self, drawing_board_id=None, drawing_board=None, user_id=None):
        if not drawing_board and not drawing_board_id:
            # Lazy loading
            raise Exception(
                "Either of these required: drawing_board or drawing_board_id"
            )

        self.drawing_board_id = drawing_board_id
        if drawing_board:
            self.__drawing_board = drawing_board
        else:
            self.__drawing_board = None
        self.user_id = user_id
        self.__shared_with_user = None

    @property
    def drawing_board(self) -> DrawingBoard:
        if self.__drawing_board is None:
            self.__drawing_board = DrawingBoard.objects.get(pk=self.drawing_board_id)
        return self.__drawing_board

    @property
    def is_public_read_drawing_board(self):
        return self.drawing_board.permission_type in (
            PermissionTypeEnum.PUBLIC_READ.value,
            PermissionTypeEnum.USER_WRITE_PUBLIC_READ.value,
        )

    @property
    def is_owner_drawing_board(self):
        return self.user_id and self.drawing_board.owner_user_id == self.user_id

    @property
    def is_protected_read_drawing_board(self):
        return (
            self.drawing_board.permission_type
            in (
                PermissionTypeEnum.PROTECTED_READ.value,
                PermissionTypeEnum.PROTECTED_WRITE.value,
                PermissionTypeEnum.USER_WRITE_PROTECTED_READ.value,
            )
            or self.is_protected_write_drawing_board
        )

    @property
    def is_protected_write_drawing_board(self):
        return (
            self.drawing_board.permission_type
            == PermissionTypeEnum.PROTECTED_WRITE.value
        )

    @property
    def is_user_read_drawing_board(self):
        return (
            self.drawing_board.permission_type == PermissionTypeEnum.USER_READ
            or self.is_user_write_drawing_board
        )

    @property
    def is_user_write_drawing_board(self):
        return self.user_id and self.drawing_board.permission_type in (
            PermissionTypeEnum.USER_WRITE,
            PermissionTypeEnum.USER_WRITE_PUBLIC_READ,
            PermissionTypeEnum.USER_WRITE_PROTECTED_READ,
        )

    @property
    def is_shared_with_user(self):
        if self.__shared_with_user is None:
            self.__shared_with_user = SharedDrawingBoard.objects.filter(
                drawing_board_id=self.drawing_board.unique_id, shared_to_id=self.user_id
            ).exists()

        return self.__shared_with_user

    @database_sync_to_async
    def get_user_read_and_write_permissions(self):
        has_read_access = False
        has_write_access = False
        # if user is owner
        if self.is_owner_drawing_board:
            has_read_access = True
            has_write_access = True

        # Public read check
        if not has_read_access and self.is_public_read_drawing_board:
            has_read_access = True

        # Protected read check
        if not has_read_access and (
            self.user_id and self.is_protected_read_drawing_board
        ):
            has_read_access = True

        # User specific read check
        if not has_read_access and (self.user_id and self.is_user_read_drawing_board):
            if self.is_shared_with_user:
                has_read_access = True

        # Protected write check
        if not has_write_access and self.is_protected_write_drawing_board:
            if self.user_id:
                has_write_access = True

        # User specific write check
        if not has_write_access and self.is_user_write_drawing_board:
            if self.is_shared_with_user:
                has_write_access = True

        return has_read_access, has_write_access


def get_permission_type(permission_type_key):
    try:
        return PermissionTypeEnum[permission_type_key].value
    except KeyError:
        return None


def validate_permission_type(permission_type_key) -> (int, str):
    """
    Validates the given permission type key by checking if it corresponds to a valid permission type.

    :param permission_type_key: The permission type key (e.g., "PUBLIC_READ") as a string.
    :return: A tuple containing the corresponding permission type value (if valid) and an error message.
             If the permission type key is valid, the error message will be None.
             If the permission type key is invalid, the permission type value will be None and an error message
             will describe the issue.

    Usage:
        permission_type, error_message = validate_permission_type("PUBLIC_READ")
        if permission_type is None:
            print(error_message)  # Output: "Invalid permission type"
    """

    permission_type = get_permission_type(permission_type_key)

    if permission_type is None:
        return None, "Invalid permission type"

    if permission_type not in [choice.value for choice in PermissionTypeEnum]:
        return None, "Invalid permission type"

    return permission_type, None


def add_user_in_drawing_board(drawing_board_id, permission_type, user_ids):
    if permission_type not in [
        PermissionTypeEnum.USER_READ.value,
        PermissionTypeEnum.USER_WRITE.value,
    ]:
        raise Exception("Invalid permission type passed")

    drawing_board = DrawingBoard.objects.get(pk=drawing_board_id)
    drawing_board.permission_type = PermissionTypeEnum.USER_WRITE.value
    drawing_board.save()

    SharedDrawingBoard.objects.bulk_create(
        [
            SharedDrawingBoard(
                shared_to_id=user_id,
                can_write=True
                if permission_type == PermissionTypeEnum.USER_WRITE.value
                else False,
                drawing_board_id=drawing_board_id,
            )
            for user_id in user_ids
        ]
    )


def remove_users_from_drawing_board_and_socket_channel(
    drawing_board_id, permission_type, user_ids
):
    if permission_type == PermissionTypeEnum.USER_READ.value:
        # better approach is to soft delete
        SharedDrawingBoard.objects.filter(
            shared_to__pk__in=user_ids, drawing_board_id=drawing_board_id
        ).delete()
    else:
        SharedDrawingBoard.objects.filter(
            shared_to__pk__in=user_ids, drawing_board_id=drawing_board_id
        ).update(can_write=False)

    close_and_delete_drawing_board_channels_for_users(drawing_board_id, user_ids)
