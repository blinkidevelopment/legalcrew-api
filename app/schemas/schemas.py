from pydantic import BaseModel


class Conversa(BaseModel):
    id: int
    id_assistente: str
    id_thread: str

    class Config:
        orm_mode = True
