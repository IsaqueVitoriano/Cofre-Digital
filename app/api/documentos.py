from pathlib import Path
from fastapi import APIRouter, HTTPException, status
from core.logging_config import logger
from models.documento import Documento
from repositories.json_repository import(
    adicionar,
    atualizar,
    remover,
    ler_arquivo_json,
    buscar_por_id
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DOCUMENTOS_FILE = BASE_DIR / "storage" / "metadata" / "documentos.json"

router = APIRouter(
    prefix="/documentos",
    tags=["documentos"]
)

@router.get("/", response_model=list[Documento])
def listar_documentos():
    documentos = ler_arquivo_json(
        DOCUMENTOS_FILE
    )
    logger.info(
        "Lista de documentos"
    )
    return documentos

@router.post("/", response_model=Documento, status_code=status.HTTP_201_CREATED)
def criar_documento(documento: Documento):
    if buscar_por_id(
        DOCUMENTOS_FILE,
        documento.id
    ):
        logger.warning(
            "Tentando criar documento duplicado com id %s", documento.id
        )
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Documento com esse id ja existe")
    dados = documento.model_dump(
        mode="json"
    )
    adicionar(DOCUMENTOS_FILE, dados)

    logger.info(
        "Documento cadastrado com id %s, %s", documento.id, documento.nome_original
    )
    return documento

@router.put("/{documento_id}", response_model=Documento, status_code= status.HTTP_200_OK)
def atualizar_documento(documento_id: str, documento: Documento):
    dados = documento.model_dump(
        mode="json"
    )
    dados["id"] = documento_id
    if not atualizar(
        DOCUMENTOS_FILE, documento_id, dados
    ):
        logger.warning(
            "Tentativa de atualizar um documento inexistente com id %s", documento_id
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento nao encontrado")
    logger.info(
        "Documento atualizado com id %s", documento_id
    )
    return dados

@router.delete("/{documento_id}", status_code= status.HTTP_200_OK)
def deletar_documento(documento_id: str):
    if not remover(
        DOCUMENTOS_FILE,
        documento_id
    ):
        logger.warning(
            "Tentando deletar um documento inexistente com id %s", documento_id
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento nao encontrado")

    logger.info(
        "Documento deletado com id %s", documento_id
    )
    return {
        "mensagem": "Documento deletado com sucesso."
    }