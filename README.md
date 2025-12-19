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

### ✅ v0.5.1 - UX Multi-Seção

**Funcionalidades:**
- ✅ Seção 1: Contexto da Ocorrência (6 perguntas)
- ✅ Seção 2: Abordagem a Veículo (8 perguntas)
- ✅ Container persistente de textos gerados (todas seções visíveis)
- ✅ Numeração completa de perguntas ([1.1], [2.3])
- ✅ Sidebar com todas 8 seções (completadas, atual, futuras)
- ✅ Botão "Copiar BO Completo" quando há 2+ seções
- ✅ Validação inteligente de respostas
- ✅ Enriquecimento automático de data (dia da semana + ano)
- ✅ Geração de texto usando Gemini 2.5 Flash
- ✅ Edição de respostas anteriores
- ✅ Sistema completo de logs (PostgreSQL/SQLite)
- ✅ Sistema de feedback (👍👎) em todas as mensagens
- ✅ Dashboard de logs para validação
- ✅ Interface responsiva (desktop, tablet e mobile)

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
| **Gemini 2.5 Flash** | LLM para geração de texto |
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
│   ├── state_machine.py     # Gerenciamento de fluxo de perguntas
│   ├── llm_service.py       # Integração com Gemini
│   ├── validator.py         # Validação de respostas
│   ├── logger.py            # Sistema de logs (SQLite/PostgreSQL)
│   ├── requirements.txt     # Dependências de produção
│   ├── requirements-dev.txt # Dependências de desenvolvimento
│   ├── automate_release.py  # Automação de screenshots/vídeo
│   ├── test_scenarios.json  # Cenários de teste automatizado
│   ├── README_AUTOMACAO.md  # Documentação da automação
│   ├── env.example          # Template de variáveis de ambiente
│   └── .env                 # Variáveis de ambiente (não versionado)
├── docs/
│   ├── index.html           # Interface principal do chat
│   ├── logs.html            # Dashboard de logs
│   └── screenshots/         # Screenshots por versão
├── .gitignore               # Arquivos ignorados
├── CHANGELOG.md             # Histórico de versões
├── README.md                # Este arquivo
├── render.yaml              # Configuração do Render
└── deploy_instructions_Render.md  # Guia de deploy
```

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
  -d '{"session_id": "uuid", "message": "22/03/2025, às 19h03", "llm_provider": "gemini"}'
```

---

## 🧪 Desenvolvimento Local

### Pré-requisitos
- Python 3.11+
- Git
- Conta no Google AI Studio (para API key do Gemini)

### Setup Backend

```bash
# Clonar repositório
git clone https://github.com/criscmaia/bo-assistant.git
cd bo-assistant/backend

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt

# Configurar API key
cp env.example .env
# Editar .env e adicionar: GEMINI_API_KEY=sua_chave_aqui

# Rodar servidor
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Setup Frontend

```bash
# Em outro terminal, na pasta docs
cd ../docs
python -m http.server 3000

# Acessar: http://localhost:3000
```

### Automação de Screenshots

```bash
# No terminal do backend (venv ativado)
python automate_release.py --version v0.4.0

# Sem vídeo (mais rápido)
python automate_release.py --version v0.4.0 --no-video
```

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

**Versão:** 0.5.1
**Última atualização:** 19/12/2025
**Status:** 🟢 Em produção
