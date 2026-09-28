import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter

from models.documento import Documento
from models.estatistica import Estatistica

router = APIRouter(prefix="/documentos", tags=["estatisticas"])

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DOCUMENTOS_FILE = BASE_DIR / "storage" / "metadata" / "documentos.json"

@router.get("/")
def exibir_estatisticas_grafico():
    estatisticas = Estatistica(
        total_documentos=qtd_documentos_json(),
        espaco_ocupado_bytes=qtd_espaco_ocupado_bytes(),
        quantidade_documentos=,
        quantidade_documentos_categoria=,
        dias_mais_upload=,
        dias_mais_download=,
    )


def qtd_documentos_json() -> int:
    with open(DOCUMENTOS_FILE, 'r', encoding="utf-8") as file:
        documentos_json = json.load(file)
        return len(documentos_json)


def qtd_espaco_ocupado_bytes() -> int:
    tot_tamanho_bytes = 0
    with open(DOCUMENTOS_FILE, 'r', encoding="utf-8") as file:
        documentos_json = json.load(file)
        for documento in documentos_json:
            tot_tamanho_bytes+= documento.tamanho

    return tot_tamanho_bytes

def documentos_por_tipo() -> dict:
