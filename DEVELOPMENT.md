# 🛠️ Guia de Desenvolvimento - BO Inteligente

**Versão:** v0.13.0
**Última atualização:** 02/01/2026

Este documento serve como memória institucional do projeto, documentando decisões arquiteturais, comandos essenciais e guias de debugging para desenvolvedores.

---

## 🚀 Quick Start

### Ambiente Local

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
```

**⚠️ CRÍTICO:** O backend DEVE ser rodado do diretório raiz do projeto para que o arquivo `.env` seja carregado corretamente pelo `python-dotenv`.

### Links de Produção

| Ambiente | URL |
|----------|-----|
| Frontend | https://criscmaia.github.io/bo-assistant/ |
| Backend API | https://bo-assistant-backend.onrender.com |
| Dashboard Logs | https://criscmaia.github.io/bo-assistant/logs.html |
| Repositório | https://github.com/criscmaia/bo-assistant |

---

## 🔄 CI/CD - GitHub Actions

**Versão:** v0.12.9+

O projeto possui workflow automatizado de CI/CD que roda em cada push ou Pull Request para a branch `main`.

### O que o CI executa:
- ✅ Testes unitários (`tests/unit/`)
- ✅ Testes de integração (`tests/integration/`)
- ❌ Testes E2E **não** rodam no CI (precisam de Playwright/browser)

### Configuração do Workflow:
- **Arquivo:** `.github/workflows/test.yml`
- **Runner:** Ubuntu latest
- **Python:** 3.13
- **Timeout:** 10 minutos
- **Variáveis:** `GEMINI_API_KEY` e `GROQ_API_KEY` mockadas

### Rodar testes localmente (igual ao CI):

**Windows (PowerShell):**
```powershell
$env:PYTHONPATH = "backend"
pytest tests/unit tests/integration -v --tb=short
```

**Linux/Mac:**
```bash
export PYTHONPATH=backend
pytest tests/unit tests/integration -v --tb=short
```

### Badge de Status:
O README.md exibe o status dos testes em tempo real via badge do GitHub Actions.

---

## 🏗️ Princípios de Desenvolvimento

1. **Nunca inventar informações** - O LLM só usa dados fornecidos pelo usuário
2. **Validação inteligente** - Rejeita respostas vagas sem ser excessivamente rígido
3. **Encoding UTF-8** - Sempre usar UTF-8 em arquivos Python (acentos!)
4. **Código simples** - JavaScript vanilla, sem frameworks complexos
5. **Testar localmente ANTES** - Não fazer push direto para produção
6. **Componentes modulares e reutilizáveis** (v0.13.0+)
7. **CSS modular por funcionalidade** - Sem dependências externas
8. **Separação clara de responsabilidades** - Entre componentes

---

## 📐 Decisões Arquiteturais (ADRs)

**Nota:** ADRs complementam o CHANGELOG.md:
- **CHANGELOG.md** = **O QUÊ** mudou e **QUANDO** (timeline de mudanças)
- **ADRs** = **POR QUÊ** as decisões foram tomadas (contexto arquitetural para futuras decisões)

### ADR-001: Sessões como Dict (v0.5.0)

**Contexto:** Na v0.4.x, sessões eram armazenadas como tuplas `(bo_id, state_machine)`.

**Decisão:** Migrar para dicionários estruturados para suportar múltiplas seções.

**Estrutura:**
```python
sessions[session_id] = {
    "bo_id": "BO-20251220-xxxxx",
    "sections": {
        1: BOStateMachine(),           # Seção 1: Contexto (1.1-1.6)
        2: BOStateMachineSection2()    # Seção 2: Veículo (2.1-2.8)
    },
    "current_section": 1,
    "section1_text": "",
    "section2_text": ""
}
```

**Impacto:** Facilita expansão para Seções 3-8 sem refatoração adicional.

---

### ADR-002: Groq como LLM Secundário (v0.6.0)

**Contexto:** Gemini 2.5 Flash tem limite de 20 req/dia (free tier), insuficiente para testes.

**Decisão:** Adicionar Groq Llama 3.3 70B (14.400 req/dia) como provider alternativo.

**Implementação:**
- `llm_service.py` suporta ambos os providers
- Frontend permite escolher via parâmetro `llm_provider: 'gemini'` ou `'groq'`
- Fallback automático se um provider falhar

**Razão:** Permite desenvolvimento e testes intensivos sem limite de quota.

---

### ADR-003: localStorage para Rascunhos (v0.6.2)

**Contexto:** Usuários perdiam progresso ao fechar o navegador.

**Decisão:** Implementar salvamento automático de rascunhos com localStorage (7 dias de expiração).

**Estrutura:**
```javascript
{
    "sessionId": "uuid",
    "boId": "BO-20251220-xxxxx",
    "sections": {
        "1": {
            "answers": { "1.1": "resposta1", ... },
            "currentStep": "1.3",
            "completed": false,
            "generatedText": ""
        },
        "2": { ... }
    },
    "timestamp": 1703000000000
}
```

**Trade-off:** Dados ficam apenas no navegador (sem sincronização cross-device), mas implementação é trivial e não requer backend adicional.

---

### ADR-004: Endpoint `/sync_session` (v0.6.4)

**Contexto:** Restaurar rascunhos com múltiplas chamadas `/chat` era lento (10+ requisições).

**Decisão:** Criar endpoint dedicado que aceita estado completo da sessão e reconstrói backend atomicamente.

**Vantagem:** Restauração 10x mais rápida (1 requisição vs 10+).

**Payload:**
```json
{
    "session_id": "uuid",
    "bo_id": "BO-20251220-xxxxx",
    "sections": {
        "1": {
            "answers": { ... },
            "current_step": "complete",
            "generated_text": "texto gerado"
        }
    },
    "current_section": 1
}
```

---

### ADR-005: Renumeração IDs Seção 2 (v0.6.4)

**Contexto:** Seção 1 usava IDs 1.1-1.6, mas Seção 2 usava 2.0-2.7 (inconsistente).

**Decisão:** Renumerar Seção 2 para 2.1-2.8 (8 perguntas).

**Razão:** Consistência visual e facilita expansão para Seções 3-8.

**Migração:** Frontend detecta rascunhos antigos e converte automaticamente.

---

### ADR-006: Redesign UX Completo (v0.13.0)

**Data:** 02/01/2026

**Contexto:**
- Sistema anterior tinha layout monolítico com sidebar + container único
- Crescimento de 6 para 53+ perguntas tornava navegação confusa
- CSS inline misturado com Tailwind via CDN aumentava complexidade
- Falta de separação clara entre componentes dificultava manutenção
- Necessidade de melhor feedback visual de progresso

**Decisão:**
Implementar redesign completo do frontend com arquitetura modular:

1. **Componentes JavaScript (6):**
   - `ProgressBar.js`: Barra horizontal com 8 nós + 4 estados visuais
   - `SectionContainer.js`: Gerenciamento independente de seção
   - `TextInput.js`: Input de texto com validação sofisticada
   - `SingleChoice.js`: Botões SIM/NÃO para perguntas binárias
   - `MultipleChoice.js`: Checkboxes para perguntas de múltipla escolha
   - `FinalScreen.js`: Tela de conclusão com resumo

2. **CSS Modular (8 arquivos):**
   - `main.css`: Reset, tipografia, layout global
   - `progress-bar.css`: Estilos da barra de progresso
   - `section-container.css`: Container, chat, badges
   - `inputs.css`: 3 componentes de input
   - `final-screen.css`: Tela de conclusão
   - `draft-modal.css`: Modal de rascunhos
   - `utilities.css`: Helpers, loading, toasts
   - `responsive.css`: Media queries mobile/tablet

3. **Arquitetura:**
   - `BOApp.js` como orquestrador central (estado global, API, navegação)
   - `sections.js` como fonte única de verdade para estrutura de seções
   - Comunicação via callbacks entre componentes
   - Estado gerenciado de forma unidirecional

**Consequências:**

✅ **Positivas:**
- UX significativamente melhorada (navegação visual clara)
- Código mais organizado e manutenível
- Reutilização de componentes
- CSS sem dependências externas (zero bloat)
- Performance melhorada (carregamento modular)
- Facilita testes isolados de componentes

⚠️ **Negativas:**
- Maior complexidade inicial (6 classes JS vs 1 monólito)
- Breaking changes na estrutura HTML
- Curva de aprendizado para novos desenvolvedores
- Mais arquivos para gerenciar (8 CSS + 6 JS)

**Status:** ✅ Implementado (v0.13.0)

---

## 🐛 Guia de Debugging

### Problema 1: Backend não gera texto (Erro 500)

**Sintoma:** Erro 500 ao clicar "Gerar texto".

**Diagnóstico:**
1. Verificar se API keys estão carregadas:
   ```python
   # Adicionar em llm_service.py.__init__()
   print(f"DEBUG: gemini_key = {os.getenv('GEMINI_API_KEY')[:10]}...")
   print(f"DEBUG: groq_key = {os.getenv('GROQ_API_KEY')[:10]}...")
   ```
   - Se retornar `None`, arquivo `.env` não está sendo carregado.

2. Verificar CWD (current working directory):
   - `python-dotenv` carrega `.env` do diretório onde o comando foi executado.
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

---

### Problema 2: Frontend conecta ao Render em vez de localhost

**Sintoma:** DevTools mostra requisições indo para `bo-assistant-backend.onrender.com` mesmo rodando localmente.

**Causa:** Código JavaScript detectava apenas `localhost`, não `127.0.0.1`.

**Solução (já implementada na v0.6.1):**
```javascript
const API_URL = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? 'http://localhost:8000'
    : 'https://bo-assistant-backend.onrender.com';
