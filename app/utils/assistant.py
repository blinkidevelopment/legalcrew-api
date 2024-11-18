import io
from fastapi import UploadFile
from openai import OpenAI
import os
import time
from dotenv import load_dotenv
from app.utils.tools import ExtrairPublicacoes


class Assistant:
    def __init__(self, nome: str, id: str, tools: list):
        load_dotenv()
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI()
        self.nome = nome
        self.id = id
        self.messages = []
        self.arquivos = []
        self.tools = tools

    def adicionar_mensagens(self, mensagens: list, thread_id: str | None):
        for mensagem in mensagens:
            if thread_id is None:
                self.messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": mensagem
                            }
                        ]
                    }
                )
            else:
                self.client.beta.threads.messages.create(
                    thread_id=thread_id,
                    role="user",
                    content=mensagem
                )

    def adicionar_mensagem_thread(self, thread_id: str, mensagem: str):
        thread_msg = self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=mensagem
        )
        return thread_msg


    def adicionar_imagens(self, id_imagens: list, thread_id: str | None):
        for imagem in id_imagens:
            if thread_id is None:
                self.messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_file",
                                "image_file": {
                                    "file_id": imagem,
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                )
            else:
                self.client.beta.threads.messages.create(
                    thread_id=thread_id,
                    role="user",
                    content=[
                        {
                            "type": "image_file",
                            "image_file": {
                                "file_id": imagem,
                                "detail": "high"
                            }
                        }
                    ]
                )

    def subir_imagens(self, imagens: list):
        id_imagens = []

        for i, imagem in enumerate(imagens):
            img_bytes = io.BytesIO()
            imagem.save(img_bytes, format="PNG")
            img_bytes.seek(0)
            img_bytes.name = f'imagem_{i+1}.png'

            response = self.client.files.create(
                file=img_bytes,
                purpose="vision"
            )

            id_imagens.append(response.id)
        return id_imagens

    def excluir_imagens(self, id_imagens: list):
        for imagem in id_imagens:
            self.client.files.delete(imagem)

    def adicionar_arquivos(self, arquivo: UploadFile):
        self.arquivos.append(arquivo)

    async def processar_arquivos(self, thread_id: str | None):
        if len(self.arquivos) > 0:
            for arquivo in self.arquivos:
                for ferramenta in self.tools:
                    #ferramenta = tool() TODO: ver casos em que há mais de uma ferramenta
                    try:
                        dados = await ferramenta.executar(arquivo)
                    except:
                        break
                    if isinstance(ferramenta, ExtrairPublicacoes):
                        self.adicionar_mensagens(dados, thread_id)
                    else:
                        id_imagens = self.subir_imagens(dados)
                        self.adicionar_imagens(id_imagens, thread_id)
                    break

    def criar_rodar_thread(self):
        run = self.client.beta.threads.create_and_run(
            assistant_id=self.id,
            thread={
                "messages": self.messages
            }
        )

        while run.status != "completed":
            run = self.client.beta.threads.runs.retrieve(
                thread_id=run.thread_id,
                run_id=run.id
            )
            time.sleep(2)

        resultado = self.client.beta.threads.messages.list(
            thread_id=run.thread_id
        )

        return resultado, run.thread_id

    def rodar_thread(self, thread_id: str):
        run = self.client.beta.threads.runs.create(
            assistant_id=self.id,
            thread_id=thread_id
        )

        while run.status != "completed":
            run = self.client.beta.threads.runs.retrieve(
                thread_id=run.thread_id,
                run_id=run.id
            )
            time.sleep(2)

        resultado = self.client.beta.threads.messages.list(
            thread_id=run.thread_id
        )

        return resultado

    def listar_mensagens_thread(self, thread_id: str):
        mensagens = self.client.beta.threads.messages.list(thread_id)
        return mensagens

    def obter_nome_assistente(self):
        assistant = self.client.beta.assistants.retrieve(self.id)
        if assistant:
            return assistant.name

    def obter_arquivo(self, file_id: str):
        conteudo = self.client.files.content(file_id)
        return conteudo
