from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class CustomerRepo(Base):
    __tablename__ = "customer_repos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    last_git_sha_successfully_processed = Column(String, nullable=True)