```

---

### Problema 3: Endpoint de edição retornando erro 500

**Sintoma:** `ValueError: too many values to unpack (expected 2)`

**Causa:** Sessões foram refatoradas de tupla para dict (v0.5.0), mas endpoint de edição não foi atualizado.

**Como debugar:**
1. Verificar estrutura em [main.py](backend/main.py):
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

---

### Problema 4: Automação de screenshots com problemas

**Problema 1:** Element não é clicável
- **Solução:** Usar `wait_for_selector(..., state='visible')` antes de interagir.

**Problema 2:** Screenshot mostra área errada
- **Causa:** Scroll executado antes de ação que também causa scroll.
- **Solução:** Executar ações → aguardar efeitos → scroll → screenshot.

**Problema 3:** Sidebar/modal com conteúdo sobreposto
- **Causa:** `full_page=True` faz scroll virtual, elementos fixed aparecem através.
- **Solução:** Usar `full_page=False` para overlays.

---

### Problema 5: Quota do LLM excedida

**Sintoma:** Erro 429 ou "rate_limit" na mensagem.

**Soluções:**
- Gemini 2.5 Flash: 20 req/dia (free tier)
- Groq Llama 3.3 70B: 14.400 req/dia (free tier) - **Recomendado para testes**
- Trocar provider no frontend ([index.html](docs/index.html) linhas 520, 1149, 1408): `llm_provider: 'groq'`

---

### Problema 6: ProgressBar não atualiza estados

**Sintoma:** Seções permanecem em estado `pending` mesmo após serem completadas

**Causa:** Estado da seção não está sendo sincronizado com ProgressBar via `setCurrentSection()`

**Solução:**
1. Verificar se `BOApp._updateAllSectionsProgress()` está sendo chamado após cada mudança de estado
2. Verificar se `sectionState.status` está sendo atualizado corretamente (`completed`, `skipped`, `in_progress`)
3. Verificar console para erros em `ProgressBar.updateSectionState()`

---

### Problema 7: SectionContainer não renderiza texto gerado

**Sintoma:** Após completar seção, texto gerado não aparece (área vazia)

**Causa:** Campo `generatedText` não está sendo passado para `loadSection()`

**Solução:**
1. Verificar se API retorna `generated_text` no response
2. Verificar se `sectionState.generatedText` está sendo salvo no estado global
3. Verificar se `loadSection()` recebe `generatedText` no objeto options
4. Adicionar log: `console.log('[SectionContainer] generatedText:', this.generatedText)`

---

### Problema 8: Follow-up questions não aparecem

**Sintoma:** Após responder pergunta condicional (ex: 1.5 = "SIM"), próxima pergunta não aparece

**Causa:** Sistema de `followUpQueue` não está sendo processado ou perguntas condicionais não estão configuradas

**Solução:**
1. Verificar se pergunta tem `followUpQuestions` definido em `sections.js`
2. Verificar se `_handleFollowUpQuestions()` está sendo chamado após resposta
3. Verificar se `followUpQueue` está sendo populado: `console.log('[SectionContainer] followUpQueue:', this.followUpQueue)`
4. Para rascunhos: verificar se `_restoreFollowUpState()` está reconstruindo a fila

---

### Problema 9: Skip reason mostra "motivo não especificado"

**Sintoma:** Ao pular seção, mensagem mostra genérica em vez de específica

**Causa:** Campo `skipReason` não está sendo passado ao carregar seção via `_navigateToSection()`

**Solução:**
1. Verificar se API retorna `generated_text` quando `section_skipped: true`
2. Verificar se `sectionState.skipReason` está sendo salvo: `console.log('[BOApp] skipReason:', sectionState.skipReason)`
3. Verificar se `loadSection()` em `_navigateToSection()` passa `skipReason: sectionState.skipReason`
4. Adicionar log em SectionContainer: `console.log('[SectionContainer] skipReason recebido:', options.skipReason)`

---

## 📝 Boas Práticas

### Logs de Debug Temporários

1. Sempre adicionar comentário `# DEBUG - remover antes do commit`
2. Usar prefixo claro: `print(f"DEBUG GROQ ERROR: {error}")`
3. Limpar antes de fazer merge para main
4. Evitar deixar prints em produção (poluem logs do Render)

