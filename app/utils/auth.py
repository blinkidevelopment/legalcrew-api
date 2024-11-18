import jwt
from fastapi import Depends, HTTPException
from fastapi.params import Cookie
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.database import obter_sessao
from app.db.models import Usuario
from app.utils.utils import SECRET_KEY, ALGORITHM


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/usuario/login")

async def obter_usuario_logado(token: str = Cookie(None, alias="access_token"), db: Session = Depends(obter_sessao)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=401,
                detail="Não autenticado"
            )
    except:
        raise HTTPException(
            status_code=401,
            detail="Não autenticado"
        )

    user = db.query(Usuario).filter(Usuario.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Usuário não encontrado"
        )
    return user