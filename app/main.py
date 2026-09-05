from fastapi import FastAPI

from app.core.logging_config import logger
app = FastAPI(
    title="Cofre Digital - Arquivos de Segurança da Informação",
    description="API para gerenciamento, proteção e auditoria de logs e evidências de cibersegurança",
    version="1.0.0",
)
