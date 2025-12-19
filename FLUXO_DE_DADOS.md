# Diagrama Completo de Fluxo de Dados - BO Inteligente

## Visão Geral do Sistema

O sistema funciona através de 5 módulos Python principais que interagem com 2 bancos de dados (SQLite local / PostgreSQL produção).

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (index.html)                    │
│                    JavaScript Vanilla + Fetch API                │
└─────────────────────────────────────────────────────────────────┘
                                    │
                          HTTP POST /new_session
                          HTTP POST /chat
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND - FastAPI (main.py)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ state_machine│  │  validator   │  │ llm_service  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                          │                                        │
│                    ┌──────────┐                                  │
│                    │  logger  │                                  │
│                    └──────────┘                                  │
└─────────────────────────────────────────────────────────────────┘
                          │                     │
                          ▼                     ▼
              ┌──────────────────┐    ┌──────────────────┐
              │  Database        │    │  Gemini 2.5 API  │
              │  (SQLite/PG)     │    │  (Google Cloud)  │
              └──────────────────┘    └──────────────────┘
```

---

## FLUXO 1: `/new_session` - Criar Nova Sessão

### 1.1 Frontend → Backend (HTTP POST)

**Arquivo:** `docs/index.html` (linhas 460-520)

```javascript
// Dados enviados
fetch('https://bo-assistant-backend.onrender.com/new_session', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
})
```

**Dados no request:**
```json
{
  // Vazio - apenas POST sem body
  // Headers: IP, User-Agent são capturados pelo FastAPI
}
```

---

### 1.2 Backend: Endpoint `/new_session`

**Arquivo:** `backend/main.py` (linhas 99-137)

**Função chamada:** `new_session(request: Request)`

#### Passo 1: Gerar session_id (UUID)

```python
# main.py linha 105
import uuid
session_id = str(uuid.uuid4())
# Exemplo: "3e4f5a6b-7c8d-9e0f-1a2b-3c4d5e6f7a8b"
```

#### Passo 2: Capturar metadados HTTP

```python
# main.py linhas 79-81, 108-109
def get_client_ip(request: Request) -> str:
    return request.headers.get("X-Forwarded-For", request.client.host)

ip_address = get_client_ip(request)          # Ex: "177.12.34.56"
user_agent = request.headers.get("User-Agent")  # Ex: "Mozilla/5.0..."
```

#### Passo 3: Criar sessão no banco via `BOLogger.create_session()`

**Arquivo:** `backend/logger.py` (linhas 142-167)

```python
# main.py linha 110
bo_id = BOLogger.create_session(
    ip_address=ip_address,
    user_agent=user_agent,
    app_version=APP_VERSION  # "0.4.0"
)
```

**O que `BOLogger.create_session()` faz:**

1. **Gera `bo_id` único:**
   ```python
   # logger.py linha 147
   bo_id = f"BO-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"
   # Exemplo: "BO-20251215-a3f8c2e1"
   ```

2. **Insere registro na tabela `bo_sessions`:**
   ```python
   # logger.py linhas 150-158
   with get_db() as db:
       session = BOSession(
           bo_id=bo_id,
           ip_address=ip_address,
           user_agent=user_agent,
           app_version=app_version,
           status="active"
       )
       db.add(session)
       db.commit()
   ```

   **Estrutura da tabela `bo_sessions` (linhas 48-68):**
   ```python
   class BOSession(Base):
       bo_id = Column(String(50), primary_key=True)
       created_at = Column(DateTime, default=lambda: datetime.now(BRASILIA_TZ))
       completed_at = Column(DateTime, nullable=True)
       status = Column(String(20), default="active")  # active/completed/abandoned
       app_version = Column(String(20), nullable=True)
       ip_address = Column(String(50), nullable=True)
       user_agent = Column(Text, nullable=True)
   ```

3. **Loga evento `session_started` na tabela `bo_events`:**
   ```python
   # logger.py linhas 161-165
   BOLogger.log_event(
       bo_id=bo_id,
       event_type="session_started",
       data={"ip": ip_address, "app_version": app_version}
   )
   ```

   **Dentro de `log_event()` (linhas 170-187):**
   ```python
   event_id = f"evt_{uuid.uuid4().hex[:8]}"  # Ex: "evt_7b2c4a5e"

   with get_db() as db:
       event = BOEvent(
           event_id=event_id,
           bo_id=bo_id,
           event_type="session_started",
           data={"ip": "177.12.34.56", "app_version": "0.4.0"}
       )
       db.add(event)
       db.commit()
   ```

   **Estrutura da tabela `bo_events` (linhas 71-88):**
   ```python
   class BOEvent(Base):
       event_id = Column(String(50), primary_key=True)
       bo_id = Column(String(50), nullable=False)
       timestamp = Column(DateTime, default=lambda: datetime.now(BRASILIA_TZ))
       event_type = Column(String(50), nullable=False)
       data = Column(JSON, nullable=True)
   ```

**Retorna:** `bo_id` (String)

---

#### Passo 4: Criar máquina de estados (`BOStateMachine`)

**Arquivo:** `backend/state_machine.py` (linhas 22-25)

```python
# main.py linha 117
state_machine = BOStateMachine()

# state_machine.py __init__
def __init__(self):
    self.current_step = "1.1"  # Primeira pergunta
    self.answers = {}          # Dict vazio para armazenar respostas
    self.step_index = 0        # Índice atual no array STEPS
