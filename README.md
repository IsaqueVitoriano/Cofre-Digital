# Cofre Digital

> Evidências de cibersegurança organizadas, preservadas e prontas para auditoria

Uma API para registrar documentos e evidências de segurança da informação, relacioná-los a eventos e verificar se seus arquivos permanecem íntegros.

**Projeto acadêmico** desenvolvido na disciplina **Persistência de Software**, ministrada pelo professor Victor.

---

## Equipe

**Integrantes**

- Isaque Vitoriano
- Jose Mayson
- Matheus Eugênio

## Tema e objetivo

O projeto aborda a persistência e auditoria de evidências de cibersegurança. Seu objetivo é manter arquivos e metadados em um só lugar, facilitar consultas e apoiar a verificação de integridade, a geração de backups e a exportação de dados.

## Requisitos

Para instalar e executar a API, você precisa de:

  - **Python 3.10 ou superior** disponível no terminal (`python3 --version` para conferir)
  - **pip** para instalar os pacotes Python
  - **Um ambiente virtual**, recomendado para isolar as dependências do projeto
  - **Acesso à internet durante a instalação** para baixar os pacotes
  - **`python-multipart`** instalado para o FastAPI receber arquivos e formulários `multipart/form-data`
  - **Permissão de leitura e escrita** na pasta do projeto, pois a API grava documentos, metadados JSON, backups, exportações e logs em `storage/`
  - **Espaço em disco** para os arquivos enviados e gerados. A configuração declara um limite de upload de 20 MB

## Bibliotecas e como são usadas

| Biblioteca | Uso no projeto |
| --- | --- |
| FastAPI | Define as rotas, parâmetros, formulários, códigos HTTP e documentação OpenAPI |
| Uvicorn | Executa a aplicação como servidor ASGI |
| Pydantic | Define e valida documentos, categorias, severidades, estatísticas e respostas |
| PyYAML | Carrega a configuração em `config/logging.yaml` |
| Starlette | Fornece respostas de arquivo para downloads de documentos e exportações |
| `python-multipart` | Processa uploads e campos `multipart/form-data` |
| Biblioteca padrão do Python | `json` persiste metadados, `csv` exporta registros, `zipfile` cria backups, `hashlib` calcula hashes, `logging` registra eventos |
## Instalação e execução

No Linux, abra o terminal na raiz do projeto e crie o ambiente:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install python-multipart
```

Inicie o servidor:

```bash
python -m uvicorn app.main:app --reload
```

A documentação interativa está em [127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Organização do projeto

```text
app/
├── api/           Rotas HTTP
├── core/          Configuração compartilhada e logging
├── models/        Modelos de dados e enums
├── repositories/  Persistência dos metadados JSON
├── services/      Serviços, incluindo cálculo de hash
└── main.py        Inicialização da aplicação FastAPI

config/            Configuração do logging
storage/
├── backups/       Arquivos ZIP
├── documentos/    Evidências enviadas
├── exportacoes/   CSVs gerados
├── logs/          Logs da aplicação e atividades
└── metadata/      Metadados JSON
```

## Endpoints principais

| Método | Rota | Descrição |
| :--- | :--- | :--- |
| `POST` | `/documentos/` | Cadastra uma evidência e seus metadados |
| `GET` | `/documentos/` | Lista documentos cadastrados |
| `GET` | `/documentos/filtragem` | Pesquisa documentos por metadados |
| `GET` | `/documentos/filtragem/monitoramento` | Filtra documentos `.log` cadastrados |
| `GET` | `/documentos/integridade/global` | Audita a integridade de todas as evidências |
| `GET` | `/documentos/{documento_id}/integridade` | Audita uma evidência específica |
| `POST` | `/backup` | Cria um backup ZIP |
| `GET` | `/exportacao/exportar/CSV` | Exporta os metadados para CSV |

A API também permite consultar, atualizar, excluir e baixar documentos, além de listar backups. Consulte `/docs` para ver todas as rotas e parâmetros

## Exemplo: consultar estatísticas

No Swagger, abra `GET /documentos/estatisticas` e **execute**. A mesma consulta pode ser feita pelo terminal:

```bash
curl "http://127.0.0.1:8000/documentos/estatisticas"
```

A API retorna, por exemplo:

```json
{
  "total_documentos": 12,
  "espaco_ocupado_bytes": 245760,
  "quantidade_documentos": {
    ".pdf": 7,
    ".log": 5
  },
  "quantidade_documentos_categoria": {
    "auditorias": 8,
    "relatorios": 4
  },
  "dias_de_mais_download": "terça-feira",
  "quantidade_documentos_severidade_critica": 2
}
```

Os valores são ilustrativos; a resposta depende dos documentos cadastrados e dos downloads registrados
## Metadados de auditoria

Cada evidência é vinculada ao evento de cibersegurança por meio de:

| Campo | Significado |
| :--- | :--- |
| `origem` | Procedência da evidência ou do evento |
| `severidade` | Criticidade atribuída: baixa, média, alta ou crítica |
| `tipo_de_evento` | Natureza do evento de segurança |
| `data_hora_evento` | Data e hora em que o evento ocorreu |
| `sistema_de_origem` | Sistema que gerou ou registrou o evento |

Também são armazenados dados do arquivo, como nome, extensão, tipo MIME, tamanho, data de cadastro e hash SHA-256

## Funcionalidade específica: monitoramento de evidências

O monitoramento consulta evidências `.log` cadastradas e permite relacioná-las aos metadados do evento de cibersegurança: origem, severidade, tipo de evento e sistema de origem

No Swagger, abra `GET /documentos/filtragem/monitoramento`, preencha os filtros desejados e **execute**. Por exemplo, para buscar evidências de severidade alta relacionadas a acessos:

```bash
curl --get "http://127.0.0.1:8000/documentos/filtragem/monitoramento" \
  --data-urlencode "severidade=alto" \
  --data-urlencode "tipo_de_evento=acesso"
```

A resposta contém uma lista de evidências que correspondem aos filtros:

```json
[
  {
    "id": "7f1d9c2e-4a63-4b18-9e75-2d8b6f0c1a43",
    "nome_original": "eventos-seguranca.log",
    "nome_armazenado": "eventos-seguranca.log",
    "tipo_mime": "text/plain",
    "tamanho": 2048,
    "extensao": ".log",
    "categoria": "auditorias",
    "descricao": "Registro de tentativas de acesso",
    "data_upload": "2026-10-06T14:30:00",
    "sha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
    "origem": "servidor de arquivos",
    "severidade": "alto",
    "tipo_de_evento": "tentativa de acesso suspeito",
    "data_hora_evento": "2026-10-06T14:25:00",
    "sistema_de_origem": "SIEM"
  }
]
```

Os filtros textuais aceitam correspondência parcial sem diferenciar maiúsculas de minúsculas; a severidade deve ser `baixo`, `medio`, `alto` ou `critico`. Se nenhum registro corresponder, a API retorna `[]`.

A rota pesquisa os metadados dos documentos `.log` em `documentos.json`
---

Os metadados dos documentos ficam em `storage/metadata/documentos.json` e os registros de backup, em `storage/metadata/backups.json`
