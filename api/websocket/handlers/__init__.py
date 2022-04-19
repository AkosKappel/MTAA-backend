import json

from sqlalchemy.orm import Session

from api.websocket.handlers import call_handler, user_handler, file_handler


def get_requested_data(request: dict, db: Session):
    """
    example request json structure:
    {
        "method": "GET",
        "path": "/users",
        "body": {
            "data": "anything",
            ...
        }
    }
    """
    method: str = request.get('method', '')
    match method.upper():
        case 'GET':
            return handle_get(request, db)
        case 'POST':
            return handle_post(request, db)
        case 'PUT':
            return handle_put(request, db)
        case 'DELETE':
            return handle_delete(request, db)
    return {'error': 'method not supported'}


def handle_get(request: dict, db: Session):
    path: str = request.get('path', '')
    body: str = request.get('body', '')
    request_body: dict = json.loads(body) if body else {}

    match path.lower():
        case '/users/all':
            return user_handler.get_all_users(request_body=request_body, db=db)
        case '/users':
            return user_handler.get_user(request_body=request_body, db=db)
        case '/users/calls':
            pass
        case '/calls/all':
            return call_handler.get_all_calls(request_body=request_body, db=db)
        case '/calls/{call_id}':
            pass
        case '/calls/{call_id}/users':
            pass
        case '/contacts':
            pass
        case '/file/download':
            return file_handler.download_profile_image(request_body=request_body, db=db)
    return {'error': 'path not supported'}


def handle_post(request: dict, db: Session):
    path: str = request.get('path', '')
    body: str = request.get('body', '')
    request_body: dict = json.loads(body) if body else {}

    match path.lower():
        case '/users/calls':
            return user_handler.create_call_for_user(request_body=request_body, db=db)
        case '/calls/{call_id}/users/{user_id}':
            pass
        case '/contacts/{contact_id}':
            pass
    return {'error': 'path not supported'}


def handle_put(request: dict, db: Session):
    path: str = request.get('path', '')
    body: str = request.get('body', '')
    request_body: dict = json.loads(body) if body else {}

    match path.lower():
        case '/users':
            pass
        case '/calls/{call_id}':
            pass
        case '/file/upload':
            return file_handler.upload_profile_image(request_body=request_body, db=db)
    return {'error': 'path not supported'}


def handle_delete(request: dict, db: Session):
    path: str = request.get('path', '')

    match path.lower():
        case '/users':
            pass
        case '/calls/{call_id}':
            pass
        case '/calls/{call_id}/users/{user_id}':
            pass
        case '/contacts/{contact_id}':
            pass
    return {'error': 'path not supported'}