```

**Constantes importantes (linhas 10-20):**
```python
QUESTIONS = {
    "1.1": "Dia, data e hora do acionamento.",
    "1.2": "Composição da guarnição e prefixo.",
    "1.3": "Natureza do empenho.",
    "1.4": "O que constava na ordem de serviço, informações do COPOM, DDU.",
    "1.5": "Local exato da ocorrência (logradouro, número, bairro).",
    "1.6": "O local é ponto de tráfico? Quais evidências anteriores? Há facção?"
}

STEPS = ["1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "complete"]
```

#### Passo 5: Armazenar sessão em memória

```python
# main.py linha 118
sessions[session_id] = (bo_id, state_machine)

# sessions é um Dict global definido na linha 40:
# sessions: Dict[str, tuple] = {}
# Estrutura: {session_id: (bo_id, state_machine_instance)}
```

#### Passo 6: Obter primeira pergunta

```python
# main.py linha 121
first_question = state_machine.get_current_question()
```

**Função `get_current_question()` em `state_machine.py` (linhas 27-34):**
```python
def get_current_question(self) -> str:
    if self.current_step == "complete":
        return "Seção 1 completa!"

    return self.QUESTIONS.get(self.current_step, "Erro: pergunta não encontrada")
    # Retorna: "Dia, data e hora do acionamento."
```

#### Passo 7: Logar evento `question_asked`

```python
# main.py linhas 124-131
BOLogger.log_event(
    bo_id=bo_id,
    event_type="question_asked",
    data={
        "step": state_machine.current_step,  # "1.1"
        "question": first_question           # "Dia, data e hora do acionamento."
    }
)
```

**Inserido no banco:**
```sql
INSERT INTO bo_events (event_id, bo_id, timestamp, event_type, data)
VALUES ('evt_9a3b5c2d', 'BO-20251215-a3f8c2e1', '2025-12-15 14:30:00', 'question_asked',
        '{"step": "1.1", "question": "Dia, data e hora do acionamento."}')
```

#### Passo 8: Retornar resposta HTTP

```python
# main.py linhas 133-137
return NewSessionResponse(
    session_id=session_id,  # UUID
    bo_id=bo_id,            # BO-20251215-a3f8c2e1
    first_question=first_question  # "Dia, data e hora do acionamento."
)
```

**Estrutura do Pydantic Model (linhas 58-61):**
```python
class NewSessionResponse(BaseModel):
    session_id: str
    bo_id: str
    first_question: str
```

### 1.3 Frontend recebe resposta

**JSON retornado:**
```json
{
  "session_id": "3e4f5a6b-7c8d-9e0f-1a2b-3c4d5e6f7a8b",
  "bo_id": "BO-20251215-a3f8c2e1",
  "first_question": "Dia, data e hora do acionamento."
}
```

**Frontend exibe a pergunta no chat.**

---

## FLUXO 2: `/chat` - Processar Resposta do Usuário

### 2.1 Frontend → Backend (HTTP POST)

**Arquivo:** `docs/index.html` (linhas 880-920)

```javascript
// Usuário digita: "22/03/2025, às 19h03"
fetch('https://bo-assistant-backend.onrender.com/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        session_id: currentSessionId,  // UUID da sessão
        message: userMessage,           // "22/03/2025, às 19h03"
        llm_provider: 'gemini'          // Sempre 'gemini'
    })
})
```

**Dados no request:**
```json
{
  "session_id": "3e4f5a6b-7c8d-9e0f-1a2b-3c4d5e6f7a8b",
  "message": "22/03/2025, às 19h03",
  "llm_provider": "gemini"
}
```

---

### 2.2 Backend: Endpoint `/chat`

**Arquivo:** `backend/main.py` (linhas 139-263)

**Função chamada:** `chat(request_body: ChatRequest, request: Request)`

#### Passo 1: Extrair dados do request

```python
# main.py linhas 142-143
session_id = request_body.session_id
# "3e4f5a6b-7c8d-9e0f-1a2b-3c4d5e6f7a8b"
```

**Estrutura do Pydantic Model `ChatRequest` (linhas 43-46):**
```python
class ChatRequest(BaseModel):
    session_id: str
    message: str
    llm_provider: Optional[str] = "gemini"
```

#### Passo 2: Recuperar sessão da memória

```python
# main.py linhas 145-146
if session_id not in sessions:
    raise HTTPException(status_code=404, detail="Sessão não encontrada")

# main.py linha 148
bo_id, state_machine = sessions[session_id]
# bo_id = "BO-20251215-a3f8c2e1"
# state_machine = instância da BOStateMachine com current_step="1.1"
```

#### Passo 3: Obter step atual

```python
# main.py linha 149
current_step = state_machine.current_step  # "1.1"
```

---

### 2.3 Validação da Resposta (`ResponseValidator`)

**Arquivo:** `backend/validator.py`

#### Passo 4: Validar resposta

```python
# main.py linhas 152-155
is_valid, error_message = ResponseValidator.validate(
    current_step,           # "1.1"
    request_body.message    # "22/03/2025, às 19h03"
)
```

**Função `validate()` em `validator.py` (linhas 51-177):**

##### Sub-passo 4.1: Verificar resposta vazia

```python
# validator.py linhas 60-64
answer = answer.strip()  # "22/03/2025, às 19h03"

if not answer or len(answer) < 3:
    return False, "Por favor, forneça uma resposta. Se não se aplica, escreva 'NÃO'."
```

##### Sub-passo 4.2: Verificar respostas "NÃO" ou "SIM"

```python
# validator.py linhas 67-78
if answer.upper() == "NÃO":
    if step in ["1.6"]:  # Histórico pode ser NÃO
        return True, None
    else:
        return False, "Esta pergunta é obrigatória. 'NÃO' não é uma resposta válida aqui."

