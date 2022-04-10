from fastapi import Depends, APIRouter, status
from sqlalchemy.orm import Session

from api import crud, schemas, OAuth2
from core.database import get_db

router = APIRouter(
    tags=['Users'],
    prefix='/users',
)


@router.get('/all', response_model=list[schemas.User], status_code=status.HTTP_200_OK)
def get_all_users(skip: int = 0,
                  limit: int = 100,
                  db: Session = Depends(get_db),
                  current_user: schemas.TokenData = Depends(OAuth2.get_current_user)):
    return crud.get_all_users(db=db, skip=skip, limit=limit)


@router.get('', response_model=schemas.User, status_code=status.HTTP_200_OK)
def get_user(email: str | None = None,
             db: Session = Depends(get_db),
             current_user: schemas.TokenData = Depends(OAuth2.get_current_user)):
    if email is not None:
        return crud.get_user_by_email(email=email, db=db)
    user_id: int = current_user.user_id
    return crud.get_user_by_id(user_id=user_id, db=db)


@router.put('', response_model=schemas.User, status_code=status.HTTP_200_OK)
def update_user(request: schemas.UserUpdate,
                db: Session = Depends(get_db),
                current_user: schemas.TokenData = Depends(OAuth2.get_current_user)):
    user_id: int = current_user.user_id
    return crud.update_user(user_id=user_id, request=request, db=db)


@router.delete('')
def delete_user(db: Session = Depends(get_db),
                current_user: schemas.TokenData = Depends(OAuth2.get_current_user)):
    user_id: int = current_user.user_id
    return crud.delete_user(user_id=user_id, db=db)


@router.get('/calls', response_model=list[schemas.Call], status_code=status.HTTP_200_OK)
def get_calls_of_user(db: Session = Depends(get_db),
                      current_user: schemas.TokenData = Depends(OAuth2.get_current_user)):
    user_id: int = current_user.user_id
    return crud.get_calls_of_user(user_id=user_id, db=db)


@router.post('/calls', response_model=schemas.Call, status_code=status.HTTP_201_CREATED)
def create_call_for_user(call: schemas.CallCreate,
                         db: Session = Depends(get_db),
                         current_user: schemas.TokenData = Depends(OAuth2.get_current_user)):
    user_id: int = current_user.user_id
    return crud.create_call_for_user(call=call, user_id=user_id, db=db)
