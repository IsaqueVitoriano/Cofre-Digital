import json
import csv
from pathlib import Path
from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from starlette.responses import FileResponse

from app.core.logging_config import logger_api, logger_atividades

from models.acoes_enum import ResultadoAtividade, AcaoAtividade

from app.models.documento import Documento, NivelSeveridade, DocumentoAtualizacao
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
EXPORTACAO_CSV = BASE_DIR / "storage" / "exportacoes" / "exportacoes.csv"

router = APIRouter(prefix="/documentos", tags=["documentos"])


@router.get("/", response_model=list[Documento])
def listar_documentos():
    documentos = ler_arquivo_json(DOCUMENTOS_FILE)
    logger_api.info("%s documentos foram listados", len(documentos))
    return documentos

@router.get("/{documento_id}", response_model=Documento)
def listar_documento_por_id(documento_id: str):
    documento = buscar_por_id(DOCUMENTOS_FILE, documento_id)
    if not documento:
        logger_api.warning("Documento nao encontrado: %s", documento_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Documento nao encontrado"
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
        logger_api.warning(
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

    try:
        adicionar(DOCUMENTOS_FILE, dados)
    except OSError:
        logger_api.warning(
            "Falha ao adicionar documento: %s", documento_id
        )
        raise


    logger_atividades.info(
        "Documento criado",
        extra={
            "acao": AcaoAtividade.DOCUMENT_CREATE.value,
            "documento_id": documento.id,
            "documento": documento.nome_original,
            "resultado": ResultadoAtividade.SUCCESS.value
        }
    )

    return documento

@router.put("/{documento_id}", response_model=Documento, status_code=status.HTTP_200_OK)
def atualizar_documento(documento_id: str, documento: DocumentoAtualizacao):
    dados_atualizacao = documento.model_dump(mode="json")
    documento_atual = buscar_por_id(DOCUMENTOS_FILE, documento_id)
    if not documento_atual:
        logger_api.warning(
            "Tentativa de atualizar um documento inexistente com id: %s", documento_id
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Documento nao encontrado"
        )

    try:
        documento_atual.update(dados_atualizacao)
        atualizar(
            DOCUMENTOS_FILE,
            documento_id,
            documento_atual
        )
    except OSError:
        logger_api.warning(
            "Erro ao atualizar documento: %s", documento_id
        )
        raise

    logger_api.info(
        "Documento de id: %s foi atualizado",
        documento_id
    )
    return documento_atual

@router.delete("/{documento_id}", status_code=status.HTTP_200_OK)
def deletar_documento(documento_id: str):
    documento = buscar_por_id(DOCUMENTOS_FILE, documento_id)
    if not documento:
        logger_api.warning(
            "Tentando deletar um documento inexistente com id: %s", documento_id
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Documento nao encontrado"
        )

    try:
        remover(DOCUMENTOS_FILE, documento_id)
    except FileNotFoundError:
        logger_api.warning(
            "Falha ao remover documento: %s, não foi encontrado", documento_id
        )
        raise

    caminho = DIRETORIO_DOCUMENTOS / documento["nome_original"]

    if caminho.exists():
        caminho.unlink()

    logger_atividades.info(
        "Documento deletado",
        extra={
            "acao": AcaoAtividade.DOCUMENT_DELETE.value,
            "documento_id": documento["id"],
            "documento": documento["nome_original"],
            "resultado": ResultadoAtividade.SUCCESS.value
        }
    )

    return {"mensagem": "Documento deletado com sucesso."}