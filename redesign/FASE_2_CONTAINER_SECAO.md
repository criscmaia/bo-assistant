# 📦 FASE 2: Container de Seção

**Projeto:** BO Inteligente - Redesign UX  
**Fase:** 2 de 8  
**Modelo recomendado:** 🟢 Haiku  
**Tempo estimado:** 2-3 horas  
**Dependências:** Fase 1 concluída (ProgressBar funcionando)

---

## 📋 Contexto

### O que foi feito nas fases anteriores?
- **Fase 0:** Branch criada, `sections.js` com 8 seções e ~53 perguntas
- **Fase 1:** Componente `ProgressBar` funcionando com estados visuais, tooltips e navegação

### O que será feito nesta fase?
Criar o componente **SectionContainer** - um container que gerencia uma seção independente:
- Área de chat scrollável (perguntas e respostas)
- Área de texto gerado (aparece ao finalizar seção)
- Botões de transição (Iniciar próxima / Pular)
- Estados: pending, in_progress, completed, skipped
- Transição suave (fade) entre seções

### Wireframe de referência
```
┌─────────────────────────────────────────────────────────────────┐
│  SEÇÃO 3: Campana                                    [👁️]      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  🤖 Quanto tempo durou a campana?                       │   │
│  │     💡 Ex: aproximadamente 30 minutos                   │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │  👤 Aproximadamente 45 minutos                          │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │  🤖 De onde a guarnição observava?                      │   │
│  │     💡 Ex: de dentro da viatura, a 50 metros            │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │                    [CHAT SCROLLÁVEL]                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  📝 Digite sua resposta...                    [Enviar]  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

APÓS COMPLETAR A SEÇÃO:

┌─────────────────────────────────────────────────────────────────┐
│  SEÇÃO 3: Campana ✅                                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  📄 TEXTO GERADO                              [Copiar]  │   │
│  │  ─────────────────────────────────────────────────────  │   │
│  │  Durante a campana de aproximadamente 45 minutos, a     │   │
│  │  guarnição posicionou-se dentro da viatura...           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  ▶️ PRÓXIMA: Seção 4 - Entrada em Domicílio 🏠          │   │
│  │                                                         │   │
│  │  [▶️ INICIAR SEÇÃO 4]     [⏭️ PULAR SEÇÃO 4]            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Objetivo

Adicionar ao `index.html`:
1. HTML do container de seção (substituir layout atual de sidebar + chat)
2. CSS para o novo layout
3. JavaScript com classe `SectionContainer`

**Importante:** O layout antigo (sidebar) será **ocultado** temporariamente, não removido. Poderemos restaurá-lo se necessário.

---

## 📁 Arquivo a Modificar

`docs/index.html`

---

## ✅ Tarefas

### Tarefa 2.1: Adicionar CSS do container de seção

**Objetivo:** Estilizar o novo layout de seção independente.

**Localização:** Dentro da tag `<style>`, APÓS os estilos da ProgressBar.

**Encontre o comentário:**
```css
        /* ============================================ */
        /* FIM BARRA DE PROGRESSO - ESTILOS */
        /* ============================================ */
