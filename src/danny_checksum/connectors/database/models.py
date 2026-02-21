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
