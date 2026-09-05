# Cofre Digital

API para gerenciamento, proteção e auditoria de arquivos, logs e evidências de segurança da informação.

O projeto utiliza **FastAPI** e está organizado para armazenar documentos, metadados, backups, exportações e logs em diretórios separados.

## Tecnologias

- Python 3.10+
- FastAPI
- Uvicorn
- Pydantic
- PyYAML

## Estrutura do projeto

```text
Cofre-Digital/
├── app/
│   ├── api/              # Rotas da API
│   ├── core/             # Configurações compartilhadas
│   ├── models/           # Modelos e schemas
│   ├── repositories/     # Persistência de dados
│   ├── services/         # Regras de negócio
│   └── main.py           # Ponto de entrada da aplicação
├── config/
│   └── logging.yaml      # Configuração de armazenamento e logs
├── storage/
│   ├── backups/
│   ├── documentos/
│   ├── exportacoes/
│   ├── logs/
│   └── metadata/
└── README.md
```

## Configuração do ambiente

Crie e ative um ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```powershell
python -m pip install fastapi uvicorn pyyaml
```

## Executando a aplicação

Na raiz do projeto, execute:

```powershell
python -m uvicorn app.main:app --reload
```

O ponto de entrada da aplicação é `app/main.py`, que expõe a instância FastAPI `app`.


## Documentação da API

Com a aplicação em execução, acesse:

- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Configuração de logs

A configuração está em `config/logging.yaml`. Os logs são enviados para o console e para:

```text
storage/logs/app.log
```

Os diretórios de armazenamento são definidos na seção `storage` do arquivo de configuração. Arquivos gerados nesses diretórios não devem ser versionados.

## Modelo de documento

O modelo `Documento`, em `app/models/documento.py`, representa os metadados de uma evidência, incluindo:

- identificação e nomes do arquivo;
- extensão, tipo MIME e tamanho;
- hash SHA-256 para integridade;
- origem e sistema de origem;
- severidade do evento;
- datas de upload e do evento.

Os níveis de severidade disponíveis são: `baixo`, `medio`, `alto` e `critico`.

## Desenvolvimento

Execute os comandos sempre a partir da raiz do repositório. Não versione arquivos específicos da máquina, como `.venv/`, `.idea/`, `__pycache__/` e logs gerados.