```

**Adicione DEPOIS:**

```css
        
        /* ============================================ */
        /* CONTAINER DE SEÇÃO - ESTILOS */
        /* ============================================ */
        
        .section-container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            display: flex;
            flex-direction: column;
            height: calc(100vh - 220px); /* Altura dinâmica */
            min-height: 500px;
            overflow: hidden;
            transition: opacity 0.2s ease, transform 0.2s ease;
        }
        
        .section-container--hidden {
            opacity: 0;
            transform: translateY(10px);
            pointer-events: none;
            position: absolute;
        }
        
        .section-container--visible {
            opacity: 1;
            transform: translateY(0);
        }
        
        /* Header da seção */
        .section-header {
            padding: 16px 20px;
            border-bottom: 1px solid #e5e7eb;
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        }
        
        .section-header__title {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 18px;
            font-weight: 600;
            color: #1e3a5f;
        }
        
        .section-header__emoji {
            font-size: 24px;
        }
        
        .section-header__badge {
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
        }
        
        .section-header__badge--in-progress {
            background-color: #dbeafe;
            color: #1d4ed8;
        }
        
        .section-header__badge--completed {
            background-color: #d1fae5;
            color: #059669;
        }
        
        .section-header__badge--skipped {
            background-color: #f3f4f6;
            color: #6b7280;
        }
        
        /* Área de chat */
        .section-chat {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        
        .section-chat::-webkit-scrollbar {
            width: 6px;
        }
        
        .section-chat::-webkit-scrollbar-track {
            background: #f1f5f9;
            border-radius: 3px;
        }
        
        .section-chat::-webkit-scrollbar-thumb {
            background: #cbd5e1;
            border-radius: 3px;
        }
        
        .section-chat::-webkit-scrollbar-thumb:hover {
            background: #94a3b8;
        }
        
        /* Mensagem do bot */
        .chat-message--bot {
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            max-width: 85%;
        }
        
        .chat-message__bubble--bot {
            background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
            border: 1px solid #bfdbfe;
            border-radius: 16px 16px 16px 4px;
            padding: 14px 18px;
            color: #1e40af;
        }
        
        .chat-message__text {
            font-size: 15px;
            line-height: 1.5;
        }
        
        .chat-message__hint {
            margin-top: 8px;
            font-size: 13px;
            color: #6b7280;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        
        .chat-message__hint::before {
            content: '💡';
        }
        
        /* Mensagem do usuário */
        .chat-message--user {
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            max-width: 85%;
            align-self: flex-end;
        }
        
        .chat-message__bubble--user {
            background: linear-gradient(135deg, #1e3a5f 0%, #1e40af 100%);
            border-radius: 16px 16px 4px 16px;
            padding: 14px 18px;
            color: white;
        }
        
        /* Área de input */
        .section-input {
            padding: 16px 20px;
            border-top: 1px solid #e5e7eb;
            background: #f8fafc;
        }
        
        .section-input__form {
            display: flex;
            gap: 12px;
        }
        
        .section-input__field {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #e5e7eb;
            border-radius: 10px;
            font-size: 15px;
            transition: border-color 0.2s, box-shadow 0.2s;
        }
        
        .section-input__field:focus {
            outline: none;
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
        
        .section-input__field::placeholder {
            color: #9ca3af;
        }
        
        .section-input__button {
            padding: 12px 24px;
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.1s, box-shadow 0.2s;
        }
        
        .section-input__button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
        }
        
        .section-input__button:active {
            transform: translateY(0);
        }
        
        .section-input__button:disabled {
            background: #d1d5db;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        
        /* Área de texto gerado */
        .section-generated {
            padding: 20px;
            background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
            border-top: 2px solid #86efac;
        }
        
        .section-generated__header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 12px;
        }
        
        .section-generated__title {
            font-weight: 600;
            color: #166534;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .section-generated__copy {
            padding: 8px 16px;
            background: #16a34a;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            transition: background 0.2s;
        }
        
        .section-generated__copy:hover {
            background: #15803d;
        }
        
        .section-generated__text {
            background: white;
            border: 1px solid #86efac;
            border-radius: 8px;
            padding: 16px;
            font-size: 14px;
            line-height: 1.7;
            color: #374151;
            white-space: pre-wrap;
            max-height: 200px;
            overflow-y: auto;
        }
        
        /* Área de transição (próxima seção) */
        .section-transition {
            padding: 20px;
            background: #f8fafc;
            border-top: 1px solid #e5e7eb;
        }
        
        .section-transition__preview {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 16px;
            background: white;
            border: 2px dashed #cbd5e1;
            border-radius: 12px;
            margin-bottom: 16px;
        }
        
        .section-transition__preview-emoji {
            font-size: 32px;
        }
        
        .section-transition__preview-info {
            flex: 1;
        }
        
        .section-transition__preview-label {
            font-size: 12px;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .section-transition__preview-name {
            font-size: 16px;
            font-weight: 600;
            color: #1e3a5f;
        }
        
        .section-transition__buttons {
            display: flex;
            gap: 12px;
        }
        
        .section-transition__btn {
            flex: 1;
            padding: 14px 20px;
            border: none;
            border-radius: 10px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            transition: transform 0.1s, box-shadow 0.2s;
        }
        
        .section-transition__btn:hover {
            transform: translateY(-2px);
        }
        
        .section-transition__btn:active {
            transform: translateY(0);
        }
        
        .section-transition__btn--start {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
        }
        
        .section-transition__btn--start:hover {
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
        }
        
        .section-transition__btn--skip {
            background: #f3f4f6;
            color: #6b7280;
            border: 2px solid #e5e7eb;
        }
        
        .section-transition__btn--skip:hover {
            background: #e5e7eb;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        
        /* Modo leitura (seção anterior) */
        .section-container--readonly .section-input {
            display: none;
        }
        
        .section-container--readonly .section-chat {
            padding-bottom: 20px;
        }
        
        .section-readonly-notice {
            padding: 12px 20px;
            background: #fef3c7;
            border-top: 1px solid #fcd34d;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .section-readonly-notice__text {
            color: #92400e;
            font-size: 14px;
        }
        
        .section-readonly-notice__btn {
            padding: 8px 16px;
            background: #f59e0b;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
        }
        
        .section-readonly-notice__btn:hover {
            background: #d97706;
        }
        
        /* Loading state */
        .section-loading {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 40px;
            color: #6b7280;
        }
        
        .section-loading__spinner {
            width: 24px;
            height: 24px;
            border: 3px solid #e5e7eb;
            border-top-color: #3b82f6;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 12px;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        /* Responsividade */
        @media (max-width: 768px) {
            .section-container {
                height: calc(100vh - 180px);
                min-height: 400px;
                border-radius: 8px;
            }
            
            .section-header {
                padding: 12px 16px;
            }
            
            .section-header__title {
                font-size: 16px;
            }
            
            .section-chat {
                padding: 16px;
                gap: 12px;
            }
            
            .chat-message--bot,
            .chat-message--user {
                max-width: 95%;
            }
            
            .section-input {
                padding: 12px 16px;
            }
            
            .section-input__form {
                flex-direction: column;
            }
            
            .section-input__button {
                width: 100%;
            }
            
            .section-transition__buttons {
                flex-direction: column;
            }
            
            .section-transition__btn {
                width: 100%;
            }
        }
        
        /* ============================================ */
        /* FIM CONTAINER DE SEÇÃO - ESTILOS */
        /* ============================================ */
```

---

### Tarefa 2.2: Adicionar HTML do container de seção

**Objetivo:** Criar a estrutura HTML do novo container.

**Localização:** Substituir o conteúdo dentro de `<main>`, mantendo a barra de progresso e ocultando a sidebar antiga.

**Encontre este trecho:**
```html
        <!-- Main Content com Sidebar -->
        <main class="flex-1 max-w-7xl w-full mx-auto p-4 flex gap-4">
            <!-- ============================================ -->
            <!-- BARRA DE PROGRESSO - NOVO DESIGN -->
            <!-- ============================================ -->
            <div id="progress-bar-container" ...>
```

**Substitua TODO o conteúdo de `<main>` por:**

```html
        <!-- Main Content - Novo Layout -->
        <main class="flex-1 max-w-4xl w-full mx-auto p-4">
            <!-- ============================================ -->
            <!-- BARRA DE PROGRESSO -->
            <!-- ============================================ -->
            <div id="progress-bar-container" class="w-full bg-white rounded-lg shadow-lg p-4 mb-4">
                <div id="progress-bar" class="progress-bar">
                    <!-- Renderizado pelo ProgressBar -->
                </div>
                
                <!-- Tooltip -->
                <div id="progress-tooltip" class="progress-tooltip hidden">
                    <span class="tooltip-emoji"></span>
                    <span class="tooltip-name"></span>
                    <span class="tooltip-status"></span>
                </div>
            </div>
            
            <!-- ============================================ -->
            <!-- CONTAINER DE SEÇÃO ATUAL -->
            <!-- ============================================ -->
            <div id="section-container" class="section-container section-container--visible">
                <!-- Renderizado pelo SectionContainer -->
            </div>
            
            <!-- ============================================ -->
            <!-- SIDEBAR ANTIGA (OCULTA - SERÁ REMOVIDA) -->
            <!-- ============================================ -->
            <aside id="sidebar" class="hidden">
                <!-- Conteúdo antigo mantido para referência -->
            </aside>
            
            <!-- Overlay para mobile (mantido para compatibilidade) -->
            <div id="sidebar-overlay" class="hidden"></div>
        </main>
```

**Nota:** A sidebar antiga foi marcada como `hidden`. O código JavaScript antigo pode dar erros, mas isso será corrigido na próxima tarefa.

---

### Tarefa 2.3: Adicionar JavaScript da classe SectionContainer

**Objetivo:** Criar a lógica do componente de seção.

**Localização:** Dentro da tag `<script>`, APÓS a classe `ProgressBar` e ANTES das variáveis globais.

**Encontre o comentário:**
```javascript
        // ============================================
        // FIM CLASSE PROGRESSBAR
        // ============================================
```

**Adicione DEPOIS:**

```javascript
        
        // ============================================
        // CLASSE SECTIONCONTAINER - CONTAINER DE SEÇÃO
        // ============================================
        
        class SectionContainer {
            /**
             * Componente que gerencia uma seção do BO
             * Inclui chat, input, texto gerado e transição
             */
            constructor(containerId, options = {}) {
                this.container = document.getElementById(containerId);
                
                // Dados da seção atual
                this.sectionData = options.sectionData || null;
                this.sectionId = options.sectionId || 1;
                
                // Estado
                this.state = 'pending'; // pending, in_progress, completed, skipped
                this.messages = []; // Histórico de mensagens do chat
                this.answers = {}; // Respostas do usuário { questionId: answer }
                this.currentQuestionIndex = 0;
                this.generatedText = null;
                this.isReadOnly = false;
                
                // Callbacks
                this.onAnswer = options.onAnswer || ((questionId, answer) => {});
                this.onComplete = options.onComplete || ((sectionId, answers) => {});
                this.onSkip = options.onSkip || ((sectionId) => {});
                this.onNavigateNext = options.onNavigateNext || ((nextSectionId) => {});
                this.onNavigateBack = options.onNavigateBack || (() => {});
                
                // Elementos internos
                this.chatEl = null;
                this.inputEl = null;
                this.inputFieldEl = null;
                this.generatedEl = null;
                this.transitionEl = null;
            }
            
            /**
             * Carrega dados de uma seção
             */
            loadSection(sectionData, options = {}) {
                this.sectionData = sectionData;
                this.sectionId = sectionData.id;
                this.state = options.state || 'in_progress';
                this.messages = options.messages || [];
                this.answers = options.answers || {};
                this.currentQuestionIndex = options.currentQuestionIndex || 0;
                this.generatedText = options.generatedText || null;
                this.isReadOnly = options.isReadOnly || false;
                
                this.render();
                
                // Se não for read-only e não tiver mensagens, mostrar primeira pergunta
                if (!this.isReadOnly && this.messages.length === 0 && this.state === 'in_progress') {
                    this._showCurrentQuestion();
                }
            }
            
            /**
             * Renderiza o container completo
             */
            render() {
                if (!this.container || !this.sectionData) return;
                
                const section = this.sectionData;
                
                this.container.innerHTML = `
                    <!-- Header da Seção -->
                    <div class="section-header">
                        <div class="section-header__title">
                            <span class="section-header__emoji">${section.emoji}</span>
                            <span>Seção ${section.id}: ${section.name}</span>
                        </div>
                        <span class="section-header__badge section-header__badge--${this.state}">
                            ${this._getStatusLabel()}
                        </span>
                    </div>
                    
                    <!-- Chat -->
                    <div class="section-chat" id="section-chat">
                        ${this._renderMessages()}
                    </div>
                    
                    <!-- Input (oculto se readonly ou completed) -->
                    ${!this.isReadOnly && this.state === 'in_progress' ? `
                    <div class="section-input" id="section-input">
                        <div class="section-input__form">
                            <input 
                                type="text" 
                                id="section-input-field"
                                class="section-input__field" 
                                placeholder="Digite sua resposta..."
                            >
                            <button 
                                type="button" 
                                id="section-input-btn"
                                class="section-input__button"
                            >
                                Enviar
                            </button>
                        </div>
                    </div>
                    ` : ''}
                    
                    <!-- Texto Gerado (se completed) -->
                    ${this.state === 'completed' && this.generatedText ? `
                    <div class="section-generated" id="section-generated">
                        <div class="section-generated__header">
                            <span class="section-generated__title">
                                📄 Texto Gerado - Seção ${section.id}
                            </span>
                            <button class="section-generated__copy" id="section-copy-btn">
                                📋 Copiar
                            </button>
                        </div>
                        <div class="section-generated__text">${this.generatedText}</div>
                    </div>
                    ` : ''}
                    
                    <!-- Transição para próxima seção (se completed e não for última) -->
                    ${this.state === 'completed' && this.sectionId < 8 ? this._renderTransition() : ''}
                    
                    <!-- Aviso de modo leitura -->
                    ${this.isReadOnly ? `
                    <div class="section-readonly-notice">
                        <span class="section-readonly-notice__text">
                            📖 Modo leitura - Esta seção já foi finalizada
                        </span>
                        <button class="section-readonly-notice__btn" id="section-back-btn">
                            ↩️ Voltar para seção atual
                        </button>
                    </div>
                    ` : ''}
                `;
                
                // Guardar referências
                this.chatEl = this.container.querySelector('#section-chat');
                this.inputEl = this.container.querySelector('#section-input');
                this.inputFieldEl = this.container.querySelector('#section-input-field');
                this.generatedEl = this.container.querySelector('#section-generated');
                this.transitionEl = this.container.querySelector('.section-transition');
                
                // Bind eventos
                this._bindEvents();
                
                // Scroll para o final do chat
                this._scrollToBottom();
            }
            
            /**
             * Retorna label do status
             */
            _getStatusLabel() {
                switch (this.state) {
                    case 'in_progress': return `${Object.keys(this.answers).length}/${this.sectionData.questions.length} perguntas`;
                    case 'completed': return '✓ Completa';
                    case 'skipped': return '⏭️ Pulada';
                    default: return 'Pendente';
                }
            }
            
            /**
             * Renderiza mensagens do chat
             */
            _renderMessages() {
                if (this.messages.length === 0) {
                    return '<div class="section-loading"><span class="section-loading__spinner"></span> Carregando...</div>';
                }
                
                return this.messages.map(msg => {
                    if (msg.type === 'bot') {
                        return `
                            <div class="chat-message chat-message--bot">
                                <div class="chat-message__bubble chat-message__bubble--bot">
                                    <div class="chat-message__text">${msg.text}</div>
                                    ${msg.hint ? `<div class="chat-message__hint">${msg.hint}</div>` : ''}
                                </div>
                            </div>
                        `;
                    } else {
                        return `
                            <div class="chat-message chat-message--user">
                                <div class="chat-message__bubble chat-message__bubble--user">
                                    <div class="chat-message__text">${msg.text}</div>
                                </div>
                            </div>
                        `;
                    }
                }).join('');
            }
            
            /**
             * Renderiza área de transição
             */
            _renderTransition() {
                const nextSection = window.SECTIONS_DATA ? window.SECTIONS_DATA.find(s => s.id === this.sectionId + 1) : null;
                
                if (!nextSection) return '';
                
                const canSkip = nextSection.skippable !== false;
                
                return `
                    <div class="section-transition">
                        <div class="section-transition__preview">
                            <span class="section-transition__preview-emoji">${nextSection.emoji}</span>
                            <div class="section-transition__preview-info">
                                <div class="section-transition__preview-label">Próxima seção</div>
                                <div class="section-transition__preview-name">Seção ${nextSection.id}: ${nextSection.name}</div>
                            </div>
                        </div>
                        <div class="section-transition__buttons">
                            <button class="section-transition__btn section-transition__btn--start" id="section-start-next">
                                ▶️ Iniciar Seção ${nextSection.id}
                            </button>
                            ${canSkip ? `
                            <button class="section-transition__btn section-transition__btn--skip" id="section-skip-next">
                                ⏭️ Pular
                            </button>
                            ` : ''}
                        </div>
                    </div>
                `;
            }
            
            /**
             * Bind de eventos
             */
            _bindEvents() {
                // Input - enviar resposta
                const inputBtn = this.container.querySelector('#section-input-btn');
                if (inputBtn) {
                    inputBtn.addEventListener('click', () => this._handleSubmit());
                }
                
                if (this.inputFieldEl) {
                    this.inputFieldEl.addEventListener('keypress', (e) => {
                        if (e.key === 'Enter') this._handleSubmit();
                    });
                    // Focar no input
                    setTimeout(() => this.inputFieldEl.focus(), 100);
                }
                
                // Copiar texto gerado
                const copyBtn = this.container.querySelector('#section-copy-btn');
                if (copyBtn) {
                    copyBtn.addEventListener('click', () => this._copyGeneratedText());
                }
                
                // Iniciar próxima seção
                const startNextBtn = this.container.querySelector('#section-start-next');
                if (startNextBtn) {
                    startNextBtn.addEventListener('click', () => {
                        this.onNavigateNext(this.sectionId + 1);
                    });
                }
                
                // Pular próxima seção
                const skipNextBtn = this.container.querySelector('#section-skip-next');
                if (skipNextBtn) {
                    skipNextBtn.addEventListener('click', () => {
                        this.onSkip(this.sectionId + 1);
                    });
                }
                
                // Voltar para seção atual
                const backBtn = this.container.querySelector('#section-back-btn');
                if (backBtn) {
                    backBtn.addEventListener('click', () => {
                        this.onNavigateBack();
                    });
                }
            }
            
            /**
             * Mostra a pergunta atual
             */
            _showCurrentQuestion() {
                if (!this.sectionData) return;
                
                const questions = this.sectionData.questions;
                
                // Verificar se tem skipQuestion primeiro
                if (this.sectionData.skipQuestion && this.currentQuestionIndex === 0 && !this.answers[this.sectionData.skipQuestion.id]) {
                    const skipQ = this.sectionData.skipQuestion;
                    this._addBotMessage(skipQ.text, skipQ.hint);
                    return;
                }
                
                // Calcular índice real (considerando skipQuestion)
                const realIndex = this.sectionData.skipQuestion ? this.currentQuestionIndex - 1 : this.currentQuestionIndex;
                
                if (realIndex >= 0 && realIndex < questions.length) {
                    const question = questions[realIndex];
                    this._addBotMessage(question.text, question.hint);
                } else if (realIndex >= questions.length) {
                    // Todas as perguntas respondidas
                    this._completeSection();
                }
            }
            
            /**
             * Adiciona mensagem do bot
             */
            _addBotMessage(text, hint = null) {
                this.messages.push({ type: 'bot', text, hint });
                this._updateChat();
            }
            
            /**
             * Adiciona mensagem do usuário
             */
            _addUserMessage(text) {
                this.messages.push({ type: 'user', text });
                this._updateChat();
            }
            
            /**
             * Atualiza área de chat
             */
            _updateChat() {
                if (this.chatEl) {
                    this.chatEl.innerHTML = this._renderMessages();
                    this._scrollToBottom();
                }
            }
            
            /**
             * Scroll para o final do chat
             */
            _scrollToBottom() {
                if (this.chatEl) {
                    this.chatEl.scrollTop = this.chatEl.scrollHeight;
                }
            }
            
            /**
             * Trata envio de resposta
             */
            _handleSubmit() {
                if (!this.inputFieldEl) return;
                
                const answer = this.inputFieldEl.value.trim();
                if (!answer) return;
                
                // Limpar input
                this.inputFieldEl.value = '';
                
                // Adicionar mensagem do usuário
                this._addUserMessage(answer);
                
                // Determinar qual pergunta foi respondida
                let questionId;
                if (this.sectionData.skipQuestion && this.currentQuestionIndex === 0) {
                    questionId = this.sectionData.skipQuestion.id;
                    
                    // Verificar se deve pular seção
                    const skipQ = this.sectionData.skipQuestion;
                    const skipOption = skipQ.options?.find(o => o.skipsSection && o.label.toUpperCase() === answer.toUpperCase());
                    if (skipOption) {
                        this._skipSection();
                        return;
                    }
                } else {
                    const realIndex = this.sectionData.skipQuestion ? this.currentQuestionIndex - 1 : this.currentQuestionIndex;
                    const question = this.sectionData.questions[realIndex];
                    questionId = question?.id;
                }
                
                // Salvar resposta
                if (questionId) {
                    this.answers[questionId] = answer;
                    this.onAnswer(questionId, answer);
                }
                
                // Avançar para próxima pergunta
                this.currentQuestionIndex++;
                
                // Atualizar badge
                this._updateBadge();
                
                // Mostrar próxima pergunta após delay
                setTimeout(() => {
                    this._showCurrentQuestion();
                }, 500);
            }
            
            /**
             * Atualiza badge de status
             */
            _updateBadge() {
                const badge = this.container.querySelector('.section-header__badge');
                if (badge) {
                    badge.textContent = this._getStatusLabel();
                }
            }
            
            /**
             * Completa a seção
             */
            _completeSection() {
                this.state = 'completed';
                
                // Simular texto gerado (será substituído pela API real na Fase 4)
                this.generatedText = `[Texto da Seção ${this.sectionId} será gerado pela API]\n\nRespostas coletadas:\n${
                    Object.entries(this.answers).map(([k, v]) => `- ${k}: ${v}`).join('\n')
                }`;
                
                // Callback
                this.onComplete(this.sectionId, this.answers);
                
                // Re-renderizar
                this.render();
            }
            
            /**
             * Pula a seção
             */
            _skipSection() {
                this.state = 'skipped';
                this.onSkip(this.sectionId);
                this.render();
            }
            
            /**
             * Copia texto gerado
             */
            _copyGeneratedText() {
                if (!this.generatedText) return;
                
                navigator.clipboard.writeText(this.generatedText).then(() => {
                    const copyBtn = this.container.querySelector('#section-copy-btn');
                    if (copyBtn) {
                        copyBtn.textContent = '✅ Copiado!';
                        setTimeout(() => {
                            copyBtn.textContent = '📋 Copiar';
                        }, 2000);
                    }
                });
            }
            
            /**
             * Mostra transição com fade
             */
            fadeOut() {
                return new Promise(resolve => {
                    this.container.classList.remove('section-container--visible');
                    this.container.classList.add('section-container--hidden');
                    setTimeout(resolve, 200);
                });
            }
            
            /**
             * Mostra seção com fade
             */
            fadeIn() {
                return new Promise(resolve => {
                    this.container.classList.remove('section-container--hidden');
                    this.container.classList.add('section-container--visible');
                    setTimeout(resolve, 200);
                });
            }
            
            /**
             * Define texto gerado (vem da API)
             */
            setGeneratedText(text) {
                this.generatedText = text;
                if (this.state === 'completed') {
                    this.render();
                }
            }
            
            /**
             * Retorna estado atual
             */
            getState() {
                return {
                    sectionId: this.sectionId,
                    state: this.state,
                    answers: this.answers,
                    messages: this.messages,
                    currentQuestionIndex: this.currentQuestionIndex,
                    generatedText: this.generatedText
                };
            }
        }
        
        // ============================================
        // FIM CLASSE SECTIONCONTAINER
        // ============================================
        
```

---

### Tarefa 2.4: Atualizar inicialização para testar SectionContainer

**Objetivo:** Modificar o código de inicialização para testar o novo componente.

**Localização:** Na função `window.addEventListener('load', ...)`.

**Encontre este trecho:**
```javascript
        // Inicializar
        window.addEventListener('load', () => {
            // ============================================
            // INICIALIZAR BARRA DE PROGRESSO (NOVO)
            // ============================================
            const progressBar = new ProgressBar('progress-bar', {
```

**Substitua TODA a função `window.addEventListener('load', ...)` por:**

```javascript
        // ============================================
        // INICIALIZAÇÃO - TESTE DOS COMPONENTES
        // ============================================
        
        // Variáveis globais para os novos componentes
        let progressBar = null;
        let sectionContainer = null;
        let currentSectionIndex = 0;
        
        window.addEventListener('load', () => {
            console.log('[App] Inicializando componentes...');
            
            // Verificar se sections.js carregou
            if (!window.SECTIONS_DATA) {
                console.error('[App] ERRO: SECTIONS_DATA não encontrado. Verifique se sections.js está carregando.');
                return;
            }
            
            console.log(`[App] ${SECTIONS_DATA.length} seções carregadas`);
            
            // ============================================
            // INICIALIZAR BARRA DE PROGRESSO
            // ============================================
            progressBar = new ProgressBar('progress-bar', {
                onSectionClick: (sectionId) => {
                    console.log('[App] Clicou na seção:', sectionId);
                    navigateToSection(sectionId);
                }
            });
            
            // Expor para debug
            window.progressBar = progressBar;
            
            // ============================================
            // INICIALIZAR CONTAINER DE SEÇÃO
            // ============================================
            sectionContainer = new SectionContainer('section-container', {
                onAnswer: (questionId, answer) => {
                    console.log('[App] Resposta:', questionId, '=', answer);
                    // Atualizar progresso na barra
                    const section = SECTIONS_DATA[currentSectionIndex];
                    const answeredCount = Object.keys(sectionContainer.answers).length;
                    progressBar.updateProgress(section.id, answeredCount, section.questions.length);
                },
                onComplete: (sectionId, answers) => {
                    console.log('[App] Seção completa:', sectionId, answers);
                    progressBar.markCompleted(sectionId);
                },
                onSkip: (sectionId) => {
                    console.log('[App] Seção pulada:', sectionId);
                    progressBar.markSkipped(sectionId);
                    // Avançar para próxima
                    navigateToSection(sectionId + 1);
                },
                onNavigateNext: (nextSectionId) => {
                    console.log('[App] Navegar para próxima seção:', nextSectionId);
                    navigateToSection(nextSectionId);
                },
                onNavigateBack: () => {
                    console.log('[App] Voltar para seção atual');
                    navigateToSection(currentSectionIndex + 1);
                }
            });
            
            // Expor para debug
            window.sectionContainer = sectionContainer;
            
            // ============================================
            // CARREGAR PRIMEIRA SEÇÃO
            // ============================================
            navigateToSection(1);
            
            console.log('[App] Inicialização completa!');
            console.log('[App] Use window.progressBar e window.sectionContainer para debug.');
        });
        
        /**
         * Navega para uma seção específica
         */
        async function navigateToSection(sectionId) {
            const sectionIndex = sectionId - 1;
            
            if (sectionIndex < 0 || sectionIndex >= SECTIONS_DATA.length) {
                console.warn('[App] Seção inválida:', sectionId);
                return;
            }
            
            const sectionData = SECTIONS_DATA[sectionIndex];
            
            console.log(`[App] Navegando para Seção ${sectionId}: ${sectionData.name}`);
            
            // Fade out
            await sectionContainer.fadeOut();
            
            // Atualizar índice atual
            currentSectionIndex = sectionIndex;
            
            // Determinar se é read-only (seção anterior já completada)
            const isReadOnly = false; // Por enquanto, sempre editável
            
            // Carregar seção
            sectionContainer.loadSection(sectionData, {
                state: 'in_progress',
                isReadOnly: isReadOnly
            });
            
            // Atualizar barra de progresso
            progressBar.setCurrentSection(sectionId);
            
            // Fade in
            await sectionContainer.fadeIn();
        }
        
        // ============================================
        // CÓDIGO ANTIGO DESABILITADO
        // ============================================
        // As funções abaixo são do sistema antigo e serão removidas na Fase 4
        // Por enquanto, estão comentadas para evitar erros
        
        /*
        // Configuração da API
        const API_URL = window.location.hostname === 'localhost' 
            ? 'http://localhost:8000' 
            : 'https://bo-assistant-backend.onrender.com';
        
        // ... resto do código antigo ...
        */
```

**Importante:** O código antigo (API_URL, sendMessage, etc.) deve ser comentado ou removido para evitar erros. Se houver erros no console sobre funções não definidas, comente o código antigo.

---

### Tarefa 2.5: Comentar código antigo que causa erros

**Objetivo:** Evitar erros de JavaScript do código antigo.

**Localização:** No final da tag `<script>`, onde estão as funções antigas.

**Ação:** Encontre e comente (ou delete) o código antigo que causa erros. Procure por:

1. `initializeSidebar()` - Comentar a função
2. `startSession()` - Comentar a função
3. Event listeners antigos (`sendButton.addEventListener`, etc.)
4. Variáveis que referenciam elementos que não existem mais (`userInput`, `sendButton`, etc.)

**Dica:** Se houver muitos erros, a maneira mais segura é:
1. Encontrar onde começa o código antigo (depois do comentário `// CÓDIGO ANTIGO DESABILITADO`)
2. Comentar TUDO até o final de `</script>` (exceto a tag de fechamento)

**Exemplo:**
```javascript
        // ============================================
        // CÓDIGO ANTIGO DESABILITADO
        // ============================================
        /*
        const API_URL = ...
        let sessionId = null;
        ... todo o código antigo ...
        */
    </script>
```

---

### Tarefa 2.6: Testar no navegador

**Objetivo:** Verificar se o novo layout funciona.

**Passos:**

1. Iniciar servidor local:
```bash
cd docs
python -m http.server 3000
```

2. Abrir `http://localhost:3000` no navegador

3. **Verificar visualmente:**
   - [ ] Barra de progresso aparece no topo
   - [ ] Container de seção aparece abaixo
   - [ ] Header mostra "Seção 1: Contexto da Ocorrência 🚔"
   - [ ] Primeira pergunta aparece no chat
   - [ ] Input de texto está visível e funcional

4. **Testar fluxo de perguntas:**
   - Digitar uma resposta e pressionar Enter
   - Verificar se a resposta aparece no chat
   - Verificar se a próxima pergunta aparece
   - Verificar se a barra de progresso atualiza

5. **Testar conclusão da seção:**
   - Responder todas as perguntas da Seção 1
   - Verificar se aparece a área de texto gerado
   - Verificar se aparecem os botões de transição

6. **Testar navegação:**
   - Clicar em "Iniciar Seção 2"
   - Verificar se há transição suave (fade)
   - Verificar se a Seção 2 carrega

7. **Verificar no console (F12):**
```javascript
// Ver estado da seção
sectionContainer.getState()

// Navegar manualmente
navigateToSection(3)

// Marcar seção como completa (teste)
progressBar.markCompleted(1)
progressBar.markCompleted(2)
```

8. **Verificar responsividade:**
   - Reduzir largura da janela
   - Input deve empilhar verticalmente
   - Chat deve permanecer legível

---

### Tarefa 2.7: Commit da Fase 2

**Objetivo:** Salvar o progresso.

**Comandos:**
```bash
cd /caminho/para/bo-assistant
git add .
git status

git commit -m "feat: implementar container de seção (Fase 2)

- Criar componente SectionContainer com chat e input
- Adicionar área de texto gerado após completar seção
- Implementar transição entre seções com fade
- Adicionar botões Iniciar/Pular próxima seção
- Integrar com ProgressBar
- Desabilitar código antigo (sidebar)
- Novo layout responsivo"

git push
```

---

## ✅ Checklist Final da Fase 2

Antes de prosseguir para a Fase 3, confirme:

- [ ] CSS do container de seção adicionado (~300 linhas)
- [ ] HTML do novo layout implementado
- [ ] Classe SectionContainer implementada
- [ ] Código de inicialização atualizado
- [ ] Código antigo comentado/desabilitado
- [ ] Primeira seção carrega corretamente
- [ ] Perguntas aparecem sequencialmente
- [ ] Respostas são registradas
- [ ] Barra de progresso atualiza
- [ ] Transição entre seções funciona
- [ ] Responsivo em mobile
- [ ] Commit feito e pushado

---

## 🐛 Troubleshooting

### Container não aparece
- Verificar se o HTML foi substituído corretamente
- Verificar se há erros no console
- Verificar se `section-container` existe no DOM

### Perguntas não aparecem
- Verificar se `SECTIONS_DATA` está carregado
- Verificar console por erros em `_showCurrentQuestion`

### Erros de "função não definida"
- Comentar TODO o código antigo
- Verificar se `initializeSidebar` e `startSession` estão comentados

### Input não funciona
- Verificar se o event listener está bindado
- Verificar se `inputFieldEl` não é null

### Transição não tem fade
- Verificar se as classes CSS `section-container--visible` e `section-container--hidden` estão presentes

---

## ⏭️ Próxima Fase

**Fase 3: Componentes de Input**
- Modelo: 🟢 Haiku
- Arquivo: `FASE_3_COMPONENTES_INPUT.md`
- Objetivo: Criar TextInput, SingleChoice e MultipleChoice como componentes reutilizáveis

---

## 📚 Referências

Arquivos na pasta `redesign/`:
- `PROPOSTA_REDESIGN_UX_BO_INTELIGENTE.md` - Seção "Container de Seção"
- `PLANO_IMPLEMENTACAO_REDESIGN_UX.md` - Fase 2 detalhada

---

*Documento gerado em 31/12/2025*  
*Para execução com Claude Haiku*
