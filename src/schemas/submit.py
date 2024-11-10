from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime
from enum import Enum


# Перечисление для статусов
class Status(str, Enum):
    new = "new"
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


class UserSchema(BaseModel):
    name: str
    email: EmailStr
    phone: str


class CoordsSchema(BaseModel):
    latitude: float
    longitude: float
    height: int


class ImageSchema(BaseModel):
    url: str


class SubmitDataRequest(BaseModel):
    beauty_title: str
    title: str
    other_titles: str
    connect: str
    coords: CoordsSchema
    images: List[ImageSchema]
    user: UserSchema


class SubmitDataResponse(BaseModel):
    message: str
    share_link: str
    status: str
    add_time: datetime
    beauty_title: Optional[str] = None
    title: Optional[str] = None
    other_titles: Optional[str] = None
    connect: Optional[str] = None
    coords: CoordsSchema
    images: List[ImageSchema]
    user: UserSchema


class SimpleResponse(BaseModel):
    message: str
    share_link: str
