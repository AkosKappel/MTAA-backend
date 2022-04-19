from sqlalchemy.orm import Session

from api import crud
from api.websocket import serializer


def get_all_calls(request_body: dict, db: Session):
    skip: int = request_body.get('skip', 0)
    limit: int = request_body.get('limit', 10)
    calls = crud.get_all_calls(db=db, skip=skip, limit=limit)
    return serializer.serialize_calls(calls)

