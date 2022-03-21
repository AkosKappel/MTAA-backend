from fastapi import Depends, APIRouter, status
from sqlalchemy.orm import Session

from api import crud, schemas
from api import OAuth2
from core.database import get_db

router = APIRouter(
    tags=['Users'],
    prefix='/users',
)


@router.get('/', response_model=list[schemas.User])
def get_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_all_users(db=db, skip=skip, limit=limit)


# TODO: potom nezabudnut pridat 'current_user=Depends(OAuth2.get_current_user)' pre potrebne endpointy
@router.get('/{user_id}', response_model=schemas.User)
def get_user_by_id(user_id: int, db: Session = Depends(get_db), current_user=Depends(OAuth2.get_current_user)):
    return crud.get_user_by_id(user_id=user_id, db=db)


@router.get('/email/{email}', response_model=schemas.User)
def get_user_by_email(email: str, db: Session = Depends(get_db)):
    return crud.get_user_by_email(email=email, db=db)


@router.put('/{user_id}', response_model=schemas.User, status_code=status.HTTP_200_OK)
def update_user(user_id: int, request: schemas.UserUpdate, db: Session = Depends(get_db)):
    return crud.update_user(user_id=user_id, request=request, db=db)


@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    return crud.delete_user(user_id=user_id, db=db)


@router.get('/{user_id}/calls', response_model=list[schemas.Call])
def get_calls_of_user(user_id: int, db: Session = Depends(get_db)):
    return crud.get_calls_of_user(user_id=user_id, db=db)


@router.post('/{user_id}/calls', response_model=schemas.Call, status_code=status.HTTP_201_CREATED)
def create_call_for_user(user_id: int, call: schemas.CallCreate, db: Session = Depends(get_db)):
    return crud.create_call_for_user(call=call, user_id=user_id, db=db)
