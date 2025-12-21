# 🏗️ Arquitetura Técnica - BO Inteligente

**Versão:** v0.8.0
**Última atualização:** 21/12/2025

Este documento detalha a arquitetura técnica do sistema, componentes, fluxos de dados e estruturas internas.

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Stack Tecnológica](#-stack-tecnológica)
- [Módulos Backend](#-módulos-backend)
- [Estruturas de Dados](#-estruturas-de-dados)
- [Fluxos de Dados](#-fluxos-de-dados)
- [Banco de Dados](#-banco-de-dados)
- [Integração LLM](#-integração-llm)
- [Fast-Start para E2E Tests](#-fast-start-para-e2e-tests)

---

## 🎯 Visão Geral

```
┌─────────────────────────────────────────────────────────────────┐
│                         USUÁRIO                                  │
│                  (Navegador Web/Mobile)                          │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    GITHUB PAGES                                  │
│              docs/index.html + docs/logs.html                    │
│              (Frontend Estático - Vanilla JS)                    │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTPS (Fetch API)
                          │ POST /new_session
                          │ POST /chat
                          │ POST /start_section/{n}
                          │ POST /sync_session
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                       RENDER                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │               FastAPI (backend/main.py)                  │    │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐     │    │
│  │  │state_machine │ │  validator   │ │ llm_service  │     │    │
│  │  │  (Seção 1)   │ │  (Seção 1)   │ │(Gemini+Groq) │     │    │
│  │  └──────────────┘ └──────────────┘ └──────┬───────┘     │    │
│  │  ┌──────────────┐ ┌──────────────┐        │              │    │
│  │  │state_machine2│ │ validator2   │        │              │    │
│  │  │  (Seção 2)   │ │  (Seção 2)   │        │              │    │
│  │  └──────────────┘ └──────────────┘        │              │    │
│  │  ┌──────────────────────────────────────────────────┐   │    │
│  │  │              logger.py (BOLogger)                 │   │    │
│  │  └──────────────────────┬───────────────────────────┘   │    │
│  └─────────────────────────┼───────────────────────────────┘    │
│                            │                                     │
│  ┌─────────────────────────▼───────────────────────────────┐    │
│  │              PostgreSQL (Produção)                       │    │
│  │           SQLite (Desenvolvimento Local)                 │    │
│  │    (bo_sessions, bo_events, feedbacks)                   │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    GOOGLE AI STUDIO                              │
│                  Gemini 2.5 Flash API                            │
│                (20 requisições/dia - free tier)                  │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      GROQ CLOUD                                  │
│                  Llama 3.3 70B Instruct                          │
│              (14.400 requisições/dia - free tier)                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Stack Tecnológica

### Backend

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| **Python** | 3.13 | Linguagem principal |
| **FastAPI** | 0.115+ | Framework web ASGI |
| **SQLAlchemy** | 2.0+ | ORM para banco de dados |
| **PostgreSQL** | 15+ | Banco de dados (produção) |
| **SQLite** | 3.x | Banco de dados (local) |
| **Uvicorn** | 0.32+ | Servidor ASGI |
| **python-dotenv** | 1.0+ | Gerenciamento de variáveis de ambiente |
| **Gemini SDK** | - | Cliente para Google AI Studio |
| **Groq SDK** | - | Cliente para Groq Cloud |

### Frontend

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| **HTML5** | - | Estrutura |
| **JavaScript** | ES6+ | Lógica (vanilla, sem frameworks) |
| **Tailwind CSS** | 3.x | Estilização (via CDN) |
| **Fetch API** | - | Requisições HTTP |
| **localStorage** | - | Sistema de rascunhos |

### Infraestrutura

| Serviço | Plano | Uso |
|---------|-------|-----|
| **Render** | Free | Backend + PostgreSQL |
| **GitHub Pages** | Free | Frontend estático |
| **GitHub** | Free | Controle de versão |

---

## 🐍 Módulos Backend

### 1. [main.py](../backend/main.py)

**Função:** API principal FastAPI - ponto de entrada do backend

**Responsabilidades:**
- Configurar aplicação FastAPI e CORS
- Definir todos os endpoints da API
- Gerenciar sessões em memória
- Orquestrar validação, geração de texto e logging

**Principais Endpoints:**

| Endpoint | Método | Função |
|----------|--------|--------|
| `/` | GET | Informações da API |
| `/health` | GET | Health check |
| `/new_session` | POST | Cria nova sessão |
| `/chat` | POST | Processa resposta do usuário |
| `/start_section/{section_number}` | POST | Inicia nova seção (ex: Seção 2) |
| `/sync_session` | POST | Sincroniza sessão em bloco (rascunhos) |
| `/chat/{session_id}/answer/{step}` | PUT | Edita resposta anterior |
| `/feedback` | POST | Registra feedback (👍👎) |
| `/api/stats` | GET | Estatísticas gerais |
| `/api/logs` | GET | Lista sessões |
| `/api/logs/{bo_id}` | GET | Detalhes de uma sessão |
| `/session/{session_id}` | DELETE | Deleta sessão |
| `/session/{session_id}/status` | GET | Status da sessão |

---

### 2. [state_machine.py](../backend/state_machine.py)

**Função:** Gerencia o fluxo de perguntas da Seção 1 (Contexto da Ocorrência)

**Responsabilidades:**
- Definir as 6 perguntas da Seção 1
- Controlar qual pergunta está ativa
- Armazenar respostas do usuário
- Verificar se seção está completa

**Perguntas (1.1-1.6):**

```python
QUESTIONS = {
    "1.1": "Dia, data e hora do acionamento.",
    "1.2": "Composição da guarnição e prefixo.",
    "1.3": "Natureza do empenho.",
    "1.4": "O que constava na ordem de serviço, informações do COPOM, DDU.",
    "1.5": "Local exato da ocorrência (logradouro, número, bairro).",
    "1.6": "O local é ponto de tráfico? Quais evidências anteriores? Há facção?"
}
```

**Principais Métodos:**

| Método | Retorno | Descrição |
|--------|---------|-----------|
| `get_current_question()` | str | Retorna texto da pergunta atual |
| `store_answer(answer)` | None | Armazena resposta para step atual |
| `next_step()` | None | Avança para próximo step |
| `is_section_complete()` | bool | Verifica se todas perguntas respondidas |
| `get_all_answers()` | Dict | Retorna todas as respostas |
| `get_progress()` | Dict | Retorna progresso (X/6, %) |

---

### 3. [state_machine_section2.py](../backend/state_machine_section2.py)

**Função:** Gerencia o fluxo de perguntas da Seção 2 (Abordagem a Veículo)

**Diferencial:** Suporta lógica condicional - se não houve veículo (pergunta 2.1 = "NÃO"), pula toda a seção.

**Perguntas (2.1-2.8):**

```python
SECTION2_QUESTIONS = {
    "2.1": "Havia veículo?",  # Condicional
    "2.2": "Marca/modelo/cor/placa.",
    "2.3": "Onde foi visto?",
    "2.4": "Qual policial percebeu e o que viu?",
    "2.5": "Como foi dada a ordem de parada?",
    "2.6": "Parou ou houve perseguição?",
    "2.7": "Como foi a abordagem e busca?",
    "2.8": "Haviam irregularidades? Veículo furtado/roubado/clonado?"
}
```

**Método Especial:**

| Método | Retorno | Descrição |
|--------|---------|-----------|
| `was_section_skipped()` | bool | Retorna True se não houve veículo |
| `get_skip_reason()` | Optional[str] | Texto explicativo se seção foi pulada |

---

### 4. [validator.py](../backend/validator.py)

**Função:** Valida respostas do usuário da Seção 1 antes de aceitar

**Regras de Validação:**

| Step | Validações | Exemplo Válido |
|------|------------|----------------|
| 1.1 | Data + hora + dia da semana válido | "22/03/2025, às 19h03, sexta-feira" |
| 1.2 | Mín 15 chars + palavra "prefixo" | "Sgt João e Cb Pedro, prefixo 1234" |
| 1.3 | Mín 10 chars + não só "tráfico" | "Tráfico de drogas em via pública" |
| 1.4 | Mín 20 chars + detalhes | "Denúncia via COPOM sobre venda de drogas" |
| 1.5 | Rua + número + bairro | "Rua X, nº 123, bairro Centro" |
| 1.6 | Mín 15 chars ou "NÃO" | "Sim, histórico de operações. Facção XYZ" |

**Validação Especial - Data/Hora (1.1):**
- Verifica presença de data (DD/MM/AAAA ou nome do mês)
- Verifica presença de hora (HH:MM ou HHhMM)
- Valida hora (0-23) e minuto (0-59)
- Rejeita datas futuras (exceto dia seguinte até 6h AM)
- Enriquece resposta com dia da semana e ano se ausentes

---

### 5. [validator_section2.py](../backend/validator_section2.py)

**Função:** Valida respostas do usuário da Seção 2

**Regras Específicas:**

| Step | Validações | Exemplo Válido |
|------|------------|----------------|
| 2.1 | Aceita "SIM", "NÃO" ou variações | "SIM" / "NÃO" / "Sim, havia um Gol" |
| 2.2 | Validação de placa Mercosul | "ABC1D23" ou "ABC-1D23" |
| 2.3 | Mín 10 chars + local específico | "Estacionado na Rua X, nº 123" |
| 2.4-2.8 | Mín 15-20 chars | Respostas descritivas |

**Validação de Placa Mercosul:**
```python
# Formato aceito: ABC1D23 ou ABC-1D23
# 3 letras + 1 número + 1 letra + 2 números
pattern = r"[A-Z]{3}-?[0-9][A-Z][0-9]{2}"
```

---

### 6. [llm_service.py](../backend/llm_service.py)

**Função:** Integração com provedores LLM para gerar textos de BO

**Arquitetura Multi-Provider:**

```python
class LLMService:
    def __init__(self):
        self.gemini_model = genai.GenerativeModel("gemini-2.0-flash-exp")
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.groq_model = "llama-3.3-70b-versatile"
```

**Método Principal:**

```python
def generate_text(
    self,
    answers: Dict[str, str],
    section: int = 1,
    provider: str = "gemini"  # ou "groq"
) -> str
```

**Fallback Automático:**
1. Tenta provider solicitado (Gemini ou Groq)
2. Se falhar, tenta provider alternativo
3. Se ambos falharem, retorna mensagem de erro

**Limites dos Provedores:**

| Provider | Modelo | Req/dia (free) | Req/min | Tokens/min |
|----------|--------|----------------|---------|------------|
| Gemini | 2.5 Flash | 20 | 15 | 1M |
| Groq | Llama 3.3 70B | 14.400 | 30 | 20k |

---

### 7. [logger.py](../backend/logger.py)

**Função:** Sistema de logging centralizado para rastreabilidade

**Responsabilidades:**
- Criar e gerenciar sessões (tabela `bo_sessions`)
- Logar eventos (tabela `bo_events`)
- Registrar feedbacks (tabela `feedbacks`)
- Fornecer queries para dashboard de logs

**Principais Métodos:**

| Método | Função |
|--------|--------|
| `create_session(ip, user_agent, version)` | Cria nova sessão e retorna `bo_id` |
| `log_event(bo_id, event_type, details)` | Registra evento (resposta, validação, geração) |
| `log_feedback(bo_id, message_id, feedback)` | Registra feedback 👍👎 |
| `complete_session(bo_id)` | Marca sessão como completa |
| `get_all_sessions(limit, offset)` | Lista sessões para dashboard |
| `get_session_details(bo_id)` | Detalhes completos de uma sessão |

---

## 📊 Estruturas de Dados

### Sessões em Memória (main.py)

**Estrutura (v0.5.0+):**

```python
sessions: Dict[str, Dict] = {
    "uuid-session-id": {
        "bo_id": "BO-20251220-a3f8c2e1",
        "sections": {
            1: BOStateMachine(),           # Seção 1: Contexto
            2: BOStateMachineSection2()    # Seção 2: Veículo (inicializado ao avançar)
        },
        "current_section": 1,               # Seção atual
        "section1_text": "",                # Texto gerado da Seção 1
        "section2_text": ""                 # Texto gerado da Seção 2
    }
}
```

**Nota Histórica:** Na v0.4.x, sessões eram tuplas `(bo_id, state_machine)`. Mudou para dict na v0.5.0 para suportar múltiplas seções.

---

### Rascunhos (localStorage - Frontend)

**Estrutura:**

```javascript
{
    "sessionId": "uuid",
    "boId": "BO-20251220-xxxxx",
    "sections": {
        "1": {
            "answers": {
                "1.1": "22/03/2025, às 19h03",
                "1.2": "Sgt João, prefixo 1234",
                // ...
            },
            "currentStep": "1.3",
            "completed": false,
            "generatedText": ""
        },
        "2": {
            "answers": { ... },
            "currentStep": "2.5",
            "completed": false,
            "generatedText": ""
        }
    },
    "currentSection": 1,
    "timestamp": 1703000000000,  // Para expiração (7 dias)
    "version": "0.8.0"
}
```

**Expiração:** 7 dias (604.800.000 ms)

---

## 🔄 Fluxos de Dados

### Fluxo 1: Criar Nova Sessão (`POST /new_session`)

```
┌──────────┐     1. POST /new_session     ┌──────────┐
│ Frontend │ ─────────────────────────────>│ Backend  │
└──────────┘                               └─────┬────┘
                                                 │
                                            2. Gerar session_id (UUID)
                                                 │
                                                 ▼
                                           ┌──────────────┐
                                           │ BOLogger     │
                                           │ .create_     │
                                           │ session()    │
                                           └──────┬───────┘
                                                  │
                                             3. Gerar bo_id
                                             4. INSERT INTO bo_sessions
                                             5. LOG event: session_started
                                                  │
                                                  ▼
┌──────────┐   6. Retorna {session_id,    ┌──────────┐
│ Frontend │ <────────────── bo_id,        │ Backend  │
└──────────┘        first_question}        └──────────┘
```

---

### Fluxo 2: Processar Resposta (`POST /chat`)

```
┌──────────┐   1. POST /chat              ┌──────────┐
│ Frontend │   {session_id, message}      │ Backend  │
└──────────┘ ───────────────────────────> └─────┬────┘
                                                 │
                                            2. Recuperar session
                                                 │
                                                 ▼
                                           ┌──────────────┐
                                           │ Validator    │
                                           │ .validate()  │
                                           └──────┬───────┘
                                                  │
                                         ┌────────┴────────┐
                                    INVÁLIDA         VÁLIDA
                                         │                │
                                         ▼                ▼
                                   ┌──────────┐    ┌──────────────┐
                                   │ Retorna  │    │StateMachine  │
                                   │ erro     │    │.store_answer │
                                   └──────────┘    │.next_step    │
                                                   └──────┬───────┘
                                                          │
                                                    ┌─────┴──────┐
                                               INCOMPLETO  COMPLETO
                                                    │           │
                                                    ▼           ▼
                                            ┌──────────┐  ┌──────────┐
                                            │ Próxima  │  │ LLMService
                                            │ pergunta │  │ .generate_
                                            └──────────┘  │ text()   │
                                                          └─────┬────┘
                                                                │
                                                                ▼
┌──────────┐   3. Retorna {question/text}  ┌──────────┐
│ Frontend │ <────────────────────────────  │ Backend  │
└──────────┘                                └──────────┘
```

---

### Fluxo 3: Iniciar Seção 2 (`POST /start_section/2`)

```
┌──────────┐   1. POST /start_section/2   ┌──────────┐
│ Frontend │   {session_id}                │ Backend  │
└──────────┘ ───────────────────────────> └─────┬────┘
                                                 │
                                            2. Recuperar session
                                                 │
                                                 ▼
                                           ┌──────────────────┐
                                           │ Inicializar      │
                                           │ sections[2] =    │
                                           │ StateMachine2()  │
                                           └──────┬───────────┘
                                                  │
                                            3. Atualizar current_section = 2
                                                  │
                                                  ▼
┌──────────┐   4. Retorna {question: 2.1}  ┌──────────┐
│ Frontend │ <────────────────────────────  │ Backend  │
└──────────┘                                └──────────┘
```

---

### Fluxo 4: Sincronizar Rascunho (`POST /sync_session`)

**Objetivo:** Restaurar sessão completa do rascunho em 1 requisição (10x mais rápido que múltiplos `/chat`).

```
┌──────────┐   1. POST /sync_session       ┌──────────┐
│ Frontend │   {session_id, bo_id,          │ Backend  │
│          │    sections: {...}}            │          │
└──────────┘ ───────────────────────────> └─────┬────┘
                                                 │
                                            2. Criar nova sessão
                                                 │
                                                 ▼
                                           ┌──────────────────┐
                                           │ Loop por seções  │
                                           │ recebidas        │
                                           └──────┬───────────┘
                                                  │
                                            3. Para cada seção:
                                               - Inicializar StateMachine
                                               - Restaurar answers
                                               - Restaurar current_step
                                               - Restaurar generated_text
                                                  │
                                                  ▼
┌──────────┐   4. Retorna {success: true}  ┌──────────┐
│ Frontend │ <────────────────────────────  │ Backend  │
└──────────┘                                └──────────┘
```

---

## 🗄️ Banco de Dados

### Tabelas

#### 1. `bo_sessions` - Metadados das Sessões

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `bo_id` | String(50) PK | Identificador único (BO-YYYYMMDD-hash) |
| `created_at` | DateTime | Data/hora de criação (timezone Brasília) |
| `completed_at` | DateTime | Data/hora de conclusão (nullable) |
| `status` | String(20) | `active`, `completed`, `abandoned` |
| `app_version` | String(20) | Versão do app (ex: "0.8.0") |
| `ip_address` | String(50) | IP do cliente |
| `user_agent` | Text | User-Agent do navegador |

#### 2. `bo_events` - Log de Eventos

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | Integer PK | Autoincrement |
| `bo_id` | String(50) FK | Referência para `bo_sessions` |
| `timestamp` | DateTime | Data/hora do evento |
| `event_type` | String(50) | Tipo (session_started, answer_valid, etc) |
| `details` | JSON | Detalhes adicionais |

**Tipos de Eventos:**
- `session_started` - Sessão criada
- `answer_valid` - Resposta aceita
- `answer_invalid` - Resposta rejeitada
- `text_generated` - Texto gerado com sucesso
- `llm_error` - Erro ao gerar texto
- `session_completed` - Sessão finalizada

#### 3. `feedbacks` - Avaliações do Usuário

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | Integer PK | Autoincrement |
| `bo_id` | String(50) FK | Referência para `bo_sessions` |
| `message_id` | String(100) | ID da mensagem avaliada |
| `feedback_type` | String(10) | `positive` (👍) ou `negative` (👎) |
| `timestamp` | DateTime | Data/hora do feedback |

---

### Consultas Úteis

**Listar sessões recentes:**
```sql
SELECT bo_id, created_at, completed_at, status
FROM bo_sessions
ORDER BY created_at DESC
LIMIT 20;
```

**Eventos de uma sessão:**
```sql
SELECT timestamp, event_type, details
FROM bo_events
WHERE bo_id = 'BO-20251220-xxxxx'
ORDER BY timestamp ASC;
```

**Taxa de conclusão:**
```sql
SELECT
    COUNT(*) as total,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
    ROUND(100.0 * SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) / COUNT(*), 2) as completion_rate
FROM bo_sessions;
```

---

## 🤖 Integração LLM

### Gemini 2.5 Flash

**Configuração:**

```python
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash-exp")
```

**Prompt Template (Seção 1):**

```python
prompt = f"""Você é um assistente especializado em redação de Boletins de Ocorrência policial...

IMPORTANTE:
- Escreva em 3ª pessoa (não use "eu")
- Seja factual e objetivo
- Não invente informações
- Use linguagem técnica policial

RESPOSTAS DO USUÁRIO:
{formatted_answers}

REDIJA O TEXTO DO BOLETIM:
"""
```

**Geração:**

```python
response = model.generate_content(prompt)
generated_text = response.text
```

---

### Groq Llama 3.3 70B

**Configuração:**

```python
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
```

**Geração:**

```python
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": "Você é um assistente..."},
        {"role": "user", "content": formatted_answers}
    ],
    temperature=0.7,
    max_tokens=2000
)
generated_text = response.choices[0].message.content
```

---

### Estratégia de Fallback

```python
def generate_text(self, answers, section=1, provider="gemini"):
    try:
        if provider == "gemini":
            return self._generate_with_gemini(answers, section)
        elif provider == "groq":
            return self._generate_with_groq(answers, section)
    except Exception as e:
        # Tenta provider alternativo
        alternative = "groq" if provider == "gemini" else "gemini"
        try:
            return self.generate_text(answers, section, alternative)
        except:
            return "Erro: Ambos os provedores LLM falharam."
```

---

## ⚡ Fast-Start para E2E Tests

### Motivação (v0.7.1)

A automação E2E original (`automate_release.py`) preenchia seções visualmente via Playwright, levando **~5 minutos**. Com a adição da Seção 3, isso se tornou impraticável para testes iterativos. A solução implementa um "fast-start" que:

1. **Preenche seções anteriores via API** (`/sync_session`) - sem abrir navegador
2. **Injeta estado via JavaScript** - sem modal de draft recovery
3. **Economiza 70% do tempo** - apenas 1.5 min para Seção 3

### Arquitetura

```
┌──────────────────────────────────────────────────────┐
│  automate_release.py --start-section 3 --no-video    │
└───────────────────┬──────────────────────────────────┘
                    │
        ┌───────────▼────────────────┐
        │ prepare_sections_via_api() │
        │ (sem navegador, apenas API)│
        └────┬──────────────────┬────┘
             │                  │
             ▼                  ▼
        /new_session      /sync_session
        (cria sessão)     (Seção 1 + 2)
             │                  │
             └───────┬──────────┘
                     ▼
            Backend: estado completo
            (sessions em memória/BD)
                     │
                     │ Navegador abre aqui (inicia vídeo)
                     ▼
        ┌──────────────────────────────┐
        │ inject_session_and_restore() │
        │ (JavaScript injection)        │
        └──────────────┬───────────────┘
                       │
              ┌────────┴────────┐
              ▼                 ▼
        Cria botão         Atualiza
        "Iniciar Seção 3"  sidebar
              │                 │
              └────────┬────────┘
                       ▼
            UI pronta para Seção 3
            (screenshots começam aqui)
```

### Componentes

#### 1. `prepare_sections_via_api(up_to_section: int)`

```python
async def prepare_sections_via_api(self, up_to_section: int):
    """
    Preenche Seções 1 até up_to_section via API.
    - Chama /new_session para criar nova sessão
    - Extrai respostas do test_scenarios.json
    - Chama /sync_session com todas as respostas
    - Não abre navegador
    """
```

**Fluxo:**
1. Lê `test_scenarios.json` e extrai steps até `up_to_section`
2. Trata IDs especiais: `_retry`, `edit_X_success` → extrai ID real
3. Filtra apenas respostas com `expect: "pass"`
4. Cria nova sessão via `/new_session` (retorna `session_id`)
5. Chama `/sync_session` com todas as respostas
6. Retorna `session_id` para próxima etapa

**Economia:**
- Seção 1: 2 min → 0 seg (não abre navegador)
- Seção 2: 2 min → 0 seg (não abre navegador)
- Total: 4 min → 0 seg ✅

#### 2. `inject_session_and_restore(page: Page, session_id: str, up_to_section: int)`

```python
async def inject_session_and_restore(self, page: Page, session_id: str, up_to_section: int):
    """
    Injeta estado da sessão via JavaScript.
    - Chama /sync_session no contexto do navegador
    - Cria botão "Iniciar Seção X" dinamicamente
    - Atualiza sidebar com seções completadas
    - Desabilita chat input para seções preenchidas
    """
```

**Fluxo:**
1. Abre página (`page.goto()`) - inicia vídeo neste ponto
2. Aguarda elemento principal carregar
3. Executa JavaScript para:
   - Chamar `/sync_session` internamente
   - Limpar chat messages
   - Criar botão "Iniciar Seção X"
   - Atualizar classes `.sidebar-section` com `.completed`
   - Desabilitar `#chat-input`
4. Aguarda botão aparecer
5. Clica em botão para iniciar seção alvo

**Implementação JavaScript:**
```javascript
// Executado no contexto do navegador
const response = await fetch('/sync_session', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id, answers })
});
// Limpa UI, cria botão, atualiza sidebar...
```

### Fluxos de Dados

#### Fluxo Completo (--start-section 3 --no-video)

```
Test Scenario JSON
     │
     ├─ Section 1 (steps 1.1-1.6)
     ├─ Section 2 (steps 2.1-2.8)
     └─ Section 3 (steps 3.1-3.8) ← alvo

            │
            ▼ prepare_sections_via_api(3)

    POST /new_session
    └─ Response: { session_id: "abc123" }

    POST /sync_session
    ├─ Body: { session_id, answers: { "1.1": "...", "2.1": "...", ... } }
    └─ Response: { status: "ok" }

            │
            ▼ inject_session_and_restore(page, "abc123", 3)

    page.goto(http://localhost:3000)
    │ ← inicia vídeo aqui
    ├─ JavaScript injection
    ├─ POST /sync_session (no browser context)
    ├─ Cria botão "Iniciar Seção 3"
    ├─ Click botão
    │
    └─ Seção 3 começa
       ├─ Screenshot 1: 3.1
       ├─ Screenshot 2: 3.2
       └─ ... até 3.8
```

### Tempo de Execução

| Etapa | Tempo | Notas |
|-------|-------|-------|
| `prepare_sections_via_api(3)` | 5-10s | Apenas API, sem navegador |
| `page.goto()` | 3s | Abre navegador, inicia vídeo |
| `inject_session_and_restore()` | 2-3s | JavaScript + restauração |
| **Seção 3 screenshots** | 60-90s | User interactions |
| **Total (--start-section 3)** | **~2 min** | **70% mais rápido** |

### Fallbacks e Erro Handling

- Se `prepare_sections_via_api()` falhar:
  - Loga erro mas continua
  - Abre navegador mesmo assim (pode estar vazio)
  - User pode preencher manualmente

- Se `inject_session_and_restore()` falhar:
  - Continua automação normal (sem fast-start)
  - Trata como seção nova

### Limitações

1. **Sem vídeo de seções anteriores** - Vídeo começa apenas na seção alvo
   - Caso de uso: Testar apenas nova seção
   - Se precisar vídeo completo: usar `--start-section 1` (padrão)

2. **Sem screenshots de seções anteriores** - Screenshots começam apenas na seção alvo
   - Caso de uso: Iteração rápida em nova feature
   - Se precisar all screenshots: usar `--start-section 1` (padrão)

3. **Requer `/sync_session` endpoint** - Não funciona sem este endpoint
   - Implementado em v0.6.4

---

## 🔗 Documentação Relacionada

- [README.md](../README.md) - Visão geral do projeto
- [DEVELOPMENT.md](../DEVELOPMENT.md) - Guia de desenvolvimento
- [SETUP.md](SETUP.md) - Setup e deploy
- [API.md](API.md) - Referência de endpoints
- [TESTING.md](TESTING.md) - Guia de testes (inclui flag `--start-section`)
- [ROADMAP.md](ROADMAP.md) - Planejamento futuro

---

## 👥 Créditos

- **Cristiano Maia** - Delivery Manager & Tech Lead
- **Claudio Moreira** - Especialista em Redação de BOs (Sargento PM)
- **Claude Sonnet 4.5** - Implementação via Claude Code
