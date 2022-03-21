from fastapi import APIRouter, File, Depends, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from api import crud
from core.database import get_db

router = APIRouter(
    tags=['Files'],
    prefix='/file',
)


@router.get('/download/{user_id}', response_class=FileResponse, status_code=status.HTTP_200_OK)
def download_profile_image(user_id: int, db: Session = Depends(get_db)):
    return crud.download_profile_image(user_id=user_id, db=db)


@router.put('/upload/{user_id}')
def upload_profile_image(user_id: int, image: bytes = File(...), db: Session = Depends(get_db)):
    return crud.upload_profile_image(user_id=user_id, image=image, db=db)
