from sqlalchemy import select

from danny_checksum.connectors.database.engine import get_session
from danny_checksum.connectors.database.models import MonitoredSlackChannel


def add_channel(channel_id: str, name: str) -> None:
    """Insert a monitored channel. No-op if it already exists."""
    with get_session() as session:
        existing = session.scalars(
            select(MonitoredSlackChannel).where(
                MonitoredSlackChannel.channel_id == channel_id
            )
        ).first()
        if existing is not None:
            return
        session.add(MonitoredSlackChannel(channel_id=channel_id, name=name))
        session.commit()


def remove_channel(channel_id: str) -> None:
    """Delete a monitored channel by channel_id."""
    with get_session() as session:
        channel = session.scalars(
            select(MonitoredSlackChannel).where(
                MonitoredSlackChannel.channel_id == channel_id
            )
        ).first()
        if channel is not None:
            session.delete(channel)
            session.commit()


def list_channels() -> list[MonitoredSlackChannel]:
    """Return all monitored channels."""
    with get_session() as session:
        return list(session.scalars(select(MonitoredSlackChannel)).all())
