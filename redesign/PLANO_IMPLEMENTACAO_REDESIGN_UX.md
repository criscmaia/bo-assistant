# 🚀 Plano de Implementação - Redesign UX BO Inteligente

**Versão:** 1.0  
**Data:** 31/12/2025  
**Documento de referência:** `PROPOSTA_REDESIGN_UX_BO_INTELIGENTE.md`

---

## 📋 Visão Geral das Fases

| Fase | Descrição | Estimativa | Modelo | Dependências |
|------|-----------|------------|--------|--------------|
| **0** | Preparação e Backup | 30 min | Manual | - |
| **1** | Barra de Progresso | 2-3h | 🟢 Haiku | Fase 0 |
| **2** | Container de Seção | 2-3h | 🟢 Haiku | Fase 1 |
| **3** | Componentes de Input | 2-3h | 🟢 Haiku | Fase 2 |
| **4** | Fluxo de Navegação | 2-3h | 🟡 Sonnet | Fase 3 |
| **5** | Tela Final (BO Completo) | 1-2h | 🟢 Haiku | Fase 4 |
| **6** | Responsividade e Polish | 2-3h | 🟢 Haiku | Fase 5 |
| **7** | Testes e Ajustes | 2-3h | 🟡 Sonnet | Fase 6 |
| **8** | Refatoração (opcional) | 2-3h | 🔴 Opus | Fase 7 |

**Total estimado:** 16-23 horas

### Legenda de Modelos
- 🟢 **Haiku** - Tarefas bem definidas, código isolado, baixo risco
- 🟡 **Sonnet** - Integração de componentes, lógica complexa, debugging
- 🔴 **Opus** - Refatoração arquitetural, decisões de design, código legado

---

## 📁 Estrutura de Arquivos

### Decisão de Arquitetura
**Manter tudo em um único arquivo `index.html`** (como hoje) para facilitar implementação incremental com Haiku. Refatoração em arquivos separados será feita na Fase 8 (opcional, com Sonnet/Opus).

### Estrutura Durante Implementação
```
docs/
├── index.html              ← Arquivo principal (tudo junto)
├── index.html.backup-v0.12 ← Backup da versão atual
└── logs.html
```

### Estrutura Após Refatoração (Fase 8 - opcional)
```
docs/
├── index.html          ← HTML + imports
├── css/
│   └── styles.css      ← CSS extraído
├── js/
│   ├── app.js          ← Lógica principal
│   ├── components/     ← Componentes separados
│   └── data/
│       └── sections.js ← Configuração das seções
└── logs.html
```

---

## 🔧 FASE 0: Preparação e Backup

### Objetivo
Criar branch, backup e estrutura de pastas.

### Tarefas

#### 0.1 - Criar branch de desenvolvimento
```bash
git checkout -b feature/ux-redesign-v1
git push -u origin feature/ux-redesign-v1
```

#### 0.2 - Backup do index.html atual
```bash
cp docs/index.html docs/index.html.backup-v0.12
```

#### 0.3 - Criar estrutura de pastas
```bash
mkdir -p docs/js/components
mkdir -p docs/js/data
```

#### 0.4 - Criar arquivo de configuração das seções
Criar `docs/js/data/sections.js` com a estrutura de todas as 8 seções.

### Checklist
- [ ] Branch criada
- [ ] Backup feito
- [ ] Pastas criadas
- [ ] `sections.js` criado com estrutura básica

---

## 📊 FASE 1: Barra de Progresso

### Objetivo
Implementar componente `ProgressBar` com visual e interatividade.

### 🟢 Modelo Recomendado: Haiku
*Componente isolado, bem especificado, sem dependências complexas.*

### Arquivo: Inline no `index.html` (seção `<script>`)

### Tarefas

#### 1.1 - Criar componente ProgressBar básico
- Renderizar 8 bolinhas com números
- Conectar com linhas
- Estilização básica

#### 1.2 - Implementar estados visuais
- `pending` (○ cinza claro)
- `in_progress` (◐ azul, parcialmente preenchido)
- `completed` (● verde)
- `skipped` (● cinza + ícone ⏭️)

#### 1.3 - Implementar preenchimento gradual
- Calcular porcentagem baseado em perguntas respondidas
- Animar preenchimento entre bolinhas

#### 1.4 - Implementar tooltips
- Mostrar nome da seção + emoji ao hover
- Mostrar status (X/Y perguntas)

