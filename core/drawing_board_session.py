from db.models import DrawingBoardUserChannel
from endpoints.websockets.util import (
    close_connection_for_channel,
    close_all_connections_in_group,
)


def get_drawing_board_group_name(drawing_board_id):
    return f"drawing_{drawing_board_id}"


def close_and_delete_user_channels(user_id):
    for channel in DrawingBoardUserChannel.objects.filter(user_id=user_id):
        close_connection_for_channel(channel_name=channel.channel_name)
        channel.delete()


def close_and_delete_drawing_board_channels(drawing_board_id):
    close_all_connections_in_group(
        group_name=get_drawing_board_group_name(drawing_board_id)
    )
    DrawingBoardUserChannel.objects.filter(drawing_board_id=drawing_board_id).delete()


def close_and_delete_drawing_board_channels_for_users(drawing_board_id, user_ids):
    for channel in DrawingBoardUserChannel.objects.filter(
        user__pk__in=user_ids, drawing_board_id=drawing_board_id
    ):
        close_connection_for_channel(channel_name=channel.channel_name)
        channel.delete()
