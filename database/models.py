from sqlalchemy import Integer, String, Column
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(length=24), unique=True, nullable=False)
    email = Column(String)
    password = Column(String(length=1024), nullable=False)