#### 1.5 - Implementar navegação por clique
- Clicar em seção visitada → navegar
- Clicar em seção futura → bloqueado (cursor not-allowed)

#### 1.6 - Responsividade mobile
- Reduzir tamanho das bolinhas em telas < 768px
- Manter área de toque mínima 44x44px

### Especificação Técnica

```javascript
// ProgressBar.js
class ProgressBar {
  constructor(containerId, options = {}) {
    this.container = document.getElementById(containerId);
    this.sections = options.sections || [];
    this.currentSection = options.currentSection || 1;
    this.onSectionClick = options.onSectionClick || (() => {});
  }
  
  render() { /* ... */ }
  updateProgress(sectionId, answeredCount, totalCount) { /* ... */ }
  setCurrentSection(sectionId) { /* ... */ }
  markCompleted(sectionId) { /* ... */ }
  markSkipped(sectionId) { /* ... */ }
}
```

### CSS Necessário

```css
.progress-bar { /* container flex */ }
.progress-node { /* bolinha */ }
.progress-node--pending { /* cinza claro */ }
.progress-node--in-progress { /* azul */ }
.progress-node--completed { /* verde */ }
.progress-node--skipped { /* cinza */ }
.progress-line { /* linha entre bolinhas */ }
.progress-line-fill { /* preenchimento animado */ }
.progress-tooltip { /* tooltip no hover */ }
```

### Checklist
- [ ] Componente básico renderizando
- [ ] Estados visuais funcionando
- [ ] Preenchimento gradual animado
- [ ] Tooltips funcionando
- [ ] Navegação por clique funcionando
- [ ] Responsivo em mobile

---

## 📦 FASE 2: Container de Seção

### Objetivo
Implementar `SectionContainer` que gerencia uma seção independente.

### 🟢 Modelo Recomendado: Haiku
*Componente com estrutura clara, tarefas bem definidas.*

### Arquivo: Inline no `index.html` (seção `<script>`)

### Tarefas

#### 2.1 - Criar estrutura HTML do container
- Área do chat (scrollável)
- Área do texto gerado (aparece ao finalizar)
- Botões de transição (Iniciar/Pular próxima seção)

#### 2.2 - Implementar gerenciamento de estado
- `pending` → seção não iniciada
- `in_progress` → respondendo perguntas
- `completed` → todas perguntas respondidas, texto gerado
- `skipped` → seção pulada

#### 2.3 - Implementar scroll interno
- Chat com overflow-y: auto
- Scroll automático para última mensagem

#### 2.4 - Implementar transição entre seções
- Fade out da seção atual (200ms)
- Fade in da próxima seção (200ms)

#### 2.5 - Implementar modo leitura
- Quando usuário clica em seção anterior
- Mostrar perguntas/respostas como lista
- Mostrar texto gerado
- Botão "Voltar para seção atual"

### Especificação Técnica

```javascript
// SectionContainer.js
class SectionContainer {
  constructor(containerId, options = {}) {
    this.container = document.getElementById(containerId);
    this.sectionData = options.sectionData;
    this.onComplete = options.onComplete || (() => {});
    this.onSkip = options.onSkip || (() => {});
    this.state = 'pending';
    this.answers = {};
  }
  
  render() { /* ... */ }
  startSection() { /* ... */ }
  submitAnswer(questionId, answer) { /* ... */ }
  completeSection(generatedText) { /* ... */ }
  skipSection() { /* ... */ }
  showReadOnly() { /* ... */ }
  transitionTo(nextSection) { /* ... */ }
}
```

### Checklist
- [ ] Container renderizando corretamente
- [ ] Estados funcionando
- [ ] Scroll interno funcionando
- [ ] Transições com fade
- [ ] Modo leitura funcionando

---

## 💬 FASE 3: Componentes de Input

### Objetivo
Implementar os 3 tipos de input para o chat.

### 🟢 Modelo Recomendado: Haiku
*Componentes pequenos e isolados, fácil de implementar separadamente.*

### Arquivos: Inline no `index.html` (seção `<script>`)

### Tarefas

#### 3.1 - Criar ChatMessage (mensagem do bot)
- Texto principal da pergunta
- Dica/exemplo (opcional, fonte menor)
- Estilo de "bolha" do bot

#### 3.2 - Criar TextInput
- Campo de texto com placeholder
- Botão "Enviar"
- Validação básica (não vazio)
- Enter para enviar

#### 3.3 - Criar SingleChoice
- Renderizar opções como botões
- Destacar opção selecionada
- Callback ao selecionar

