# 📚 BO Inteligente - Documentação Técnica

Documentação técnica completa do sistema BO Inteligente, detalhando a arquitetura, funcionamento de cada componente e fluxos de dados.

---

## 📋 Índice

1. [Visão Geral da Arquitetura](#visão-geral-da-arquitetura)
2. [Backend - Arquivos Python](#backend---arquivos-python)
3. [Frontend - Arquivos HTML/JS](#frontend---arquivos-htmljs)
4. [Banco de Dados](#banco-de-dados)
5. [Fluxos de Dados](#fluxos-de-dados)
6. [Configuração e Deploy](#configuração-e-deploy)
7. [Automação e Testes](#automação-e-testes)

---

## 🏗️ Visão Geral da Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                         USUÁRIO                                  │
│                    (Navegador Web/Mobile)                        │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    GITHUB PAGES                                  │
│              docs/index.html + docs/logs.html                    │
│                  (Frontend Estático)                             │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTPS (API Calls)
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                       RENDER                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   FastAPI (main.py)                      │    │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐     │    │
│  │  │state_machine │ │  validator   │ │ llm_service  │     │    │
│  │  │     .py      │ │     .py      │ │     .py      │     │    │
│  │  └──────────────┘ └──────────────┘ └──────┬───────┘     │    │
│  │                                           │              │    │
│  │  ┌──────────────────────────────────────────────────┐   │    │
│  │  │              logger.py (BOLogger)                 │   │    │
│  │  └──────────────────────┬───────────────────────────┘   │    │
│  └─────────────────────────┼───────────────────────────────┘    │
│                            │                                     │
│  ┌─────────────────────────▼───────────────────────────────┐    │
│  │                   PostgreSQL                             │    │
│  │    (bo_sessions, bo_events, feedbacks)                   │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    GOOGLE AI STUDIO                              │
│                   Gemini 2.5 Flash API                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🐍 Backend - Arquivos Python

### 📄 `main.py`
**Função:** API principal FastAPI - ponto de entrada do backend

**Responsabilidades:**
- Configurar aplicação FastAPI e CORS
- Definir todos os endpoints da API
- Gerenciar sessões em memória
- Orquestrar validação, geração de texto e logging

**Componentes principais:**

```python
# Modelos Pydantic para validação de requests/responses
class ChatRequest          # Recebe mensagem do usuário
class ChatResponse         # Retorna próxima pergunta ou texto gerado
class NewSessionResponse   # Retorna session_id e primeira pergunta
class UpdateAnswerRequest  # Recebe edição de resposta
class FeedbackRequest      # Recebe feedback do usuário

# Armazenamento em memória
sessions: Dict[str, tuple]  # session_id -> (bo_id, state_machine)
```

**Endpoints:**

| Endpoint | Método | Função |
|----------|--------|--------|
| `/` | GET | Informações da API |
| `/health` | GET | Health check |
| `/new_session` | POST | Cria nova sessão |
| `/chat` | POST | Processa resposta do usuário |
| `/chat/{session_id}/answer/{step}` | PUT | Edita resposta anterior |
| `/feedback` | POST | Registra feedback |
| `/api/stats` | GET | Estatísticas gerais |
| `/api/logs` | GET | Lista sessões |
| `/api/logs/{bo_id}` | GET | Detalhes de uma sessão |
| `/session/{session_id}` | DELETE | Deleta sessão |
| `/session/{session_id}/status` | GET | Status da sessão |

**Fluxo do endpoint `/chat`:**
1. Recebe `session_id` e `message`
2. Recupera `state_machine` da sessão
3. Valida resposta com `ResponseValidator`
4. Se inválida: retorna erro + loga evento
5. Se válida: armazena resposta, avança step
6. Se completo: gera texto com `LLMService`
7. Retorna próxima pergunta ou texto gerado

---

### 📄 `state_machine.py`
**Função:** Gerencia o fluxo de perguntas da Seção 1

**Responsabilidades:**
- Definir as 6 perguntas da Seção 1
- Controlar qual pergunta está ativa
- Armazenar respostas do usuário
- Verificar se seção está completa

**Estrutura:**

```python
class BOStateMachine:
    # Perguntas fixas
    QUESTIONS = {
        "1.1": "Dia, data e hora do acionamento.",
        "1.2": "Composição da guarnição e prefixo.",
        "1.3": "Natureza do empenho.",
        "1.4": "O que constava na ordem de serviço, informações do COPOM, DDU.",
        "1.5": "Local exato da ocorrência (logradouro, número, bairro).",
        "1.6": "O local é ponto de tráfico? Quais evidências anteriores? Há facção?"
    }
    
    # Ordem de execução
    STEPS = ["1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "complete"]
    
    # Estado
    current_step: str      # Step atual (ex: "1.3")
    answers: Dict[str, str] # Respostas armazenadas
    step_index: int        # Índice no array STEPS
```

**Métodos:**

| Método | Retorno | Descrição |
|--------|---------|-----------|
| `get_current_question()` | str | Retorna texto da pergunta atual |
| `store_answer(answer)` | None | Armazena resposta para step atual |
| `next_step()` | None | Avança para próximo step |
| `is_section_complete()` | bool | Verifica se todas perguntas respondidas |
| `get_all_answers()` | Dict | Retorna todas as respostas |
| `get_formatted_answers()` | str | Formata respostas para debug |
| `get_progress()` | Dict | Retorna progresso (X/6, %) |
| `reset()` | None | Reinicia máquina de estados |

---

### 📄 `validator.py`
**Função:** Valida respostas do usuário antes de aceitar

**Responsabilidades:**
- Verificar se resposta tem tamanho mínimo
- Validar formato de data/hora (step 1.1)
- Verificar presença de palavras-chave obrigatórias
- Rejeitar respostas muito vagas

**Regras de validação por step:**

| Step | Validações | Exemplo válido |
|------|------------|----------------|
| 1.1 | Data + hora + dia válido | "22/03/2025, às 19h03" |
| 1.2 | Mín 15 chars + "prefixo" | "Sgt João e Cb Pedro, prefixo 1234" |
| 1.3 | Mín 10 chars + não só "tráfico" | "Tráfico de drogas" |
| 1.4 | Mín 20 chars + detalhes | "Denúncia via COPOM sobre venda de drogas" |
| 1.5 | Rua + número + bairro | "Rua X, nº 123, bairro Centro" |
| 1.6 | Mín 15 chars ou "NÃO" | "Sim, histórico de operações. Facção XYZ" |

**Validação de data/hora (step 1.1):**
```python
# Verifica presença de data (DD/MM ou nome do mês)
# Verifica presença de hora (HH:MM ou HHhMM)
# Valida hora (0-23) e minuto (0-59)
# Valida dia do mês (considera meses com 28-31 dias)
```

**Método principal:**
```python
@staticmethod
def validate(step: str, answer: str) -> Tuple[bool, Optional[str]]:
    """
    Returns:
        (is_valid, error_message)
        - is_valid: True se resposta é válida
        - error_message: Mensagem de erro se inválida, None se válida
    """
```

---

### 📄 `llm_service.py`
**Função:** Integração com Gemini para geração de texto

**Responsabilidades:**
- Conectar com API do Gemini
- Enriquecer datas (adicionar dia da semana)
- Construir prompt especializado
- Gerar texto do BO

**Enriquecimento de datas:**
```python
# Entrada: "22/03/2025, às 19h03"
# Saída: "sexta-feira, 22 de março de 2025, às 19h03min"
```

**Estrutura do prompt:**

1. **Contexto:** "Você é um assistente especializado em redigir BOs..."
2. **Dados coletados:** Respostas do usuário formatadas
3. **Regra crítica:** "NUNCA INVENTAR INFORMAÇÕES"
4. **Regras de redação:** Voz ativa, frases curtas, norma culta
5. **Estrutura esperada:** Modelo baseado na documentação do Claudio
6. **Exemplos:** Comparação certo vs errado
7. **Formato de saída:** Parágrafo corrido, dois espaços entre frases

**Método principal:**
```python
async def generate_section_text(
    self, 
    section_data: Dict[str, str],  # Respostas do usuário
    provider: str = "gemini"       # LLM a usar
) -> str:                          # Texto gerado
```

---

### 📄 `logger.py`
**Função:** Sistema de logs e persistência em banco de dados

**Responsabilidades:**
- Detectar ambiente (local vs produção)
- Gerenciar conexão com banco (SQLite ou PostgreSQL)
- Registrar eventos de sessão
- Armazenar feedbacks dos usuários

**Detecção de ambiente:**
```python
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Produção: PostgreSQL (Render)
    # Corrige postgres:// para postgresql://
else:
    # Local: SQLite (bo_logs.db)
```

**Modelos SQLAlchemy:**

```python
class BOSession:
    bo_id: str           # PK, formato "BO-YYYYMMDD-xxxxxxxx"
    created_at: datetime # Timestamp de criação
    completed_at: datetime # Timestamp de conclusão (nullable)
    status: str          # "active", "completed", "abandoned"
    app_version: str     # Versão do sistema
    ip_address: str      # IP do cliente
    user_agent: str      # User-Agent do navegador

class BOEvent:
    event_id: str        # PK, formato "evt_xxxxxxxx"
    bo_id: str           # FK para BOSession
    timestamp: datetime  # Quando ocorreu
    event_type: str      # Tipo do evento
    data: JSON           # Dados específicos do evento

class Feedback:
    feedback_id: str     # PK, formato "fb_xxxxxxxx"
    bo_id: str           # FK para BOSession
    event_id: str        # FK para BOEvent (opcional)
    timestamp: datetime  # Quando enviado
    feedback_type: str   # "positive" ou "negative"
    category: str        # "bug", "suggestion" (opcional)
    user_message: str    # Mensagem do usuário (opcional)
    context: JSON        # Contexto (step, mensagem)
    meta_data: JSON      # Metadados (IP, user-agent, etc)
    status: str          # "new", "reviewed", "resolved"
```

**Tipos de eventos:**

| event_type | Quando | Dados |
|------------|--------|-------|
| `session_started` | Nova sessão | ip, app_version |
| `question_asked` | Exibe pergunta | step, question |
| `answer_submitted` | Usuário responde | step, answer, is_valid |
| `validation_error` | Resposta inválida | step, answer, error_message |
| `answer_edited` | Edição de resposta | step, old_answer, new_answer |
| `text_generated` | BO gerado | llm_provider, text, tempo |
| `generation_error` | Erro na geração | error, llm_provider |

**Classe BOLogger (métodos estáticos):**

| Método | Descrição |
|--------|-----------|
| `create_session()` | Cria nova sessão, retorna bo_id |
| `log_event()` | Registra evento, retorna event_id |
| `update_session_status()` | Atualiza status (completed/abandoned) |
| `add_feedback()` | Registra feedback do usuário |
| `get_session()` | Busca sessão por bo_id |
| `get_events()` | Lista eventos de uma sessão |
| `get_feedbacks()` | Lista feedbacks de uma sessão |
| `list_sessions()` | Lista sessões com filtros |
| `get_stats()` | Estatísticas gerais |

---

## 🌐 Frontend - Arquivos HTML/JS

### 📄 `docs/index.html`
**Função:** Interface principal do chat

**Estrutura HTML:**
```
┌─────────────────────────────────────────────────────────────┐
│ HEADER: "BO Inteligente v0.4.0" + botão mobile              │
├──────────────────┬──────────────────────────────────────────┤
│                  │                                          │
│    SIDEBAR       │           CHAT CONTAINER                 │
│  (Progresso)     │      (Mensagens + Feedback)              │
│                  │                                          │
│  1. ✓ Pergunta 1 │  ┌──────────────────────────────────┐   │
│  2. ✓ Pergunta 2 │  │ Bot: Pergunta atual              │   │
│  3. ⏳ Pergunta 3 │  │                        👍 👎     │   │
│  4. ○ Pergunta 4 │  ├──────────────────────────────────┤   │
│  5. ○ Pergunta 5 │  │ User: Resposta         ✏️ Editar │   │
│  6. ○ Pergunta 6 │  │                        👍 👎     │   │
│                  │  └──────────────────────────────────┘   │
│  [Barra 3/6]     │                                          │
│                  ├──────────────────────────────────────────┤
│                  │ INPUT: [Digite aqui...] [Enviar]         │
└──────────────────┴──────────────────────────────────────────┘
```

**JavaScript - Estado:**
```javascript
let sessionId = null;        // UUID da sessão
let currentBoId = null;      // ID do BO (ex: "BO-20251211-abc123")
let isWaitingResponse = false; // Aguardando API
let currentQuestionStep = '1.1'; // Step atual
let answersState = {};       // Respostas locais { '1.1': 'texto', ... }
```

**JavaScript - Funções principais:**

| Função | Descrição |
|--------|-----------|
| `startSession()` | Inicia sessão via API, exibe primeira pergunta |
| `sendMessage()` | Envia resposta, processa retorno, atualiza UI |
| `editAnswer()` | Abre modo edição inline |
| `sendFeedback()` | Envia feedback (👍/👎) |
| `openFeedbackModal()` | Modal para feedback detalhado |
| `addMessage()` | Adiciona mensagem ao chat |
| `initializeSidebar()` | Renderiza lista de perguntas |
| `updateSidebarStatus()` | Atualiza cores/ícones |
| `updateSidebarAnswer()` | Atualiza preview da resposta |
| `updateSidebarProgress()` | Atualiza barra de progresso |

**Responsividade:**
- Desktop: Sidebar fixa à esquerda (w-80)
- Mobile: Sidebar como drawer lateral com overlay
- Botão "📝 Progresso" no header abre sidebar

---

### 📄 `docs/logs.html`
**Função:** Dashboard de logs para validação

**Estrutura:**
```
┌─────────────────────────────────────────────────────────────┐
│ HEADER: "Dashboard de Logs" + link voltar                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │ Total   │ │Completos│ │   👍    │ │   👎    │           │
│  │   12    │ │    8    │ │    5    │ │    2    │           │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ BO-20251211-abc123  │ ✅ Concluído │ 👍2 👎1 [Ver] │   │
│  │ BO-20251211-def456  │ ⏳ Ativo     │ 👍0 👎0 [Ver] │   │
│  │ ...                                                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Modal de detalhes (timeline):**
```
┌─────────────────────────────────────────────────────────────┐
│ BO-20251211-abc123                              [X] Fechar  │
│ ✅ Concluído | 11/12/2025 às 14:30 | Duração: 5 min        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 💬 Olá! Vou te ajudar a fazer o BO...                      │
│                                                             │
│ 1. Data e hora do acionamento                               │
│    "asd" ❌                                                 │
│    ⚠️ Por favor, informe dia, data E hora completos        │
│    "22/03/2025, 19h03" ✅ 👎 "horário estava errado"       │
│                                                             │
│ 2. Composição da guarnição                                  │
│    "Sgt João, prefixo 1234" ✅ ✏️                           │
│                                                             │
│ ... (demais perguntas)                                      │
│                                                             │
│ 📄 TEXTO GERADO PELO SISTEMA 👍                            │
│ ⏱️ Gerado em 2.3s                                          │
│ ┌─────────────────────────────────────────────────────┐    │
│ │ No dia sexta-feira, 22 de março de 2025...          │    │
│ └─────────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Funções principais:**

| Função | Descrição |
|--------|-----------|
| `loadStats()` | Carrega estatísticas do `/api/stats` |
| `loadSessions()` | Lista sessões do `/api/logs` |
| `openDetail()` | Abre modal com detalhes de um BO |
| `renderDetail()` | Renderiza timeline da conversa |
| `renderFeedbackBadges()` | Exibe badges 👍👎 inline |

**Auto-refresh:** A cada 30 segundos atualiza stats e lista

---

## 🗄️ Banco de Dados

### Esquema

```sql
-- Sessões de BO
CREATE TABLE bo_sessions (
    bo_id VARCHAR(50) PRIMARY KEY,      -- "BO-YYYYMMDD-xxxxxxxx"
    created_at TIMESTAMP,                -- Quando iniciou
    completed_at TIMESTAMP,              -- Quando finalizou (null se ativo)
    status VARCHAR(20),                  -- "active", "completed", "abandoned"
    app_version VARCHAR(20),             -- "0.4.0"
    ip_address VARCHAR(50),              -- IP do cliente
    user_agent TEXT                      -- User-Agent do navegador
);

-- Eventos de uma sessão
CREATE TABLE bo_events (
    event_id VARCHAR(50) PRIMARY KEY,    -- "evt_xxxxxxxx"
    bo_id VARCHAR(50) NOT NULL,          -- FK para bo_sessions
    timestamp TIMESTAMP,                  -- Quando ocorreu
    event_type VARCHAR(50),              -- Tipo do evento
    data JSON                            -- Dados específicos
);

-- Feedbacks dos usuários
CREATE TABLE feedbacks (
    feedback_id VARCHAR(50) PRIMARY KEY, -- "fb_xxxxxxxx"
    bo_id VARCHAR(50) NOT NULL,          -- FK para bo_sessions
    event_id VARCHAR(50),                -- FK para bo_events (opcional)
    timestamp TIMESTAMP,                  -- Quando enviado
    feedback_type VARCHAR(20),           -- "positive" ou "negative"
    category VARCHAR(20),                -- "bug", "suggestion"
    user_message TEXT,                   -- Descrição do usuário
    context JSON,                        -- { step, message }
    meta_data JSON,                      -- { ip, user_agent, ... }
    status VARCHAR(20)                   -- "new", "reviewed", "resolved"
);
```

### Ambientes

| Ambiente | Banco | Conexão |
|----------|-------|---------|
| **Local** | SQLite | `sqlite:///./bo_logs.db` |
| **Produção** | PostgreSQL | `DATABASE_URL` (Render) |

---

## 🔄 Fluxos de Dados

### Fluxo 1: Iniciar Sessão

```
Frontend                    Backend                      Banco
    │                          │                           │
    │ POST /new_session        │                           │
    │─────────────────────────>│                           │
    │                          │ BOLogger.create_session() │
    │                          │──────────────────────────>│
    │                          │       bo_id               │
    │                          │<──────────────────────────│
    │                          │ BOStateMachine()          │
    │                          │ sessions[session_id] = ...│
    │                          │ BOLogger.log_event()      │
    │                          │──────────────────────────>│
    │   { session_id, bo_id,   │                           │
    │     first_question }     │                           │
    │<─────────────────────────│                           │
```

### Fluxo 2: Enviar Resposta (válida)

```
Frontend                    Backend                      Banco
    │                          │                           │
    │ POST /chat               │                           │
    │ { session_id, message }  │                           │
    │─────────────────────────>│                           │
    │                          │ ResponseValidator.validate()
    │                          │ (is_valid = true)         │
    │                          │                           │
    │                          │ BOLogger.log_event()      │
    │                          │ (answer_submitted)        │
    │                          │──────────────────────────>│
    │                          │                           │
    │                          │ state_machine.store_answer()
    │                          │ state_machine.next_step() │
    │                          │                           │
    │                          │ BOLogger.log_event()      │
    │                          │ (question_asked)          │
    │                          │──────────────────────────>│
    │                          │                           │
    │   { question,            │                           │
    │     current_step }       │                           │
    │<─────────────────────────│                           │
```

### Fluxo 3: Gerar Texto (seção completa)

```
Frontend                    Backend                      Gemini
    │                          │                           │
    │ POST /chat (step 1.6)    │                           │
    │─────────────────────────>│                           │
    │                          │ state_machine.is_section_complete()
    │                          │ (true)                    │
    │                          │                           │
    │                          │ llm_service.generate_section_text()
    │                          │──────────────────────────>│
    │                          │    (prompt + respostas)   │
    │                          │<──────────────────────────│
    │                          │    (texto gerado)         │
    │                          │                           │
    │                          │ BOLogger.log_event()      │
    │                          │ (text_generated)          │
    │                          │ BOLogger.update_session_status()
    │                          │                           │
    │   { generated_text,      │                           │
    │     is_section_complete: │                           │
    │     true }               │                           │
    │<─────────────────────────│                           │
```

---

## ⚙️ Configuração e Deploy

### Arquivos de Configuração

#### `render.yaml`
```yaml
services:
  - type: web
    name: bo-assistant-backend
    runtime: python
    plan: free
    region: oregon
    branch: main
    buildCommand: cd backend && pip install -r requirements.txt
    startCommand: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health
    autoDeploy: true
    envVars:
      - key: PYTHON_VERSION
        value: 3.13.4
      - key: GEMINI_API_KEY
        sync: false  # Definir manualmente no dashboard
```

#### `requirements.txt` (Produção)
```
fastapi==0.115.5
uvicorn==0.32.1
google-generativeai==0.8.3
sqlalchemy==2.0.36
psycopg2-binary==2.9.10
python-dotenv==1.0.1
```

#### `requirements-dev.txt` (Desenvolvimento)
```
-r requirements.txt          # Herda produção

# Automação
playwright>=1.40.0
opencv-python>=4.8.0
pillow>=10.0.0

# Testes
pytest>=7.4.0
pytest-asyncio>=0.21.0
httpx>=0.25.0

# Desenvolvimento
black>=23.0.0
isort>=5.12.0
```

#### `.env` (Local - não versionado)
```bash
GEMINI_API_KEY=sua_chave_aqui
# DATABASE_URL não definido = usa SQLite
```

#### `env.example` (Template)
```bash
# API Keys
GEMINI_API_KEY=sua_chave_aqui

# Database (opcional)
DATABASE_URL=postgresql://user:pass@host/db
```

---

## 🤖 Automação e Testes

### `automate_release.py`
**Função:** Gerar screenshots e vídeos automaticamente para releases

**Uso:**
```bash
# Básico
python automate_release.py --version v0.4.0

# Sem vídeo (mais rápido)
python automate_release.py --version v0.4.0 --no-video

# URLs customizadas
python automate_release.py --version v0.4.0 \
    --backend http://localhost:8000 \
    --frontend http://localhost:3000
```

**Saída:**
```
docs/screenshots/v0.4.0/
├── 01-desktop-sidebar-empty.png
├── 02-desktop-sidebar-progress.png
├── 03-desktop-editando.png
├── 04-desktop-editando-erro.png
├── 05-desktop-editando-sucesso.png
├── 06-desktop-final.png
├── 07-mobile-empty.png
├── 08-mobile-sidebar-open.png
├── 09-mobile-final.png
├── demo.webm
└── README.md
```

### `test_scenarios.json`
**Função:** Configuração de cenários de teste

**Estrutura:**
```json
{
  "version": "v0.4.0",
  "backend_url": "http://localhost:8000",
  "frontend_url": "http://localhost:3000",
  "resolutions": {
    "desktop": {"width": 1280, "height": 720},
    "mobile": {"width": 430, "height": 932}
  },
  "test_flow": [
    {
      "step": 1,
      "answer": "21:11, dia 22/03",
      "should_pass": true
    },
    // ... mais cenários
  ]
}
```

---

## 📝 Notas Adicionais

### Timezone
- Todos os timestamps usam horário de Brasília (UTC-3)
- Função `now_brasilia()` em `logger.py`

### Sessões em Memória
- Sessões são armazenadas em `sessions: Dict[str, tuple]`
- Perdidas se servidor reiniciar
- Logs persistem no banco de dados

### CORS
- Configurado para aceitar qualquer origem (`allow_origins=["*"]`)
- Necessário para GitHub Pages acessar Render

### Imports Compatíveis
- `main.py` usa try/except para imports
- Funciona tanto rodando direto quanto via uvicorn
- Funciona local e no Render

---

**Última atualização:** 12/12/2025  
**Versão do sistema:** 0.4.0
