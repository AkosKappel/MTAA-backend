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


@router.get('/calls/{call_id}', response_model=schemas.Call)
def get_call(call_id: int, db: Session = Depends(get_db)):
    return crud.get_call(call_id=call_id, db=db)


@router.put('/calls/{call_id}', response_model=schemas.Call)
def put_call(call_id: int, request: schemas.CallUpdate, db: Session = Depends(get_db)):
    return crud.update_call(call_id=call_id, request=request, db=db)


@router.delete('/calls/{call_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_call(call_id: int, db: Session = Depends(get_db)):
    return crud.remove_call(call_id=call_id, db=db)


@router.get('/calls/users/{call_id}', response_model=list[schemas.User])
def get_users_of_call(call_id: int, db: Session = Depends(get_db)):
    return crud.get_users_of_call(call_id=call_id, db=db)


# @router.put('calls/users/{call_id}', response_model=schemas.Call)
# def put_user_to_call(call_id: int, request: schemas.User, db: Session = Depends(get_db)):
#     return crud.add_user_to_call(call_id=call_id, user_id=request.id, db=db)


# @router.delete('calls/users/{call_id}', response_model=schemas.Call)
# def delete_user_to_call(call_id: int, request: schemas.User, db: Session = Depends(get_db)):
#     return crud.remove_user_from_call(call_id=call_id, user_id=request.id, db=db)
