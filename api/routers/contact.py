from fastapi import Depends, APIRouter, status
from sqlalchemy.orm import Session

from api import crud, schemas, OAuth2
from core.database import get_db

router = APIRouter(
    tags=['Contacts'],
    prefix='/contacts',
)


@router.get('', response_model=list[schemas.UserBase], status_code=status.HTTP_200_OK)
def get_user_contacts(db: Session = Depends(get_db),
                      current_user: schemas.TokenData = Depends(OAuth2.get_current_user)):
    user_id: int = current_user.user_id
    return crud.get_contacts(user_id=user_id, db=db)


@router.post('/{contact_id}', response_model=list[schemas.UserBase], status_code=status.HTTP_200_OK)
def add_user_contact(contact_id: int,
                     db: Session = Depends(get_db),
                     current_user: schemas.TokenData = Depends(OAuth2.get_current_user)):
    user_id: int = current_user.user_id
    return crud.add_contact(user_id=user_id, contact_id=contact_id, db=db)


@router.delete('/{contact_id}', response_model=list[schemas.UserBase], status_code=status.HTTP_200_OK)
def remove_user_contact(contact_id: int,
                        db: Session = Depends(get_db),
                        current_user: schemas.TokenData = Depends(OAuth2.get_current_user)):
    user_id: int = current_user.user_id
    return crud.remove_contact(user_id=user_id, contact_id=contact_id, db=db)