if answer.upper() == "SIM":
    if step in ["1.6"]:
        return False, "Se sim, forneça detalhes: quantas operações anteriores? Qual facção?..."
    else:
        return False, "Esta pergunta exige detalhes. 'SIM' sozinho não é suficiente."
```

##### Sub-passo 4.3: Buscar regras específicas do step

```python
# validator.py linhas 81-83
rules = ResponseValidator.VALIDATION_RULES.get(step)
if not rules:
    return True, None  # Sem regras específicas, aceitar
```

**Regras para step "1.1" (linhas 12-17):**
```python
VALIDATION_RULES = {
    "1.1": {
        "min_length": 10,
        "custom_check": "datetime",  # Validação especial
        "examples": ["22/03/2025, às 19h03", "15 de março de 2024, 14h30"],
        "error_message": "Por favor, informe dia, data E hora completos. Ex: '22/03/2025, às 19h03'"
    },
    # ... outras regras para 1.2, 1.3, 1.4, 1.5, 1.6
}
```

##### Sub-passo 4.4: Validar tamanho mínimo

```python
# validator.py linhas 86-87
if len(answer) < rules.get("min_length", 0):  # 10
    return False, rules.get("error_message", "Resposta muito curta...")
# len("22/03/2025, às 19h03") = 21 ✅ OK
```

##### Sub-passo 4.5: Validação customizada para datetime (step 1.1)

```python
# validator.py linhas 90-148
if rules.get("custom_check") == "datetime":
    import re
    from datetime import datetime as dt, timedelta
```

**4.5.1 - Verificar formato de data:**
```python
# linhas 95-101
has_date = "/" in answer or any(mes in answer.lower() for mes in [
    "janeiro", "fevereiro", "março", "marco", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
])

if not has_date:
    return False, "Faltou a data. " + rules.get("error_message")
# "/" encontrado em "22/03/2025" ✅ OK
```

**4.5.2 - Verificar formato de horário:**
```python
# linhas 104-107
time_match = re.search(r'(\d{1,2})[h:](\d{0,2})', answer)
# Match: group(1)="19", group(2)="03"

if not time_match:
    return False, "Faltou o horário. " + rules.get("error_message")
# ✅ OK - encontrou "19h03"
```

**4.5.3 - Validar hora e minuto:**
```python
# linhas 110-118
hour = int(time_match.group(1))    # 19
minute_str = time_match.group(2)   # "03"
minute = int(minute_str) if minute_str else 0  # 3

if hour > 23:
    return False, f"Hora inválida ({hour}h). Use formato 24h (0-23)..."

if minute > 59:
    return False, f"Minuto inválido ({minute}min). Use 0-59..."
# ✅ OK - 19 <= 23, 3 <= 59
```

**4.5.4 - Validar data (dia/mês/ano):**
```python
# linhas 121-140
date_match = re.search(r'(\d{1,2})/(\d{1,2})(?:/(\d{4}))?', answer)
# Match: group(1)="22", group(2)="03", group(3)="2025"

if date_match:
    day = int(date_match.group(1))    # 22
    month = int(date_match.group(2))  # 3
    year = int(date_match.group(3)) if date_match.group(3) else dt.now().year  # 2025

    # Validar mês
    if month < 1 or month > 12:
        return False, f"Mês inválido ({month}). Use 1-12..."

    # Validar data usando datetime (valida automaticamente dias por mês)
    try:
        input_date = dt(year, month, day, hour, minute)
        # dt(2025, 3, 22, 19, 3) ✅ OK
    except ValueError:
        return False, f"Data inválida ({day}/{month:02d}/{year}). Verifique o dia..."

    # Validar se data/hora não é futura (margem de 5 minutos)
    now = dt.now() + timedelta(minutes=5)
    if input_date > now:
        return False, "Data/hora futura não permitida. A ocorrência deve ter acontecido no passado."
```

**4.5.5 - Retornar validação bem-sucedida:**
```python
# linha 148
return True, None
```

**Resultado:**
```python
is_valid = True
error_message = None
```

---

#### Passo 5: Logar evento `answer_submitted`

```python
# main.py linhas 158-166
event_id = BOLogger.log_event(
    bo_id=bo_id,                    # "BO-20251215-a3f8c2e1"
    event_type="answer_submitted",
    data={
        "step": current_step,       # "1.1"
        "answer": request_body.message,  # "22/03/2025, às 19h03"
        "is_valid": is_valid        # True
    }
)
# Retorna: event_id (ex: "evt_4b8c9a3e")
```

**Inserido no banco:**
```sql
INSERT INTO bo_events (event_id, bo_id, timestamp, event_type, data)
VALUES ('evt_4b8c9a3e', 'BO-20251215-a3f8c2e1', '2025-12-15 14:31:05', 'answer_submitted',
        '{"step": "1.1", "answer": "22/03/2025, às 19h03", "is_valid": true}')
```

---

#### Passo 6: Caso inválido - Retornar erro

```python
# main.py linhas 168-188
if not is_valid:
    # Log adicional: erro de validação
    BOLogger.log_event(
        bo_id=bo_id,
        event_type="validation_error",
        data={
            "step": current_step,
            "answer": request_body.message,
            "error_message": error_message
        }
    )

    return ChatResponse(
        session_id=session_id,
        bo_id=bo_id,
        question=state_machine.get_current_question(),  # Mesma pergunta
        is_section_complete=False,
        current_step=current_step,
        validation_error=error_message,  # Erro para exibir no frontend
        event_id=event_id
    )
