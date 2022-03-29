from fastapi import Depends, APIRouter, status
from sqlalchemy.orm import Session

from api import crud, schemas, OAuth2
from core.database import get_db

router = APIRouter(
    tags=['Calls'],
    prefix='/calls',
)


@router.get('', response_model=list[schemas.Call], status_code=status.HTTP_200_OK)
def get_all_calls(skip: int = 0,
                  limit: int = 100,
                  db: Session = Depends(get_db),
                  current_user=Depends(OAuth2.get_current_user)):
    return crud.get_all_calls(skip=skip, limit=limit, db=db)


@router.get('/{call_id}', response_model=schemas.Call, status_code=status.HTTP_200_OK)
def get_call_by_id(call_id: int,
                   db: Session = Depends(get_db),
                   current_user=Depends(OAuth2.get_current_user)):
    return crud.get_call_by_id(call_id=call_id, db=db)


@router.put('/{call_id}', response_model=schemas.Call, status_code=status.HTTP_200_OK)
def update_call(call_id: int,
                request: schemas.CallUpdate,
                db: Session = Depends(get_db),
                current_user=Depends(OAuth2.get_current_user)):
    return crud.update_call(call_id=call_id, request=request, db=db)


@router.delete('/{call_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_call(call_id: int,
                db: Session = Depends(get_db),
                current_user=Depends(OAuth2.get_current_user)):
    return crud.remove_call(call_id=call_id, db=db)


@router.get('/{call_id}/users', response_model=list[schemas.UserBase], status_code=status.HTTP_200_OK)
def get_users_of_call(call_id: int,
                      db: Session = Depends(get_db),
                      current_user=Depends(OAuth2.get_current_user)):
    return crud.get_users_of_call(call_id=call_id, db=db)


@router.post('/{call_id}/users/{user_id}', response_model=schemas.CallUsers, status_code=status.HTTP_200_OK)
def add_user_to_call(call_id: int,
                     user_id: int,
                     db: Session = Depends(get_db),
                     current_user=Depends(OAuth2.get_current_user)):
    return crud.add_user_to_call(call_id=call_id, user_id=user_id, db=db)


@router.delete('/{call_id}/users/{user_id}', response_model=schemas.CallUsers, status_code=status.HTTP_200_OK)
def remove_user_from_call(call_id: int,
                          user_id: int,
                          db: Session = Depends(get_db),
                          current_user=Depends(OAuth2.get_current_user)):
    return crud.remove_user_from_call(call_id=call_id, user_id=user_id, db=db)
