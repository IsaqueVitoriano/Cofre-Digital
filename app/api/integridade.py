from fastapi import APIRouter, HTTPException, status
from pathlib import Path
from app.core.logging_config import logger_api, logger_atividades
from app.repositories.json_repository import buscar_por_id, ler_arquivo_json
from app.services.integridade_service import calcula_hash
from app.models.atividade_enum import AcaoAtividade, ResultadoAtividade
from app.models.integridade_relatorio import RelatoriosIntegridade

router = APIRouter(
    prefix="/documentos",
    tags=["integridade"],
)


BASE_DIR = Path(__file__).resolve().parent.parent.parent
DOCUMENTOS_FILE = BASE_DIR / "storage" / "metadata" / "documentos.json"
DIRETORIO_DOCUMENTOS = BASE_DIR / "storage" / "documentos"


@router.get(
    "/integridade/global",
    status_code=status.HTTP_200_OK,
    response_model=RelatoriosIntegridade,
)
def auditoria_global():
    documentos = ler_arquivo_json(DOCUMENTOS_FILE)

    if not documentos:
        logger_api.warning("Tentativa de auditar com %s documentos.", len(documentos))
        return {
            "documentos_verificados": 0,
            "documentos_integros": 0,
            "documentos_alterados": 0,
            "arquivos_nao_encontrados": 0,
        }

    relatorio = {
        "documentos_verificados": len(documentos),
        "documentos_integros": 0,
        "documentos_alterados": 0,
        "arquivos_nao_encontrados": 0,
    }

    logger_api.info(
        "Iniciando verificacao de integridade global com %s documentos", len(documentos)
    )

    for doc in documentos:

        nome_armazenado = doc.get("nome_armazenado")
        if not nome_armazenado:
            logger_api.warning("Registro sem nome_armazenado: %s", doc.get("id"))
            relatorio["arquivos_nao_encontrados"] += 1
            continue

        caminho_arquivo = DIRETORIO_DOCUMENTOS / nome_armazenado
        if not caminho_arquivo.exists():
            relatorio["arquivos_nao_encontrados"] += 1
            logger_api.warning(
                "Arquivo fisico nao encontrado para o documento: %s",
                doc.get("nome_armazenado"),
            )
            continue

        hash_atual = calcula_hash(caminho_arquivo)

        if hash_atual == doc.get("sha256"):
            relatorio["documentos_integros"] += 1
        else:
            relatorio["documentos_alterados"] += 1
            logger_api.error(
                "Quebra de integridade no documento: %s", doc.get("nome_armazenado")
            )

    logger_api.info("Verificacao de integridade global concluida.")
    return relatorio


@router.get("/{documento_id}/integridade", status_code=status.HTTP_200_OK)
def auditoria_por_id(documento_id: str):
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
            "resultado": ResultadoAtividade.SUCCESS.value,
        },
    )

    return {
        "id": documento["id"],
        "nome": documento["nome_original"],
        "hash_original": hash_original,
        "hash_atual": hash_atual,
        "integro": integro,
    }
