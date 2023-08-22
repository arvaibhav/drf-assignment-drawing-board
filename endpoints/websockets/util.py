from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def close_connection_for_channel(channel_name):
    channel_layer = get_channel_layer()
    # Send a 'websocket.close' event to the channel_name.
    async_to_sync(channel_layer.send)(channel_name, {"type": "websocket.close"})


def close_all_connections_in_group(group_name):
    channel_layer = get_channel_layer()
    # Send a 'websocket.close' event to the group.
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "websocket.close",
        },
    )
