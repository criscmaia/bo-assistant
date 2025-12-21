# Changelog v0.6.4

## 📜 Histórico de Features por Fase

### ✅ Fase 1 Concluída - Validação e Polimento (v0.4.1 - v0.6.4)

#### v0.6.0-v0.6.4 (Dez 2025)
- [x] **Groq API Integration** (v0.6.0) - Llama 3.3 70B com 14.400 req/dia
- [x] **Arquitetura Multi-Provider** - Gemini + Groq com fallback automático
- [x] **Sistema de Rascunhos** (v0.6.2) - Salvamento automático com localStorage (7 dias)
- [x] **Endpoint `/sync_session`** (v0.6.4) - Restauração atômica de rascunhos (10x mais rápido)
- [x] **Renumeração IDs Seção 2** (v0.6.4) - 2.0-2.7 → 2.1-2.8 para consistência
- [x] **Correção crítica persistência** (v0.6.4) - Rascunho não persiste após BO completo
- [x] **Migração automática** - Frontend detecta e converte rascunhos v0.6.3
- [x] **Correções edição e validação** (v0.6.1-v0.6.3) - Endpoint PUT, estrutura dict
- [x] **Suporte a múltiplas seções em rascunhos** - localStorage com Seção 1 + Seção 2

#### v0.5.1 (Dez 2025) - UX Multi-Seção
- [x] **UX Multi-Seção** - Melhorias críticas de experiência do usuário
- [x] Container persistente de textos gerados (todas seções visíveis)
- [x] Numeração completa de perguntas ([1.1], [2.3])
- [x] Sidebar com todas 8 seções (completadas, atual, futuras)
- [x] Botão "Copiar BO Completo" quando há 2+ seções
- [x] Layout responsivo (mobile/tablet/desktop)
- [x] Accordion nativo (`<details>`) para performance

#### v0.5.0 (Dez 2025) - Seção 2
- [x] **Seção 2: Abordagem a Veículo** - 8 perguntas (inicialmente 2.0-2.7)
- [x] Validação de placa Mercosul (ABC1D23, ABC-1D23)
- [x] Lógica condicional (pular seção se não houve veículo)
- [x] Geração de texto via LLM para Seção 2
- [x] Endpoint `/start_section/{section_number}`
- [x] Refatoração de sessions para suportar múltiplas seções (tupla → dict)

#### v0.4.1 (Dez 2025) - Validação e Logs
- [x] Salvamento automático de rascunho (localStorage, 7 dias)
- [x] Validação de data/hora futura
- [x] Sugestão de data/hora atual
- [x] Correção de encoding UTF-8
- [x] Dashboard de logs
- [x] Sistema de feedback (👍👎)

---

## [0.6.4] - 2025-12-20 🎯 **CORREÇÃO CRÍTICA: Sistema de Rascunhos**

### ✨ Novo - Endpoint de Sincronização em Bloco
- **CRÍTICO: Implementado `/sync_session` para restauração de rascunhos**
  - Problema anterior: `restoreFromDraft()` fazia 1 requisição HTTP por resposta (14 requests para BO completo)
  - Tempo anterior: 14-20 segundos (1-1.5s por request)
  - Risco: Estado inconsistente se requisição falhasse no meio
  - Solução: Endpoint que processa todas as respostas atomicamente em 1 requisição
  - Performance: **10-14x mais rápido** (1-2s vs 14-20s)
  - Garantia: Sincronização atômica (ou processa tudo, ou falha tudo)
  - Arquivos: `backend/main.py` linhas 422-508

### 🔧 Refatorado - Sistema de Rascunhos v0.6.4
- **Enhanced saveDraft() - Estrutura completa**
  - Agora salva: `chatHistory` + `generatedTexts` + `sectionStatuses`
  - Permite restauração exata da interface visual
  - Arquivos: `docs/index.html` linhas 380-439

- **Reescrito restoreFromDraft() - Sincronização em bloco**
  - Usa `/sync_session` em vez de loop serial de 14 requests
  - Migração automática de IDs v0.6.3 (2.0-2.7 → 2.1-2.8)
  - Fallback para rascunhos sem `chatHistory`
  - Estado sincronizado atomicamente com backend
  - Arquivos: `docs/index.html` linhas 475-679

### 🔄 Alterado - Renumeração de IDs da Seção 2
- **BREAKING CHANGE: IDs renumerados para consistência**
  - Antes: 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7
  - Agora: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8
  - Motivação: Padrão consistente com Seção 1 (que usa 1.1-1.6)
  - Compatibilidade: Migração automática para rascunhos v0.6.3
  - Arquivos:
    - Backend: `state_machine_section2.py` (linhas 14-24)
    - Backend: `validator_section2.py` (linhas 17-87)
    - Frontend: `index.html` (linhas 307-316)

