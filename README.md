# Cofre Digital

API para cadastro, armazenamento e auditoria de documentos e evidências de segurança da informação. Desenvolvida com FastAPI, mantém arquivos e metadados em diretórios separados.

## Tecnologias

- Python 3.10+
- FastAPI
- Uvicorn
- Pydantic
- PyYAML

## Estrutura do projeto

```text
app/
├── api/              # Endpoints da API
├── core/             # Configuração compartilhada, como logging
├── models/           # Modelos Pydantic e enums
├── repositories/     # Persistência dos metadados JSON
├── services/         # Serviços, como cálculo de hash
└── main.py           # Criação da aplicação FastAPI

config/
└── logging.yaml      # Formatters, handlers e níveis de log

storage/
├── backups/          # Backups ZIP
├── documentos/       # Arquivos enviados
├── exportacoes/      # Arquivos CSV gerados
├── logs/             # Logs da aplicação e de atividades
└── metadata/         # documentos.json e backups.json
```

Os diretórios em `storage/` recebem arquivos gerados durante a execução. Não versione dados locais nem logs gerados; os arquivos `.gitkeep` preservam os diretórios vazios no Git.

## Configuração do ambiente

Na raiz do projeto, crie e ative um ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```powershell
python -m pip install -r requirements.txt
python -m pip install python-multipart
```

`python-multipart` é necessário para os endpoints que recebem arquivos e campos de formulário.

## Executar a aplicação

Inicie o servidor a partir da raiz do repositório:

```powershell
python -m uvicorn app.main:app --reload
```

Com o servidor em execução, acesse:

- Swagger UI: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>

## Endpoints

| Método | Caminho | Descrição |
| --- | --- | --- |
| `GET` | `/documentos/` | Lista documentos cadastrados |
| `GET` | `/documentos/{documento_id}` | Consulta um documento pelo ID |
| `POST` | `/documentos/` | Envia um arquivo e cadastra seus metadados |
| `PUT` | `/documentos/{documento_id}` | Atualiza os metadados de um documento |
| `DELETE` | `/documentos/{documento_id}` | Remove um documento |
| `GET` | `/documentos/filtragem` | Filtra documentos por nome, extensão, categoria e data/hora do evento |
| `GET` | `/documentos/filtragem/monitoramento` | Filtra documentos cadastrados com extensão `.log` |
| `GET` | `/documentos/estatisticas` | Retorna estatísticas dos documentos e downloads |
| `GET` | `/documentos/integridade/global` | Verifica a integridade dos documentos cadastrados |
| `GET` | `/documentos/{documento_id}/integridade` | Verifica a integridade de um documento |
| `GET` | `/download/{documento_id}/download` | Baixa o arquivo associado ao documento |
| `POST` | `/backup` | Cria um backup ZIP dos arquivos armazenados |
| `GET` | `/backup/listagem_backup` | Lista os backups cadastrados |
| `GET` | `/exportacao/exportar/CSV` | Gera e retorna um CSV dos metadados |

### Upload

O endpoint `POST /documentos/` recebe `multipart/form-data` com:

- `arquivo` — arquivo a ser enviado;
- `categoria` — categoria do documento;
- `origem`;
- `severidade` — `baixo`, `medio`, `alto` ou `critico`;
- `tipo_de_evento`;
- `sistema_de_origem`;
- `descricao` — opcional.

As categorias aceitas atualmente são `comprovante`, `auditorias`, `manuais`, `formularios`, `contratos`, `relatorios`, `curriculos`, `prints` e `slides`.

Os metadados incluem nome original e armazenado, extensão, tipo MIME, tamanho, datas e hash SHA-256.

### Monitoramento

O endpoint `/documentos/filtragem/monitoramento` consulta os registros em `storage/metadata/documentos.json` e filtra documentos cuja extensão registrada seja `.log`. Ele não pesquisa diretamente o conteúdo de `storage/logs/app.log` ou `storage/logs/atividade.log`.

## Persistência e integridade

Os metadados dos documentos são armazenados em `storage/metadata/documentos.json`; os metadados dos backups, em `storage/metadata/backups.json`. As operações de persistência JSON são centralizadas em `app/repositories/json_repository.py`.

A verificação de integridade calcula o hash SHA-256 do arquivo armazenado e compara o resultado com o hash registrado nos metadados.

## Logs

A configuração está em `config/logging.yaml`:

- `storage/logs/app.log` registra eventos gerais da aplicação;
- `storage/logs/atividade.log` registra atividades com ação, ID do documento, nome e resultado;
- os logs da aplicação e as atividades também são enviados ao console, com formatters próprios.

## Desenvolvimento

Execute os comandos a partir da raiz do repositório. Não versione ambientes virtuais, caches, logs gerados nem dados locais de `storage/`.