```

**⚠️ Neste caso (is_valid=True), este bloco NÃO é executado.**

---

#### Passo 7: Armazenar resposta válida na state machine

```python
# main.py linhas 191-192
state_machine.store_answer(request_body.message)
state_machine.next_step()
```

**Função `store_answer()` em `state_machine.py` (linhas 36-41):**
```python
def store_answer(self, answer: str) -> None:
    if self.current_step != "complete":
        self.answers[self.current_step] = answer.strip()
        # self.answers["1.1"] = "22/03/2025, às 19h03"
```

**Função `next_step()` em `state_machine.py` (linhas 43-49):**
```python
def next_step(self) -> None:
    if self.step_index < len(self.STEPS) - 1:  # 0 < 6
        self.step_index += 1           # step_index = 1
        self.current_step = self.STEPS[self.step_index]  # "1.2"
```

**Estado da state machine após execução:**
```python
{
    "current_step": "1.2",
    "step_index": 1,
    "answers": {
        "1.1": "22/03/2025, às 19h03"
    }
}
```

---

#### Passo 8: Verificar se seção está completa

```python
# main.py linha 195
if state_machine.is_section_complete():
    # Gerar texto do BO
```

**Função `is_section_complete()` em `state_machine.py` (linhas 51-55):**
```python
def is_section_complete(self) -> bool:
    return self.current_step == "complete"
    # Neste caso: "1.2" != "complete" → False
```

**⚠️ Como retorna False, o bloco de geração de texto (linhas 196-241) NÃO é executado ainda.**

---

#### Passo 9: Obter próxima pergunta

```python
# main.py linha 244
next_question = state_machine.get_current_question()
# Retorna: "Composição da guarnição e prefixo."
```

#### Passo 10: Logar evento `question_asked`

```python
# main.py linhas 247-254
BOLogger.log_event(
    bo_id=bo_id,
    event_type="question_asked",
    data={
        "step": state_machine.current_step,  # "1.2"
        "question": next_question            # "Composição da guarnição e prefixo."
    }
)
```

**Inserido no banco:**
```sql
INSERT INTO bo_events (event_id, bo_id, timestamp, event_type, data)
VALUES ('evt_2c9a4b5e', 'BO-20251215-a3f8c2e1', '2025-12-15 14:31:06', 'question_asked',
        '{"step": "1.2", "question": "Composição da guarnição e prefixo."}')
```

---

#### Passo 11: Retornar resposta HTTP

```python
# main.py linhas 256-263
return ChatResponse(
    session_id=session_id,           # UUID
    bo_id=bo_id,                     # "BO-20251215-a3f8c2e1"
    question=next_question,          # "Composição da guarnição e prefixo."
    is_section_complete=False,       # Ainda faltam perguntas
    current_step=state_machine.current_step,  # "1.2"
    event_id=event_id                # "evt_4b8c9a3e"
)
```

**Estrutura do Pydantic Model `ChatResponse` (linhas 48-56):**
```python
class ChatResponse(BaseModel):
    session_id: str
    bo_id: str
    question: Optional[str] = None
    generated_text: Optional[str] = None
    is_section_complete: bool = False
    current_step: str
    validation_error: Optional[str] = None
    event_id: Optional[str] = None
```

### 2.4 Frontend recebe resposta

**JSON retornado:**
```json
{
  "session_id": "3e4f5a6b-7c8d-9e0f-1a2b-3c4d5e6f7a8b",
  "bo_id": "BO-20251215-a3f8c2e1",
  "question": "Composição da guarnição e prefixo.",
  "generated_text": null,
  "is_section_complete": false,
  "current_step": "1.2",
  "validation_error": null,
  "event_id": "evt_4b8c9a3e"
}
```

**Frontend exibe a próxima pergunta (1.2) no chat.**

---

## FLUXO 3: Após 6 Perguntas - Geração de Texto do BO

### Cenário: Usuário respondeu todas as 6 perguntas

**Estado da state machine:**
```python
{
    "current_step": "complete",  # Avançou após responder 1.6
    "step_index": 6,
    "answers": {
        "1.1": "22/03/2025, às 19h03",
        "1.2": "Sgt João Silva e Cb Pedro Santos, prefixo 1234",
        "1.3": "Denúncia anônima via 190",
        "1.4": "COPOM reportou venda de drogas na esquina",
        "1.5": "Rua das Acácias, número 456, bairro Floresta",
        "1.6": "Sim, local com histórico de 3 operações em 2024. Facção ABC atua na região"
    }
}
```

---

### 3.1 Verificação de seção completa

```python
# main.py linha 195
if state_machine.is_section_complete():  # True!
```

---

### 3.2 Gerar texto com LLM

**Arquivo:** `backend/main.py` (linhas 196-241)

#### Passo 1: Marcar tempo inicial

```python
# main.py linha 198
start_time = datetime.now()
```

#### Passo 2: Chamar LLM Service

```python
# main.py linhas 200-203
generated_text = await llm_service.generate_section_text(
    section_data=state_machine.get_all_answers(),
    provider=request_body.llm_provider  # "gemini"
)
```

**Função `get_all_answers()` em `state_machine.py` (linhas 57-61):**
```python
def get_all_answers(self) -> Dict[str, str]:
    return self.answers
    # Retorna:
    # {
    #     "1.1": "22/03/2025, às 19h03",
    #     "1.2": "Sgt João Silva e Cb Pedro Santos, prefixo 1234",
    #     "1.3": "Denúncia anônima via 190",
    #     "1.4": "COPOM reportou venda de drogas na esquina",
    #     "1.5": "Rua das Acácias, número 456, bairro Floresta",
    #     "1.6": "Sim, local com histórico de 3 operações em 2024. Facção ABC"
    # }