### Fluxo de Deploy

#### Passo 1: Testes Locais
1. Testar localmente com Groq (provider principal - 14.4k req/dia)
   - Gemini existe como fallback mas não é testado rotineiramente
2. Verificar se nenhum print de debug foi esquecido
3. Rodar testes E2E com Playwright (gera screenshots + vídeo)
   ```bash
   # Terminal 3 (com backend + frontend rodando)
   python tests/e2e/automate_release.py --version 0.8.0 --no-video
   # OU com vídeo (mais demorado, mas recomendado)
   python tests/e2e/automate_release.py --version 0.8.0
   # Fast-start (apenas Seção 4)
   python tests/e2e/automate_release.py --version 0.8.0 --start-section 4 --no-video
   ```

#### Passo 2: Atualizar Versão (CRÍTICO!)
Atualizar versão em **TODOS** estes locais (não é opcional):

**Backend:**
- `backend/main.py` linha 34: `APP_VERSION = "0.8.0"`

**Frontend:**
- `docs/index.html`: buscar por `version:` (constante no JS)

**Documentação:**
- `README.md`: versão no rodapé
- `CHANGELOG.md`: versão e release notes
- `DEVELOPMENT.md` linha 3: versão
- `docs/SETUP.md` linha 3: versão
- `docs/API.md` linha 3: versão
- `docs/ARCHITECTURE.md` linha 3: versão
- `docs/ROADMAP.md` linha 3: versão
- `docs/TESTING.md` linha 3: versão

