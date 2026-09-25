from fastapi import APIRouter, HTTPException, status
from app.repositories.json_repository import (
    buscar_por_id
)
from app.core.logging_config import logger_api
from pathlib import Path
from starlette.responses import FileResponse

router = APIRouter(
    prefix="/download",
    tags=["download"]
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DOCUMENTOS_FILE = BASE_DIR / "storage" / "metadata" / "documentos.json"
DIRETORIO_DOCUMENTOS = BASE_DIR / "storage" / "documentos"


@router.get("/{documento_id}/download", status_code=status.HTTP_200_OK)
def baixar_documento(documento_id: str):
    documento = buscar_por_id(DOCUMENTOS_FILE, documento_id)
    if not documento:
        logger_api.warning(
            "Tentando baixar um documento inexistente com id: %s",
            documento_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Documento nao encontrado"
        )

    caminho_arquivo = DIRETORIO_DOCUMENTOS / documento["nome_armazenado"]

    if not caminho_arquivo.exists():
        logger_api.error(
            "Arquivo fisico nao encontrado para o documento com id: %s", documento_id
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo de documentos nao encontrado",
        )

    logger_api.info("Iniciando o download do documento com id: %s", documento_id)
    return FileResponse(path=caminho_arquivo, filename=documento["nome_original"])
