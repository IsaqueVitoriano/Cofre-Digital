from fastapi import FastAPI
from app.api import documentos, exportacao, download, integridade

app = FastAPI(
    title="Cofre Digital - Arquivos de Segurança da Informação",
    description="API para gerenciamento, proteção e auditoria de logs e evidências de cibersegurança",
    version="1.0.0",
)

app.include_router(documentos.router)
app.include_router(exportacao.router)
app.include_router(download.router)
app.include_router(integridade.router)