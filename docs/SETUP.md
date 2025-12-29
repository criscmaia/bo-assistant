# 🛠️ Setup e Deploy - BO Inteligente

**Versão:** v0.12.4
**Última atualização:** 29/12/2025

Este documento cobre setup de desenvolvimento local e deploy em produção (Render + GitHub Pages).

---

## 📋 Índice

- [Desenvolvimento Local](#-desenvolvimento-local)
- [Deploy em Produção](#-deploy-em-produção)
- [Troubleshooting](#-troubleshooting)
- [Automação de Screenshots](#-automação-de-screenshots)

---

## 🧪 Desenvolvimento Local

### Pré-requisitos

- **Python 3.11+**
- **Git**
- **Conta no Google AI Studio** (para API key do Gemini 2.5 Flash)
- **Conta no Groq** (para API key do Llama 3.3 70B - opcional mas recomendado)

### Setup Backend

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

# 4. Instalar dependências de desenvolvimento (inclui Playwright para E2E)
pip install -r requirements-dev.txt

# 4b. Instalar navegadores do Playwright (necessário para automação E2E)
playwright install

# 5. Configurar API keys - IMPORTANTE: .env deve estar na RAIZ do projeto
cd ..
cp backend/env.example .env

# 6. Editar .env e adicionar suas chaves:
# GEMINI_API_KEY=sua_chave_aqui
# GROQ_API_KEY=sua_chave_groq_aqui
```

**Obter API Keys:**

1. **Gemini 2.5 Flash:**
   - Acesse: https://aistudio.google.com/app/apikey
   - Crie um projeto e gere uma API key
   - Limite free tier: 20 requisições/dia

2. **Groq Llama 3.3 70B:**
   - Acesse: https://console.groq.com/keys
   - Crie uma conta e gere uma API key
   - Limite free tier: 14.400 requisições/dia (recomendado para testes)

### Rodar o Backend

```bash
# Terminal 1 - Backend (rodar do diretório RAIZ do projeto)
cd C:\AI\bo-assistant  # ou caminho do seu projeto
.\backend\venv\Scripts\activate      # Windows
source backend/venv/bin/activate     # Mac/Linux
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**⚠️ CRÍTICO:** O backend DEVE ser rodado do diretório raiz do projeto para que o arquivo `.env` seja carregado corretamente pelo `python-dotenv`.

**Comandos ERRADOS (não funcionam):**
```bash
cd backend && uvicorn main:app --reload  # ❌ Procura .env em backend/
cd backend && python -m uvicorn main:app  # ❌ Procura .env em backend/
```

**Comando CORRETO:**
```bash
python -m uvicorn backend.main:app --reload  # ✅ Procura .env na raiz
```

### Rodar o Frontend

```bash
# Terminal 2 - Frontend
cd docs
python -m http.server 3000 --bind 127.0.0.1

# Acessar: http://127.0.0.1:3000 ou http://localhost:3000
```

**Nota:** O frontend detecta automaticamente se está rodando localmente (`localhost` ou `127.0.0.1`) e usa `http://localhost:8000` como API. Em produção, usa `https://bo-assistant-backend.onrender.com`.

---

## 🚀 Deploy em Produção

### Arquitetura de Deploy

| Componente | Plataforma | URL | Custo |
|------------|-----------|-----|-------|
| Backend | Render (Web Service) | https://bo-assistant-backend.onrender.com | Grátis |
| Frontend | GitHub Pages | https://criscmaia.github.io/bo-assistant/ | Grátis |
| Banco de Dados | Render (PostgreSQL) | Interno | Grátis |

---

### Passo 1: Preparar Repositório

```bash
# Na pasta bo-assistant/
git init
git add .
git commit -m "Deploy inicial v0.6.4"

# Criar repo no GitHub e conectar
git remote add origin https://github.com/SEU_USUARIO/bo-assistant.git
git push -u origin main
```

---

### Passo 2: Deploy do Backend no Render

#### 2.1 Criar Conta no Render

1. Acesse: https://render.com
2. Faça login com GitHub

#### 2.2 Criar Web Service

1. Clique em **"New +"** → **"Web Service"**
2. Conecte seu repositório GitHub (`SEU_USUARIO/bo-assistant`)
3. Configure:
   - **Name:** `bo-assistant-backend`
   - **Region:** Oregon (mais próximo do Brasil)
   - **Branch:** `main`
   - **Root Directory:** deixe vazio
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** Free

#### 2.3 Adicionar Variáveis de Ambiente

1. Na página do service, vá em **"Environment"**
2. Adicione as seguintes variáveis:

   | Key | Value | Descrição |
   |-----|-------|-----------|
   | `GEMINI_API_KEY` | sua_chave_gemini | Chave do Google AI Studio |
   | `GROQ_API_KEY` | sua_chave_groq | Chave do Groq Console |
   | `DATABASE_URL` | (automático) | Render gera automaticamente ao criar PostgreSQL |

#### 2.4 Criar Banco de Dados PostgreSQL (Opcional)

1. No dashboard do Render, clique em **"New +"** → **"PostgreSQL"**
2. Configure:
   - **Name:** `bo-assistant-db`
   - **Region:** Oregon (mesma do backend)
   - **Instance Type:** Free
3. Clique em **"Create Database"**
4. Copie a **Internal Database URL**
5. Volte ao Web Service e adicione como variável `DATABASE_URL`

**Nota:** O backend funciona sem PostgreSQL (usa SQLite localmente), mas em produção é recomendado usar PostgreSQL para persistência.

#### 2.5 Deploy Automático

- Render vai fazer build e deploy automaticamente (~5 minutos)
- URL final: `https://bo-assistant-backend.onrender.com`
- Teste: Acesse `https://bo-assistant-backend.onrender.com/health`

---

### Passo 3: Deploy do Frontend no GitHub Pages

#### 3.1 Configurar GitHub Pages

1. No seu repositório GitHub, vá em **Settings** → **Pages**
2. Em **"Source"**, selecione:
   - **Branch:** `main`
   - **Folder:** `/docs`
3. Clique em **"Save"**
4. Aguarde ~2 minutos
5. URL final: `https://SEU_USUARIO.github.io/bo-assistant/`

#### 3.2 Atualizar URL do Backend (se necessário)

O frontend já está configurado para detectar o ambiente automaticamente (linhas 64-66 de [index.html](index.html)):

```javascript
const API_URL = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? 'http://localhost:8000'
    : 'https://bo-assistant-backend.onrender.com';
```

Se você usar um nome de serviço diferente no Render, edite a URL de produção.

---

### Passo 4: Configurar Deploy Contínuo

#### render.yaml (já está configurado)

O arquivo [render.yaml](../render.yaml) na raiz do projeto configura deploy automático:

```yaml
services:
  - type: web
    name: bo-assistant-backend
    env: python
    region: oregon
    plan: free
    buildCommand: pip install -r backend/requirements.txt
    startCommand: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: GEMINI_API_KEY
        sync: false
      - key: GROQ_API_KEY
        sync: false
```

**Como funciona:**
- Qualquer push para `main` dispara rebuild automático no Render (~2 min)
- GitHub Pages atualiza instantaneamente ao fazer push

---

### Passo 5: Testar Produção

1. Acesse a URL do frontend: `https://SEU_USUARIO.github.io/bo-assistant/`
2. Responda as 6 perguntas da Seção 1
3. Clique em "Gerar texto" (primeira requisição pode demorar 30-60s)
4. Inicie a Seção 2 e responda as 8 perguntas
5. Clique em "Copiar BO Completo" e verifique o texto

---

## 🐛 Troubleshooting

### Problema 1: Backend não conecta / Erro 500

**Sintoma:** Frontend mostra erro de conexão ou erro 500 ao gerar texto.

**Possíveis causas e soluções:**

#### 1.1 Arquivo .env não está sendo carregado (desenvolvimento local)

- **Sintoma:** Backend inicia mas API keys retornam `None`
- **Causa:** `python-dotenv` carrega `.env` do CWD (current working directory)
- **Solução:** Arquivo `.env` DEVE estar na raiz do projeto (`bo-assistant/.env`)
- **Comando correto:** `python -m uvicorn backend.main:app --reload` (do diretório raiz)
- **Comando ERRADO:** `cd backend && uvicorn main:app --reload`

#### 1.2 Porta 8000 já está em uso (desenvolvimento local)

- **Sintoma:** Backend não inicia ou falha silenciosamente
- **Solução (Windows):**
  ```bash
  netstat -ano | findstr :8000
  taskkill /F /IM python.exe
  ```
- **Solução (Mac/Linux):**
  ```bash
  lsof -i :8000
  kill -9 <PID>
  ```

#### 1.3 Variáveis de ambiente não configuradas (produção)

- **Sintoma:** Logs do Render mostram `GEMINI_API_KEY not found`
- **Solução:**
  1. Acesse o dashboard do Render
  2. Vá em **Environment** do seu Web Service
  3. Adicione `GEMINI_API_KEY` e `GROQ_API_KEY`
  4. Clique em **"Save Changes"** (dispara rebuild automático)

---

### Problema 2: Frontend conectando ao Render em vez de localhost

**Sintoma:** DevTools mostra requisições indo para `bo-assistant-backend.onrender.com` mesmo rodando localmente.

**Causa:** Você está acessando via IP em vez de hostname.

**Solução (já implementada na v0.6.1):**
```javascript
const API_URL = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? 'http://localhost:8000'
    : 'https://bo-assistant-backend.onrender.com';
```

**Verificação:** Abra DevTools → Network e confirme que requisições vão para `localhost:8000`.

---

### Problema 3: Render "dorme" após 15 minutos

**Sintoma:** Primeira requisição demora 30-60 segundos após inatividade.

**Causa:** Plano gratuito do Render coloca serviço em standby após 15 min de inatividade.

**Soluções:**
1. **Gratuita:** Avisar usuários que primeira requisição pode demorar
2. **Paga ($7/mês):** Upgrade para Render Starter (servidor não dorme)
3. **Alternativa:** Adicionar health check a cada 14 min (pode ser banido)

---

### Problema 4: Quota do LLM excedida

**Sintoma:** Erro 429 ou mensagem "rate_limit".

**Soluções:**
- **Gemini 2.5 Flash:** 20 req/dia (free tier)
- **Groq Llama 3.3 70B:** 14.400 req/dia (free tier) - **Recomendado para testes**
- **Trocar provider:** No frontend ([index.html](index.html) linhas 520, 1149, 1408), mude:
  ```javascript
  llm_provider: 'groq'  // Em vez de 'gemini'
  ```

---

### Problema 5: GitHub Pages não atualiza

**Sintoma:** Mudanças no código não aparecem no site.

**Soluções:**
1. Aguarde 2-3 minutos após push
2. Limpe cache do navegador (Ctrl+Shift+R)
3. Verifique se commit foi para branch `main`
4. Confirme que GitHub Actions não falhou (aba "Actions" do repo)

---

## 📸 Automação de Screenshots e Vídeos

### Objetivo

Script [automate_release.py](../tests/e2e/automate_release.py) captura screenshots e vídeo do frontend para documentação de releases com suporte a fast-start.

### Setup

```bash
# Instalar dependências de dev (já inclui Playwright e httpx)
pip install -r backend/requirements-dev.txt

# Instalar navegadores do Playwright
playwright install
```

### Uso Básico

```bash
# No terminal (venv ativado)

# Modo completo (Seção 1 → 2 → 3)
python tests/e2e/automate_release.py --version v0.8.0

# Sem vídeo (mais rápido - ~2 min)
python tests/e2e/automate_release.py --version v0.8.0 --no-video
```

### Uso com Fast-Start (v0.7.1+)

```bash
# Apenas Seção 3 (Seções 1-2 preenchidas via API)
python tests/e2e/automate_release.py --version v0.8.0 --start-section 3 --no-video

# Apenas Seção 2 (Seção 1 preenchida via API)
python tests/e2e/automate_release.py --version v0.8.0 --start-section 2 --no-video

# Apenas Seção 3 com vídeo
python tests/e2e/automate_release.py --version v0.8.0 --start-section 3
```

**Economia de Tempo:**
- Seção 1 (completa): ~5 min
- Seção 2 (start-section 2): ~3 min (40% mais rápido)
- Seção 3 (start-section 3): ~1.5 min (70% mais rápido)

### Saída

Screenshots são salvos em `docs/screenshots/v0.8.0/`:
```
docs/screenshots/v0.8.0/
├── 01-section1-empty.png
├── 02-section1-progress.png
├── ...
├── 17-section3-start.png
├── ...
├── 24-section4-start.png
├── ...
├── 26-section4-final.png
└── demo.webm (se vídeo habilitado)
```

### Configuração

Cenários de teste estão em [test_scenarios.json](../tests/e2e/test_scenarios.json). Para adicionar novos cenários, edite este arquivo.

**Documentação completa:** [tests/e2e/README.md](../tests/e2e/README.md) e [docs/TESTING.md](TESTING.md)

---

## 📊 Limitações do Tier Gratuito

### Render Free

| Limite | Valor |
|--------|-------|
| Horas/mês | 750h (suficiente para POC) |
| Standby após inatividade | 15 minutos |
| Cold start | 30-60 segundos |
| Memória RAM | 512 MB |
| CPU | Compartilhada |

### GitHub Pages

| Limite | Valor |
|--------|-------|
| Tamanho do site | 1 GB |
| Largura de banda | 100 GB/mês |
| Builds/hora | 10 |

### Gemini 2.5 Flash (Free Tier)

| Limite | Valor |
|--------|-------|
| Requisições/dia | 20 |
| Requisições/minuto | 15 |
| Tokens de entrada/minuto | 1 milhão |

### Groq Llama 3.3 70B (Free Tier)

| Limite | Valor |
|--------|-------|
| Requisições/dia | 14.400 |
| Requisições/minuto | 30 |
| Tokens/minuto | 20.000 |

**Recomendação:** Use Groq para desenvolvimento e testes, Gemini para produção.

---

## 💰 Custos Futuros (quando escalar)

### Se precisar de mais recursos:

| Serviço | Plano | Preço/mês | Benefícios |
|---------|-------|-----------|------------|
| **Render Starter** | Starter | $7 | Servidor não dorme, 0.5 GB RAM |
| **Render Standard** | Standard | $25 | 2 GB RAM, prioridade |
| **Railway** | Pro | $5 | 500h + $5 de créditos |
| **Vercel/Netlify** | Pro | $20 | CDN global, analytics |

**Para POC, 100% gratuito é suficiente!**

---

## 🔗 Documentação Relacionada

- [README.md](../README.md) - Visão geral do projeto
- [DEVELOPMENT.md](../DEVELOPMENT.md) - Guia de desenvolvimento e debugging
- [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitetura técnica detalhada
- [API.md](API.md) - Referência completa de endpoints
- [CHANGELOG.md](../CHANGELOG.md) - Histórico de versões

---

## 👥 Suporte

Para dúvidas ou problemas:
- Abra uma [Issue](https://github.com/criscmaia/bo-assistant/issues)
- Consulte [DEVELOPMENT.md](../DEVELOPMENT.md) para debugging avançado
