from enum import Enum, IntFlag


class PermissionTypeEnum(IntFlag):
    PUBLIC_READ = 1
    USER_READ = 2
    USER_WRITE = 4
    PROTECTED_READ = 8  # not to particular user but any registered user
    PROTECTED_WRITE = 16
    # combination
    USER_WRITE_PUBLIC_READ = USER_WRITE | PUBLIC_READ  # 5
    PROTECTED_WRITE_PUBLIC_READ = PROTECTED_WRITE | PUBLIC_READ  # 17
    USER_WRITE_PROTECTED_READ = USER_WRITE | PROTECTED_READ  # 12


class ActionTypeEnum(Enum):
    FREEHAND_DRAW = 1
    DRAW_LINE = 2
    DRAW_POLYGON = 3
    WRITE_TEXT = 4
