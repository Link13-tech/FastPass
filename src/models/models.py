from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
from enum import Enum as PyEnum

Base = declarative_base()


# Модерация статусов
class Status(PyEnum):
    new = "new"
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


# Модель пользователей
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=False)


# Модель координат
class Coords(Base):
    __tablename__ = "coords"

    id = Column(Integer, primary_key=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    height = Column(Integer, nullable=False)


# Модель перевалов
class PerevalAdded(Base):
    __tablename__ = "pereval_added"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    coord_id = Column(Integer, ForeignKey("coords.id"), nullable=False)
    beauty_title = Column(String)
    title = Column(String)
    other_titles = Column(String)
    connect = Column(String)
    add_time = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(Status), default=Status.new)

    user = relationship("User", backref="perevals")
    coords = relationship("Coords", backref="perevals")


# Модель для изображений
class PerevalImages(Base):
    __tablename__ = "pereval_images"

    id = Column(Integer, primary_key=True)
    pereval_id = Column(Integer, ForeignKey("pereval_added.id"), nullable=False)
    image_url = Column(String, nullable=False)