**Dica:** Use find/replace no editor:
```
Buscar: v0.7.x
Substituir: v0.8.0
Buscar: 0\.7\.x (em JSON)
Substituir: 0.8.0
```

#### Passo 3: Commit e Push
```bash
git add -A
git commit -m "Release v0.8.0: Seção 4 (Entrada em Domicílio)"
git push origin main
```

#### Passo 4: Deploy Automático
- Backend no Render faz deploy automático (~2 min)
- Frontend no GitHub Pages atualiza instantaneamente

#### Passo 5: Validação em Produção
- Testar em produção com casos de teste reais
- Verificar se backend acordou (primeira requisição pode demorar 30-60s)
- Validar gerações de texto para as 4 seções

### Fluxo de Correção de Bugs com Claude Code Skills

Ao usar o skill `/fix-issue` para corrigir bugs, siga este fluxo padronizado:

#### Passo 1: Iniciar Correção
```bash
/fix-issue 6
```

#### Passo 2: Implementar Correção
- Analise o bug descrito na issue
- Identifique os arquivos relacionados
- Implemente a correção
- Teste localmente

#### Passo 3: Atualizar Versão
Após implementar a correção, atualize a versão:

1. Encontre a versão atual em `backend/main.py` (linha ~34):
   ```python
   APP_VERSION = "0.12.2"
   ```

