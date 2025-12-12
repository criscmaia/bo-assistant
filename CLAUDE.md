# BO Inteligente

Sistema de IA para auxiliar policiais militares na redação de Boletins de Ocorrência de tráfico de drogas.

## Links de Produção

| Ambiente | URL |
|----------|-----|
| Frontend | https://criscmaia.github.io/bo-assistant/ |
| Backend API | https://bo-assistant-backend.onrender.com |
| Dashboard Logs | https://criscmaia.github.io/bo-assistant/logs.html |
| Repositório | https://github.com/criscmaia/bo-assistant |

## Stack Técnica

- **Backend**: Python 3.13 + FastAPI + SQLAlchemy
- **Frontend**: HTML5 + Vanilla JavaScript + Tailwind CSS (via CDN)
- **LLM**: Google Gemini 2.5 Flash
- **Banco de Dados**: PostgreSQL (produção) / SQLite (local)
- **Deploy**: Render (backend) + GitHub Pages (frontend)

## Estrutura do Projeto

```
bo-assistant/
├── backend/
│   ├── main.py              # API FastAPI (endpoints)
│   ├── state_machine.py     # Fluxo de 6 perguntas da Seção 1
│   ├── llm_service.py       # Integração com Gemini
│   ├── validator.py         # Validação de respostas
│   ├── logger.py            # Sistema de logs (PostgreSQL/SQLite)
│   ├── requirements.txt     # Dependências de produção
│   └── requirements-dev.txt # Dependências de desenvolvimento
├── docs/
│   ├── index.html           # Interface principal do chat
│   └── logs.html            # Dashboard de logs
├── CHANGELOG.md             # Histórico de versões
├── README.md                # Documentação principal
└── render.yaml              # Configuração do Render
```

## Comandos para Desenvolvimento Local

```bash
# Terminal 1 - Backend
cd backend
.\venv\Scripts\activate      # Windows
source venv/bin/activate     # Mac/Linux
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd docs
python -m http.server 3000

# Acessar: http://localhost:3000
```

## Fluxo da Aplicação

1. Usuário inicia sessão → `POST /new_session` → retorna `session_id` e `bo_id`
2. Sistema faz 6 perguntas sequenciais (Seção 1: Contexto da Ocorrência)
3. Cada resposta é validada pelo `validator.py`
4. Respostas válidas são armazenadas no `state_machine.py`
5. Após 6 respostas, `llm_service.py` gera o texto do BO via Gemini
6. Todos os eventos são logados no banco via `logger.py`

## Perguntas da Seção 1

1. **1.1** - Dia, data e hora do acionamento
2. **1.2** - Composição da guarnição e prefixo
3. **1.3** - Natureza do empenho
4. **1.4** - Ordem de serviço / COPOM / DDU
5. **1.5** - Local exato da ocorrência
6. **1.6** - Histórico do local / facção

## Principais Endpoints da API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/new_session` | Inicia nova sessão |
| POST | `/chat` | Processa resposta do usuário |
| PUT | `/chat/{session_id}/answer/{step}` | Edita resposta anterior |
| POST | `/feedback` | Registra feedback (👍👎) |
| GET | `/api/logs` | Lista sessões |
| GET | `/api/stats` | Estatísticas gerais |

## Variáveis de Ambiente

```bash
# backend/.env
GEMINI_API_KEY=sua_chave_aqui
DATABASE_URL=postgresql://...  # Apenas em produção
```

## Princípios de Desenvolvimento

1. **Nunca inventar informações** - O LLM só usa dados fornecidos pelo usuário
2. **Validação inteligente** - Rejeita respostas vagas sem ser excessivamente rígido
3. **Encoding UTF-8** - Sempre usar UTF-8 em arquivos Python (acentos!)
4. **Código simples** - JavaScript vanilla, sem frameworks complexos

## Versão Atual

**v0.4.1** (12/12/2025)
- Rascunho automático (localStorage)
- Sugestão de data/hora atual na pergunta 1.1
- Validação de data/hora futura
- Correção de encoding UTF-8

## Equipe

- **Cristiano Maia** - Delivery Manager & Tech Lead
- **Claudio Moreira** - Especialista em Redação de BOs (Sargento PM)

## Notas Importantes

- O backend no Render (free tier) "dorme" após 15 min de inatividade
- Primeira requisição pode demorar 30-60s para "acordar"
- Frontend é estático no GitHub Pages (deploy automático no push)
- Testar localmente ANTES de fazer push para produção
