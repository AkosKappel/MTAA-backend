import string
from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status
import hashlib
import random
from api import models, schemas


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    salt = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(64))
    hashed_password = hashlib.sha256((user.password + salt).encode()).hexdigest()  # TODO: add salt + hashing
    # print(salt)
    # print(hashed_password.hexdigest())
    # print(hashlib.sha256(('stefan' + salt).encode()).hexdigest())
    db_user = models.User(
        email=user.email,
        password_hash=hashed_password,
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

    # todo: dorobit osetrenia na heslo a email aby sa vedel iba owner updatnut

    # todo not valid dict
    salt = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(64))

    # dic = {'profile_picture': request.profile_picture,
    #        'email': request.email,
    #        'password_hash': hashlib.sha256((request.password + salt).encode()).hexdigest(),
    #        'password_salt': salt,
    #        }

    user.profile_picture = request.profile_picture
    user.email = request.email
    user.password_hash = hashlib.sha256((request.password + salt).encode()).hexdigest()
    user.password_salt = salt
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


def create_user_call(db: Session, call: schemas.CallCreate, user_id: int):
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
    # todo: vracat iba email a id
    db_user = get_user(user_id=user_id, db=db)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User not found',
        )

    return db_user.contacts


def add_contact(user_id, db: Session, request):
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


def remove_contact(user_id, db: Session, request):
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Contact is not in your contact list',
        )

    db_user.contacts.remove(db_contact)
    db.commit()


def get_calls(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Call).offset(skip).limit(limit).all()


def get_call(call_id, db):
    call = db.query(models.Call).filter(models.Call.id == call_id)

    if not call.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Call not found',
        )

    return call.first()


def update_call(call_id, request, db):
    call = db.query(models.Call).filter(models.Call.id == call_id)

    if not call.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Call not found',
        )

    # todo: iba owner vie spravit update

    call.update(request.dict())
    db.commit()
    return call.first()


def remove_call(call_id, db):
    call = db.query(models.Call).filter(models.Call.id == call_id)

    # todo: pridat iba owner vie mazat treba delete cascase

    if not call.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Call not found',
        )

    call.delete(synchronize_session=False)
    db.commit()


def get_users_of_call(call_id, db):
    call = db.query(models.Call).filter(models.Call.id == call_id)
    print(call)

    if not call.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Call not found',
        )

    return call.first().users


def login(request, db):
    print('janko')
    db_user = get_user_by_email(email=request.email, db=db)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User with email {request.email} not found'
        )

    if db_user.password_hash != hashlib.sha256((request.password + db_user.password_salt).encode()).hexdigest():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'Wrong password'
        )
