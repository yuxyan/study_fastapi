from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = 'userTable'
    uid = Column(Integer, primary_key=True)
    username = Column(String(10))
    password = Column(String(50))
    privilege = Column(String(3))
