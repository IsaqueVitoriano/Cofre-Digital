from pydantic import BaseModel, Field


class Estatistica(BaseModel):
    total_documentos: int = Field(..., description="Quantidade de documentos no banco")
    espaco_ocupado_bytes: float
    quantidade_documentos: dict[str, int] = Field(
        ..., description="Quantidade de documentos pelo tipo"
    )
    quantidade_documentos_categoria: dict[str, int] = Field(
        ..., description="Quantidade de documentos por categoria"
    )

    # ATRIBUTOS ESPECÍFICOS DO PROJETO
    dias_de_mais_download: str | None = Field(
        ..., description="Dias da semana que houveram mais download"
    )
    quantidade_documentos_severidade_critica: int = Field(
        ..., description="Quantidade de documentos com grau de severidade CRÍTICA"
    )
