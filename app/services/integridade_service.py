import hashlib
from pathlib import Path


def calcula_hash(caminho: Path):
    hash_sha256 = hashlib.sha256()

    with open(caminho, mode="rb") as arquivo:
        bloco = arquivo.read(4096)

        while len(bloco) > 0:
            hash_sha256.update(bloco)
            bloco = arquivo.read(4096)

        return hash_sha256.hexdigest()
