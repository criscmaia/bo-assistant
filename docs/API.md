# 📡 Referência de API - BO Inteligente

**Versão:** v0.12.7
**Base URL (Produção):** `https://bo-assistant-backend.onrender.com`
**Base URL (Local):** `http://localhost:8000`

Este documento detalha todos os endpoints da API, exemplos de requisições e respostas.

---

## 📋 Índice

- [Informações Gerais](#-informações-gerais)
- [Endpoints de Sessão](#-endpoints-de-sessão)
- [Endpoints de Logs e Estatísticas](#-endpoints-de-logs-e-estatísticas)
- [Modelos de Dados](#-modelos-de-dados)
- [Códigos de Erro](#-códigos-de-erro)

---

## ℹ️ Informações Gerais

### Autenticação
- **Não requer autenticação** (sistema público por enquanto)
- Sessões são identificadas por `session_id` (UUID)

### Content-Type
- Todas as requisições POST/PUT: `application/json`
- Todas as respostas: `application/json`

### CORS
- Permitido para qualquer origem (`*`)
- Headers permitidos: `Content-Type`, `Authorization`

### Rate Limiting
- **Gemini 2.5 Flash:** 20 req/dia (free tier)
- **Groq Llama 3.3 70B:** 14.400 req/dia (free tier)
- Sem rate limiting por IP no backend

---

## 🎯 Endpoints de Sessão

### 1. Informações da API

```http
GET /
```

**Descrição:** Retorna informações básicas da API.

**Resposta:**
```json
{
  "name": "BO Inteligente API",
  "version": "0.9.0",
  "description": "API para geração de Boletins de Ocorrência usando IA",
  "endpoints": ["/new_session", "/chat", "..."]
}
```

---

### 2. Health Check

```http
GET /health
```

**Descrição:** Verifica se o servidor está ativo.

**Resposta:**
```json
{
  "status": "healthy"
}
```

---

### 3. Criar Nova Sessão

```http
POST /new_session
```

**Descrição:** Inicia uma nova sessão de BO e retorna a primeira pergunta.

**Request Body:** Vazio

**Resposta:**
```json
{
  "session_id": "3e4f5a6b-7c8d-9e0f-1a2b-3c4d5e6f7a8b",
  "bo_id": "BO-20251220-a3f8c2e1",
  "first_question": "Dia, data e hora do acionamento."
}
```

**Exemplo (curl):**
```bash
curl -X POST https://bo-assistant-backend.onrender.com/new_session \
  -H "Content-Type: application/json"
```

**Exemplo (JavaScript):**
```javascript
const response = await fetch(`${API_URL}/new_session`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
});
const data = await response.json();
console.log(data.session_id, data.bo_id);
```

---

### 4. Processar Resposta do Usuário

```http
POST /chat
```

**Descrição:** Envia resposta do usuário, valida, e retorna próxima pergunta ou texto gerado.

**Request Body:**
```json
{
  "session_id": "3e4f5a6b-7c8d-9e0f-1a2b-3c4d5e6f7a8b",
  "message": "22/03/2025, às 19h03, sexta-feira",
  "llm_provider": "groq"  // Opcional: "gemini" (padrão) ou "groq"
}
```

**Parâmetros:**
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `session_id` | string | Sim | ID da sessão (UUID) |
| `message` | string | Sim | Resposta do usuário |
| `llm_provider` | string | Não | Provider LLM ("gemini" ou "groq") |

**Resposta (próxima pergunta):**
```json
{
  "question": "Composição da guarnição e prefixo.",
  "step": "1.2",
  "total_steps": 6,
  "section": 1
}
```

**Resposta (validação falhou):**
```json
{
  "error": "Por favor, inclua dia da semana, data e hora completos (ex: segunda-feira, 22/03/2025, às 19h03)."
}
```

**Resposta (seção completa):**
```json
{
  "message": "Texto do BO gerado com sucesso!",
  "generated_text": "No dia 22 de março de 2025 (sexta-feira), às 19h03...",
  "section_complete": true,
  "section": 1,
  "next_section": 2,
  "can_proceed": true
}
```

**Exemplo (curl):**
```bash
curl -X POST https://bo-assistant-backend.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "uuid",
    "message": "22/03/2025, às 19h03",
    "llm_provider": "groq"
  }'
```

**Códigos de Status:**
- `200 OK` - Sucesso
- `400 Bad Request` - Resposta inválida
- `404 Not Found` - Sessão não encontrada
- `500 Internal Server Error` - Erro ao gerar texto

---

### 5. Iniciar Nova Seção

```http
POST /start_section/{section_number}
```

**Descrição:** Inicia uma nova seção do BO (ex: Seção 2 - Abordagem a Veículo, Seção 3 - Campana, Seção 4 - Entrada em Domicílio, Seção 5 - Fundada Suspeita, Seção 6 - Reação e Uso da Força).

**Path Parameters:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `section_number` | int | Número da seção (2-6) |

**Request Body:**
```json
{
  "session_id": "3e4f5a6b-7c8d-9e0f-1a2b-3c4d5e6f7a8b"
}
```

**Resposta (Seção 2):**
```json
{
  "message": "Seção 2 iniciada",
  "section": 2,
  "question": "Havia veículo?",
  "step": "2.1",
  "total_steps": 8
}
```

**Resposta (Seção 3):**
```json
{
  "message": "Seção 3 iniciada",
  "section": 3,
  "question": "A equipe realizou campana antes da abordagem?",
  "step": "3.1",
  "total_steps": 8
}
```

**Resposta (Seção 4):**
```json
{
  "message": "Seção 4 iniciada",
  "section": 4,
  "question": "Houve entrada em domicílio durante a ocorrência?",
  "step": "4.1",
  "total_steps": 5
}
```

**Resposta (Seção 5):**
```json
{
  "message": "Seção 5 iniciada",
  "section": 5,
  "question": "Houve abordagem por fundada suspeita (sem veículo, campana ou entrada em domicílio)?",
  "step": "5.1",
  "total_steps": 4
}
```

**Resposta (Seção 6):**
```json
{
  "message": "Seção 6 iniciada",
  "section": 6,
  "question": "Houve resistência durante a abordagem?",
  "step": "6.1",
  "total_steps": 5
}
```

**Exemplo (curl - Seção 2):**
```bash
curl -X POST https://bo-assistant-backend.onrender.com/start_section/2 \
  -H "Content-Type: application/json" \
  -d '{"session_id": "uuid"}'
```

**Exemplo (curl - Seção 3):**
```bash
curl -X POST https://bo-assistant-backend.onrender.com/start_section/3 \
  -H "Content-Type: application/json" \
  -d '{"session_id": "uuid"}'
```

**Exemplo (curl - Seção 4):**
```bash
curl -X POST https://bo-assistant-backend.onrender.com/start_section/4 \
  -H "Content-Type: application/json" \
  -d '{"session_id": "uuid"}'
```

**Exemplo (curl - Seção 5):**
```bash
curl -X POST https://bo-assistant-backend.onrender.com/start_section/5 \
  -H "Content-Type: application/json" \
  -d '{"session_id": "uuid"}'
```

**Exemplo (curl - Seção 6):**
```bash
curl -X POST https://bo-assistant-backend.onrender.com/start_section/6 \
  -H "Content-Type: application/json" \
  -d '{"session_id": "uuid"}'
```

**Resposta (Seção 7):**
```json
{
  "message": "Seção 7 iniciada",
  "section": 7,
  "question": "Houve apreensão de drogas?",
  "step": "7.1",
  "total_steps": 4
}
```

**Exemplo (curl - Seção 7):**
```bash
curl -X POST https://bo-assistant-backend.onrender.com/start_section/7 \
  -H "Content-Type: application/json" \
  -d '{"session_id": "uuid"}'
```

**Códigos de Status:**
- `200 OK` - Sucesso
- `400 Bad Request` - Seção inválida ou já iniciada
- `404 Not Found` - Sessão não encontrada

---

### 6. Sincronizar Sessão (Restaurar Rascunho)

```http
POST /sync_session
```

**Descrição:** Sincroniza estado completo da sessão em uma única requisição (restauração de rascunhos).

**Request Body:**
```json
{
  "session_id": "3e4f5a6b-7c8d-9e0f-1a2b-3c4d5e6f7a8b",
  "bo_id": "BO-20251220-a3f8c2e1",
  "sections": {
    "1": {
      "answers": {
        "1.1": "22/03/2025, às 19h03",
        "1.2": "Sgt João, prefixo 1234",
        "1.3": "Tráfico de drogas",
        "1.4": "Denúncia via COPOM",
        "1.5": "Rua X, 123, Centro",
        "1.6": "Sim, ponto conhecido"
      },
      "current_step": "complete",
      "completed": true,
      "generated_text": "No dia 22 de março de 2025..."
    },
    "2": {
      "answers": {
        "2.1": "SIM",
        "2.2": "Gol preto, placa ABC1D23"
      },
      "current_step": "2.3",
      "completed": false,
      "generated_text": ""
    },
    "3": {
      "answers": {},
      "current_step": "3.1",
      "completed": false,
      "generated_text": ""
    }
  },
  "current_section": 2
}
```

**Resposta:**
```json
{
  "success": true,
  "message": "Sessão sincronizada com sucesso",
  "session_id": "3e4f5a6b-7c8d-9e0f-1a2b-3c4d5e6f7a8b",
  "current_section": 2,
  "current_question": "Onde foi visto?",
  "current_step": "2.3"
}
```

**Exemplo (JavaScript):**
```javascript
const draft = JSON.parse(localStorage.getItem('bo_draft'));

const response = await fetch(`${API_URL}/sync_session`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(draft)
});
```

**Códigos de Status:**
- `200 OK` - Sucesso
- `400 Bad Request` - Dados inválidos
- `500 Internal Server Error` - Erro ao sincronizar

---

### 7. Editar Resposta Anterior

```http
PUT /chat/{session_id}/answer/{step}
```

**Descrição:** Edita uma resposta já fornecida anteriormente.

**Path Parameters:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `session_id` | string | ID da sessão (UUID) |
| `step` | string | ID da pergunta (ex: "1.3", "2.5") |

**Request Body:**
```json
{
  "new_answer": "Tráfico de drogas em via pública"
}
```

**Resposta:**
```json
{
  "message": "Resposta atualizada com sucesso",
  "step": "1.3",
  "new_answer": "Tráfico de drogas em via pública"
}
```

**Exemplo (curl):**
```bash
curl -X PUT https://bo-assistant-backend.onrender.com/chat/uuid/answer/1.3 \
  -H "Content-Type: application/json" \
  -d '{"new_answer": "Tráfico de drogas em via pública"}'
```

**Códigos de Status:**
- `200 OK` - Sucesso
- `400 Bad Request` - Step inválido ou nova resposta inválida
- `404 Not Found` - Sessão não encontrada

---

### 8. Registrar Feedback

```http
POST /feedback
```

**Descrição:** Registra feedback do usuário (👍 positivo ou 👎 negativo).

**Request Body:**
```json
{
  "bo_id": "BO-20251220-a3f8c2e1",
  "message_id": "section1_generated_text",
  "feedback_type": "positive"
}
```

**Parâmetros:**
| Campo | Tipo | Valores | Descrição |
|-------|------|---------|-----------|
| `bo_id` | string | - | ID do BO |
| `message_id` | string | - | ID da mensagem avaliada |
| `feedback_type` | string | "positive" ou "negative" | Tipo de feedback |

**Resposta:**
```json
{
  "message": "Feedback registrado com sucesso"
}
```

**Exemplo (curl):**
```bash
curl -X POST https://bo-assistant-backend.onrender.com/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "bo_id": "BO-20251220-xxxxx",
    "message_id": "section1_text",
    "feedback_type": "positive"
  }'
```

---

### 9. Deletar Sessão

```http
DELETE /session/{session_id}
```

**Descrição:** Remove uma sessão da memória (não deleta do banco).

**Path Parameters:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `session_id` | string | ID da sessão (UUID) |

**Resposta:**
```json
{
  "message": "Sessão deletada com sucesso"
}
```

**Códigos de Status:**
- `200 OK` - Sucesso
- `404 Not Found` - Sessão não encontrada

---

### 10. Status da Sessão

```http
GET /session/{session_id}/status
```

**Descrição:** Retorna o estado atual de uma sessão.

**Path Parameters:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `session_id` | string | ID da sessão (UUID) |

**Resposta:**
```json
{
  "session_id": "3e4f5a6b-7c8d-9e0f-1a2b-3c4d5e6f7a8b",
  "bo_id": "BO-20251220-a3f8c2e1",
  "current_section": 7,
  "section1_complete": true,
  "section2_complete": true,
  "section3_complete": true,
  "section4_complete": true,
  "section5_complete": true,
  "section6_complete": true,
  "section7_complete": false,
  "section1_text": "No dia 22 de março...",
  "section2_text": "VW Gol branco...",
  "section3_text": "Equipe realizou campana...",
  "section4_text": "Entrada em domicílio...",
  "section5_text": "Fundada suspeita...",
  "section6_text": "Resistência durante abordagem...",
  "section7_text": ""
}
```

**Códigos de Status:**
- `200 OK` - Sucesso
- `404 Not Found` - Sessão não encontrada

---

## 📊 Endpoints de Logs e Estatísticas

### 11. Listar Sessões

```http
GET /api/logs?limit=20&offset=0
```

**Descrição:** Lista todas as sessões registradas (dashboard de logs).

**Query Parameters:**
| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `limit` | int | 20 | Número máximo de resultados |
| `offset` | int | 0 | Offset para paginação |

**Resposta:**
```json
{
  "sessions": [
    {
      "bo_id": "BO-20251220-a3f8c2e1",
      "created_at": "2025-12-20T19:03:45",
      "completed_at": "2025-12-20T19:15:32",
      "status": "completed",
      "app_version": "0.9.0",
      "ip_address": "177.12.34.56"
    },
    {
      "bo_id": "BO-20251220-b4g9d3f2",
      "created_at": "2025-12-20T18:45:12",
      "completed_at": null,
      "status": "abandoned",
      "app_version": "0.9.0",
      "ip_address": "189.23.45.67"
    }
  ],
  "total": 42,
  "limit": 20,
  "offset": 0
}
```

**Exemplo (curl):**
```bash
curl https://bo-assistant-backend.onrender.com/api/logs?limit=10&offset=0
```

---

### 12. Detalhes de uma Sessão

```http
GET /api/logs/{bo_id}
```

**Descrição:** Retorna todos os eventos e detalhes de uma sessão específica.

**Path Parameters:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `bo_id` | string | ID do BO (ex: "BO-20251220-a3f8c2e1") |

**Resposta:**
```json
{
  "bo_id": "BO-20251220-a3f8c2e1",
  "created_at": "2025-12-20T19:03:45",
  "completed_at": "2025-12-20T19:15:32",
  "status": "completed",
  "app_version": "0.9.0",
  "ip_address": "177.12.34.56",
  "events": [
    {
      "timestamp": "2025-12-20T19:03:45",
      "event_type": "session_started",
      "details": {}
    },
    {
      "timestamp": "2025-12-20T19:04:12",
      "event_type": "answer_valid",
      "details": {
        "step": "1.1",
        "answer": "22/03/2025, às 19h03"
      }
    },
    {
      "timestamp": "2025-12-20T19:15:30",
      "event_type": "text_generated",
      "details": {
        "section": 1,
        "provider": "groq",
        "text_length": 1250
      }
    }
  ]
}
```

---

### 13. Estatísticas Gerais

```http
GET /api/stats
```

**Descrição:** Retorna estatísticas gerais do sistema.

**Resposta:**
```json
{
  "total_sessions": 142,
  "completed_sessions": 89,
  "abandoned_sessions": 53,
  "completion_rate": 62.68,
  "total_feedbacks": 67,
  "positive_feedbacks": 52,
  "negative_feedbacks": 15,
  "positive_rate": 77.61
}
```

---

### 14. Lista de Feedbacks

```http
GET /api/feedbacks?limit=20&offset=0
```

**Descrição:** Lista todos os feedbacks registrados.

**Query Parameters:**
| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `limit` | int | 20 | Número máximo de resultados |
| `offset` | int | 0 | Offset para paginação |

**Resposta:**
```json
{
  "feedbacks": [
    {
      "bo_id": "BO-20251220-a3f8c2e1",
      "message_id": "section1_text",
      "feedback_type": "positive",
      "timestamp": "2025-12-20T19:16:45"
    },
    {
      "bo_id": "BO-20251219-c5h0e4g3",
      "message_id": "section2_text",
      "feedback_type": "negative",
      "timestamp": "2025-12-19T20:30:12"
    }
  ],
  "total": 67,
  "limit": 20,
  "offset": 0
}
```

---

## 📦 Modelos de Dados

### ChatRequest

```python
{
  "session_id": str,         # UUID da sessão
  "message": str,            # Resposta do usuário
  "llm_provider": str        # "gemini" ou "groq" (opcional)
}
```

### ChatResponse

```python
{
  "question": str,           # Próxima pergunta (se não completo)
  "step": str,               # ID da pergunta (ex: "1.3")
  "total_steps": int,        # Total de perguntas da seção
  "section": int,            # Número da seção atual
  "generated_text": str,     # Texto gerado (se completo)
  "section_complete": bool,  # True se seção completa
  "next_section": int,       # Próxima seção disponível
  "can_proceed": bool,       # True se pode avançar para próxima seção
  "error": str               # Mensagem de erro (se validação falhou)
}
```

### NewSessionResponse

```python
{
  "session_id": str,         # UUID da nova sessão
  "bo_id": str,              # ID do BO (BO-YYYYMMDD-hash)
  "first_question": str      # Primeira pergunta (1.1)
}
```

### FeedbackRequest

```python
{
  "bo_id": str,              # ID do BO
  "message_id": str,         # ID da mensagem avaliada
  "feedback_type": str       # "positive" ou "negative"
}
```

---

## ⚠️ Códigos de Erro

### HTTP Status Codes

| Código | Significado | Exemplo |
|--------|-------------|---------|
| `200 OK` | Sucesso | Resposta processada |
| `400 Bad Request` | Requisição inválida | Resposta muito curta |
| `404 Not Found` | Recurso não encontrado | Sessão não existe |
| `500 Internal Server Error` | Erro no servidor | Erro ao gerar texto |
| `503 Service Unavailable` | Serviço indisponível | Render "dormindo" |

### Mensagens de Erro Comuns

**Sessão não encontrada:**
```json
{
  "detail": "Sessão não encontrada"
}
```

**Resposta inválida:**
```json
{
  "error": "Por favor, inclua mais detalhes na sua resposta."
}
```

**Erro de LLM:**
```json
{
  "error": "Erro ao gerar texto. Por favor, tente novamente.",
  "details": "Quota exceeded"
}
```

**Seção já iniciada:**
```json
{
  "error": "Seção 2 já foi iniciada"
}
```

---

## 🔗 Documentação Relacionada

- [README.md](../README.md) - Visão geral do projeto
- [DEVELOPMENT.md](../DEVELOPMENT.md) - Guia de desenvolvimento
- [SETUP.md](SETUP.md) - Setup e deploy
- [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitetura técnica
- [TESTING.md](TESTING.md) - Guia de testes

---

## 🌐 URLs Importantes

- **Frontend (Produção):** https://criscmaia.github.io/bo-assistant/
- **Backend API (Produção):** https://bo-assistant-backend.onrender.com
- **Dashboard de Logs:** https://criscmaia.github.io/bo-assistant/logs.html
- **Repositório GitHub:** https://github.com/criscmaia/bo-assistant

---

## 📝 Notas

### Cold Start (Render Free Tier)
- Servidor "dorme" após 15 min de inatividade
- Primeira requisição pode demorar 30-60s
- Health check `/health` pode ser usado para "acordar" o servidor

### Rate Limiting de LLM
- Gemini: 20 req/dia (free tier)
- Groq: 14.400 req/dia (free tier)
- Recomendado usar Groq para testes e desenvolvimento

### Persistência
- Sessões ficam apenas em memória (perdem-se ao reiniciar servidor)
- Logs e feedbacks são salvos em PostgreSQL (persistentes)
- Frontend usa localStorage para rascunhos (7 dias de expiração)
