from fastapi import FastAPI
from app.routers import assistente, usuario
from fastapi.middleware.cors import CORSMiddleware
import os


app = FastAPI()

origins = os.getenv("ALLOWED_ORIGINS", "").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(usuario.router, prefix="/usuario", tags=["Usuários"])
app.include_router(assistente.router, prefix="/assistente", tags=["Assistentes"])
