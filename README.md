# 📋 BO Inteligente

[![Tests](https://github.com/criscmaia/bo-assistant/actions/workflows/test.yml/badge.svg)](https://github.com/criscmaia/bo-assistant/actions/workflows/test.yml)
[![Security Scan](https://github.com/criscmaia/bo-assistant/actions/workflows/security-scan.yml/badge.svg)](https://github.com/criscmaia/bo-assistant/actions/workflows/security-scan.yml)

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

### ✅ v0.12.4 - CI/CD e Melhorias de Infraestrutura

**Novidades v0.12.4:**
- ✅ **CI/CD com GitHub Actions** - Testes automatizados em PRs
- ✅ **Testes E2E separados** - Estrutura reorganizada (Playwright isolado)
- ✅ **Badge de Status** - Visibilidade em tempo real da saúde do código
- ✅ **Comandos de teste** documentados para rodar localmente igual ao CI

### ✅ v0.12.2 - Seção 8: Condução e Pós-Ocorrência (FINAL)

**Novidades v0.12.2:**
- ✅ **Seção 8: Condução e Pós-Ocorrência** - 6 perguntas (8.1 a 8.6) - ÚLTIMA SEÇÃO
- ✅ **BO 100% COMPLETO** - Todas as 8 seções implementadas (8/8)
- ✅ **Marca BO como Completo** - Seção 8 marca `boCompleted = true`
- ✅ **Validação `allow_none_response`** - 4 perguntas aceitam respostas negativas (8.2, 8.3, 8.4, 8.5)
- ✅ **Validação de Graduação Militar Obrigatória** - 8.1 e 8.6 exigem (Sargento, Soldado, Cabo, etc.)
- ✅ **Validação de Destino Obrigatório** - 8.6 exige CEFLAN, Delegacia, DIPC, Central, etc.
- ✅ **Testes completos** - 30+ unitários + 20+ integração passando
- ✅ **Fundamento Jurídico** - Lei 11.343/06, Lei 13.869/19, CPP Arts. 282-284
- ✅ **Geração de Texto Final via LLM** - Consolidação da narrativa completa

**Recursos v0.12.2:**
- ✅ Seção 1: Contexto da Ocorrência (6 perguntas - 1.1 a 1.6)
- ✅ Seção 2: Abordagem a Veículo (8 perguntas - 2.1 a 2.8)
- ✅ Seção 3: Campana - Vigilância Velada (8 perguntas - 3.1 a 3.8)
- ✅ Seção 4: Entrada em Domicílio (5 perguntas - 4.1 a 4.5)
- ✅ Seção 5: Fundada Suspeita (4 perguntas - 5.1 a 5.4)
- ✅ Seção 6: Reação e Uso da Força (5 perguntas - 6.1 a 6.5)
- ✅ Seção 7: Apreensões e Cadeia de Custódia (4 perguntas - 7.1 a 7.4)
- ✅ Seção 8: Condução e Pós-Ocorrência (6 perguntas - 8.1 a 8.6) - MARCA BO COMPLETO
- ✅ Container persistente de textos gerados (todas seções visíveis)
- ✅ Sidebar com todas 8 seções (100% completa)
- ✅ Botão "Copiar BO Completo" quando há 2+ seções
- ✅ Validação inteligente de respostas
- ✅ Geração de texto usando **Gemini 2.5 Flash** ou **Groq Llama 3.3 70B** (14.4k req/dia)
- ✅ Sistema completo de logs (PostgreSQL/SQLite)
- ✅ Sistema de feedback (👍👎) em todas as mensagens
- ✅ Interface responsiva (desktop, tablet e mobile)
- ✅ Sistema de rascunhos com localStorage (7 dias de expiração)

---

## 🎯 Como Usar

1. Acesse: https://criscmaia.github.io/bo-assistant/
2. Responda as 6 perguntas da Seção 1 (1.1 a 1.6 - Contexto da Ocorrência)
3. O sistema valida cada resposta e pede mais detalhes se necessário
4. Ao final da Seção 1, o texto é gerado automaticamente
5. Clique em "Iniciar Seção 2" (perguntas 2.1 a 2.8 - Abordagem a Veículo)
6. Ao final da Seção 2, outro texto é gerado
7. Clique em "Iniciar Seção 3" (perguntas 3.1 a 3.8 - Campana/Vigilância Velada)
8. Ao final da Seção 3, mais um texto é gerado
9. Clique em "Iniciar Seção 4" (perguntas 4.1 a 4.5 - Entrada em Domicílio)
10. Ao final da Seção 4, outro texto é gerado
11. Clique em "Iniciar Seção 5" (perguntas 5.1 a 5.4 - Fundada Suspeita)
12. Ao final da Seção 5, outro texto é gerado
13. Clique em "Iniciar Seção 6" (perguntas 6.1 a 6.5 - Reação e Uso da Força)
14. Ao final da Seção 6, outro texto é gerado
15. Clique em "Iniciar Seção 7" (perguntas 7.1 a 7.4 - Apreensões e Cadeia de Custódia)
16. Ao final da Seção 7, aguarde a Seção 8 (ainda em desenvolvimento)
17. Use "Copiar BO Completo" para copiar todas as 7 seções de uma vez
18. Rascunhos são salvos automaticamente e podem ser restaurados ao reabrir a página

### ⏰ Nota sobre Performance

O backend está hospedado no plano gratuito do Render e "dorme" após 15 minutos de inatividade. A primeira requisição pode demorar 30-60 segundos enquanto o servidor acorda. Requisições subsequentes são instantâneas.

---

## 🛠️ Tecnologias

### Backend

| Tecnologia | Uso |
|------------|-----|
| **FastAPI** | Framework web Python |
| **Python 3.13** | Linguagem |
| **Groq Llama 3.3 70B** | LLM principal (14.4k req/dia) |
| **Gemini 2.5 Flash** | Fallback (20 req/dia) |
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
│   ├── main.py                    # API FastAPI (endpoints)
│   ├── state_machine.py           # Fluxo Seção 1 (6 perguntas)
│   ├── state_machine_section2.py  # Fluxo Seção 2 (8 perguntas)
│   ├── state_machine_section3.py  # Fluxo Seção 3 (8 perguntas)
│   ├── state_machine_section4.py  # Fluxo Seção 4 (5 perguntas)
│   ├── state_machine_section5.py  # Fluxo Seção 5 (4 perguntas)
│   ├── state_machine_section6.py  # Fluxo Seção 6 (5 perguntas)
│   ├── state_machine_section7.py  # Fluxo Seção 7 (4 perguntas) - NOVO
│   ├── llm_service.py             # Integração Gemini + Groq
│   ├── validator.py               # Validação Seção 1
│   ├── validator_section2.py      # Validação Seção 2
│   ├── validator_section3.py      # Validação Seção 3
│   ├── validator_section4.py      # Validação Seção 4
│   ├── validator_section5.py      # Validação Seção 5
│   ├── validator_section6.py      # Validação Seção 6
│   ├── validator_section7.py      # Validação Seção 7 - NOVO
│   ├── logger.py                  # Sistema de logs
│   ├── automate_release.py        # Automação screenshots/vídeo
│   ├── test_scenarios.json        # Cenários de teste
│   ├── requirements.txt           # Dependências de produção
│   └── requirements-dev.txt       # Dependências de desenvolvimento
├── docs/
│   ├── index.html                 # Interface principal
│   ├── logs.html                  # Dashboard de logs
│   ├── SETUP.md                   # Guia de setup e deploy
│   ├── ARCHITECTURE.md            # Arquitetura técnica
│   ├── API.md                     # Referência de endpoints
│   ├── TESTING.md                 # Guia de testes
│   ├── ROADMAP.md                 # Planejamento de features
│   └── PROMPT_IDENTIDADE_VISUAL.md # Guia de identidade visual
├── .env                           # Variáveis de ambiente (RAIZ, não versionado)
├── .gitignore                     # Arquivos ignorados
├── CHANGELOG.md                   # Histórico de versões
├── README.md                      # Este arquivo
├── DEVELOPMENT.md                 # Guia de desenvolvimento
├── render.yaml                    # Configuração do Render
└── materiais-claudio/             # Material do especialista (Sgt. Claudio Moreira)
```

---

## 📚 Documentação

### Para Usuários

- [README.md](README.md) - Visão geral e quick start (este arquivo)
- [CHANGELOG.md](CHANGELOG.md) - Histórico de versões e mudanças

### Para Desenvolvedores

- [DEVELOPMENT.md](DEVELOPMENT.md) - Guia de desenvolvimento, debugging e ADRs
- [docs/SETUP.md](docs/SETUP.md) - Setup local e deploy em produção
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Arquitetura técnica detalhada
- [docs/API.md](docs/API.md) - Referência completa de endpoints
- [docs/TESTING.md](docs/TESTING.md) - Guia de testes e automação
- [docs/ROADMAP.md](docs/ROADMAP.md) - Planejamento de features futuras

### Material Especialista

- [materiais-claudio/](materiais-claudio/) - Material do Sgt. Claudio Moreira (redação de BOs)

---

## 🚀 Quick Start (Desenvolvimento Local)

### Pré-requisitos

- Python 3.11+
- Git
- Conta no Google AI Studio (para API key do Gemini)
- Conta no Groq (para API key do Groq - opcional)

### Setup Rápido

```bash
# 1. Clonar repositório
git clone https://github.com/criscmaia/bo-assistant.git
cd bo-assistant

# 2. Criar ambiente virtual
cd backend
python -m venv venv

# 3. Ativar ambiente virtual
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. Instalar dependências
pip install -r requirements-dev.txt

# 5. Configurar API keys
cd ..
cp backend/env.example .env
# Editar .env e adicionar GEMINI_API_KEY e GROQ_API_KEY

# 6. Rodar backend (do diretório raiz)
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# 7. Rodar frontend (outro terminal)
cd docs
python -m http.server 3000 --bind 127.0.0.1

# 8. Acessar: http://localhost:3000
```

**⚠️ IMPORTANTE:** O backend DEVE ser rodado do diretório raiz do projeto para que o arquivo `.env` seja carregado corretamente.

**Guia completo:** Ver [docs/SETUP.md](docs/SETUP.md)

---

## 📝 Roadmap

Veja o roadmap completo e detalhado em [docs/ROADMAP.md](docs/ROADMAP.md).

### Resumo das próximas fases:

- ✅ **Fase 1** - Validação e Polimento (v0.4.1 - v0.6.4) ← **CONCLUÍDA**
- 🔄 **Fase 2** - Seções 3-8 (v0.7.0+)
  - ✅ Seção 3: Campana (Vigilância Velada) - v0.7.0
  - ✅ Seção 4: Entrada em Domicílio - v0.8.0
  - ✅ Seção 5: Fundada Suspeita - v0.9.0
  - ⏳ Seção 6: Reação e Uso da Força
  - ⏳ Seção 7: Apreensões
  - ⏳ Seção 8: Condução e Ocorrências
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

**Versão:** 0.12.9
**Última atualização:** 30/12/2024
**Status:** Em produção
