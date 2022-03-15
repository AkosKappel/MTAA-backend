from pydantic import BaseModel
from datetime import datetime


class CallCreate(BaseModel):
    title: str
    date: datetime
    duration: int


class Call(BaseModel):
    id: int
    title: str
    owner_id: int
    date: datetime
    duration: int

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    email: str
    password: str


class UserUpdate(BaseModel):
    profile_picture: str


class User(BaseModel):
    id: int
    email: str
    calls: list[Call] = []
    profile_picture: str

    class Config:
        orm_mode = True
