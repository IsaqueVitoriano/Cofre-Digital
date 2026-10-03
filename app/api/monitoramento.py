from fastapi import APIRouter
from pathlib import Path
from app.core.logging_config import logger_api
from app.models.documento import Documento, NivelSeveridade
from app.repositories.json_repository import ler_arquivo_json

router = APIRouter(prefix="/documentos", tags=["filtragem"])

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DOCUMENTOS_FILE = BASE_DIR / "storage" / "metadata" / "documentos.json"


@router.get("/filtragem/monitoramento", response_model=list[Documento])
def consultas_logs(
    origem: str | None = None,
    severidade: NivelSeveridade | None = None,
    tipo_de_evento: str | None = None,
    sistema_de_origem: str | None = None,
):
    documentos = ler_arquivo_json(DOCUMENTOS_FILE)

    logs = [doc for doc in documentos if doc.get("extensao") == ".log"]

    filtros_texto= {
        "origem": origem,
        "tipo_de_evento": tipo_de_evento,
        "sistema_de_origem": sistema_de_origem,
    }

    for campo, termo in filtros_texto.items():
        if termo:
            termo_normalizado = termo.casefold()
            logs = [
                log for log in logs
                if termo_normalizado in log.get(campo, "").casefold()
            ]

    if severidade:
        logs = [
            log for log in logs
            if log.get("severidade") == severidade.value
        ]

    logger_api.info(
        "Consulta realizada. Filtros - origem: %s, nivel de severidade: %s, tipo de evento: %s, sistema de origem: %s",
        origem,
        severidade,
        tipo_de_evento,
        sistema_de_origem,
    )

    return logs