#### 3.4 - Criar MultipleChoice
- Renderizar opções como checkboxes estilizados
- Permitir múltiplas seleções
- Botão "Confirmar"
- Callback ao confirmar

#### 3.5 - Criar ChatMessage (resposta do usuário)
- Estilo de "bolha" do usuário (alinhada à direita)
- Botão editar (dentro da seção atual)

### Especificação Técnica

```javascript
// ChatMessage.js
class ChatMessage {
  constructor(options = {}) {
    this.type = options.type; // 'bot' | 'user'
    this.content = options.content;
    this.hint = options.hint;
    this.onEdit = options.onEdit;
  }
  render() { /* retorna HTMLElement */ }
}

// TextInput.js
class TextInput {
  constructor(options = {}) {
    this.placeholder = options.placeholder;
    this.onSubmit = options.onSubmit;
    this.validation = options.validation;
  }
  render() { /* retorna HTMLElement */ }
  focus() { /* foca no input */ }
  clear() { /* limpa o input */ }
}

// SingleChoice.js
class SingleChoice {
  constructor(options = {}) {
    this.options = options.options; // ['SIM', 'NÃO']
    this.onSelect = options.onSelect;
  }
  render() { /* retorna HTMLElement */ }
}

// MultipleChoice.js
class MultipleChoice {
  constructor(options = {}) {
    this.options = options.options;
    this.minSelections = options.minSelections || 1;
    this.maxSelections = options.maxSelections;
    this.onConfirm = options.onConfirm;
  }
  render() { /* retorna HTMLElement */ }
}
```

### Checklist
- [ ] ChatMessage bot renderizando
- [ ] ChatMessage user renderizando
- [ ] TextInput funcionando
- [ ] SingleChoice funcionando
- [ ] MultipleChoice funcionando
- [ ] Todos com estilo consistente

---

## 🔄 FASE 4: Fluxo de Navegação

### Objetivo
Integrar todos os componentes e implementar o fluxo completo.

### 🟡 Modelo Recomendado: Sonnet
*Integração de múltiplos componentes, lógica de estado complexa, potencial para bugs.*

### Arquivo: Inline no `index.html` (seção `<script>`)

### Tarefas

#### 4.1 - Refatorar app.js principal
- Inicializar ProgressBar
- Inicializar SectionContainer
- Gerenciar estado global

#### 4.2 - Implementar fluxo de perguntas
- Carregar perguntas da seção atual
- Exibir pergunta com tipo correto de input
- Processar resposta
- Avançar para próxima pergunta

#### 4.3 - Implementar finalização de seção
- Detectar última pergunta respondida
- Chamar API para gerar texto
- Exibir texto gerado
- Mostrar botões Iniciar/Pular

#### 4.4 - Implementar navegação entre seções
- Atualizar ProgressBar ao mudar de seção
- Salvar estado da seção anterior
- Carregar estado da próxima seção

#### 4.5 - Implementar "Pular seção"
- Marcar seção como skipped
- Avançar para próxima
- Atualizar ProgressBar

#### 4.6 - Implementar navegação para seção anterior
- Clicar na bolinha da ProgressBar
- Carregar seção em modo leitura
- Botão para voltar à seção atual

### Especificação Técnica

```javascript
// app.js
class BOApp {
  constructor() {
    this.sections = SECTIONS_DATA; // do sections.js
    this.currentSectionIndex = 0;
    this.sectionStates = {}; // { sectionId: { status, answers, generatedText } }
    
    this.progressBar = null;
    this.sectionContainer = null;
  }
  
  init() { /* inicializa componentes */ }
  loadSection(sectionIndex) { /* carrega seção */ }
  handleAnswer(questionId, answer) { /* processa resposta */ }
  handleSectionComplete() { /* finaliza seção */ }
  handleSectionSkip() { /* pula seção */ }
  navigateToSection(sectionIndex) { /* navega para seção */ }
  handleBOComplete() { /* todas seções finalizadas */ }
}

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
  const app = new BOApp();
  app.init();
});
```

### Checklist
- [ ] App inicializando corretamente
- [ ] Fluxo de perguntas funcionando
- [ ] Geração de texto funcionando
- [ ] Navegação Iniciar/Pular funcionando
- [ ] Navegação pela ProgressBar funcionando
- [ ] Modo leitura funcionando

---

## 🏁 FASE 5: Tela Final (BO Completo)

### Objetivo
Implementar tela de conclusão com todos os textos gerados.

