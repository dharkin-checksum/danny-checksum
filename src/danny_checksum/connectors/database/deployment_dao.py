from danny_checksum.connectors.database.engine import get_session
from danny_checksum.connectors.database.models import Deployment


def create_deployment(component: str, sha: str) -> None:
    """Insert a new deployment record."""
    with get_session() as session:
        session.add(Deployment(component=component, sha=sha))
        session.commit()
