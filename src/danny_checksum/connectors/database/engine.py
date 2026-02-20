from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DB_PATH = PROJECT_ROOT / "localdev.db"

engine = create_engine(f"sqlite:///{DB_PATH}")

def get_session() -> Session:
    return Session(engine)
