from urllib.parse import parse_qs

from channels.generic.websocket import AsyncJsonWebsocketConsumer

from core.concurrent_drawing_control import (
    close_all_drawing_session_of_user_id,
    do_drawing_operation_sessions,
    DrawingOperationException, end_drawing_operation_session,
)
from core.drawing_board_session import get_drawing_board_group_name
from core.drawing_board_user_permission import DrawingBoardAuthorization


class DrawingBoardConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        query_string = parse_qs(self.scope["query_string"].decode("utf-8"))
        self.drawing_board_id = query_string["drawing_board_id"][0]
        auth_payload: dict = self.scope.get(
            "auth_payload", {}
        )  # jwt_payload update via middleware
        self.user_id = auth_payload["user_id"]
        self.group_name = get_drawing_board_group_name(self.drawing_board_id)
        permissions = await DrawingBoardAuthorization(
            drawing_board_id=self.drawing_board_id, user_id=self.user_id
        ).get_user_read_and_write_permissions()
        self.can_read, self.can_write = permissions
        if not self.can_read:
            await self.close(code=4001)

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await close_all_drawing_session_of_user_id(
            user_id=self.user_id, drawing_board_id=self.drawing_board_id
        )
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content):
        if not self.can_write:
            await self.send_json({"error": "Write Permission Required"})

        end_drawing_session_id = content.get('end_drawing_session_id') # None implies new session start request
        action = content.get('action')

        if end_drawing_session_id:
            try:
                drawing_session_resp = await end_drawing_operation_session(self.drawing_board_id,end_drawing_session_id)
                await self.channel_layer.group_send(
                    self.group_name,
                    {"type": "broadcast_message", "message": drawing_session_resp},
                )
            except DrawingOperationException:
                await self.send_json({"error": "concurrent operation in process"})

        if not end_drawing_session_id or action in ["UNDO", "REDO"]:
            action = content["action"]
            action_meta = content["action_meta"]

            try:
                drawing_session_resp = await do_drawing_operation_sessions(
                    drawing_board_id=self.drawing_board_id,
                    action=action,
                    action_meta=action_meta,
                    user_id=self.user_id,
                )
                await self.channel_layer.group_send(
                    self.group_name,
                    {"type": "broadcast_message", "message": drawing_session_resp},
                )
            except DrawingOperationException:
                await self.send_json({"error": "concurrent operation in process"})

    async def broadcast_message(self, event):
        await self.send_json(event["message"])
