import json
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter

from app.core.logging_config import logger_api
from app.models.documento import NivelSeveridade
from app.models.estatistica import Estatistica

router = APIRouter(prefix="/documentos", tags=["estatisticas"])

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DOCUMENTOS_FILE = BASE_DIR / "storage" / "metadata" / "documentos.json"
ATIVIDADE_LOG_FILE = BASE_DIR / "storage" / "logs" / "atividade.log"
APP_LOG_FILE = BASE_DIR / "storage" / "logs" / "app.log"

@router.get("/", response_model=Estatistica)
def exibir_estatisticas():
    estatisticas = Estatistica(
        total_documentos=qtd_documentos_json(),
        espaco_ocupado_bytes=qtd_espaco_ocupado_bytes(),
        quantidade_documentos=documentos_por_extensao(),
        quantidade_documentos_categoria=documentos_por_categoria(),
        dias_mais_download=maior_ocorrencia_download(),
        quantidade_documentos_severidade_critica=qtd_documentos_severidade_critica()
    )

    return estatisticas

def qtd_documentos_json() -> int:
    with open(DOCUMENTOS_FILE, 'r', encoding="utf-8") as file:
        documentos_json = json.load(file)
        return len(documentos_json)


def qtd_espaco_ocupado_bytes() -> int:
    tot_tamanho_bytes = 0
    with open(DOCUMENTOS_FILE, 'r', encoding="utf-8") as file:
        for documento in json.load(file):
            tot_tamanho_bytes+= documento["tamanho"]

    return tot_tamanho_bytes

def documentos_por_extensao() -> dict[str, int]:
    extensao_dict: dict[str,int] = {}

    with open(DOCUMENTOS_FILE, 'r', encoding='utf-8') as file:
        for documento in json.load(file):
            extensao = documento["extensao"]
            extensao_dict[extensao] = extensao_dict.get(extensao, 0)+1

    return extensao_dict

def documentos_por_categoria() -> dict[str, int]:
    categoria_dict: dict[str, int] = {}

    with open(DOCUMENTOS_FILE, 'r', encoding='utf-8') as file:
        for documento in json.load(file):
            categoria = documento["categoria"]
            categoria_dict[categoria] = categoria_dict.get(categoria, 0) + 1

    return categoria_dict

def maior_ocorrencia_download() -> str | None:
    dias_ocorrencia: dict[str, int] = {}

    with open(ATIVIDADE_LOG_FILE, 'r', encoding='utf-8')as file_log:

        dias = [
            "segunda-feira", "terça-feira", "quarta-feira",
            "quinta-feira", "sexta-feira", "sábado", "domingo",
        ]

        for linha in file_log:
            if "DOCUMENT_DOWNLOAD" in linha:

                data = datetime.strptime(linha[:23], "%Y-%m-%d %H:%M:%S,%f")

                dia_semana = dias[data.weekday()]

                dias_ocorrencia[dia_semana] = dias_ocorrencia.get(dia_semana, 0) + 1

    if not dias_ocorrencia:
        logger_api.warning("Nenhuma ocorrência foi encontrada no log.")
        return None

    dia, quantidade = max(
        dias_ocorrencia.items(),
        key=lambda item: item[1]
    )

    return dia

def qtd_documentos_severidade_critica():
    qtd_docs_criticos = 0

    with open(DOCUMENTOS_FILE, 'r', encoding='utf-8') as file:

        for documento in json.load(file):
            if documento["severidade"] == NivelSeveridade.CRITICO.value:
                qtd_docs_criticos+= 1

        return qtd_docs_criticos
