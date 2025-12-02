# 🚀 Deploy no Render (Gratuito)

## Preparação

### 1. Criar repositório no GitHub

```bash
# Na pasta bo-assistant/
git init
git add .
git commit -m "POC v0.1 - Seção 1 funcionando"

# Criar repo no GitHub e conectar
git remote add origin https://github.com/SEU_USUARIO/bo-assistant.git
git push -u origin main
```

### 2. Adicionar arquivos necessários

Crie estes arquivos na **raiz do projeto** (`bo-assistant/`):

#### `render.yaml`
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
```

#### `.gitignore`
```
# Python
venv/
__pycache__/
*.pyc
*.pyo
.env

# IDEs
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

### 3. Atualizar frontend para usar URL do deploy

Edite `frontend/index.html`, linha ~65:

```javascript
// ANTES (localhost):
const API_URL = 'http://localhost:8000';

// DEPOIS (Render):
const API_URL = 'https://bo-assistant-backend.onrender.com';
// OU usar variável que detecta ambiente:
const API_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000' 
    : 'https://bo-assistant-backend.onrender.com';
```

---

## Deploy

### 1. Criar conta no Render
- Acesse: https://render.com
- Faça login com GitHub

### 2. Criar Web Service
1. Clique em "New +" → "Web Service"
2. Conecte seu repositório GitHub
3. Configure:
   - **Name:** `bo-assistant-backend`
   - **Region:** Oregon (mais próximo)
   - **Branch:** `main`
   - **Root Directory:** deixe vazio
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

### 3. Adicionar variáveis de ambiente
1. Na página do service, vá em "Environment"
2. Adicione:
   - **Key:** `GEMINI_API_KEY`
   - **Value:** sua chave do Gemini

### 4. Deploy automático
- Render vai fazer build e deploy
- Aguarde ~5 minutos
- URL será: `https://bo-assistant-backend.onrender.com`

---

## Servir Frontend

### Opção 1: GitHub Pages (Recomendado - Grátis)

1. No seu repositório GitHub, vá em **Settings** → **Pages**
2. Em "Source", selecione a branch `main` e pasta `/frontend`
3. Salve
4. Aguarde ~2 minutos
5. URL será: `https://SEU_USUARIO.github.io/bo-assistant/`

### Opção 2: Render Static Site

1. No Render, clique "New +" → "Static Site"
2. Conecte o mesmo repositório
3. Configure:
   - **Build Command:** deixe vazio
   - **Publish Directory:** `frontend`
4. Deploy

---

## Testar

1. Acesse a URL do frontend
2. Responda as 6 perguntas
3. Veja o texto gerado
4. Compartilhe a URL com o Claudio!

---

## Limitações do Tier Gratuito

**Render Free:**
- Servidor "dorme" após 15 min de inatividade
- Primeira requisição após dormir demora ~30s
- 750 horas/mês grátis (suficiente para POC)

**Solução:** Avisar o Claudio que a primeira requisição pode demorar.

---

## Custos Futuros (quando escalar)

- **Render Starter ($7/mês):** Servidor não dorme
- **Railway ($5/mês):** 500h + $5 de créditos
- **Vercel/Netlify:** Frontend sempre grátis

Para POC, **100% gratuito** é suficiente!
