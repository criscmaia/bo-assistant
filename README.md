# 📋 BO Inteligente

Sistema de auxílio à elaboração de Boletins de Ocorrência policiais, utilizando IA para gerar textos técnicos seguindo as normas jurídicas estabelecidas.

---

## 🚀 Acessar Sistema

| Ambiente | URL |
|----------|-----|
| 🌐 **Frontend** | https://criscmaia.github.io/bo-assistant/ |
| ⚙️ **Backend API** | https://bo-assistant-backend.onrender.com |
| 📊 **Dashboard de Logs** | https://criscmaia.github.io/bo-assistant/logs.html |

---

## 📊 Status Atual

### ✅ v0.6.1 - Correções Críticas + Groq API

**Funcionalidades:**
- ✅ Seção 1: Contexto da Ocorrência (6 perguntas)
- ✅ Seção 2: Abordagem a Veículo (8 perguntas)
- ✅ Container persistente de textos gerados (todas seções visíveis)
- ✅ Numeração completa de perguntas ([1.1], [2.3])
- ✅ Sidebar com todas 8 seções (completadas, atual, futuras)
- ✅ Botão "Copiar BO Completo" quando há 2+ seções
- ✅ Validação inteligente de respostas
- ✅ Enriquecimento automático de data (dia da semana + ano)
- ✅ Geração de texto usando **Gemini 2.5 Flash** ou **Groq Llama 3.3 70B** (14.4k req/dia)
- ✅ Edição de respostas anteriores (CORRIGIDO na v0.6.1)
- ✅ Sistema completo de logs (PostgreSQL/SQLite)
- ✅ Sistema de feedback (👍👎) em todas as mensagens
- ✅ Dashboard de logs para validação
- ✅ Interface responsiva (desktop, tablet e mobile)
- ✅ Frontend detecta localhost E 127.0.0.1

---

## 🎯 Como Usar

1. Acesse: https://criscmaia.github.io/bo-assistant/
2. Responda as 6 perguntas da Seção 1 (Contexto da Ocorrência)
3. O sistema valida cada resposta e pede mais detalhes se necessário
4. Ao final da Seção 1, o texto é gerado automaticamente
5. Clique em "Iniciar Seção 2" para continuar (Abordagem a Veículo - 8 perguntas)
6. Ao final da Seção 2, outro texto é gerado
7. Use "Copiar BO Completo" para copiar todas as seções de uma vez

### ⏰ Nota sobre Performance

O backend está hospedado no plano gratuito do Render e "dorme" após 15 minutos de inatividade. A primeira requisição pode demorar 30-60 segundos enquanto o servidor acorda. Requisições subsequentes são instantâneas.

---

## 🛠️ Tecnologias

### Backend
| Tecnologia | Uso |
|------------|-----|
| **FastAPI** | Framework web Python |
| **Python 3.13** | Linguagem |
| **Gemini 2.5 Flash** | LLM principal (20 req/dia) |
| **Groq Llama 3.3 70B** | LLM alternativo (14.4k req/dia) |
| **SQLAlchemy** | ORM para banco de dados |
| **PostgreSQL** | Banco de dados em produção |
| **SQLite** | Banco de dados local |
| **Uvicorn** | Servidor ASGI |

### Frontend
| Tecnologia | Uso |
|------------|-----|
| **HTML5** | Estrutura |
| **JavaScript Vanilla** | Lógica |
| **Tailwind CSS** | Estilização (via CDN) |

### Infraestrutura
| Serviço | Uso |
|---------|-----|
| **Render** | Backend + PostgreSQL (free tier) |
| **GitHub Pages** | Frontend estático |
| **GitHub** | Controle de versão |

---

## 📁 Estrutura do Projeto