```

---

### 3.3 Dentro do LLM Service

**Arquivo:** `backend/llm_service.py`

#### Função `generate_section_text()` (linhas 167-185)

```python
async def generate_section_text(
    self,
    section_data: Dict[str, str],
    provider: str = "gemini"
) -> str:
    if provider == "gemini":
        return self._generate_with_gemini(section_data)
    elif provider == "claude":
        raise NotImplementedError("Claude ainda não implementado")
    elif provider == "openai":
        raise NotImplementedError("OpenAI ainda não implementado")
    else:
        raise ValueError(f"Provider {provider} não suportado")
```

---

#### Função `_generate_with_gemini()` (linhas 187-206)

##### Sub-passo 1: Construir prompt

```python
# llm_service.py linha 195
prompt = self._build_prompt(section_data)
```

**Função `_build_prompt()` (linhas 82-165):**

**1. Enriquecer data/hora:**
```python
# linhas 93-94
datetime_raw = section_data.get("1.1", "Não informado")
# "22/03/2025, às 19h03"

datetime_enriched = self._enrich_datetime(datetime_raw)
```

**Função `_enrich_datetime()` (linhas 31-80):**
```python
# Extrair data
date_match = re.search(r'(\d{1,2})/(\d{1,2})(?:/(\d{4}))?', datetime_str)
# Match: day=22, month=03, year=2025

day = 22
month = 3
year = 2025

# Criar objeto datetime
date_obj = datetime(2025, 3, 22)  # Sábado

# Mapear dia da semana
weekdays = ['segunda-feira', 'terça-feira', 'quarta-feira',
           'quinta-feira', 'sexta-feira', 'sábado', 'domingo']
weekday = weekdays[date_obj.weekday()]  # "sábado"

# Mapear mês
months = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
         'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
month_name = months[month - 1]  # "março"

# Extrair hora
time_match = re.search(r'(\d{1,2})[h:](\d{0,2})', datetime_str)
# Match: hour=19, minute=03

hour = "19"
minute = "03"
time_str = f"às {hour}h{minute}min"  # "às 19h03min"

# Formato final
return f"{weekday}, {day} de {month_name} de {year}, {time_str}"
# Retorna: "sábado, 22 de março de 2025, às 19h03min"
```

**2. Montar texto das respostas:**
```python
# linhas 97-112
questions_map = {
    "1.1": "Dia, data e hora do acionamento",
    "1.2": "Composição da guarnição e prefixo",
    "1.3": "Natureza do empenho",
    "1.4": "Ordem de serviço / COPOM / DDU",
    "1.5": "Local exato da ocorrência",
    "1.6": "Histórico do local / facção"
}

answers_text = f"{questions_map['1.1']}: {datetime_enriched}\n"
# "Dia, data e hora do acionamento: sábado, 22 de março de 2025, às 19h03min\n"

for key, question in questions_map.items():
    if key == "1.1":
        continue  # Já adicionado
    answer = section_data.get(key, "Não informado")
    answers_text += f"{question}: {answer}\n"
```

**Resultado final do `answers_text`:**
```
Dia, data e hora do acionamento: sábado, 22 de março de 2025, às 19h03min
Composição da guarnição e prefixo: Sgt João Silva e Cb Pedro Santos, prefixo 1234
Natureza do empenho: Denúncia anônima via 190
Ordem de serviço / COPOM / DDU: COPOM reportou venda de drogas na esquina
Local exato da ocorrência: Rua das Acácias, número 456, bairro Floresta
Histórico do local / facção: Sim, local com histórico de 3 operações em 2024. Facção ABC atua na região
```

**3. Montar prompt completo:**
```python
# linhas 114-165
prompt = f"""Você é um assistente especializado em redigir Boletins de Ocorrência policiais de tráfico de drogas, seguindo o manual do Claudio Moreira.

Sua tarefa é gerar o texto da SEÇÃO 1 - CONTEXTO DA OCORRÊNCIA com base nas informações coletadas.

INFORMAÇÕES COLETADAS:
{answers_text}

⚠️ REGRA CRÍTICA - NUNCA INVENTAR INFORMAÇÕES:
- Use APENAS as informações fornecidas acima
- Se algo não foi informado, NÃO invente (número de OS, horário, endereço completo, etc)
- Se falta informação, use formulações genéricas: "a equipe foi acionada", "no local indicado"
- PROIBIDO inventar: números, nomes, horários, endereços, facções, prefixos

REGRAS DE REDAÇÃO (nunca violar):
1. Narração em 3ª pessoa, voz ativa, ordem direta
2. Frases curtas, estilo jornalístico, dois espaços entre frases
3. Norma culta - ZERO juridiquês, ZERO gerúndio, ZERO "linguagem policial"
4. PROIBIDO termos vazios: "em atitude suspeita", "resistiu ativamente", "movimentação típica"
5. Substituições obrigatórias: "veio a óbito"→"foi a óbito"; "caiu ao solo"→"caiu no chão"
6. Individualizar locais: use o endereço FORNECIDO, não invente números ou nomes
7. Evitar repetições: use pronomes ou sinônimos ("a guarnição", "os militares", "a equipe")

ESTRUTURA ESPERADA (baseada nos modelos do Claudio):
1. Início com contexto temporal: "Cumprindo a ordem de serviço, prevista para [dia da semana], [dia] de [mês] de [ano], por volta das [hora]h[min]min..."
2. Identificar equipe: "a equipe composta pelo [posto + nome]..." (ou "pelos [posto + nomes]" se múltiplos)
3. Se prefixo fornecido: "na viatura [prefixo]..."
4. Descrever acionamento: "foi acionada para...", "recebeu determinação para...", "foi empenhada para..."
5. Informar conteúdo da ordem: O que foi fornecido - use VARIAÇÃO: "A ordem indicava...", "Segundo a denúncia...", "O acionamento reportava..."
6. Detalhar local: Use EXATAMENTE o que foi fornecido - "O local indicado foi..." ou "no endereço..."
7. Histórico (se aplicável): "O endereço consta em registros anteriores..." ou "O local possui histórico..."

EXEMPLOS DE QUALIDADE (do manual do Claudio):

✅ CERTO (informações completas):
"Cumprindo a ordem de serviço nº 123/2024, prevista para sexta-feira, 15 de março de 2024, por volta das 14h30min, a equipe composta pelo Sgt João Silva e Cb Pedro Santos, na viatura prefixo 1234, foi acionada para atender ocorrência de tráfico de drogas.  A ordem de serviço indicava denúncia anônima via COPOM reportando comercialização de entorpecentes na Rua das Flores, número 123, bairro Centro, próximo ao Bar do João.  O endereço consta em registros e relatórios anteriores como ponto de tráfico e reincidência de denúncias.  Segundo as denúncias e boletins anteriores, trata-se de área sob influência da facção denominada XYZ."

✅ TAMBÉM CERTO (informações parciais - SEM INVENTAR):
"No dia 22 de março de 2025, a guarnição foi acionada via COPOM para atender denúncia anônima de tráfico de drogas.  O local indicado foi a Rua das Acácias, bairro Floresta.  O endereço possui histórico de operações anteriores relacionadas ao tráfico."

❌ ERRADO (inventou informações):
"No dia 22/03, às 14h30min..." (inventou horário)
"...ordem de serviço nº 123/2024..." (inventou número de OS)
"...número 456..." (inventou número do endereço)

FORMATO DE SAÍDA:
- Parágrafo corrido, SEM bullet points
- Dois espaços entre frases
- Completude: incluir elementos FORNECIDOS, sem inventar

GERE AGORA o texto da Seção 1 usando SOMENTE as informações fornecidas:"""
```

---

##### Sub-passo 2: Chamar Gemini API

```python
# llm_service.py linhas 198-199
response = self.gemini_model.generate_content(prompt)
```

**Configuração do modelo Gemini (linhas 24-27):**
```python
genai.configure(api_key=self.gemini_api_key)
# API Key do .env: [GEMINI_API_KEY_REDACTED]

