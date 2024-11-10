from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from .base import Base


# Модерация статусов
class Status(PyEnum):
    new = "new"
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


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

    user = relationship("User", back_populates="perevals")
    coords = relationship("Coords", back_populates="perevals")
    images = relationship("PerevalImages", back_populates="pereval")
