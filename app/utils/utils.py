import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def hash_senha(senha: str) -> str:
    return pwd_context.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    return pwd_context.verify(senha, senha_hash)


def criar_token(data: dict):
    to_encode = data.copy()
    expirar = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expirar})
    jwt_codificado = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return jwt_codificado