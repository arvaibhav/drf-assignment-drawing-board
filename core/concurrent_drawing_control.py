from datetime import timedelta
from enum import Enum

from channels.db import database_sync_to_async

from db.models import *
from utils.distibuted_lock import InMemoryLock
from django.utils.timezone import datetime

lock = InMemoryLock()


@database_sync_to_async
def close_all_drawing_session_of_user_id(user_id, drawing_board_id):
    DrawingSession.objects.filter(
        drawing_board_id=drawing_board_id, user_id=user_id
    ).update(ended_at=datetime.utcnow())


class DrawingOperationException(Exception):
    pass


@database_sync_to_async
def end_drawing_operation_session(drawing_board_id, drawing_board_session_id):
    can_lock = lock.acquire(key=drawing_board_id, timeout=25)
    if not can_lock:
        raise DrawingOperationException

    drawing_session: DrawingSession = DrawingSession.objects.get(drawing_board_session_id=drawing_board_session_id)
    lock.release(key=drawing_board_id)
    return {
        "action_type": ActionTypeEnum(drawing_session.action_meta).name,
        "action_meta": drawing_session.action_meta,
        "action_by_user_id": drawing_session.user_id,
        "drawing_session_id": drawing_session.pk,
    }


@database_sync_to_async
def do_drawing_operation_sessions(drawing_board_id, action_type, action_meta, user_id):
    can_lock = lock.acquire(key=drawing_board_id, timeout=5)
    if not can_lock:
        raise DrawingOperationException

    is_drawing_already_in_process = DrawingSession.objects.filter(
        ended_at__isnull=True, drawing_board_id=drawing_board_id,
        created_on__gte=datetime.now() - timedelta(hours=1)  # ignore old non ended sessions rare cases condition
    )
    if is_drawing_already_in_process:
        raise DrawingOperationException

    drawing_session = None
    if action_type == "UNDO":
        drawing_session = (
            DrawingSession.objects.filter(
                drawing_board_id=drawing_board_id, user_id=user_id
            )
            .order_by("-created_on")
            .first()
        )
        drawing_session.undo = True
        drawing_session.save()

    if action_type == "REDO":
        drawing_session = (
            DrawingSession.objects.filter(
                drawing_board_id=drawing_board_id, user_id=user_id, undo=True
            )
            .order_by("-created_on")
            .first()
        )
        drawing_session.undo = False
        drawing_session.save()

    else:
        drawing_session = DrawingSession.objects.create(
            drawing_board_id=drawing_board_id,
            user_id=user_id,
            action_meta=action_meta,
            action_type=ActionTypeEnum[action_type].value,
        )

    lock.release(key=drawing_board_id)
    return {
        "action_type": action_type,
        "action_meta": action_meta,
        "action_by_user_id": user_id,
        "drawing_session_id": drawing_session.pk,
    }
