from _datetime import datetime

from sqlalchemy.orm import Session

from api import crud, schemas
from api.websocket import serializer


def get_all_users(request_body: dict, db: Session):
    skip: int = request_body.get('skip', 0)
    limit: int = request_body.get('limit', 10)
    users = crud.get_all_users(db=db, skip=skip, limit=limit)
    return serializer.serialize_users(users)


def get_user(request_body: dict, db: Session):
    # TODO: get user_id from request_body
    # user_id = request_body.get('user_id')
    user = crud.get_user_by_id(user_id=16, db=db)
    return serializer.serialize_user(user)


def create_call_for_user(request_body: dict, db: Session):
    title: str = request_body.get('title')
    date_string: str = request_body.get('date')
    duration: int = request_body.get('duration')

    # check if any of the fields are missing
    if not all([title, date_string, duration]):
        return {'error': 'missing fields'}

    # TODO: date este nefunguje
    date = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%fZ')
    call = schemas.CallCreate(title=title, date=date, duration=duration)
    call = crud.create_call_for_user(call=call, user_id=13, db=db)
    return serializer.serialize_call(call)
