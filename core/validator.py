import re

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from api import models
from core.config import settings


def validate_email_format(email: str):
    if not re.match(settings.EMAIL_REGEX, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Incorrect email address.',
        )


def validate_password_length(password: str):
    min_pw_length = settings.MIN_PASSWORD_LENGTH
    if len(password) < min_pw_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Password too short. Must be at least {min_pw_length} characters.',
        )


def validate_unique_email(email: str, db: Session):
    db_user = db.query(models.User).filter(models.User.email == email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email already registered.',
        )


def validate_title(title: str):
    if not title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Title is required.',
        )


def validate_duration(duration: int):
    if duration <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Duration must be greater than 0.',
        )
