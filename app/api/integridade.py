from fastapi import APIRouter, HTTPException, status
from pathlib import Path
from app.core.logging_config import logger_api, logger_atividades
from app.repositories.json_repository import (
    buscar_por_id
)
from app.services.integridade_service import calcula_hash
from app.models.acoes_enum import AcaoAtividade, ResultadoAtividade

router = APIRouter(
    prefix="/integridade",
    tags=["integridade"],
)


BASE_DIR = Path(__file__).resolve().parent.parent.parent
DOCUMENTOS_FILE = BASE_DIR / "storage" / "metadata" / "documentos.json"
DIRETORIO_DOCUMENTOS = BASE_DIR / "storage" / "documentos"


@router.get("/{documento_id}/integridade", status_code=status.HTTP_200_OK)
def obter_hash_documento(documento_id: str):
    documento = buscar_por_id(DOCUMENTOS_FILE, documento_id)

    if not documento:
        logger_api.warning(
            "Tentando verificar integridade de um documento inexistente com id: %s",
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

    hash_atual = calcula_hash(caminho_arquivo)
    hash_original = documento.get("sha256")
    integro = hash_atual == hash_original

    logger_api.info(
        "Verificacao de integridade concluida para o documento com id: %s", documento_id
    )

    logger_atividades.info(
        "Verificacao de integridade",
        extra={
            "acao": AcaoAtividade.INTEGRITY_CHECK.value,
            "documento_id": documento["id"],
            "documento": documento["nome_original"],
            "resultado": ResultadoAtividade.SUCCESS.value
        }
    )

    return {
        "id": documento["id"],
        "nome": documento["nome_original"],
        "hash_original": hash_original,
        "hash_atual": hash_atual,
        "integro": integro,
    }
