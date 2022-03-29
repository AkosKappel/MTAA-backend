from fastapi import Depends, APIRouter, status
from sqlalchemy.orm import Session

from api import crud, schemas, OAuth2
from core.database import get_db

router = APIRouter(
    tags=['Contacts'],
    prefix='/contacts',
)


@router.get('/{user_id}', response_model=list[schemas.UserBase])
def get_user_contacts(user_id: int,
                      db: Session = Depends(get_db),
                      current_user=Depends(OAuth2.get_current_user)):
    return crud.get_contacts(user_id=user_id, db=db)


@router.post('/{user_id}', response_model=list[schemas.UserBase], status_code=status.HTTP_200_OK)
def add_user_contact(user_id: int, request: schemas.Contact,
                     db: Session = Depends(get_db),
                     current_user=Depends(OAuth2.get_current_user)):
    return crud.add_contact(user_id=user_id, request=request, db=db)


@router.delete('/{user_id}', response_model=list[schemas.UserBase], status_code=status.HTTP_200_OK)
def remove_user_contact(user_id: int, request: schemas.Contact,
                        db: Session = Depends(get_db),
                        current_user=Depends(OAuth2.get_current_user)):
    return crud.remove_contact(user_id=user_id, request=request, db=db)
