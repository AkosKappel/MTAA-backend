from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from api import models, schemas


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = user.password + 'not_really_hashed'  # TODO: add salt + hashing
    db_user = models.User(
        email=user.email,
        password_hash=hashed_password,
        password_salt='not implemented',
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
            detail=f'User with id {user_id} not found',
        )

    user.update(request.dict())
    db.commit()
    return user.first()


def delete_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id)

    if not user.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User with id {user_id} not found',
        )

    user.delete(synchronize_session=False)
    db.commit()


def get_user_calls(db: Session, user_id: int):
    db_user = get_user(user_id=user_id, db=db)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User with id {user_id} not found',
        )

    return db_user.calls


def create_user_call(db: Session, call: schemas.CallCreate, user_id: int):
    db_call = models.Call(**call.dict(), owner_id=user_id)
    db_user = get_user(user_id=user_id, db=db)
    db_call.users.append(db_user)
    db.add(db_call)
    db.commit()
    db.refresh(db_call)
    return db_call


def add_user_to_call(db: Session, user_id: int, call_id: int):
    pass


def remove_user_from_call(db: Session, user_id: int, call_id: int):
    pass


def get_contacts(db: Session, user_id: int):
    db_user = get_user(user_id=user_id, db=db)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User with id {user_id} not found',
        )

    return db_user.contacts


def add_contact(user_id, db: Session, request):
    db_user = get_user(user_id=user_id, db=db)
    db_contact = get_user(user_id=request.contact_id, db=db)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User with id {user_id} not found',
        )

    if not db_contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User with id {request.contact_id} not found',
        )

    db_user.contacts.append(db_contact)
    db.commit()


def remove_contact(user_id, db: Session, request):
    db_user = get_user(user_id=user_id, db=db)
    db_contact = get_user(user_id=request.contact_id, db=db)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User with id {user_id} not found',
        )

    if not db_contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User with id {request.contact_id} not found',
        )

    if db_contact not in db_user.contacts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User with id {user_id} does not have contact with id {request.contact_id}',
        )

    db_user.contacts.remove(db_contact)
    db.commit()


def get_calls(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Call).offset(skip).limit(limit).all()

