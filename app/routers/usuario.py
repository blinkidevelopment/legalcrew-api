from fastapi import APIRouter, Form, HTTPException, Response
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.database import obter_sessao
from app.db.models import Conversa, Usuario
from app.schemas.schemas import Conversa as ConversaSchema
from app.utils.auth import obter_usuario_logado
from app.utils.utils import hash_senha, verificar_senha, criar_token


router = APIRouter()


@router.post("/")
async def registrar_usuario(
        nome: str = Form(...),
        email: str = Form(...),
        senha: str = Form(...),
        db: Session = Depends(obter_sessao)
):
    usuario = db.query(Usuario).filter(Usuario.email == email).first()

    if usuario is None:
        senha_hash = hash_senha(senha)
        usuario_novo = Usuario(
            nome=nome,
            email=email,
            senha=senha_hash
        )

        db.add(usuario_novo)
        db.commit()
        db.refresh(usuario_novo)
        return usuario_novo
    return {"erro": "O usuário já existe"}


@router.get("/")
async def obter_usuario(usuario_logado: Usuario = Depends(obter_usuario_logado)):
    return usuario_logado


@router.post("/login")
async def login(
        response: Response,
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(obter_sessao)
):
    usuario = db.query(Usuario).filter(Usuario.email == form_data.username).first()

    if not usuario:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    if not verificar_senha(form_data.password, usuario.senha):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    access_token = criar_token(data={"sub": usuario.email})

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="none"
    )

    return {"status": True}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return True


@router.get("/conversas", response_model=list[ConversaSchema])
async def listar_conversas(
        usuario: Usuario = Depends(obter_usuario_logado),
        db: Session = Depends(obter_sessao)
):
    if usuario is not None:
        conversas = db.query(Conversa).filter_by(id_usuario=usuario.id).all()
        return conversas
    return {"erro": "Nenhum usuário logado"}
