from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

from api import models
from api.routers import call, user, contact, file
from core.config import settings
from core.database import engine


def get_application():
    _app = FastAPI(title=settings.PROJECT_NAME)

    # _app.add_middleware(HTTPSRedirectMiddleware)
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    _app.include_router(user.router)
    _app.include_router(call.router)
    _app.include_router(contact.router)
    _app.include_router(file.router)

    return _app


models.Base.metadata.create_all(bind=engine)

app = get_application()
