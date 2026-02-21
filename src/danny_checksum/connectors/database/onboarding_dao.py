import json

from sqlalchemy import select

from danny_checksum.connectors.database.engine import get_session
from danny_checksum.connectors.database.models import OnboardingSession

ONBOARDING_FIELDS = [
    "customer_name",
    "repository",
    "api_endpoints",
    "auth_method",
    "auth_details",
    "test_output_folder",
    "test_output_format",
    "test_descriptions",
    "additional_context",
]

# Fields stored as JSON strings
_JSON_FIELDS = {"api_endpoints", "test_descriptions"}


def create_session(phase: str = "sales") -> int:
    """Create a new onboarding session and return its ID."""
    with get_session() as session:
        obj = OnboardingSession(phase=phase)
        session.add(obj)
        session.commit()
        return obj.id


def get_onboarding_session(session_id: int) -> dict | None:
    """Return the onboarding session as a dict, or None if not found."""
    with get_session() as db:
        obj = db.scalars(
            select(OnboardingSession).where(OnboardingSession.id == session_id)
        ).first()
        if obj is None:
            return None
        result = {field: getattr(obj, field) for field in ONBOARDING_FIELDS}
        # Deserialise JSON fields
        for field in _JSON_FIELDS:
            if result[field] is not None:
                result[field] = json.loads(result[field])
        result["id"] = obj.id
        result["phase"] = obj.phase
        return result


def update_field(session_id: int, field_name: str, value: object) -> None:
    """Update a single onboarding field. Raises ValueError for invalid fields."""
    if field_name not in ONBOARDING_FIELDS:
        raise ValueError(
            f"Invalid field: {field_name}. Must be one of {ONBOARDING_FIELDS}"
        )
    with get_session() as db:
        obj = db.scalars(
            select(OnboardingSession).where(OnboardingSession.id == session_id)
        ).first()
        if obj is None:
            raise ValueError(f"Session {session_id} not found")
        # Serialise lists/dicts to JSON for JSON fields
        if field_name in _JSON_FIELDS and not isinstance(value, str):
            value = json.dumps(value)
        setattr(obj, field_name, value)
        db.commit()


def update_phase(session_id: int, phase: str) -> None:
    """Transition the session to a new phase ('sales' or 'customer')."""
    with get_session() as db:
        obj = db.scalars(
            select(OnboardingSession).where(OnboardingSession.id == session_id)
        ).first()
        if obj is None:
            raise ValueError(f"Session {session_id} not found")
        obj.phase = phase
        db.commit()


def get_unanswered_fields(session_id: int) -> list[str]:
    """Return list of field names that are still None."""
    data = get_onboarding_session(session_id)
    if data is None:
        raise ValueError(f"Session {session_id} not found")
    return [f for f in ONBOARDING_FIELDS if data[f] is None]
