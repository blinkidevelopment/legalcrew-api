from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    senha = Column(String)
    ativo = Column(Boolean, default=True)


class Conversa(Base):
    __tablename__ = "conversas"

    id = Column(Integer, primary_key=True, index=True)
    id_assistente = Column(String, ForeignKey("assistentes.id"))
    id_thread = Column(String, unique=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id"))
    assistente = relationship("Assistente", backref="conversas")
    arquivos = relationship("Arquivo", backref="conversa")
    usuario = relationship("Usuario", backref="conversas")


class Arquivo(Base):
    __tablename__ = "arquivos"

    id = Column(String, primary_key=True, index=True)
    id_conversa = Column(Integer, ForeignKey("conversas.id"))


class Assistente(Base):
    __tablename__ = "assistentes"

    id = Column(String, primary_key=True, index=True)
    nome = Column(String)
    slug = Column(String)
    ferramentas = relationship("Ferramenta", secondary="ferramentas_agentes", backref="ferramentas")


class Ferramenta(Base):
    __tablename__ = "ferramentas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True)


class FerramentasAgentes(Base):
    __tablename__ = "ferramentas_agentes"

    id = Column(Integer, primary_key=True, index=True)
    id_assistente = Column(String, ForeignKey("assistentes.id"))
    id_ferramenta = Column(Integer, ForeignKey("ferramentas.id"))
