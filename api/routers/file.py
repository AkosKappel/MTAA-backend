from fastapi import APIRouter, File, Depends, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from api import crud, OAuth2, schemas
from core.database import get_db

router = APIRouter(
    tags=['Files'],
    prefix='/file',
)


@router.get('/download', response_class=FileResponse, status_code=status.HTTP_200_OK)
def download_profile_image(db: Session = Depends(get_db),
                           current_user: schemas.TokenData = Depends(OAuth2.get_current_user)):
    user_id: int = current_user.user_id
    return crud.download_profile_image(user_id=user_id, db=db)


@router.put('/upload')
def upload_profile_image(image: bytes = File(...),
                         db: Session = Depends(get_db),
                         current_user: schemas.TokenData = Depends(OAuth2.get_current_user)):
    user_id: int = current_user.user_id
    return crud.upload_profile_image(user_id=user_id, image=image, db=db)