```
bo-assistant/
├── backend/
│   ├── main.py              # API FastAPI (endpoints)
│   ├── state_machine.py     # Fluxo de perguntas Seção 1
│   ├── state_machine_section2.py  # Fluxo de perguntas Seção 2
│   ├── llm_service.py       # Integração com Gemini + Groq
│   ├── validator.py         # Validação de respostas Seção 1
│   ├── validator_section2.py  # Validação de respostas Seção 2
│   ├── logger.py            # Sistema de logs (SQLite/PostgreSQL)
│   ├── requirements.txt     # Dependências de produção
│   ├── requirements-dev.txt # Dependências de desenvolvimento
│   ├── automate_release.py  # Automação de screenshots/vídeo
│   ├── test_scenarios.json  # Cenários de teste automatizado
│   ├── README_AUTOMACAO.md  # Documentação da automação
│   └── env.example          # Template de variáveis de ambiente
├── docs/
│   ├── index.html           # Interface principal do chat
│   ├── logs.html            # Dashboard de logs
│   └── screenshots/         # Screenshots por versão
├── .env                     # Variáveis de ambiente (RAIZ, não versionado)
├── .gitignore               # Arquivos ignorados
├── CHANGELOG.md             # Histórico de versões
├── README.md                # Este arquivo
├── CLAUDE.md                # Documentação para desenvolvimento
├── render.yaml              # Configuração do Render
└── deploy_instructions_Render.md  # Guia de deploy
```

**⚠️ Nota importante:** O arquivo `.env` DEVE estar na raiz do projeto (`bo-assistant/.env`), não dentro de `backend/`. Ele já está no `.gitignore` e não será versionado.

---

## 🔌 API Endpoints

### Principais

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/health` | Status do servidor |
| `POST` | `/new_session` | Inicia nova sessão de BO |
| `POST` | `/chat` | Processa resposta do usuário |
| `PUT` | `/chat/{session_id}/answer/{step}` | Edita resposta anterior |
| `POST` | `/feedback` | Registra feedback (👍👎) |
| `DELETE` | `/session/{session_id}` | Deleta sessão |
| `GET` | `/session/{session_id}/status` | Status da sessão |

### Logs e Estatísticas

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/api/stats` | Estatísticas gerais |
| `GET` | `/api/logs` | Lista todas as sessões |
| `GET` | `/api/logs/{bo_id}` | Detalhes de uma sessão |
| `GET` | `/api/feedbacks` | Lista feedbacks |

### Exemplos de Uso

**Iniciar sessão:**
```bash
curl -X POST https://bo-assistant-backend.onrender.com/new_session
```

**Resposta:**
```json
{
  "session_id": "uuid",
  "bo_id": "BO-20251211-abc123",
  "first_question": "Dia, data e hora do acionamento."
}
```

**Enviar resposta:**
```bash
curl -X POST https://bo-assistant-backend.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "uuid", "message": "22/03/2025, às 19h03", "llm_provider": "groq"}'
```

**Nota:** `llm_provider` pode ser `"gemini"` ou `"groq"`.

---

## 🧪 Desenvolvimento Local

### Pré-requisitos
- Python 3.11+
- Git
- Conta no Google AI Studio (para API key do Gemini)
- Conta no Groq (para API key do Groq - opcional)

### Setup Backend

```bash
# Clonar repositório
git clone https://github.com/criscmaia/bo-assistant.git
cd bo-assistant

# Criar ambiente virtual
cd backend
python -m venv venv

# Ativar ambiente virtual
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt

# Configurar API keys - IMPORTANTE: .env deve estar na RAIZ do projeto
cd ..
cp backend/env.example .env
# Editar .env e adicionar:
# GEMINI_API_KEY=sua_chave_aqui
# GROQ_API_KEY=sua_chave_groq_aqui (opcional)

# Rodar servidor (DEVE rodar do diretório raiz)
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**⚠️ IMPORTANTE:** O backend DEVE ser iniciado do diretório raiz do projeto, não de `backend/`. Isso garante que o arquivo `.env` seja carregado corretamente pelo python-dotenv.

### Setup Frontend

```bash
# Em outro terminal, na pasta docs
cd docs
python -m http.server 3000 --bind 127.0.0.1

# Acessar: http://127.0.0.1:3000 ou http://localhost:3000
```

### Automação de Screenshots

```bash
# No terminal do backend (venv ativado)
python automate_release.py --version v0.6.1

