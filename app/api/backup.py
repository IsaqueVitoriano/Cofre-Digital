import zipfile
from datetime import datetime
from fastapi import APIRouter, status, HTTPException
from pathlib import Path
from app.models.documento import BackupJson
from app.core.logging_config import logger_api
from app.repositories.json_repository import(
    adicionar,
    ler_arquivo_json
)

router = APIRouter(
    prefix="/backup",
    tags=["backup"],
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DIRETORIO_DOCUMENTOS = BASE_DIR / "storage" / "documentos"
DOCUMENTOS_COMPACTADO = BASE_DIR / "storage" / "backups"
DOCUMENTOS_FILE = BASE_DIR / "storage" / "metadata" / "backups.json"

@router.post("", status_code=status.HTTP_201_CREATED)
def documento_compactado():
    if DIRETORIO_DOCUMENTOS.exists():
        arquivos = [
            arquivo for arquivo in DIRETORIO_DOCUMENTOS.iterdir()
            if arquivo.is_file() and arquivo.name != ".gitkeep"
        ]
    else :
        arquivos = []

    if not arquivos:
        logger_api.warning(
            "Tentativa de realizar backup sem documentos no diretorio"
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diretorio sem documentos para backup"
        )

    nome_original = "backup_" + datetime.now().strftime("%Y-%m-%d_%H%M%S_%f") + ".zip"
    caminho = DOCUMENTOS_COMPACTADO / nome_original
    DOCUMENTOS_COMPACTADO.mkdir(parents=True, exist_ok=True)
    DOCUMENTOS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with zipfile.ZipFile(caminho, "w") as file_zip:
        for arquivo in arquivos:
            if arquivo.is_file():
                file_zip.write(
                    arquivo,
                    arcname=arquivo.name,
                )
        registro_json = BackupJson(
            nome_original=nome_original,
            tamanho=arquivo.stat().st_size,
        )
        dados = registro_json.model_dump(mode="json")
        adicionar(
            DOCUMENTOS_FILE,
            dados
        )
    logger_api.info(
        "backup realizado com sucesso"
    )
    return {"messagem" : "backup realizado com sucesso"}

@router.get("/listagem_backup", response_model=list[BackupJson])
def listagem_backup():
    dados = ler_arquivo_json(DOCUMENTOS_FILE)
    logger_api.info(
        "%s backups foram listados", len(dados)
    )
    return dados