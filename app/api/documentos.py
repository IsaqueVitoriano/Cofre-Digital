from pathlib import Path
from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from app.core.logging_config import logger
from app.models.documento import Documento, NivelSeveridade
from app.repositories.json_repository import (
    adicionar,
    atualizar,
    remover,
    ler_arquivo_json,
    buscar_por_id,
)

from app.services.integridade_service import calcula_hash

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DOCUMENTOS_FILE = BASE_DIR / "storage" / "metadata" / "documentos.json"
DIRETORIO_DOCUMENTOS = BASE_DIR / "storage" / "documentos"

router = APIRouter(prefix="/documentos", tags=["documentos"])


@router.get("/", response_model=list[Documento])
def listar_documentos():
    documentos = ler_arquivo_json(DOCUMENTOS_FILE)
    logger.info("Lista de documentos")
    return documentos

@router.get("/{documento_id}", response_model=Documento)
def listar_documento_por_ID(documento_id: str):
    documento = buscar_por_id(DOCUMENTOS_FILE, documento_id)
    if not documento:
        logger.warning(
            "Documento nao encontrado: %s", documento_id
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento nao encontrado"
        )
    return documento

@router.post("/", response_model=Documento, status_code=status.HTTP_201_CREATED)
def criar_documento(
    arquivo: UploadFile = File(...),
    categoria: str = Form(...),
    descricao: str | None = Form(None),
    origem: str = Form(...),
    severidade: NivelSeveridade = Form(...),
    tipo_de_evento: str = Form(...),
    sistema_de_origem: str = Form(...),
):
    documento_id = str(uuid4())

    if buscar_por_id(DOCUMENTOS_FILE, documento_id):
        logger.warning(
            "Tentativa de cadastrar um documento duplicado com id: %s", documento_id
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Documento ja existe",
        )

    DIRETORIO_DOCUMENTOS.mkdir(parents=True, exist_ok=True)

    nome_original = arquivo.filename or "arquivo"
    nome_armazenado = f"{nome_original}"
    caminho = DIRETORIO_DOCUMENTOS / nome_armazenado

    conteudo = arquivo.file.read()
    with open(caminho, "wb") as file:
        file.write(conteudo)

    sha256 = calcula_hash(caminho)

    documento = Documento(
        id=documento_id,
        nome_original=nome_original,
        nome_armazenado=nome_armazenado,
        extensao=Path(nome_original).suffix,
        tipo_mime=arquivo.content_type or "application/octet-stream",
        tamanho=len(conteudo),
        categoria=categoria,
        descricao=descricao,
        data_upload=datetime.now(),
        sha256=sha256,
        origem=origem,
        severidade=severidade,
        tipo_de_evento=tipo_de_evento,
        data_hora_evento=datetime.now(),
        sistema_de_origem=sistema_de_origem,
    )

    dados = documento.model_dump(mode="json")
    adicionar(DOCUMENTOS_FILE, dados)
    logger.info(
        "Documento cadastrado com id: %s, nome: %s",
        documento.id,
        documento.nome_original,
    )
    return documento
@router.put("/{documento_id}", response_model=Documento, status_code=status.HTTP_200_OK)
def atualizar_documento(documento_id: str, documento: Documento):
    dados = documento.model_dump(mode="json")
    dados["id"] = documento_id
    if not atualizar(DOCUMENTOS_FILE, documento_id, dados):
        logger.warning(
            "Tentativa de atualizar um documento inexistente com id: %s", documento_id
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Documento nao encontrado"
        )
    logger.info("Documento atualizado com id: %s", documento_id)
    return dados


@router.delete("/{documento_id}", status_code=status.HTTP_200_OK)
def deletar_documento(documento_id: str):
    if not remover(DOCUMENTOS_FILE, documento_id):
        logger.warning(
            "Tentando deletar um documento inexistente com id: %s", documento_id
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Documento nao encontrado"
        )

    logger.info("Documento deletado com id: %s", documento_id)
    return {"mensagem": "Documento deletado com sucesso."}


@router.get("/{documento_id}/integridade", status_code=status.HTTP_200_OK)
def obter_hash_documento(documento_id: str):
    documento = buscar_por_id(DOCUMENTOS_FILE, documento_id)

    if not documento:
        logger.warning(
            "Tentando verificar integridade de um documento inexistente com id: %s",
            documento_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Documento nao encontrado"
        )

    caminho_arquivo = DIRETORIO_DOCUMENTOS / documento["nome_armazenado"]

    if not caminho_arquivo.exists():
        logger.error(
            "Arquivo fisico nao encontrado para o documento com id: %s", documento_id
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo de documentos nao encontrado",
        )

    hash_atual = calcula_hash(caminho_arquivo)
    hash_original = documento.get("sha256")
    integro = hash_atual == hash_original

    logger.info(
        "Verificacao de integridade concluida para o documento com id: %s", documento_id
    )

    return {
        "id": documento["id"],
        "nome": documento["nome_original"],
        "hash_original": hash_original,
        "hash_atual": hash_atual,
        "integro": integro,
    }
