import csv
import json
from pathlib import Path
from fastapi import APIRouter
from starlette.responses import FileResponse
from app.core.logging_config import logger_api

router = APIRouter(
    prefix="/exportacao",
    tags=["exportacao"],
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DOCUMENTOS_FILE = BASE_DIR / "storage" / "metadata" / "documentos.json"
EXPORTACAO_CSV = BASE_DIR / "storage" / "exportacoes" / "exportacoes.csv"

@router.get("/exportar/CSV")
def exportacao_csv():
    with open(DOCUMENTOS_FILE, mode="r", encoding="utf-8") as file:
        dados = json.load(file)
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
        arquivo = csv.DictWriter(file, fieldnames=fieldnames)
        arquivo.writeheader()
        arquivo.writerows(dados)

    logger_api.info("Exportanto csv ...")
    return FileResponse(
        path=EXPORTACAO_CSV, media_type="text/csv", filename="documentos.csv"
    )