from api import schemas


def serialize_user(user: schemas.User | schemas.UserBase):
    return {
        'id': user.id,
        'email': user.email,
    }


def serialize_users(users: list[schemas.User | schemas.UserBase]):
    return [serialize_user(user) for user in users]


def serialize_call(call: schemas.Call):
    return {
        'id': call.id,
        'title': call.title,
        'owner_id': call.owner_id,
        'date': 'TODO',
        'duration': call.duration,
        'users': serialize_users(call.users),
    }


def serialize_calls(calls: list[schemas.Call]):
    return [serialize_call(call) for call in calls]
