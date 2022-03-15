from pydantic import BaseModel
from datetime import datetime


class CallBase(BaseModel):
    title: str


class CallCreate(CallBase):
    date: datetime
    duration: int


class Call(CallBase):
    id: int
    owner_id: int
    date: datetime
    duration: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    password: str
    profile_picture: str


class User(UserBase):
    id: int
    calls: list[Call] = []
    profile_picture: str

    class Config:
        orm_mode = True
