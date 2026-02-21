from sqlalchemy import select

from danny_checksum.connectors.database.engine import get_session
from danny_checksum.connectors.database.models import SlackChannel


def get_last_thread_ts(channel_id: str) -> str | None:
    """Return the last seen thread_ts for a channel, or None if not found."""
    with get_session() as session:
        channel = session.scalars(
            select(SlackChannel).where(SlackChannel.channel_id == channel_id)
        ).first()
        if channel is None:
            return None
        return channel.last_thread_ts


def set_last_thread_ts(channel_id: str, thread_ts: str) -> None:
    """Create or update the last seen thread_ts for a channel."""
    with get_session() as session:
        channel = session.scalars(
            select(SlackChannel).where(SlackChannel.channel_id == channel_id)
        ).first()

        if channel is None:
            channel = SlackChannel(channel_id=channel_id)
            session.add(channel)

        channel.last_thread_ts = thread_ts
        session.commit()
