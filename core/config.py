import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


class Settings:
    # project settings
    PROJECT_NAME: str = 'Meetuj'
    PROJECT_VERSION: str = '1.0.0'

    # database config
    POSTGRES_USER: str = os.getenv('POSTGRES_USER')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
    POSTGRES_SERVER: str = os.getenv('POSTGRES_SERVER', 'localhost')
    POSTGRES_PORT: str = os.getenv('POSTGRES_PORT', 5432)
    POSTGRES_DB: str = os.getenv('POSTGRES_DB')
    DATABASE_URL = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}'

    # command pre vygenerovanie secret key: openssl rand -hex 32
    SECRET_KEY = 'ccccde617c75da86d9b3f10ff36051d35957016dbcae181f60cc6cc72ff9acad'
    ALGORITHM = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    # profile picture settings
    IMAGES_FOLDER = 'images/'
    IMAGE_EXTENSION = '.jpg'
    DEFAULT_PROFILE_PICTURE = f'{IMAGES_FOLDER}default{IMAGE_EXTENSION}'


settings = Settings()