### ✨ Novo - Lógica de Seção "Não Aplicável"
- **Seção 2 pulada quando não há veículo**
  - Pergunta 2.1: "Havia veículo?"
  - Se resposta = "NÃO" → Seção marcada como `NOT_APPLICABLE`
  - UI mostra texto explicativo em cinza/itálico
  - BO finalizado (até Seção 3 ser implementada)
  - Arquivos:
    - Backend: `state_machine_section2.py` (linhas 59-67, 91-95)
    - Backend: `main.py` (linhas 243-269)
    - Frontend: `index.html` (linhas 1550-1570)

### 🐛 Corrigido - Persistência de Rascunho Após Conclusão
- **CRÍTICO: Rascunho aparecia após completar todas as seções**
  - Bug #1: `answersState` resetado ao iniciar Seção 2 (linha 1541)
    - Causava perda de respostas da Seção 1
    - Solução: Removido reset, `answersState` agora mantém todas as respostas
  - Bug #2: `beforeunload` salvava rascunho mesmo após BO completo
    - Solução: Adicionada flag `boCompleted` [index.html:328](docs/index.html#L328)
    - Flag marcada como `true` quando Seção 2 finaliza [index.html:1575](docs/index.html#L1575)
    - `beforeunload` verifica `!boCompleted` antes de salvar [index.html:1653](docs/index.html#L1653)
  - Bug #3: Flag não resetada em nova sessão
    - Solução: `boCompleted = false` em `startSession()` [index.html:1351](docs/index.html#L1351)
  - Arquivos: `docs/index.html` (linhas 328, 1351, 1402, 1575, 1653)

### 🧪 Testes
- **8 testes backend (test_backend_changes.py)**: ✅ 100% passando
- **4 testes integração (test_integration_sync.py)**: ✅ 100% passando
  - Sincronização Seção 1 incompleta
  - Sincronização Seção 2 incompleta
  - Sincronização completa (14 respostas)
  - Seção 2 pulada (NÃO havia veículo)
- **Teste manual persistência**: ✅ 100% passando
  - Rascunho salvo até pergunta 2.7 → Recarrega → Modal aparece ✓
  - Completa 2.8 → Recarrega → Modal NÃO aparece ✓

### 🔍 Impacto
- **4 arquivos modificados** (3 backend, 1 frontend)
- **~500 linhas** alteradas/adicionadas
- **Compatibilidade retroativa** com v0.6.3 (migração automática)
- **Performance**: Restauração de rascunho 10x mais rápida
- **Consistência**: IDs alinhados, estado sincronizado atomicamente

---

## [0.6.3] - 2025-12-20

### 🐛 Corrigido - Restauração de Rascunhos com Múltiplas Seções
- **CRÍTICO: Respostas restauradas fora de ordem**
  - Problema: `Object.entries()` não garante ordem, causava respostas da Seção 2 aparecerem na Seção 1
  - Exemplo: Resposta de 2.1 aparecia em 1.1, resposta de 2.2 aparecia em 1.2
  - Solução: Implementado sort customizado que ordena por seção e step numericamente:
    ```javascript
    const sortedSteps = Object.keys(answersState).sort((a, b) => {
        const [sectionA, stepA] = a.split('.').map(Number);
        const [sectionB, stepB] = b.split('.').map(Number);
        if (sectionA !== sectionB) return sectionA - sectionB;
        return stepA - stepB;
    });
    ```
  - Arquivos: `docs/index.html` linhas 519-524

- **CRÍTICO: Backend não iniciava Seção 2 ao restaurar rascunho**
  - Problema: Ao restaurar rascunho da Seção 2, backend continuava na Seção 1
  - Solução: Adicionada chamada `POST /start_section/2` antes de sincronizar respostas da Seção 2
  - Arquivos: `docs/index.html` linhas 532-543

---

## [0.6.2] - 2025-12-20

### 🐛 Corrigido - Sistema de Rascunhos (LocalStorage)
- **CRÍTICO: Sistema de rascunhos quebrado com Seção 2**
  - Problema 1: `saveDraft()` não salvava `currentSection`, causando erro ao restaurar
  - Problema 2: `formatDraftPreview()` sempre mostrava "X/6" mesmo na Seção 2 (deveria mostrar "X/14")
  - Problema 3: `restoreFromDraft()` assumia apenas Seção 1, quebrava com perguntas 2.x
  - Solução:
    - `saveDraft()` agora salva `currentSection` e atualiza version para '0.6.2'
    - `formatDraftPreview()` detecta automaticamente Seção 2 via `step.startsWith('2.')`
    - `restoreFromDraft()` refatorado para suportar ambas seções:
      - Restaura `currentSection` com fallback para v0.5.x
      - Busca perguntas de `SECTION1_QUESTIONS` ou `SECTION2_QUESTIONS` conforme step
      - Calcula progresso dinamicamente (6 ou 8 perguntas)
      - Determina próxima pergunta baseada em `sectionNum` e `stepNum`
  - Arquivos: `docs/index.html` linhas 359, 436-461, 475-583

### 🧪 Testes
- Adicionado script `test_draft_recovery.py` com Playwright para validar restauração de rascunhos
- Cobertura: Seção 1 (3 perguntas) e Seção 2 (8 perguntas da S1 + 2 da S2)

---

## [0.6.1] - 2025-12-20

### 🐛 Corrigido - Backend
- **CRÍTICO: Arquivo .env não estava sendo carregado**
  - Problema: Backend rodando de `backend/` não carregava `.env` corretamente
  - Solução: `.env` movido para raiz do projeto (`C:\AI\bo-assistant\.env`)
  - Backend deve ser iniciado do diretório raiz: `python -m uvicorn backend.main:app`
  - GROQ_API_KEY agora é carregado corretamente na inicialização

- **Endpoint de edição quebrado após refatoração multi-seção**
  - Problema: `PUT /chat/{session_id}/answer/{step}` tentava desempacotar `sessions[session_id]` como tupla
  - Causa: Estrutura mudou de tupla `(bo_id, state_machine)` para dict `{"bo_id": ..., "sections": {...}}`
  - Solução: Acessa `session_data["bo_id"]` e determina state_machine baseado no prefixo do step (1.x ou 2.x)
  - Commits: `f5bc007`

### 🐛 Corrigido - Automação de Release
- **Script de automação falhando na edição**
  - Problema: Seletor de input não aguardava elemento ficar visível
  - Solução: Adicionado `wait_for_selector('input.px-2', state='visible')` antes de interagir
  - Commits: `ef0b723`

- **Vídeo não capturando início da Seção 2**
  - Problema: Scroll para topo acontecia ANTES do click, depois página voltava
  - Solução: Movido scroll para DEPOIS do click no botão "Iniciar Seção 2"
  - Commits: `bd1b569`

- **Screenshot mobile da sidebar com sobreposição visual**
  - Problema: `full_page=True` fazia scroll e conteúdo aparecia através da sidebar fixed
  - Solução: Mudado para `full_page=False` (captura apenas viewport 430x932px)
  - Commits: `9041dfc`

### 🔧 Técnico
- **Frontend**: Suporte para `127.0.0.1` além de `localhost` na detecção de ambiente local
- **Frontend**: Versão atualizada para v0.6.1 em 3 locais (header, footer, JS)
- **Backend**: Removidos prints de debug temporários usados no diagnóstico
- **Backend**: Validação correta por seção no endpoint de edição (ResponseValidator vs ResponseValidatorSection2)
- **Documentação**: CLAUDE.md atualizado com comandos corretos de startup e troubleshooting

### ⚠️ Breaking Changes
- Arquivo `.env` DEVE estar na raiz do projeto, não mais em `backend/.env`
- Comando de startup mudou de `cd backend && uvicorn main:app` para `python -m uvicorn backend.main:app` (do diretório raiz)

### 📚 Lições Aprendidas
1. **python-dotenv carrega .env do CWD (current working directory)**
   - Se backend roda de `backend/`, procura `.env` em `backend/.env`
   - Se backend roda da raiz, procura `.env` na raiz
   - Solução: Sempre rodar de um diretório fixo e documentar

2. **Estruturas de dados em APIs devem ser imutáveis ou bem documentadas**
   - Mudança de tupla para dict quebrou endpoint de edição
   - Testes automatizados pegaram o bug imediatamente

3. **Screenshots full_page com elementos fixed/absolute**
   - `full_page=True` faz scroll virtual da página toda
   - Elementos `position: fixed` (como sidebar mobile) podem ter problemas
   - Usar `full_page=False` para capturar overlays/modals

4. **Ordem de operações em automação importa**
   - Scroll antes de click pode ser revertido pelo próprio click
   - Sempre testar a ordem: ação → efeito → captura

### ✅ Validado
- ✅ Groq API funcionando corretamente em localhost
- ✅ Seção 1 e Seção 2 gerando textos com sucesso
- ✅ Edição de respostas funcionando (ambas seções)
- ✅ Automação de release completa (screenshots + vídeo)
- ✅ `.env` está no `.gitignore` (linha 12) - seguro para commit

---

## [0.6.0] - 2025-12-20

### ✨ Adicionado
- **Suporte ao Groq API (Llama 3.3 70B)**
  - Integração completa com Groq para Seção 1 e Seção 2
  - 14.400 requisições/dia (720x mais que Gemini 2.5 Flash)
  - Modelo llama-3.3-70b-versatile com temperature 0.3
  - Tratamento de erro específico para rate limits do Groq

- **Arquitetura Multi-Provider Consolidada**
  - Backend suporta múltiplos providers: Gemini, Groq
  - Preparado para Claude e OpenAI (TODOs documentados)
  - Método `validate_api_keys()` inclui Groq
  - Fácil troca de provider no frontend (1 linha)

### 🔧 Técnico
- **Backend**: `groq==1.0.0` adicionado ao requirements.txt
- **Backend**: Novos métodos `_generate_with_groq()` e `_generate_section2_with_groq()`
- **Backend**: Provider routing atualizado em ambas seções
- **Frontend**: `llm_provider` alterado de 'gemini' para 'groq' (linhas 520, 1149, 1408)

### 🎯 Benefícios
- **Testes intensivos**: 14.4k req/dia permite iterações rápidas na fase de desenvolvimento
- **Flexibilidade**: Arquitetura permite voltar para Gemini ou testar outros providers facilmente
- **Custo zero**: Groq free tier sem necessidade de cartão de crédito
- **Performance**: Groq é 2-3x mais rápido que Gemini em média

### 🐛 Corrigido
- Atualizado Groq de 0.11.0 para 1.0.0 (compatibilidade com httpx 0.28.1)
- Erro de quota do Gemini agora tem mensagem específica (429 vs 500)

---

## [0.4.1] - 2025-12-12

### ✨ Adicionado
- **Sistema de Rascunho Automático (localStorage)**
  - Salva automaticamente após cada resposta válida
  - Modal ao carregar página perguntando se deseja continuar rascunho
  - Preview do rascunho mostrando respostas salvas e data
  - Expira automaticamente após 7 dias
  - Limpa automaticamente ao completar o BO
  - Indicador visual "💾 Rascunho salvo!" na sidebar
  - Salva também ao fechar aba (beforeunload)

- **Melhorias de UX**
  - Footer atualizado com indicador de salvamento automático
  - Toast de confirmação ao restaurar rascunho
  - Sincronização automática com backend ao restaurar

### 🛠 Corrigido
- Versão atualizada para v0.4.1 no header e footer

### 🎯 Benefícios
- **Reduz frustração**: Usuário não perde respostas se fechar aba acidentalmente
- **Tolerância a falhas**: Se servidor Render "dormir", rascunho permanece local
- **Experiência contínua**: Pode parar e continuar depois sem perder progresso

---

## Implementação Técnica

### Estrutura do Rascunho (localStorage)
```javascript
{
  sessionId: "uuid",           // ID da sessão (referência)
  boId: "BO-YYYYMMDD-xxxxx",   // ID do BO
  currentStep: "1.3",          // Próximo step a responder
  answers: {                    // Respostas salvas
    "1.1": "22/03/2025, 19h03",
    "1.2": "Sgt João, prefixo 1234"
  },
  savedAt: "2025-12-12T10:30:00Z",  // Timestamp
  version: "0.4.1"             // Versão do sistema
}
```

### Chave no localStorage
```
bo_inteligente_draft
```

### Fluxo de Restauração
1. Ao carregar página, verifica `loadDraft()`
2. Se existe rascunho válido (< 7 dias), mostra modal
3. Usuário escolhe "Continuar" ou "Começar Novo"
4. Se continuar: cria nova sessão no backend, restaura respostas localmente
5. Sincroniza cada resposta com backend via `/chat`
6. Mostra próxima pergunta

### Arquivos Modificados
- `docs/index.html` - Frontend com lógica de localStorage

---

## Como Testar

1. Responda 2-3 perguntas
2. Feche a aba do navegador
3. Abra novamente - deve aparecer modal de rascunho
4. Clique "Continuar" - deve restaurar respostas
5. Complete o BO - rascunho deve ser limpo automaticamente

---

**Desenvolvido por:** Claude + Cristiano Maia  
**Data:** 12/12/2025
