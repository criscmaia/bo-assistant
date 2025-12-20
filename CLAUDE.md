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
- **LLM**: Google Gemini 2.5 Flash (20 req/dia) + Groq Llama 3.3 70B (14.4k req/dia)
- **Banco de Dados**: PostgreSQL (produção) / SQLite (local)
- **Deploy**: Render (backend) + GitHub Pages (frontend)

## Estrutura do Projeto

```
bo-assistant/
├── backend/
│   ├── main.py                    # API FastAPI (endpoints)
│   ├── state_machine.py           # Fluxo Seção 1 (6 perguntas)
│   ├── state_machine_section2.py  # Fluxo Seção 2 (8 perguntas)
│   ├── llm_service.py             # Integração Gemini + Groq
│   ├── validator.py               # Validação Seção 1
│   ├── validator_section2.py      # Validação Seção 2
│   ├── logger.py                  # Sistema de logs (PostgreSQL/SQLite)
│   ├── automate_release.py        # Automação screenshots/vídeo
│   ├── requirements.txt           # Dependências de produção
│   └── requirements-dev.txt       # Dependências de desenvolvimento
├── docs/
│   ├── index.html           # Interface principal do chat
│   └── logs.html            # Dashboard de logs
├── .env                     # Variáveis de ambiente (RAIZ)
├── CHANGELOG.md             # Histórico de versões
├── README.md                # Documentação principal
├── CLAUDE.md                # Este arquivo
└── render.yaml              # Configuração do Render
```

## Comandos para Desenvolvimento Local

```bash
# Terminal 1 - Backend (rodar do diretório RAIZ do projeto)
cd C:\AI\bo-assistant  # ou caminho do seu projeto
.\backend\venv\Scripts\activate      # Windows
source backend/venv/bin/activate     # Mac/Linux
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd docs
python -m http.server 3000 --bind 127.0.0.1

# Acessar: http://127.0.0.1:3000 ou http://localhost:3000
# (Se localhost não funcionar, use 127.0.0.1 diretamente)
```

**IMPORTANTE:** O backend DEVE ser rodado do diretório raiz do projeto para que o arquivo `.env` seja carregado corretamente.

## Fluxo da Aplicação

1. Usuário inicia sessão → `POST /new_session` → retorna `session_id` e `bo_id`
2. **Seção 1 (Contexto da Ocorrência)**: Sistema faz 6 perguntas sequenciais
3. Cada resposta é validada pelo `validator.py`
4. Respostas válidas são armazenadas no `state_machine.py`
5. Após 6 respostas, `llm_service.py` gera texto via Gemini ou Groq
6. **Seção 2 (Abordagem a Veículo)**: Usuário clica "Iniciar Seção 2"
7. Sistema faz 8 perguntas (validadas por `validator_section2.py`)
8. Após 8 respostas, novo texto é gerado
9. Todos os eventos são logados no banco via `logger.py`

## Perguntas da Seção 1 (Contexto)

1. **1.1** - Dia, data e hora do acionamento
2. **1.2** - Composição da guarnição e prefixo
3. **1.3** - Natureza do empenho
4. **1.4** - Ordem de serviço / COPOM / DDU
5. **1.5** - Local exato da ocorrência
6. **1.6** - Histórico do local / facção

## Perguntas da Seção 2 (Abordagem a Veículo)

