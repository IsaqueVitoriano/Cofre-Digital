import csv
from pathlib import Path
from fastapi import APIRouter
from starlette.responses import FileResponse
from app.core.logging_config import logger_api, logger_atividades
from app.models.atividade_enum import AcaoAtividade, ResultadoAtividade
from app.repositories.json_repository import ler_arquivo_json

router = APIRouter(
    prefix="/exportacao",
    tags=["exportacao"],
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DOCUMENTOS_FILE = BASE_DIR / "storage" / "metadata" / "documentos.json"
EXPORTACAO_CSV = BASE_DIR / "storage" / "exportacoes" / "exportacoes.csv"

@router.get("/exportar/CSV")
def exportacao_csv():
    dados= ler_arquivo_json(DOCUMENTOS_FILE)
    with open(EXPORTACAO_CSV, mode="w", newline="", encoding="utf-8") as file:
        fieldnames = [
            "id",
            "nome_original",
            "nome_armazenado",
            "extensao",
            "tipo_mime",
            "tamanho",
            "categoria",
            "descricao",
            "data_upload",
            "sha256",
            "origem",
            "severidade",
            "tipo_de_evento",
            "data_hora_evento",
            "sistema_de_origem",
        ]

        try:
            arquivo = csv.DictWriter(file, fieldnames=fieldnames)
            arquivo.writeheader()
            arquivo.writerows(dados)
        except OSError:
            logger_api.warning(
                "Falha ao escrever no arquivo"
            )
            raise

    logger_atividades.info("Exportacao via csv concluida",
                           extra={
                               "acao": AcaoAtividade.EXPORT_DOCUMENTS.value,
                               "documento_id": "-",
                               "documento": "todos",
                               "resultado": ResultadoAtividade.SUCCESS.value
                           })

    return FileResponse(
        path=EXPORTACAO_CSV, media_type="text/csv", filename="documentos.csv"
    )