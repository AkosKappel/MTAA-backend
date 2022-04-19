import base64
from pathlib import Path

from sqlalchemy.orm import Session

from api import crud
from core.config import settings


def download_profile_image(request_body: dict, db: Session):
    # TODO: set user_id
    user_id: int = 15
    db_user = crud.get_user_by_id(user_id=user_id, db=db)
    file_path = Path(db_user.profile_picture)

    if not file_path.exists() or not file_path.is_file():
        file_path = settings.PROFILE_IMAGE_DEFAULT_PATH
    with open(file_path, 'rb') as f:
        image = f.read()
        image_base64 = base64.b64encode(image)
    return {'image': image_base64.decode('utf-8')}


def upload_profile_image(request_body: dict, db: Session):
    # TODO: set user_id
    image_base64: str = request_body.get('image', '')
    image = base64.b64decode(image_base64)
    crud.upload_profile_image(user_id=15, image=image, db=db)
    return {'image': 'OK'}
