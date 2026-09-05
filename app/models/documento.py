from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class NivelSeveridade(str, Enum):
    BAIXO = "baixo"
    MEDIO = "medio"
    ALTO = "alto"
    CRITICO = "critico"


class Documento(BaseModel):
    # Metadados gerais da aplicação

    id: str = Field(..., description="Identificador único, preferencialmente UUID")

    nome_original: str

    nome_armazenado: str

    extensao: str

    tipo_mime: str

    tamanho: int = Field(..., description="Tamanho do arquivo em bytes")

    categoria: str

    descricao: str | None = None

    data_upload: datetime

    sha256: str = Field(..., description="Hash para verificação de integridade")

    # Metadados específicos de domínio

    origem: str

    severidade: NivelSeveridade

    tipo_de_evento: str

    data_hora_evento: datetime

    sistema_de_origem: str
