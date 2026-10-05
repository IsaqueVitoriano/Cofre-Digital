from pydantic import BaseModel


class RelatoriosIntegridade(BaseModel):
    documentos_verificados: int
    documentos_integros: int
    documentos_alterados: int
    arquivos_nao_encontrados: int
