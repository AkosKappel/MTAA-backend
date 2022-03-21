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

    access_token = JWT.create_access_token(data={'sub': db_user.email})
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

    if 'password' in params:
        password = params['password']
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


def create_call_for_user(user_id: int, db: Session, call: schemas.CallCreate):
    db_user = get_user_by_id(user_id=user_id, db=db)
    db_call = models.Call(**call.dict(), owner_id=user_id)
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
    return db_call


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
    return db_call


def get_contacts(db: Session, user_id: int):
    db_user = get_user_by_id(user_id=user_id, db=db)
    return db_user.contacts


def add_contact(user_id: int, db: Session, request: schemas.Contact):
    if user_id == request.contact_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'User can not be added as a contact',
        )

    db_user = get_user_by_id(user_id=user_id, db=db)
    db_contact = get_user_by_id(user_id=request.contact_id, db=db)

    if db_contact in db_user.contacts:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'Contact is already in contact list',
        )

    db_user.contacts.append(db_contact)
    db.commit()
    return db_user.contacts


def remove_contact(user_id, db: Session, request: schemas.Contact):
    db_user = get_user_by_id(user_id=user_id, db=db)
    db_contact = get_user_by_id(user_id=request.contact_id, db=db)

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


def get_call_by_id(call_id: int, db: Session):
    db_call = db.query(models.Call).filter(models.Call.id == call_id).first()

    if not db_call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Call not found',
        )

    return db_call


def update_call(call_id: int, request: schemas.CallUpdate, db: Session):
    call = db.query(models.Call).filter(models.Call.id == call_id)

    if not call.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Call not found',
        )

    params = {k: v for k, v in request.dict().items() if v}

    call.update(params)
    db.commit()
    return call.first()


def remove_call(call_id: int, db: Session):
    call = db.query(models.Call).filter(models.Call.id == call_id)

    if not call.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Call not found',
        )

    call.delete(synchronize_session=False)
    db.commit()


def get_users_of_call(call_id: int, db: Session):
    db_call = get_call_by_id(call_id=call_id, db=db)
    return db_call.users


def download_profile_image(user_id: int, db: Session):
    db_user = get_user_by_id(user_id=user_id, db=db)
    file_path = Path(db_user.profile_picture)

    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    return FileResponse(settings.DEFAULT_PROFILE_PICTURE)


def upload_profile_image(user_id: int, image: bytes, db: Session):
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
    return user.first()
