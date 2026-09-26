from fastapi import APIRouter
from pathlib import Path
from datetime import datetime
from app.core.logging_config import logger_api
from app.models.documento import Documento
from app.repositories.json_repository import ler_arquivo_json

router = APIRouter(prefix="/documentos", tags=["filtragem"])

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DOCUMENTOS_FILE = BASE_DIR / "storage" / "metadata" / "documentos.json"


@router.get("/filtragem", response_model=list[Documento])
def filtra_documentos(
    nome_original: str | None = None,
    extensao: str | None = None,
    categoria: str | None = None,
    data_hora_evento: datetime | None = None,
):
    documentos = ler_arquivo_json(DOCUMENTOS_FILE)
    resultados = documentos

    if nome_original:
        resultados = [
            doc for doc in resultados if doc.get("nome_original") == nome_original
        ]

    if extensao:
        resultados = [doc for doc in resultados if doc.get("extensao") == extensao]

    if categoria:
        resultados = [doc for doc in resultados if doc.get("categoria") == categoria]

    if data_hora_evento:
        resultados = [
            doc
            for doc in resultados
            if doc.get("data_hora_evento")
            and datetime.fromisoformat(str(doc.get("data_hora_evento"))) == data_hora_evento
        ]

    logger_api.info(
        "Filtragem realizada. Filtros - nome original: %s,  extensao: %s, categoria: %s, data e hora: %s",
        nome_original,
        extensao,
        categoria,
        data_hora_evento,
    )

    return resultados
