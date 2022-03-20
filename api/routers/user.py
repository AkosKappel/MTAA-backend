from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from api import crud, schemas
from api import OAuth2
from core.database import get_db

router = APIRouter(
    tags=['Users'],
)


@router.post('/register/', response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register(request: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db=db, email=request.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email already registered',
        )
    return crud.create_user(request=request, db=db)


@router.post('/login/', response_model=schemas.Token, status_code=status.HTTP_202_ACCEPTED)
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return crud.login(request, db)


@router.get('/users/', response_model=list[schemas.User])
def get_all_users(current_user=Depends(OAuth2.get_current_user), skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_users(db=db, skip=skip, limit=limit)


@router.get('/users/{user_id}', response_model=schemas.User)
def get_user_by_id(user_id: int, db: Session = Depends(get_db), current_user=Depends(OAuth2.get_current_user)):
    db_user = crud.get_user(user_id=user_id, db=db)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User not found'
        )
    return db_user


@router.get('/users-email/{email}', response_model=schemas.User)
def get_user_by_email(email: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(email=email, db=db)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User not found'
        )
    return db_user


@router.put('/users/{user_id}', response_model=schemas.User, status_code=status.HTTP_200_OK)
def update_user(user_id: int, request: schemas.UserUpdate, db: Session = Depends(get_db)):
    return crud.update_user(user_id=user_id, request=request, db=db)


@router.delete('/users/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    return crud.delete_user(user_id=user_id, db=db)


@router.get('/users/calls/{user_id}', response_model=list[schemas.Call])
def get_calls_of_user(user_id: int, db: Session = Depends(get_db)):
    return crud.get_user_calls(user_id=user_id, db=db)


@router.post('/users/calls/{user_id}', response_model=schemas.Call, status_code=status.HTTP_201_CREATED)
def create_call_for_user(user_id: int, call: schemas.CallCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user(user_id=user_id, db=db)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User not found'
        )
    return crud.create_call_for_user(call=call, user_id=user_id, db=db)
