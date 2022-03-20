from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from api import models, schemas, hashing, JWT


def login(request: OAuth2PasswordRequestForm, db: Session):
    db_user = get_user_by_email(email=request.username, db=db)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Invalid credentials'
        )

    if not hashing.verify(request.password, db_user.password_hash, db_user.password_salt):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'Incorrect password'
        )

    access_token = JWT.create_access_token(data={'sub': db_user.email})
    return {'access_token': access_token, 'token_type': 'bearer'}


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, request: schemas.UserCreate):
    salt = hashing.generate_salt()
    db_user = models.User(
        email=request.email,
        password_hash=hashing.bcrypt(request.password, salt),
        password_salt=salt,
        profile_picture='not implemented',
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


def get_user_calls(db: Session, user_id: int):
    db_user = get_user(user_id=user_id, db=db)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User not found',
        )

    return db_user.calls


def create_call_for_user(db: Session, call: schemas.CallCreate, user_id: int):
    db_call = models.Call(**call.dict(), owner_id=user_id)
    db_user = get_user(user_id=user_id, db=db)
    db_call.users.append(db_user)
    db.add(db_call)
    db.commit()
    db.refresh(db_call)
    return db_call


def add_user_to_call(db: Session, user_id: int, call_id: int):
    db_call = db.query(models.Call).filter(models.Call.id == call_id).first()
    db_user = get_user(user_id=user_id, db=db)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User not found',
        )

    if not db_call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Call not found',
        )

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
    db_call = db.query(models.Call).filter(models.Call.id == call_id).first()
    db_user = get_user(user_id=user_id, db=db)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User not found',
        )

    if not db_call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Call not found',
        )

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
    db_user = get_user(user_id=user_id, db=db)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User not found',
        )

    return db_user.contacts


def add_contact(user_id: int, db: Session, request: schemas.Contact):
    if user_id == request.contact_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Can not add yourself as contact',
        )

    db_user = get_user(user_id=user_id, db=db)
    db_contact = get_user(user_id=request.contact_id, db=db)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User not found',
        )

    if not db_contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User not found',
        )

    if db_contact in db_user.contacts:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'Contact is already in your contact list',
        )

    db_user.contacts.append(db_contact)
    db.commit()
    return db_user.contacts


def remove_contact(user_id, db: Session, request: schemas.Contact):
    db_user = get_user(user_id=user_id, db=db)
    db_contact = get_user(user_id=request.contact_id, db=db)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User not found',
        )

    if not db_contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User not found',
        )

    if db_contact not in db_user.contacts:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'Contact is not in your contact list',
        )

    db_user.contacts.remove(db_contact)
    db.commit()
    return db_user.contacts


def get_calls(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Call).offset(skip).limit(limit).all()


def get_call(call_id: int, db: Session):
    call = db.query(models.Call).filter(models.Call.id == call_id).first()

    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Call not found',
        )

    return call


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
    call = db.query(models.Call).filter(models.Call.id == call_id).first()

    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Call not found',
        )

    return call.users
