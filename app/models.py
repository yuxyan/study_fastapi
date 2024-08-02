from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = 'userTable'
    uid = Column(Integer, primary_key=True)
    username = Column(String(10))
    password = Column(String(50))
    privilege = Column(String(3))


class Household(Base):
    __tablename__ = 'household'
    building_number = Column(String(4), primary_key=True)
    room_number = Column(String(4), primary_key=True)
    area = Column(Integer)
    telephone_number = Column(String(11))
    person_name = Column(String(10))
    work_unit = Column(String(50))
    home_number = Column(Integer)
    weixiu_money = Column(Integer)
