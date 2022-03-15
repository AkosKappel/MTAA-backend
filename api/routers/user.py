from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from fastapi import status

from api import crud, schemas
from core.database import get_db

router = APIRouter(
    tags=['users'],
)


@router.get('/users/', response_model=list[schemas.User])
def get_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_users(db=db, skip=skip, limit=limit)


@router.get('/users/{user_id}', response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(user_id=user_id, db=db)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User with id {user_id} not found'
        )
    return db_user


@router.post('/users/', response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db=db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email already registered',
        )
    return crud.create_user(user=user, db=db)


@router.put('/users/{user_id}', response_model=schemas.User)
def update_user(user_id: int, request: schemas.UserUpdate, db: Session = Depends(get_db)):
    return crud.update_user(user_id=user_id, request=request, db=db)


@router.delete('/users/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    return crud.delete_user(user_id=user_id, db=db)


@router.get('/users/{user_id}/calls/', response_model=list[schemas.Call])
def get_calls_of_user(user_id: int, db: Session = Depends(get_db)):
    return crud.get_user_calls(user_id=user_id, db=db)


@router.post('/users/{user_id}/calls/', response_model=schemas.Call)
def create_call_for_user(user_id: int, call: schemas.CallCreate, db: Session = Depends(get_db)):
    return crud.create_user_call(call=call, user_id=user_id, db=db)


@router.get('/users/{user_id}/contacts/', response_model=list[schemas.User])
def get_user_contacts(user_id: int, db: Session = Depends(get_db)):
    return crud.get_contacts(user_id=user_id, db=db)
