from sqlalchemy import select

from danny_checksum.connectors.database.engine import get_session
from danny_checksum.connectors.database.models import SlackThread


def create_thread(channel_id: str, thread_ts: str, session_id: int) -> SlackThread:
    """Create a SlackThread row and return it."""
    with get_session() as session:
        obj = SlackThread(
            channel_id=channel_id, thread_ts=thread_ts, session_id=session_id
        )
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj


def get_thread_by_ts(thread_ts: str) -> SlackThread | None:
    """Look up a SlackThread by its thread_ts."""
    with get_session() as session:
        return session.scalars(
            select(SlackThread).where(SlackThread.thread_ts == thread_ts)
        ).first()


def get_active_threads(channel_id: str) -> list[SlackThread]:
    """Return all tracked threads for a channel."""
    with get_session() as session:
        return list(
            session.scalars(
                select(SlackThread).where(SlackThread.channel_id == channel_id)
            ).all()
        )


def update_message_history(
    thread_ts: str, message_history_json: str, last_reply_ts: str
) -> None:
    """Persist agent message history and the latest reply ts."""
    with get_session() as session:
        obj = session.scalars(
            select(SlackThread).where(SlackThread.thread_ts == thread_ts)
        ).first()
        if obj is None:
            raise ValueError(f"SlackThread with thread_ts={thread_ts!r} not found")
        obj.message_history_json = message_history_json
        obj.last_reply_ts = last_reply_ts
        session.commit()
