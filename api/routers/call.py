from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from starlette import status

from api import crud, schemas
from core.database import get_db

router = APIRouter(
    tags=['calls'],
)


@router.get('/calls/', response_model=list[schemas.Call])
def get_all_calls(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_calls(db, skip=skip, limit=limit)


@router.get('/calls/{call_id}')
def get_call(call_id: int, db: Session = Depends(get_db)):
    return {'TODO': 'get call'}


@router.put('/calls/{call_id}')
def update_call(call_id: int, db: Session = Depends(get_db)):
    return {'TODO': 'update call'}


@router.delete('/calls/{call_id}')
def delete_call(call_id: int, db: Session = Depends(get_db)):
    return {'TODO': 'delete call'}