1. **2.0** - Havia veículo? (se NÃO, pula seção)
2. **2.1** - Marca e modelo do veículo
3. **2.2** - Placa do veículo (formato Mercosul)
4. **2.3** - Ocupantes (graduação, nome, função)
5. **2.4** - Posição do veículo
6. **2.5** - Atitude do condutor
7. **2.6** - Descrição da abordagem
8. **2.7** - Motivo da suspeição

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
# .env (na RAIZ do projeto, não em backend/)
GEMINI_API_KEY=sua_chave_aqui
GROQ_API_KEY=sua_chave_groq_aqui
DATABASE_URL=postgresql://...  # Apenas em produção
```

**IMPORTANTE:** O arquivo `.env` deve estar na raiz do projeto (`C:\AI\bo-assistant\.env`) para ser carregado corretamente pelo backend.

## Princípios de Desenvolvimento

1. **Nunca inventar informações** - O LLM só usa dados fornecidos pelo usuário
2. **Validação inteligente** - Rejeita respostas vagas sem ser excessivamente rígido
3. **Encoding UTF-8** - Sempre usar UTF-8 em arquivos Python (acentos!)
4. **Código simples** - JavaScript vanilla, sem frameworks complexos

## Versão Atual

**v0.6.4** (20/12/2025)
- ✅ Correção crítica: Sincronização backend durante restauração de rascunhos
- ✅ Sistema de rascunhos 100% funcional para Seção 1 e Seção 2
- Backend atualiza `currentQuestionStep` durante loop de sincronização
- Validação de respostas alinhada com pergunta apresentada
- Suporte ao Groq API (Llama 3.3 70B) - 14.400 req/dia
- Arquitetura multi-provider (Gemini + Groq)

## Equipe

- **Cristiano Maia** - Delivery Manager & Tech Lead
- **Claudio Moreira** - Especialista em Redação de BOs (Sargento PM)

## Notas Importantes

- O backend no Render (free tier) "dorme" após 15 min de inatividade
- Primeira requisição pode demorar 30-60s para "acordar"
- Frontend é estático no GitHub Pages (deploy automático no push)
- Testar localmente ANTES de fazer push para produção

---

## 🐛 Debugging Tips

### Backend não está gerando texto (Erro 500)

**Diagnóstico:**
1. Verificar se API keys estão carregadas:
   - Adicionar print temporário em `llm_service.py.__init__()`:
   ```python
   print(f"DEBUG: gemini_key = {os.getenv('GEMINI_API_KEY')[:10]}...")
   print(f"DEBUG: groq_key = {os.getenv('GROQ_API_KEY')[:10]}...")
   ```
   - Se retornar `None`, arquivo `.env` não está sendo carregado

2. Verificar CWD (current working directory):
   - `python-dotenv` carrega `.env` do diretório onde o comando foi executado
   - **ERRADO:** `cd backend && uvicorn main:app` (procura `.env` em `backend/`)
   - **CORRETO:** `python -m uvicorn backend.main:app` (procura `.env` na raiz)

3. Verificar se porta 8000 está livre:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   taskkill /F /IM python.exe

   # Mac/Linux
   lsof -i :8000
   kill -9 <PID>
   ```

### Frontend conectando ao Render em vez de localhost

**Problema:** DevTools mostra requisições indo para `bo-assistant-backend.onrender.com` mesmo rodando localmente.

**Causa:** Código JavaScript detecta apenas `localhost`, não `127.0.0.1`.

**Solução (já implementada na v0.6.1):**
```javascript
const API_URL = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? 'http://localhost:8000'
    : 'https://bo-assistant-backend.onrender.com';
```

### Endpoint de edição retornando erro 500

**Sintoma:** `ValueError: too many values to unpack (expected 2)`

**Causa:** Sessões foram refatoradas de tupla para dict, mas endpoint de edição não foi atualizado.

**Como debugar:**
1. Verificar estrutura em `main.py`:
   ```python
   print(f"DEBUG: sessions[session_id] = {sessions[session_id]}")
   ```
2. Estrutura correta (v0.5.0+):
   ```python
   {
       "bo_id": "BO-20251220-xxxxx",
       "sections": {
           1: StateMachine(),
           2: StateMachineSection2()
       }
   }
   ```

### Automação de screenshots com problemas

**Problema 1:** Element não é clicável
- **Solução:** Usar `wait_for_selector(..., state='visible')` antes de interagir

**Problema 2:** Screenshot mostra área errada
- **Causa:** Scroll executado antes de ação que também causa scroll
- **Solução:** Executar ações → aguardar efeitos → scroll → screenshot

**Problema 3:** Sidebar/modal com conteúdo sobreposto
- **Causa:** `full_page=True` faz scroll virtual, elementos fixed aparecem através
- **Solução:** Usar `full_page=False` para overlays

### Quota do LLM excedida

**Sintoma:** Erro 429 ou "rate_limit" na mensagem.

**Soluções:**
- Gemini 2.5 Flash: 20 req/dia (free tier)
- Groq Llama 3.3 70B: 14.400 req/dia (free tier) - **Recomendado para testes**
- Trocar provider no frontend (`index.html` linhas 520, 1149, 1408): `llm_provider: 'groq'`

### Logs de debug temporários

**Boas práticas:**
1. Sempre adicionar comentário `# DEBUG - remover antes do commit`
2. Usar prefixo claro: `print(f"DEBUG GROQ ERROR: {error}")`
3. Limpar antes de fazer merge para main
4. Evitar deixar prints em produção (poluem logs do Render)

---