### 🟢 Modelo Recomendado: Haiku
*Componente isolado com lógica simples (accordion + copiar).*

### Arquivo: Inline no `index.html` (seção `<script>`)

### Tarefas

#### 5.1 - Criar componente BOComplete
- Título "BO COMPLETO!"
- Lista de seções (accordion)
- Cada seção mostra texto gerado
- Seções puladas indicadas

#### 5.2 - Implementar accordion
- Clique expande/colapsa seção
- Inicialmente todas expandidas (ou colapsadas?)

#### 5.3 - Implementar "Copiar Seção"
- Botão em cada seção
- Copia texto para clipboard
- Feedback visual "Copiado!"

#### 5.4 - Implementar "Copiar BO Completo"
- Concatena todos os textos
- Adiciona separadores entre seções
- Copia para clipboard

#### 5.5 - Implementar botões de ação
- "Iniciar Novo BO" → reset do estado
- "Exportar PDF" → placeholder (v2.0)

### Especificação Técnica

```javascript
// BOComplete.js
class BOComplete {
  constructor(containerId, options = {}) {
    this.container = document.getElementById(containerId);
    this.sections = options.sections; // com textos gerados
    this.onNewBO = options.onNewBO;
  }
  
  render() { /* ... */ }
  copySection(sectionId) { /* ... */ }
  copyAll() { /* ... */ }
  toggleSection(sectionId) { /* ... */ }
}
```

### Checklist
- [ ] Tela renderizando corretamente
- [ ] Accordion funcionando
- [ ] Copiar seção funcionando
- [ ] Copiar tudo funcionando
- [ ] Iniciar Novo BO funcionando

---

## 📱 FASE 6: Responsividade e Polish

### Objetivo
Garantir que tudo funciona em mobile e adicionar acabamentos visuais.

### 🟢 Modelo Recomendado: Haiku
*Ajustes de CSS e pequenas adições, tarefas bem definidas.*

### Tarefas

#### 6.1 - Testar e ajustar mobile (< 768px)
- ProgressBar compacta
- Botões empilhados
- Chat 100% largura
- Área de toque adequada

#### 6.2 - Testar e ajustar tablet (768px - 1023px)
- Proporções intermediárias

#### 6.3 - Adicionar animações
- Fade entre seções (200ms)
- Transição suave no preenchimento da ProgressBar
- Feedback visual nos botões (hover, active)

#### 6.4 - Adicionar estados de loading
- Spinner durante geração de texto
- Desabilitar inputs durante loading

#### 6.5 - Adicionar feedback visual
- Toast "Copiado!" ao copiar texto
- Highlight na bolinha atual da ProgressBar
- Animação sutil ao responder pergunta

#### 6.6 - Revisar acessibilidade
- Labels em inputs
- Contraste de cores
- Navegação por teclado

### Checklist
- [ ] Mobile funcionando bem
- [ ] Tablet funcionando bem
- [ ] Animações implementadas
- [ ] Loading states implementados
- [ ] Feedbacks visuais implementados
- [ ] Acessibilidade básica OK

---

## 🧪 FASE 7: Testes e Ajustes

### Objetivo
Testar fluxo completo e corrigir bugs.

### 🟡 Modelo Recomendado: Sonnet
*Debugging e correção de bugs requer análise contextual mais profunda.*

### Tarefas

#### 7.1 - Teste de fluxo completo (happy path)
- Responder todas as perguntas de todas as seções
- Verificar textos gerados
- Verificar tela final

#### 7.2 - Teste de seções puladas
- Pular seções 2, 4, 6
- Verificar ProgressBar
- Verificar tela final

#### 7.3 - Teste de navegação
- Navegar para seções anteriores
- Verificar modo leitura
- Voltar para seção atual

#### 7.4 - Teste mobile
- Testar em dispositivo real ou emulador
- Verificar touch areas
- Verificar scroll

#### 7.5 - Teste de edge cases
- Respostas muito longas
- Conexão lenta (loading)
- Erro na API

#### 7.6 - Ajustes finais
- Corrigir bugs encontrados
- Ajustar espaçamentos
- Revisar textos/labels

### Checklist
- [ ] Happy path OK
- [ ] Seções puladas OK
- [ ] Navegação OK
- [ ] Mobile OK
- [ ] Edge cases tratados
- [ ] Bugs corrigidos

---

## 🔄 FASE 8: Refatoração (Opcional)

