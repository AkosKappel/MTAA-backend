from pydantic import BaseModel
from datetime import datetime


class UserID(BaseModel):
    id: int

    class Config:
        orm_mode = True


class UserBase(UserID):
    email: str

    class Config:
        orm_mode = True


class CallUsers(BaseModel):
    users: list[UserBase] = []

    class Config:
        orm_mode = True


class Call(BaseModel):
    id: int
    title: str
    owner_id: int
    date: datetime
    duration: int
    users: list[UserBase] = []

    class Config:
        orm_mode = True


class User(UserBase):
    calls: list[Call] = []
    profile_picture: str

    class Config:
        orm_mode = True


class Contact(BaseModel):
    contact_id: int


class CallCreate(BaseModel):
    title: str
    date: datetime
    duration: int


class UserCreate(BaseModel):
    email: str
    password: str


class CallUpdate(BaseModel):
    title: str | None = None
    date: datetime | None = None
    duration: int | None = None


class UserUpdate(BaseModel):
    profile_picture: str | None = None
    email: str | None = None
    password: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None