2. Incremente a versão patch (0.12.2 → 0.12.3) ou minor (0.12.x → 0.13.0)

3. Faça commit com a versão:
   ```bash
   git add -A
   git commit -m "chore: Atualizar versão de v0.12.2 para v0.12.3"
   ```

#### Passo 4: Mover para Teste Local
Após atualizar a versão, mova a issue para "🧪 Teste Local":
```bash
/test-local 6
```

Isso marca a issue como pronta para testes locais antes de ir para produção.

**Resumo do fluxo:**
1. `/fix-issue N` → Corrigir bug
2. Atualizar versão e fazer commit
3. `/test-local N` → Mover para coluna de Teste Local no Kanban

### Variáveis de Ambiente

```bash
# .env (na RAIZ do projeto, não em backend/)
GEMINI_API_KEY=sua_chave_aqui
GROQ_API_KEY=sua_chave_groq_aqui
DATABASE_URL=postgresql://...  # Apenas em produção (Render)
```

**Nota:** O arquivo `.env` já está no `.gitignore` e não será versionado.

---

### Componentes Modulares (v0.13.0+)

**Testar componentes isoladamente:**
```javascript
// Teste isolado de TextInput
const input = new TextInput({
    placeholder: 'Digite sua resposta...',
    validation: { required: true, minLength: 5 },
    onSubmit: (value) => console.log('Resposta:', value)
});
document.body.appendChild(input.render());
```

**Debugar state management:**
```javascript
// No BOApp.js, adicionar logs estratégicos
_updateSectionState(sectionId, updates) {
    console.log('[BOApp] Updating section', sectionId, 'with:', updates);
    Object.assign(this.state.sections[sectionId], updates);
    console.log('[BOApp] New state:', this.state.sections[sectionId]);
}
```

**Verificar comunicação entre componentes:**
- BOApp → ProgressBar: `setCurrentSection()`, `updateSectionState()`
- BOApp → SectionContainer: `loadSection()`, callbacks `onAnswer`, `onNavigateNext`
- SectionContainer → Input Components: `render()`, callback `onSubmit`

---

## 🔗 Documentação Relacionada

- [README.md](README.md) - Visão geral e instruções de uso
- [docs/SETUP.md](docs/SETUP.md) - Guia completo de setup e deploy
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Arquitetura técnica detalhada
- [docs/API.md](docs/API.md) - Referência completa de endpoints
- [docs/ROADMAP.md](docs/ROADMAP.md) - Planejamento de features futuras
- [docs/CLAUDE_CODE.md](docs/CLAUDE_CODE.md) - Guia completo Claude Code (modelos, custos, comandos)
- [docs/TESTING.md](docs/TESTING.md) - Guia completo de testes
- [CHANGELOG.md](CHANGELOG.md) - Histórico completo de versões
- [docs/archive/](docs/archive/) - Documentação de versões anteriores (v0.12.9, propostas redesign)

---

## 👥 Equipe

- **Cristiano Maia** - Delivery Manager & Tech Lead
- **Claudio Moreira** - Especialista em Redação de BOs (Sargento PM)

---

## ⚠️ Notas Importantes

- O backend no Render (free tier) "dorme" após 15 min de inatividade
- Primeira requisição pode demorar 30-60s para "acordar"
- Frontend é estático no GitHub Pages (deploy automático no push)
- Render usa PostgreSQL em produção, SQLite localmente
