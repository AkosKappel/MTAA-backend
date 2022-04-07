from fastapi import Depends, APIRouter, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from api import crud, schemas
from core.database import get_db

router = APIRouter(
    tags=['Authentication'],
)


@router.post('/register', response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register(request: schemas.UserCreate, db: Session = Depends(get_db)):
    crud.validate_email_format(email=request.email)
    crud.validate_password_length(password=request.password)
    crud.validate_unique_email(email=request.email, db=db)
    return crud.create_user(request=request, db=db)


@router.post('/login', response_model=schemas.Token, status_code=status.HTTP_202_ACCEPTED)
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return crud.login(request=request, db=db)
