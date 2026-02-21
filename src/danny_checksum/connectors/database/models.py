from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class CustomerRepo(Base):
    __tablename__ = "customer_repos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    last_git_sha_successfully_processed = Column(String, nullable=True)


class Deployment(Base):
    __tablename__ = "deployments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    component = Column(String, nullable=False)
    sha = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())


class OnboardingSession(Base):
    __tablename__ = "onboarding_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_name = Column(String, nullable=True)
    repository = Column(String, nullable=True)
    api_endpoints = Column(String, nullable=True)  # JSON string
    auth_method = Column(String, nullable=True)
    auth_details = Column(String, nullable=True)
    test_output_folder = Column(String, nullable=True)
    test_output_format = Column(String, nullable=True)
    test_descriptions = Column(String, nullable=True)  # JSON string
    additional_context = Column(String, nullable=True)
    phase = Column(String, nullable=False, default="sales")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