# Sem vídeo (mais rápido)
python automate_release.py --version v0.6.1 --no-video
```

---

## 🐛 Troubleshooting

### Backend não conecta / Erro 500

**Problema:** Frontend mostra erro de conexão ou erro 500 ao gerar texto.

**Possíveis causas e soluções:**

1. **Arquivo .env não está sendo carregado**
   - Sintoma: Backend inicia mas API keys retornam `None`
   - Causa: python-dotenv carrega `.env` do CWD (current working directory)
   - Solução: Arquivo `.env` DEVE estar na raiz do projeto (`bo-assistant/.env`)
   - Comando correto: `python -m uvicorn backend.main:app --reload` (do diretório raiz)
   - Comando ERRADO: `cd backend && uvicorn main:app --reload`

2. **Porta 8000 já está em uso**
   - Sintoma: Backend não inicia ou falha silenciosamente
   - Solução: Matar processos Python: `taskkill /F /IM python.exe` (Windows)
   - Verificar porta: `netstat -ano | findstr :8000`

3. **Frontend usando URL de produção em vez de localhost**
   - Sintoma: Requisições vão para `bo-assistant-backend.onrender.com` em vez de `localhost:8000`
   - Causa: Frontend acessado via `127.0.0.1` mas código só detectava `localhost`
   - Solução: Versão v0.6.1+ já detecta ambos automaticamente

### Edição de respostas não funciona

**Problema:** Erro 500 ao tentar editar resposta anterior.

**Causa:** Estrutura de sessões mudou de tupla para dict na v0.5.0 mas endpoint de edição não foi atualizado.

**Solução:** Atualizado na v0.6.1. Certifique-se de estar usando a versão mais recente.

### Screenshots de automação com problemas visuais

**Problema:** Screenshots mostram conteúdo sobreposto ou não capturam a área desejada.

**Soluções:**
- Para elementos `position: fixed` (sidebar, modals): use `full_page=False` (captura apenas viewport)
- Para capturar página inteira: use `full_page=True`
- Ordem importa: executar ações → aguardar efeitos → fazer scroll → capturar

### Quota do Gemini/Groq excedida

**Problema:** Erro 429 - Rate limit excedido.

**Soluções:**
- Gemini 2.5 Flash free tier: 20 requisições/dia
- Groq Llama 3.3 70B free tier: 14.400 requisições/dia (recomendado para testes)
- Trocar provider no frontend (`llm_provider: 'groq'` ou `'gemini'`)

---

## 📚 Lições Aprendidas (Debugging)

### 1. python-dotenv e CWD
O `python-dotenv` carrega `.env` do **current working directory** (CWD), não do diretório do script:
- Se rodar `cd backend && uvicorn main:app`, procura `.env` em `backend/.env`
- Se rodar `python -m uvicorn backend.main:app` da raiz, procura `.env` na raiz
- **Solução:** Padronizar CWD e documentar claramente nos comandos

### 2. Estruturas de dados em APIs
Mudanças em estruturas de dados (tupla → dict) podem quebrar endpoints silenciosamente:
- **Problema:** Testes automatizados pegaram bug em edição após refatoração
- **Solução:** Sempre revisar TODOS os endpoints ao mudar estruturas compartilhadas

### 3. Playwright e elementos fixed/absolute
Screenshots `full_page=True` fazem scroll virtual da página toda:
- Elementos `position: fixed` (sidebars, headers) podem aparecer através do conteúdo
- **Solução:** Use `full_page=False` para overlays/modals, `full_page=True` para páginas completas

### 4. Ordem de operações em automação
Algumas ações têm side effects que revertem operações anteriores:
- **Exemplo:** Scroll → Click pode ser revertido se o click também causar scroll
- **Solução:** Sempre testar ordem: ação → efeito → captura

---

## 📝 Roadmap

Veja o roadmap completo e detalhado em **[ROADMAP.md](ROADMAP.md)**.

### Resumo das próximas fases:
- ✅ **Fase 1** - Validação e Polimento (v0.4.1 - v0.5.1)
- 🔄 **Fase 2** - Seções 3-8: Campana, Entrada Domicílio, Fundada Suspeita, Reação, Apreensões, Condução
- 🔐 **Fase 3** - Autenticação e Qualidade (PDF, múltiplos LLMs)
- 📊 **Fase 4** - Analytics e Relatórios para Gestores
- 📱 **Fase 5** - Expansão (múltiplos BOs, mobile)

---

## 👥 Equipe

- **Cristiano Maia** - Delivery Manager & Tech Lead
- **Claudio Moreira** - Especialista em Redação de BOs & Comercial

---

## 📄 Licença

Este projeto está sob licença privada. Todos os direitos reservados.

---

## 📞 Contato

Para dúvidas, sugestões ou feedback:
- Abra uma [Issue](https://github.com/criscmaia/bo-assistant/issues)
- Entre em contato via GitHub

---

**Versão:** 0.6.1
**Última atualização:** 20/12/2025
**Status:** 🟢 Em produção
