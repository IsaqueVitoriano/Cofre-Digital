from pydantic import BaseModel, Field


class Estatistica(BaseModel):
    total_documentos: int = Field(..., description="Quantidade de documentos no banco")
    espaco_ocupado_bytes: float
    quantidade_documentos: dict[str,int] = Field(..., description="Quantidade de documentos pelo tipo")
    quantidade_documentos_categoria: dict[str, int] = Field(..., description="Quantidade de documentos por categoria")
    dias_mais_upload: str = Field(..., description="Dias da semana que houveram mais upload")
    dias_mais_download: str = Field(..., description="Dias da semana que houveram mais download")