### Objetivo
Separar código em arquivos modulares para melhor manutenibilidade.

### 🔴 Modelo Recomendado: Opus
*Refatoração arquitetural requer visão holística do código e decisões de design.*

### Quando Fazer
- Após sistema estável e testado
- Se o arquivo `index.html` ultrapassar ~2000 linhas
- Antes de adicionar novas features significativas

### Tarefas

#### 8.1 - Extrair CSS para arquivo separado
- Criar `docs/css/styles.css`
- Mover todos os estilos do `<style>` para o arquivo
- Atualizar `<link>` no HTML

#### 8.2 - Extrair dados das seções
- Criar `docs/js/data/sections.js`
- Mover `SECTIONS_DATA` para o arquivo
- Carregar via `<script>`

#### 8.3 - Extrair componentes
- Criar `docs/js/components/ProgressBar.js`
- Criar `docs/js/components/SectionContainer.js`
- Criar `docs/js/components/ChatMessage.js`
- Criar `docs/js/components/TextInput.js`
- Criar `docs/js/components/SingleChoice.js`
- Criar `docs/js/components/MultipleChoice.js`
- Criar `docs/js/components/BOComplete.js`

#### 8.4 - Extrair lógica principal
- Criar `docs/js/app.js`
- Mover classe `BOApp` para o arquivo
- Atualizar ordem de carregamento dos scripts

#### 8.5 - Atualizar index.html
- Remover código inline
- Adicionar `<script>` tags na ordem correta
- Testar se tudo continua funcionando

### Estrutura Final
```
docs/
├── index.html
├── css/
│   └── styles.css
├── js/
│   ├── app.js
│   ├── components/
│   │   ├── ProgressBar.js
│   │   ├── SectionContainer.js
│   │   ├── ChatMessage.js
│   │   ├── TextInput.js
│   │   ├── SingleChoice.js
│   │   ├── MultipleChoice.js
│   │   └── BOComplete.js
│   └── data/
│       └── sections.js
└── logs.html
```

### Checklist
- [ ] CSS extraído e funcionando
- [ ] Dados das seções extraídos
- [ ] Componentes extraídos
- [ ] App.js extraído
- [ ] Tudo funcionando como antes
- [ ] Código mais organizado e manutenível

---

## 📝 Template para Documentos de Fase

Cada fase terá um documento detalhado no formato:

```markdown
# FASE X: [Nome da Fase]

## Contexto
[Breve descrição do que já foi feito e o que esta fase vai fazer]

## Arquivos a Modificar/Criar
- `path/to/file.js` - [descrição]

## Tarefas Detalhadas

### Tarefa X.1: [Nome]
**Objetivo:** [O que deve ser feito]

**Código:**
[Código completo para copiar/colar ou instruções de modificação]

**Teste:**
[Como verificar se funcionou]

### Tarefa X.2: [Nome]
...

## Checklist Final
- [ ] Item 1
- [ ] Item 2

## Próxima Fase
[Link ou referência para a próxima fase]
```

---

## 🎯 Ordem de Execução Recomendada

```
Fase 0 (Manual)
    │
    ▼
Fase 1 (Haiku) ─── ProgressBar
    │
    ▼
Fase 2 (Haiku) ─── SectionContainer
    │
    ▼
Fase 3 (Haiku) ─── Componentes de Input
    │
    ▼
Fase 4 (Sonnet) ── Integração ⚠️ Fase crítica
    │
    ▼
Fase 5 (Haiku) ─── Tela Final
    │
    ▼
Fase 6 (Haiku) ─── Responsividade
    │
    ▼
Fase 7 (Sonnet) ── Testes ⚠️ Debugging
    │
    ▼
Fase 8 (Opus) ──── Refatoração (opcional)
```

### Notas sobre os Modelos

**🟢 Haiku** - Use para:
- Componentes isolados e bem especificados
- Tarefas com entrada/saída claras
- Código que pode ser testado independentemente

**🟡 Sonnet** - Use para:
- Integração de múltiplos componentes
- Debugging e correção de bugs
- Lógica de estado complexa
- Quando Haiku falhar ou produzir código com bugs

**🔴 Opus** - Use para:
- Refatoração arquitetural
- Decisões de design que afetam múltiplos arquivos
- Análise de código legado
- Quando Sonnet não conseguir resolver

---

## ⏭️ Próximo Passo

Gerar documento detalhado da **Fase 0** para iniciar a implementação.

---

*Documento gerado em 31/12/2025*
