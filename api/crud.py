import re
from datetime import timedelta
from pathlib import Path

from fastapi import HTTPException, status
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from api import models, schemas, hashing, JWT
from core.config import settings


def login(request: OAuth2PasswordRequestForm, db: Session):
    db_user = get_user_by_email(email=request.username, db=db)

    if not hashing.verify(request.password, db_user.password_hash, db_user.password_salt):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'Incorrect password'
        )

    access_token = JWT.create_access_token(data={'user_id': db_user.id})
    return {'access_token': access_token, 'token_type': 'bearer'}


def get_all_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def get_user_by_id(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User not found'
        )

    return db_user


def get_user_by_email(db: Session, email: str):
    db_user = db.query(models.User).filter(models.User.email == email).first()

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User not found'
        )

    return db_user


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
            detail='Email already registered',
        )


def create_user(db: Session, request: schemas.UserCreate):
    salt = hashing.generate_salt()
    db_user = models.User(
        email=request.email,
        password_hash=hashing.bcrypt(request.password, salt),
        password_salt=salt,
        profile_picture=f'{settings.DEFAULT_PROFILE_PICTURE}',
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, request: schemas.UserUpdate):
    user = db.query(models.User).filter(models.User.id == user_id)

    if not user.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User not found',
        )

    params = {k: v for k, v in request.dict().items() if v}

    if 'email' in params:
        validate_email_format(email=request.email)
        if params['email'] != user.first().email:
            validate_unique_email(email=request.email, db=db)

    if 'password' in params:
        password = params['password']
        validate_password_length(password=request.password)
        del params['password']
        salt = hashing.generate_salt()
        params['password_hash'] = hashing.bcrypt(password, salt)
        params['password_salt'] = salt

    user.update(params)
    db.commit()
    return user.first()


def delete_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id)

    if not user.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User not found',
        )

    user.delete(synchronize_session=False)
    db.commit()


def get_calls_of_user(db: Session, user_id: int):
    db_user = get_user_by_id(user_id=user_id, db=db)
    return db_user.calls


def create_call_for_user(db: Session, user_id: int, call: schemas.CallCreate):
    db_user = get_user_by_id(user_id=user_id, db=db)
    db_call = models.Call(**call.dict(), owner_id=user_id)

    zero_time = timedelta(minutes=0)
    new_call_start = db_call.date
    new_call_end = db_call.date + timedelta(minutes=db_call.duration)
    for c in db_user.owned_calls:
        old_call_start = c.date
        old_call_end = c.date + timedelta(minutes=c.duration)
        if min(new_call_end, old_call_end) - max(new_call_start, old_call_start) > zero_time:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f'You already have a scheduled meeting in this timeslot',
            )

    db_call.users.append(db_user)

    db.add(db_call)
    db.commit()
    db.refresh(db_call)
    return db_call


def add_user_to_call(db: Session, user_id: int, call_id: int):
    db_user = get_user_by_id(user_id=user_id, db=db)
    db_call = get_call_by_id(call_id=call_id, db=db)

    if db_user in db_call.users:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'User is already in this call',
        )

    db_call.users.append(db_user)
    db.commit()
    db.refresh(db_call)
    return db_call.users


def remove_user_from_call(db: Session, user_id: int, call_id: int):
    db_user = get_user_by_id(user_id=user_id, db=db)
    db_call = get_call_by_id(call_id=call_id, db=db)

    if db_user not in db_call.users:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'User is not in this call',
        )

    db_call.users.remove(db_user)
    db.commit()
    db.refresh(db_call)
    return db_call.users


def get_contacts(db: Session, user_id: int):
    db_user = get_user_by_id(user_id=user_id, db=db)
    return db_user.contacts


def add_contact(db: Session, user_id: int, contact_id: int):
    if user_id == contact_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'User can not be added as a contact',
        )

    db_user = get_user_by_id(user_id=user_id, db=db)
    db_contact = get_user_by_id(user_id=contact_id, db=db)

    if db_contact in db_user.contacts:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'Contact is already in contact list',
        )

    db_user.contacts.append(db_contact)
    db.commit()
    return db_user.contacts


def remove_contact(db: Session, user_id: int, contact_id: int):
    db_user = get_user_by_id(user_id=user_id, db=db)
    db_contact = get_user_by_id(user_id=contact_id, db=db)

    if db_contact not in db_user.contacts:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'Contact is not in contact list',
        )

    db_user.contacts.remove(db_contact)
    db.commit()
    return db_user.contacts


def get_all_calls(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Call).offset(skip).limit(limit).all()


def get_call_by_id(db: Session, call_id: int):
    db_call = db.query(models.Call).filter(models.Call.id == call_id).first()

    if not db_call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Call not found',
        )

    return db_call


def update_call(db: Session, call_id: int, user_id: int, request: schemas.CallUpdate):
    call = db.query(models.Call).filter(models.Call.id == call_id)

    if not call.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Call not found',
        )

    if call.first().owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'Only owner can update this call',
        )

    params = {k: v for k, v in request.dict().items() if v}

    call.update(params)
    db.commit()
    return call.first()


def remove_call(db: Session, call_id: int, user_id: int):
    call = db.query(models.Call).filter(models.Call.id == call_id)

    if not call.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Call not found',
        )

    if call.first().owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'Only owner can delete this call',
        )

    call.delete(synchronize_session=False)
    db.commit()


def get_users_of_call(db: Session, call_id: int):
    db_call = get_call_by_id(call_id=call_id, db=db)
    return db_call.users


def download_profile_image(db: Session, user_id: int):
    db_user = get_user_by_id(user_id=user_id, db=db)
    file_path = Path(db_user.profile_picture)

    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    return FileResponse(settings.DEFAULT_PROFILE_PICTURE)


def upload_profile_image(db: Session, user_id: int, image: bytes):
    user = db.query(models.User).filter(models.User.id == user_id)

    if not user.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User not found',
        )

    file_path = Path(settings.IMAGES_FOLDER) / f'{user_id}{settings.IMAGE_EXTENSION}'
    with open(file_path, 'wb') as f:
        f.write(image)

    user.update({'profile_picture': str(file_path)})
    db.commit()
