from enum import Enum


class PermissionTypeEnum(Enum):
    PUBLIC_READ = 1
    USER_READ = 2
    USER_READ_WRITE = 3
    PROTECTED_READ = 4
    PROTECTED_READ_WRITE = 5


class ActionTypeEnum(Enum):
    FREEHAND_DRAW = 1
    DRAW_LINE = 2
    DRAW_POLYGON = 3
    WRITE_TEXT = 4
