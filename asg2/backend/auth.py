from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

SECRET_KEY = "secret"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"])

def hash_password(p):
    return pwd_context.hash(p)

def verify_password(p, h):
    return pwd_context.verify(p, h)

def create_token(user_id):
    payload = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + timedelta(hours=5)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