self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
```

**🌐 Chamada HTTP para Google Gemini API:**
```
POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent
Headers:
  - Authorization: Bearer [GEMINI_API_KEY_REDACTED]
  - Content-Type: application/json

Body:
{
  "contents": [{
    "parts": [{
      "text": "[PROMPT COMPLETO DE 3000+ CARACTERES ACIMA]"
    }]
  }]
}
```

**Resposta do Gemini (exemplo):**
```json
{
  "candidates": [{
    "content": {
      "parts": [{
        "text": "No sábado, 22 de março de 2025, por volta das 19h03min, a equipe composta pelo Sgt João Silva e Cb Pedro Santos, na viatura prefixo 1234, foi acionada via 190 para atender denúncia anônima de tráfico de drogas.  O COPOM reportou venda de drogas na esquina do endereço indicado.  O local da ocorrência foi a Rua das Acácias, número 456, bairro Floresta.  O endereço possui histórico de 3 operações anteriores realizadas em 2024.  Segundo registros, a facção ABC atua na região."
      }]
    }
  }]
}
```

##### Sub-passo 3: Extrair texto gerado

```python
# llm_service.py linha 201
generated_text = response.text.strip()
# "No sábado, 22 de março de 2025, por volta das 19h03min..."

# linha 203
return generated_text
```

---

### 3.4 De volta ao endpoint `/chat`

#### Passo 3: Calcular tempo de geração

```python
# main.py linha 205
generation_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
# Exemplo: 2340 ms (2.34 segundos)
```

#### Passo 4: Logar evento `text_generated`

```python
# main.py linhas 208-217
BOLogger.log_event(
    bo_id=bo_id,
    event_type="text_generated",
    data={
        "llm_provider": request_body.llm_provider,  # "gemini"
        "generated_text": generated_text,
        "generation_time_ms": generation_time_ms,   # 2340
        "answers": state_machine.get_all_answers()  # Dict com 6 respostas
    }
)
```

**Inserido no banco:**
```sql
INSERT INTO bo_events (event_id, bo_id, timestamp, event_type, data)
VALUES ('evt_3a9b2c5d', 'BO-20251215-a3f8c2e1', '2025-12-15 14:35:12', 'text_generated',
        '{
          "llm_provider": "gemini",
          "generated_text": "No sábado, 22 de março de 2025...",
          "generation_time_ms": 2340,
          "answers": {
            "1.1": "22/03/2025, às 19h03",
            "1.2": "Sgt João Silva e Cb Pedro Santos, prefixo 1234",
            "1.3": "Denúncia anônima via 190",
            "1.4": "COPOM reportou venda de drogas na esquina",
            "1.5": "Rua das Acácias, número 456, bairro Floresta",
            "1.6": "Sim, local com histórico de 3 operações em 2024. Facção ABC"
          }
        }')
```

#### Passo 5: Atualizar status da sessão

```python
# main.py linha 220
BOLogger.update_session_status(bo_id, "completed")
```

**Função `update_session_status()` em `logger.py` (linhas 190-198):**
```python
def update_session_status(bo_id: str, status: str):
    with get_db() as db:
        session = db.query(BOSession).filter(BOSession.bo_id == bo_id).first()
        if session:
            session.status = status                # "completed"
            if status == "completed":
                session.completed_at = now_brasilia()  # "2025-12-15T14:35:12-03:00"
            db.commit()
