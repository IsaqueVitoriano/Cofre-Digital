import json
from pathlib import Path
from typing import Any

from app.core.logging_config import logger


def garantir_arquivo_json(caminho_arquivo: Path) -> None:
    caminho_arquivo.parent.mkdir(parents=True, exist_ok=True)

    if not caminho_arquivo.exists():
        with open(caminho_arquivo, mode="w", encoding="utf-8") as arquivo:
            json.dump([], arquivo, ensure_ascii=False, indent=4)

    logger.info("O arquivo JSON %s foi criado.", caminho_arquivo.name)


def ler_arquivo_json(caminho_arquivo: Path) -> list[dict[str, Any]]:
    garantir_arquivo_json(caminho_arquivo)

    try:
        with open(caminho_arquivo, mode="r", encoding="utf-8") as arquivo:
            return json.load(arquivo)

    except json.JSONDecodeError as erro:
        logger.error("O JSON é inválido em %s, o erro: %s", caminho_arquivo.name, erro)

    raise ValueError(f"{caminho_arquivo.name} contém JSON inválido.")


def escrever_arquivo_json(caminho_arquivo: Path, dados: list[dict[str, Any]]) -> None:
    garantir_arquivo_json(caminho_arquivo)

    with open(caminho_arquivo, mode="w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=4)

    logger.debug(
        "O arquivo %s foi atualizado com %d registro(s)",
        caminho_arquivo.name,
        len(dados),
    )


def buscar_por_id(caminho_arquivo: Path, registro_id: str) -> dict[str, Any] | None:
    dados = ler_arquivo_json(caminho_arquivo)

    for item in dados:
        if item["id"] == registro_id:
            return item

    return None


def adicionar(caminho_arquivo: Path, novo_registro: dict[str, Any]) -> None:
    dados = ler_arquivo_json(caminho_arquivo)
    dados.append(novo_registro)
    escrever_arquivo_json(caminho_arquivo, dados)


def atualizar(
    caminho_arquivo: Path, registro_id: str, novo_registro: dict[str, Any]
) -> bool:
    dados = ler_arquivo_json(caminho_arquivo)

    for i, item in enumerate(dados):
        if item["id"] == registro_id:
            novo_registro["id"] = registro_id
            dados[i] = novo_registro
            escrever_arquivo_json(caminho_arquivo, dados)

            return True

    return False


def remover(caminho_arquivo: Path, registro_id: str) -> bool:
    dados = ler_arquivo_json(caminho_arquivo)

    nova_lista = [item for item in dados if item["id"] != registro_id]

    if len(nova_lista) == len(dados):
        return False

    escrever_arquivo_json(caminho_arquivo, nova_lista)

    return True
