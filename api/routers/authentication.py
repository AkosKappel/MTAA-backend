import re

from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from api import crud, schemas, models
from core.database import get_db

router = APIRouter(
    tags=['Authentication'],
)


@router.post('/register/', response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register(request: schemas.UserCreate, db: Session = Depends(get_db)):
    if not re.match(r'^[.\w-]+@([\w-]+\.)+[\w-]{2,4}$', request.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Incorrect email address.',
        )

    min_pw_length = 7
    if len(request.password) < min_pw_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Password too short. Must be at least {min_pw_length} characters.',
        )

    db_user = db.query(models.User).filter(models.User.email == request.email).first()

    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email already registered',
        )

    return crud.create_user(request=request, db=db)


@router.post('/login/', response_model=schemas.Token, status_code=status.HTTP_202_ACCEPTED)
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return crud.login(request=request, db=db)
