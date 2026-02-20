from sqlalchemy import select

from danny_checksum.connectors.database.engine import get_session
from danny_checksum.connectors.database.models import CustomerRepo


def get_last_sha(repo_name: str) -> str | None:
    """Return the last processed SHA for a repo, or None if not found."""
    with get_session() as session:
        customer_repo = session.scalars(
            select(CustomerRepo).where(CustomerRepo.name == repo_name)
        ).first()
        if customer_repo is None:
            return None
        return customer_repo.last_git_sha_successfully_processed


def set_last_sha(repo_name: str, sha: str) -> None:
    """Create or update the last processed SHA for a repo."""
    with get_session() as session:
        customer_repo = session.scalars(
            select(CustomerRepo).where(CustomerRepo.name == repo_name)
        ).first()

        if customer_repo is None:
            customer_repo = CustomerRepo(name=repo_name)
            session.add(customer_repo)

        customer_repo.last_git_sha_successfully_processed = sha
        session.commit()
