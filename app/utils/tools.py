import io
import re
import PyPDF2
from fastapi import UploadFile
from PIL import Image
import fitz
from openai import OpenAI
from pdf2image import convert_from_bytes


class Tool:
    def __init__(self, mimetypes: list):
        self.arquivos_suportados = mimetypes
        pass

    async def verificar_arquivo(self, arquivo: UploadFile):
        if arquivo.content_type not in self.arquivos_suportados:
            return False
        else:
            return True

    async def executar(self, arquivo: UploadFile, client: OpenAI):
        pass


class ExtrairPublicacoes(Tool):
    def __init__(self):
        super().__init__(["application/pdf"])

    async def executar(self, arquivo, client):
        conteudo = await arquivo.read()
        file_stream = io.BytesIO(conteudo)
        leitor = PyPDF2.PdfReader(file_stream)
        texto_extraido = ""

        for num_pagina in range(len(leitor.pages)):
            pagina = leitor.pages[num_pagina]
            texto_extraido += pagina.extract_text()

        publicacoes_lista = re.split(r'\n\d+ -\s*', texto_extraido)
        return [pub.strip() for pub in publicacoes_lista if pub.strip()][1:]


class ExtrairImagensPDF(Tool):
    def __init__(self):
        super().__init__(["application/pdf"])

    async def executar(self, arquivo, client):
        pdf_bytes = await arquivo.read()
        pdf_file = fitz.open(stream=pdf_bytes, filetype="pdf")

        imagens = []

        for num_pagina in range(len(pdf_file)):
            pagina = pdf_file[num_pagina]
            lista_imagens = pagina.get_images(full=True)

            for img_index, img in enumerate(lista_imagens):
                xref = img[0]
                base_image = pdf_file.extract_image(xref)
                image_bytes = base_image["image"]

                imagem = Image.open(io.BytesIO(image_bytes))
                imagens.append(imagem)
        pdf_file.close()
        return imagens


class DigitalizarPDF(Tool):
    def __init__(self):
        super().__init__(["application/pdf"])

    async def executar(self, arquivo, client):
        pdf_bytes = await arquivo.read()
        imagens_paginas = convert_from_bytes(pdf_bytes)

        imagens = []

        for imagem_pagina in imagens_paginas:
            img_byte_arr = io.BytesIO()
            imagem_pagina.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()

            imagem = Image.open(io.BytesIO(img_byte_arr))
            imagens.append(imagem)
        return imagens
    

class ToolMapper:
    @staticmethod
    def mapear_ferramentas(nomes_ferramentas):
        mapeamento = {
            "ExtrairPublicacoes": ExtrairPublicacoes,
            "ExtrairImagensPDF": ExtrairImagensPDF,
            "DigitalizarPDF": DigitalizarPDF
        }

        return [mapeamento[nome]() for nome in nomes_ferramentas if nome in mapeamento]
