import random
import string

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def generate_salt(length: int = 64):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))


def bcrypt(password: str, salt: str = ''):
    if salt:
        password += salt
    return pwd_context.hash(password)


def verify(plain_password: str, hashed_password: str, salt: str = ''):
    if salt:
        plain_password += salt
    return pwd_context.verify(plain_password, hashed_password)
