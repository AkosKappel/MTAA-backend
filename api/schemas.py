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
    # users: list[User] = []

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    email: str
    password: str


class UserUpdate(BaseModel):
    profile_picture: str
    email: str
    # todo pridat password a hesh


class User(BaseModel):
    id: int
    email: str
    calls: list[Call] = []
    profile_picture: str

    class Config:
        orm_mode = True


class Contact(BaseModel):
    contact_id: int


class CallUpdate(BaseModel):
    title: str
    date: datetime
    duration: int
