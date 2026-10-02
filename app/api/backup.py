
import zipfile
from datetime import datetime
from fastapi import APIRouter, status, HTTPException
from pathlib import Path

from app.core.logging_config import logger_api

router = APIRouter(
    prefix="/backup",
    tags=["backup"],
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DIRETORIO_DOCUMENTOS = BASE_DIR / "storage" / "documentos"
DOCUMENTOS_COMPACTADO = BASE_DIR / "storage" / "backups"

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
    
    with zipfile.ZipFile(caminho, "w") as zip:
        for arquivo in DIRETORIO_DOCUMENTOS.iterdir():
            if arquivo.is_file():
                zip.write(
                    arquivo,
                    arcname=arquivo.name,
                )
    logger_api.info(
        "backup realizado com sucesso"
    )
    return {"messagem" : "backup realizado com sucesso"}