```

**Atualizado no banco:**
```sql
UPDATE bo_sessions
SET status = 'completed',
    completed_at = '2025-12-15 14:35:12'
WHERE bo_id = 'BO-20251215-a3f8c2e1';
```

#### Passo 6: Retornar resposta HTTP

```python
# main.py linhas 222-229
return ChatResponse(
    session_id=session_id,
    bo_id=bo_id,
    generated_text=generated_text,  # Texto gerado pelo Gemini
    is_section_complete=True,       # ✅ Seção completa!
    current_step=state_machine.current_step,  # "complete"
    event_id=event_id
)
```

### 3.5 Frontend recebe texto final

**JSON retornado:**
```json
{
  "session_id": "3e4f5a6b-7c8d-9e0f-1a2b-3c4d5e6f7a8b",
  "bo_id": "BO-20251215-a3f8c2e1",
  "question": null,
  "generated_text": "No sábado, 22 de março de 2025, por volta das 19h03min, a equipe composta pelo Sgt João Silva e Cb Pedro Santos, na viatura prefixo 1234, foi acionada via 190 para atender denúncia anônima de tráfico de drogas.  O COPOM reportou venda de drogas na esquina do endereço indicado.  O local da ocorrência foi a Rua das Acácias, número 456, bairro Floresta.  O endereço possui histórico de 3 operações anteriores realizadas em 2024.  Segundo registros, a facção ABC atua na região.",
  "is_section_complete": true,
  "current_step": "complete",
  "validation_error": null,
  "event_id": "evt_3a9b2c5d"
}
```

**Frontend exibe o texto final do BO com botão de copiar.**

---

## RESUMO: Estruturas de Dados Completas

### 1. Tabela `bo_sessions`

```sql
CREATE TABLE bo_sessions (
    bo_id VARCHAR(50) PRIMARY KEY,        -- "BO-20251215-a3f8c2e1"
    created_at TIMESTAMP,                  -- "2025-12-15 14:30:00"
    completed_at TIMESTAMP,                -- "2025-12-15 14:35:12"
    status VARCHAR(20),                    -- "active" | "completed" | "abandoned"
    app_version VARCHAR(20),               -- "0.4.0"
    ip_address VARCHAR(50),                -- "177.12.34.56"
    user_agent TEXT                        -- "Mozilla/5.0..."
);
```

### 2. Tabela `bo_events`

```sql
CREATE TABLE bo_events (
    event_id VARCHAR(50) PRIMARY KEY,      -- "evt_4b8c9a3e"
    bo_id VARCHAR(50),                     -- "BO-20251215-a3f8c2e1"
    timestamp TIMESTAMP,                   -- "2025-12-15 14:31:05"
    event_type VARCHAR(50),                -- "answer_submitted", "text_generated", etc
    data JSON                              -- {"step": "1.1", "answer": "...", "is_valid": true}
);
```

**Tipos de eventos:**
- `session_started` - Sessão iniciada
- `question_asked` - Pergunta exibida
- `answer_submitted` - Resposta enviada
- `validation_error` - Erro de validação
- `answer_edited` - Resposta editada
- `text_generated` - Texto do BO gerado
- `text_copied` - Texto copiado
- `session_completed` - Sessão concluída
- `session_abandoned` - Sessão abandonada

### 3. Tabela `feedbacks`

```sql
CREATE TABLE feedbacks (
    feedback_id VARCHAR(50) PRIMARY KEY,   -- "fb_7c8a9b3e"
    bo_id VARCHAR(50),                     -- "BO-20251215-a3f8c2e1"
    event_id VARCHAR(50),                  -- "evt_3a9b2c5d" (opcional)
    timestamp TIMESTAMP,                   -- "2025-12-15 14:36:00"
    feedback_type VARCHAR(20),             -- "positive" | "negative"
    category VARCHAR(20),                  -- "bug" | "suggestion"
    user_message TEXT,                     -- Mensagem do usuário (opcional)
    context JSON,                          -- Contexto adicional
    meta_data JSON,                        -- Metadados (IP, User-Agent)
    status VARCHAR(20)                     -- "new" | "reviewed" | "resolved"
);
```

### 4. State Machine (em memória)

```python
{
    "current_step": "1.2",           # Step atual ("1.1" a "1.6", depois "complete")
    "step_index": 1,                 # Índice no array STEPS (0-6)
    "answers": {                     # Respostas coletadas
        "1.1": "22/03/2025, às 19h03",
        "1.2": "...",
        # ... (até 6 respostas)
    }
}
```

### 5. Sessions em memória

```python
sessions = {
    "3e4f5a6b-7c8d-9e0f-1a2b-3c4d5e6f7a8b": (
        "BO-20251215-a3f8c2e1",      # bo_id
        BOStateMachine()             # Instância da state machine
    )
}
```

---

## FLUXO VISUAL SIMPLIFICADO

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. POST /new_session                                            │
├─────────────────────────────────────────────────────────────────┤
│ Frontend → Backend                                              │
│   ↓ main.py:new_session()                                       │
│   ↓ uuid.uuid4() → session_id                                   │
│   ↓ BOLogger.create_session() → bo_id                           │
│       ↓ INSERT INTO bo_sessions                                 │
│       ↓ INSERT INTO bo_events (session_started)                 │
│   ↓ BOStateMachine() → state_machine                            │
│   ↓ sessions[session_id] = (bo_id, state_machine)               │
│   ↓ state_machine.get_current_question() → "Dia, data e hora..."│
│   ↓ INSERT INTO bo_events (question_asked)                      │
│   ↓ return {session_id, bo_id, first_question}                  │
│ Backend → Frontend                                              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 2. POST /chat (perguntas 1-5)                                   │
├─────────────────────────────────────────────────────────────────┤
│ Frontend → Backend: {session_id, message, llm_provider}         │
│   ↓ main.py:chat()                                              │
│   ↓ sessions[session_id] → (bo_id, state_machine)               │
│   ↓ ResponseValidator.validate(step, message)                   │
│       ↓ Verifica: tamanho, palavras-chave, formato             │
│       ↓ Para 1.1: valida data/hora, hora/minuto, data futura   │
│   ↓ INSERT INTO bo_events (answer_submitted, is_valid=true)     │
│   ↓ state_machine.store_answer(message)                         │
│   ↓ state_machine.next_step() → current_step = "1.2"            │
│   ↓ state_machine.is_section_complete() → False                 │
│   ↓ state_machine.get_current_question() → próxima pergunta     │
│   ↓ INSERT INTO bo_events (question_asked)                      │
│   ↓ return {question, is_section_complete=false}                │
│ Backend → Frontend                                              │
│                                                                  │
│ (Repete para perguntas 1.2, 1.3, 1.4, 1.5)                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 3. POST /chat (pergunta 6 - GERA TEXTO)                         │
├─────────────────────────────────────────────────────────────────┤
│ Frontend → Backend: {session_id, message, llm_provider}         │
│   ↓ main.py:chat()                                              │
│   ↓ ResponseValidator.validate("1.6", message) → True           │
│   ↓ INSERT INTO bo_events (answer_submitted)                    │
│   ↓ state_machine.store_answer(message)                         │
│   ↓ state_machine.next_step() → current_step = "complete"       │
│   ↓ state_machine.is_section_complete() → TRUE ✅              │
│   ↓ llm_service.generate_section_text(answers, "gemini")        │
│       ↓ llm_service._generate_with_gemini(answers)              │
│           ↓ _build_prompt(answers)                              │
│               ↓ _enrich_datetime("22/03/2025, às 19h03")        │
│                   ↓ Regex extrai: dia=22, mês=3, ano=2025       │
│                   ↓ Calcula dia da semana: "sábado"             │
│                   ↓ Mapeia mês: "março"                         │
│                   ↓ Retorna: "sábado, 22 de março de 2025..."   │
│               ↓ Monta prompt completo (3000+ chars)             │
│           ↓ genai.GenerativeModel.generate_content(prompt)      │
│               ↓ POST https://generativelanguage.googleapis.com  │
│               ↓ API Key: [GEMINI_API_KEY_REDACTED]│
│               ↓ Gemini processa + retorna texto                 │
│           ↓ return generated_text                               │
│   ↓ INSERT INTO bo_events (text_generated, generation_time_ms)  │
│   ↓ UPDATE bo_sessions SET status='completed', completed_at=NOW │
│   ↓ return {generated_text, is_section_complete=true}           │
│ Backend → Frontend                                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## ARQUIVOS ENVOLVIDOS E RESPONSABILIDADES

| Arquivo | Responsabilidade | Funções Principais |
|---------|------------------|-------------------|
| **main.py** | Endpoints da API | `new_session()`, `chat()`, `update_answer()`, `add_feedback()` |
| **state_machine.py** | Controle do fluxo de perguntas | `get_current_question()`, `store_answer()`, `next_step()`, `is_section_complete()` |
| **validator.py** | Validação de respostas | `validate()`, validação datetime customizada |
| **llm_service.py** | Integração com LLMs | `generate_section_text()`, `_generate_with_gemini()`, `_build_prompt()`, `_enrich_datetime()` |
| **logger.py** | Logging e banco de dados | `create_session()`, `log_event()`, `update_session_status()`, `add_feedback()` |

---

## DEPENDÊNCIAS EXTERNAS

1. **Google Gemini API**
   - Endpoint: `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent`
   - Autenticação: API Key via environment variable `GEMINI_API_KEY`
   - Biblioteca: `google-generativeai==0.8.3`

2. **Banco de Dados**
   - **Local:** SQLite (`bo_logs.db`)
   - **Produção:** PostgreSQL (via `DATABASE_URL` do Render)
   - ORM: SQLAlchemy 2.0.36

---

## OBSERVAÇÕES IMPORTANTES

1. **Encoding UTF-8:** Todos os arquivos Python usam `# -*- coding: utf-8 -*-` (validator.py linha 1)

2. **Timezone Brasília:** Todos os timestamps usam `BRASILIA_TZ = timezone(timedelta(hours=-3))` (logger.py linha 16)

3. **Sessões em memória:** `sessions` é um Dict global que **não persiste** entre restarts do servidor. Se o backend reiniciar, todas as sessões ativas são perdidas (mas os dados ficam no banco).

4. **Validação robusta:**
   - Step 1.1 valida: formato, hora (0-23), minuto (0-59), mês (1-12), dia válido para o mês, data não futura
   - Step 1.2 valida: presença de "prefixo" + tamanho mínimo 15 chars
   - Step 1.5 valida: sinônimos de rua/avenida, número, bairro/região

5. **Prompt engineering:** O prompt do Gemini tem 3000+ caracteres com exemplos CERTOS e ERRADOS para evitar alucinações

6. **Logs estruturados:** Cada evento tem `event_type` + `data` (JSON), permitindo análises posteriores

7. **No plan mode:** Este documento é apenas informativo/de pesquisa, não requer implementação
