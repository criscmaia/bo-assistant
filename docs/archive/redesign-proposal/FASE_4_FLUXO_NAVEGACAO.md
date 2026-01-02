# 🔄 FASE 4: Fluxo de Navegação e Integração com API

**Projeto:** BO Inteligente - Redesign UX  
**Fase:** 4 de 8  
**Modelo recomendado:** 🟡 **Sonnet** (integração complexa)  
**Tempo estimado:** 2-3 horas  
**Dependências:** Fase 3 concluída (Componentes de Input funcionando)

---

## ⚠️ FASE CRÍTICA

Esta fase integra todos os componentes e conecta com a API real. É a mais complexa porque:
1. Gerencia estado global da aplicação
2. Integra ProgressBar + SectionContainer + Inputs
3. Conecta com backend FastAPI
4. Gerencia navegação entre 8 seções
5. Trata geração de texto via Gemini

**Use Sonnet para esta fase.**

---

## 📋 Contexto

### O que foi feito nas fases anteriores?
- **Fase 0:** Branch criada, `sections.js` com 8 seções
- **Fase 1:** `ProgressBar` com estados visuais e navegação
- **Fase 2:** `SectionContainer` com chat e transições
- **Fase 3:** `TextInput`, `SingleChoice`, `MultipleChoice`

### O que será feito nesta fase?
1. Criar classe `BOApp` - gerenciador global da aplicação
2. Integrar com API real (FastAPI backend)
3. Implementar fluxo completo: início → perguntas → geração → fim
4. Gerenciar estado persistente (localStorage para rascunhos)
5. Tratar erros de API graciosamente

### Arquitetura Final

```
┌─────────────────────────────────────────────────────────────────┐
│                          BOApp                                  │
│  (Gerenciador Global - Estado, API, Navegação)                  │
├─────────────────────────────────────────────────────────────────┤
│                              │                                  │
│         ┌────────────────────┼────────────────────┐             │
│         ▼                    ▼                    ▼             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │ ProgressBar  │    │SectionContainer│   │   APIClient  │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                              │                                  │
│              ┌───────────────┼───────────────┐                  │
│              ▼               ▼               ▼                  │
│       ┌──────────┐    ┌──────────┐    ┌──────────┐             │
│       │TextInput │    │SingleChoice│   │MultiChoice│            │
│       └──────────┘    └──────────┘    └──────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Objetivo

Adicionar ao `index.html`:
1. Classe `APIClient` para comunicação com backend
2. Classe `BOApp` para gerenciamento global
3. Lógica de inicialização completa
4. Tratamento de erros e loading states
5. Persistência local (rascunho)

---

## 📁 Arquivo a Modificar

`docs/index.html`

---

## ✅ Tarefas

### Tarefa 4.1: Criar classe APIClient

**Objetivo:** Encapsular toda comunicação com o backend.

**Localização:** Dentro da tag `<script>`, APÓS as classes de Input (TextInput, SingleChoice, MultipleChoice).

**Encontre o comentário:**
```javascript
        // ============================================
        // FIM CLASSE MULTIPLECHOICE
        // ============================================
```

**Adicione DEPOIS:**

```javascript
        
        // ============================================
        // CLASSE APICLIENT - COMUNICAÇÃO COM BACKEND
        // ============================================
        
        class APIClient {
            /**
             * Cliente para comunicação com a API FastAPI
             */
            constructor(baseUrl = null) {
                this.baseUrl = baseUrl || this._detectBaseUrl();
                this.sessionId = null;
                this.boId = null;
            }
            
            /**
             * Detecta URL base baseado no ambiente
             */
            _detectBaseUrl() {
                if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
                    return 'http://localhost:8000';
                }
                return 'https://bo-assistant-backend.onrender.com';
            }
            
            /**
             * Faz requisição genérica
             */
            async _request(endpoint, options = {}) {
                const url = `${this.baseUrl}${endpoint}`;
                
                const defaultOptions = {
                    headers: {
                        'Content-Type': 'application/json',
                    },
                };
                
                const finalOptions = { ...defaultOptions, ...options };
                
                try {
                    console.log(`[API] ${options.method || 'GET'} ${endpoint}`);
                    
                    const response = await fetch(url, finalOptions);
                    
                    if (!response.ok) {
                        const errorData = await response.json().catch(() => ({}));
                        throw new APIError(
                            errorData.detail || `Erro ${response.status}`,
                            response.status,
                            errorData
                        );
                    }
                    
                    return await response.json();
                } catch (error) {
                    if (error instanceof APIError) {
                        throw error;
                    }
                    
                    // Erro de rede
                    throw new APIError(
                        'Não foi possível conectar ao servidor. Verifique sua conexão.',
                        0,
                        { originalError: error.message }
                    );
                }
            }
            
            /**
             * Verifica se servidor está online
             */
            async healthCheck() {
                try {
                    const data = await this._request('/health');
                    return { online: true, ...data };
                } catch (error) {
                    return { online: false, error: error.message };
                }
            }
            
            /**
             * Inicia nova sessão de BO
             */
            async startSession() {
                const data = await this._request('/new_session', {
                    method: 'POST',
                });
                
                this.sessionId = data.session_id;
                this.boId = data.bo_id;
                
                console.log(`[API] Sessão iniciada: ${this.boId}`);
                
                return data;
            }
            
            /**
             * Envia resposta para o backend (validação + próxima pergunta)
             * NOTA: O backend atual só suporta Seção 1. Para outras seções,
             * usaremos modo offline temporariamente.
             */
            async sendAnswer(message, llmProvider = 'gemini') {
                if (!this.sessionId) {
                    throw new APIError('Sessão não iniciada', 400);
                }
                
                const data = await this._request('/chat', {
                    method: 'POST',
                    body: JSON.stringify({
                        session_id: this.sessionId,
                        message: message,
                        llm_provider: llmProvider,
                    }),
                });
                
                return data;
            }
            
            /**
             * Edita uma resposta anterior
             */
            async editAnswer(step, message, llmProvider = 'gemini') {
                if (!this.sessionId) {
                    throw new APIError('Sessão não iniciada', 400);
                }
                
                const data = await this._request(`/chat/${this.sessionId}/answer/${step}`, {
                    method: 'PUT',
                    body: JSON.stringify({
                        message: message,
                        llm_provider: llmProvider,
                    }),
                });
                
                return data;
            }
            
            /**
             * Envia feedback
             */
            async sendFeedback(feedbackType, eventId = null, userMessage = null, context = null) {
                if (!this.boId) {
                    console.warn('[API] BO ID não disponível para feedback');
                    return null;
                }
                
                const data = await this._request('/feedback', {
                    method: 'POST',
                    body: JSON.stringify({
                        bo_id: this.boId,
                        event_id: eventId,
                        feedback_type: feedbackType,
                        user_message: userMessage,
                        context: context,
                        metadata: {
                            screen_resolution: `${screen.width}x${screen.height}`,
                            viewport: `${window.innerWidth}x${window.innerHeight}`,
                            user_agent: navigator.userAgent,
                        },
                    }),
                });
                
                return data;
            }
            
            /**
             * Obtém status da sessão
             */
            async getSessionStatus() {
                if (!this.sessionId) {
                    return null;
                }
                
                const data = await this._request(`/session/${this.sessionId}/status`);
                return data;
            }
            
            /**
             * Retorna IDs atuais
             */
            getIds() {
                return {
                    sessionId: this.sessionId,
                    boId: this.boId,
                };
            }
            
            /**
             * Restaura sessão existente
             */
            restoreSession(sessionId, boId) {
                this.sessionId = sessionId;
                this.boId = boId;
            }
        }
        
        /**
         * Classe de erro customizada para API
         */
        class APIError extends Error {
            constructor(message, status, data = null) {
                super(message);
                this.name = 'APIError';
                this.status = status;
                this.data = data;
            }
        }
        
        // ============================================
        // FIM CLASSE APICLIENT
        // ============================================
        
```

---

### Tarefa 4.2: Criar classe BOApp (Gerenciador Global)

**Objetivo:** Orquestrar todos os componentes e gerenciar estado.

**Localização:** Logo após a classe APIClient.

**Adicione:**

```javascript
        // ============================================
        // CLASSE BOAPP - GERENCIADOR GLOBAL
        // ============================================
        
        class BOApp {
            /**
             * Aplicação principal do BO Inteligente
             * Gerencia estado global, navegação e integração
             */
            constructor() {
                // Componentes
                this.api = new APIClient();
                this.progressBar = null;
                this.sectionContainer = null;
                
                // Estado global
                this.currentSectionIndex = 0;
                this.sectionsState = {}; // { sectionId: { status, answers, generatedText } }
                this.isLoading = false;
                this.isOnline = true;
                
                // Configurações
                this.autoSave = true;
                this.autoSaveKey = 'bo_draft';
                
                // Bind de métodos para callbacks
                this._onAnswer = this._onAnswer.bind(this);
                this._onSectionComplete = this._onSectionComplete.bind(this);
                this._onSectionSkip = this._onSectionSkip.bind(this);
                this._onNavigateNext = this._onNavigateNext.bind(this);
                this._onNavigateBack = this._onNavigateBack.bind(this);
                this._onProgressBarClick = this._onProgressBarClick.bind(this);
            }
            
            /**
             * Inicializa a aplicação
             */
            async init() {
                console.log('[BOApp] Inicializando...');
                
                // Verificar dados de seções
                if (!window.SECTIONS_DATA) {
                    this._showFatalError('Dados de seções não encontrados. Recarregue a página.');
                    return;
                }
                
                // Inicializar estado das seções
                this._initSectionsState();
                
                // Inicializar ProgressBar
                this._initProgressBar();
                
                // Inicializar SectionContainer
                this._initSectionContainer();
                
                // Verificar conexão com API
                await this._checkApiConnection();
                
                // Tentar restaurar rascunho
                const hasDraft = this._tryRestoreDraft();
                
                if (!hasDraft) {
                    // Iniciar nova sessão
                    await this._startNewSession();
                }
                
                // Carregar primeira seção (ou seção do rascunho)
                this._loadCurrentSection();
                
                console.log('[BOApp] Inicialização completa!');
            }
            
            /**
             * Inicializa estado de todas as seções
             */
            _initSectionsState() {
                SECTIONS_DATA.forEach(section => {
                    this.sectionsState[section.id] = {
                        status: 'pending', // pending, in_progress, completed, skipped
                        answers: {},
                        messages: [],
                        currentQuestionIndex: 0,
                        generatedText: null,
                    };
                });
            }
            
            /**
             * Inicializa ProgressBar
             */
            _initProgressBar() {
                this.progressBar = new ProgressBar('progress-bar', {
                    onSectionClick: this._onProgressBarClick,
                });
                
                window.progressBar = this.progressBar; // Debug
            }
            
            /**
             * Inicializa SectionContainer
             */
            _initSectionContainer() {
                this.sectionContainer = new SectionContainer('section-container', {
                    onAnswer: this._onAnswer,
                    onComplete: this._onSectionComplete,
                    onSkip: this._onSectionSkip,
                    onNavigateNext: this._onNavigateNext,
                    onNavigateBack: this._onNavigateBack,
                });
                
                window.sectionContainer = this.sectionContainer; // Debug
            }
            
            /**
             * Verifica conexão com API
             */
            async _checkApiConnection() {
                this._showLoading('Conectando ao servidor...');
                
                const health = await this.api.healthCheck();
                
                this._hideLoading();
                
                if (!health.online) {
                    this.isOnline = false;
                    this._showWarning('Servidor offline. Funcionando em modo rascunho.');
                    console.warn('[BOApp] API offline:', health.error);
                } else {
                    this.isOnline = true;
                    console.log('[BOApp] API online');
                }
            }
            
            /**
             * Inicia nova sessão
             */
            async _startNewSession() {
                if (!this.isOnline) {
                    console.log('[BOApp] Modo offline - sessão local');
                    return;
                }
                
                try {
                    this._showLoading('Iniciando sessão...');
                    
                    const data = await this.api.startSession();
                    
                    console.log('[BOApp] Sessão:', data.bo_id);
                    
                    this._hideLoading();
                    
                } catch (error) {
                    this._hideLoading();
                    console.error('[BOApp] Erro ao iniciar sessão:', error);
                    this._showWarning('Erro ao conectar. Funcionando em modo rascunho.');
                    this.isOnline = false;
                }
            }
            
            /**
             * Carrega a seção atual
             */
            _loadCurrentSection() {
                const sectionData = SECTIONS_DATA[this.currentSectionIndex];
                const sectionState = this.sectionsState[sectionData.id];
                
                // Marcar como em progresso se pendente
                if (sectionState.status === 'pending') {
                    sectionState.status = 'in_progress';
                }
                
                // Atualizar ProgressBar
                this.progressBar.setCurrentSection(sectionData.id);
                
                // Carregar no container
                this.sectionContainer.loadSection(sectionData, {
                    state: sectionState.status,
                    messages: sectionState.messages,
                    answers: sectionState.answers,
                    currentQuestionIndex: sectionState.currentQuestionIndex,
                    generatedText: sectionState.generatedText,
                    isReadOnly: false,
                });
            }
            
            /**
             * Callback: resposta enviada
             */
            async _onAnswer(questionId, answer) {
                console.log('[BOApp] Resposta:', questionId, '=', answer);
                
                const sectionId = this.currentSectionIndex + 1;
                const sectionState = this.sectionsState[sectionId];
                
                // Salvar resposta no estado
                sectionState.answers[questionId] = answer;
                sectionState.currentQuestionIndex = this.sectionContainer.currentQuestionIndex;
                sectionState.messages = [...this.sectionContainer.messages];
                
                // Atualizar progresso
                const section = SECTIONS_DATA[this.currentSectionIndex];
                const answeredCount = Object.keys(sectionState.answers).length;
                const totalQuestions = section.questions.length + (section.skipQuestion ? 1 : 0);
                
                this.progressBar.updateProgress(sectionId, answeredCount, totalQuestions);
                
                // Auto-save
                if (this.autoSave) {
                    this._saveDraft();
                }
                
                // Se online e seção 1, enviar para API (validação)
                // NOTA: Backend atual só suporta seção 1
                if (this.isOnline && sectionId === 1) {
                    try {
                        const response = await this.api.sendAnswer(answer);
                        
                        if (response.validation_error) {
                            // Mostrar erro de validação
                            this._showValidationError(response.validation_error);
                        }
                    } catch (error) {
                        console.error('[BOApp] Erro ao enviar resposta:', error);
                        // Continuar offline
                    }
                }
            }
            
            /**
             * Callback: seção completa
             */
            async _onSectionComplete(sectionId, answers) {
                console.log('[BOApp] Seção completa:', sectionId);
                
                const sectionState = this.sectionsState[sectionId];
                sectionState.status = 'completed';
                sectionState.answers = answers;
                sectionState.messages = [...this.sectionContainer.messages];
                
                // Marcar na barra de progresso
                this.progressBar.markCompleted(sectionId);
                
                // Gerar texto (se online e seção 1)
                if (this.isOnline && sectionId === 1) {
                    await this._generateSectionText(sectionId);
                } else {
                    // Texto placeholder para outras seções
                    sectionState.generatedText = this._generatePlaceholderText(sectionId, answers);
                    this.sectionContainer.setGeneratedText(sectionState.generatedText);
                }
                
                // Auto-save
                if (this.autoSave) {
                    this._saveDraft();
                }
            }
            
            /**
             * Gera texto via API
             */
            async _generateSectionText(sectionId) {
                this._showLoading('Gerando texto...');
                
                try {
                    // O backend já gera o texto quando a seção completa
                    // Buscar do último response
                    const status = await this.api.getSessionStatus();
                    
                    // Por enquanto, usar placeholder
                    // TODO: Integrar com geração real quando backend suportar
                    const sectionState = this.sectionsState[sectionId];
                    sectionState.generatedText = this._generatePlaceholderText(sectionId, sectionState.answers);
                    
                    this.sectionContainer.setGeneratedText(sectionState.generatedText);
                    
                } catch (error) {
                    console.error('[BOApp] Erro ao gerar texto:', error);
                    
                    // Usar placeholder
                    const sectionState = this.sectionsState[sectionId];
                    sectionState.generatedText = this._generatePlaceholderText(sectionId, sectionState.answers);
                    this.sectionContainer.setGeneratedText(sectionState.generatedText);
                    
                } finally {
                    this._hideLoading();
                }
            }
            
            /**
             * Gera texto placeholder (para seções sem API)
             */
            _generatePlaceholderText(sectionId, answers) {
                const section = SECTIONS_DATA.find(s => s.id === sectionId);
                
                let text = `[SEÇÃO ${sectionId}: ${section.name}]\n\n`;
                text += `Respostas coletadas:\n`;
                
                Object.entries(answers).forEach(([key, value]) => {
                    text += `• ${key}: ${value}\n`;
                });
                
                text += `\n[Texto será gerado pela API quando integração estiver completa]`;
                
                return text;
            }
            
            /**
             * Callback: seção pulada
             */
            _onSectionSkip(sectionId) {
                console.log('[BOApp] Seção pulada:', sectionId);
                
                const sectionState = this.sectionsState[sectionId];
                sectionState.status = 'skipped';
                
                // Marcar na barra de progresso
                this.progressBar.markSkipped(sectionId);
                
                // Avançar para próxima
                this._navigateToNextSection();
                
                // Auto-save
                if (this.autoSave) {
                    this._saveDraft();
                }
            }
            
            /**
             * Callback: navegar para próxima seção
             */
            _onNavigateNext(nextSectionId) {
                console.log('[BOApp] Navegar para seção:', nextSectionId);
                this._navigateToSection(nextSectionId);
            }
            
            /**
             * Callback: voltar para seção atual
             */
            _onNavigateBack() {
                console.log('[BOApp] Voltar para seção atual');
                this._loadCurrentSection();
            }
            
            /**
             * Callback: clique na barra de progresso
             */
            _onProgressBarClick(sectionId) {
                console.log('[BOApp] Clique na seção:', sectionId);
                
                const sectionState = this.sectionsState[sectionId];
                
                // Só permitir navegar para seções já visitadas
                if (sectionState.status === 'pending' && sectionId > this.currentSectionIndex + 1) {
                    console.log('[BOApp] Seção ainda não disponível');
                    return;
                }
                
                this._navigateToSection(sectionId, true);
            }
            
            /**
             * Navega para uma seção específica
             */
            async _navigateToSection(sectionId, isReadOnly = false) {
                const sectionIndex = sectionId - 1;
                
                if (sectionIndex < 0 || sectionIndex >= SECTIONS_DATA.length) {
                    console.warn('[BOApp] Seção inválida:', sectionId);
                    return;
                }
                
                // Fade out
                await this.sectionContainer.fadeOut();
                
                // Atualizar índice
                this.currentSectionIndex = sectionIndex;
                
                // Carregar seção
                const sectionData = SECTIONS_DATA[sectionIndex];
                const sectionState = this.sectionsState[sectionId];
                
                // Determinar se é read-only
                const shouldBeReadOnly = isReadOnly || 
                    (sectionState.status === 'completed' && sectionId < this._getCurrentActiveSectionId());
                
                // Marcar como em progresso se necessário
                if (sectionState.status === 'pending') {
                    sectionState.status = 'in_progress';
                }
                
                // Atualizar ProgressBar
                this.progressBar.setCurrentSection(sectionId);
                
                // Carregar no container
                this.sectionContainer.loadSection(sectionData, {
                    state: sectionState.status,
                    messages: sectionState.messages,
                    answers: sectionState.answers,
                    currentQuestionIndex: sectionState.currentQuestionIndex,
                    generatedText: sectionState.generatedText,
                    isReadOnly: shouldBeReadOnly,
                });
                
                // Fade in
                await this.sectionContainer.fadeIn();
            }
            
            /**
             * Navega para próxima seção disponível
             */
            _navigateToNextSection() {
                const nextIndex = this.currentSectionIndex + 1;
                
                if (nextIndex < SECTIONS_DATA.length) {
                    this._navigateToSection(nextIndex + 1);
                } else {
                    // Todas as seções completas
                    this._showFinalScreen();
                }
            }
            
            /**
             * Retorna ID da seção ativa mais recente
             */
            _getCurrentActiveSectionId() {
                for (let i = SECTIONS_DATA.length - 1; i >= 0; i--) {
                    const state = this.sectionsState[i + 1];
                    if (state.status === 'in_progress') {
                        return i + 1;
                    }
                }
                return 1;
            }
            
            /**
             * Mostra tela final (todas seções completas)
             */
            _showFinalScreen() {
                console.log('[BOApp] Todas as seções completas!');
                // TODO: Implementar na Fase 5
                alert('🎉 Todas as seções foram completadas!\n\nO texto completo do BO está pronto.');
            }
            
            // ==========================================
            // PERSISTÊNCIA (RASCUNHO)
            // ==========================================
            
            /**
             * Salva rascunho no localStorage
             */
            _saveDraft() {
                try {
                    const draft = {
                        version: '1.0',
                        timestamp: new Date().toISOString(),
                        currentSectionIndex: this.currentSectionIndex,
                        sectionsState: this.sectionsState,
                        apiIds: this.api.getIds(),
                    };
                    
                    localStorage.setItem(this.autoSaveKey, JSON.stringify(draft));
                    console.log('[BOApp] Rascunho salvo');
                    
                } catch (error) {
                    console.error('[BOApp] Erro ao salvar rascunho:', error);
                }
            }
            
            /**
             * Tenta restaurar rascunho
             */
            _tryRestoreDraft() {
                try {
                    const saved = localStorage.getItem(this.autoSaveKey);
                    
                    if (!saved) return false;
                    
                    const draft = JSON.parse(saved);
                    
                    // Verificar se rascunho é recente (menos de 24h)
                    const savedTime = new Date(draft.timestamp);
                    const now = new Date();
                    const hoursDiff = (now - savedTime) / (1000 * 60 * 60);
                    
                    if (hoursDiff > 24) {
                        console.log('[BOApp] Rascunho expirado, removendo...');
                        localStorage.removeItem(this.autoSaveKey);
                        return false;
                    }
                    
                    // Perguntar ao usuário
                    const shouldRestore = confirm(
                        '📝 Encontramos um rascunho salvo.\n\n' +
                        `Salvo em: ${savedTime.toLocaleString()}\n\n` +
                        'Deseja continuar de onde parou?'
                    );
                    
                    if (!shouldRestore) {
                        localStorage.removeItem(this.autoSaveKey);
                        return false;
                    }
                    
                    // Restaurar estado
                    this.currentSectionIndex = draft.currentSectionIndex;
                    this.sectionsState = draft.sectionsState;
                    
                    // Restaurar sessão API se disponível
                    if (draft.apiIds?.sessionId) {
                        this.api.restoreSession(draft.apiIds.sessionId, draft.apiIds.boId);
                    }
                    
                    // Atualizar ProgressBar com estados salvos
                    Object.entries(this.sectionsState).forEach(([id, state]) => {
                        const sectionId = parseInt(id);
                        if (state.status === 'completed') {
                            this.progressBar.markCompleted(sectionId);
                        } else if (state.status === 'skipped') {
                            this.progressBar.markSkipped(sectionId);
                        }
                    });
                    
                    console.log('[BOApp] Rascunho restaurado');
                    return true;
                    
                } catch (error) {
                    console.error('[BOApp] Erro ao restaurar rascunho:', error);
                    localStorage.removeItem(this.autoSaveKey);
                    return false;
                }
            }
            
            /**
             * Limpa rascunho
             */
            clearDraft() {
                localStorage.removeItem(this.autoSaveKey);
                console.log('[BOApp] Rascunho removido');
            }
            
            // ==========================================
            // UI HELPERS
            // ==========================================
            
            /**
             * Mostra loading overlay
             */
            _showLoading(message = 'Carregando...') {
                this.isLoading = true;
                
                let overlay = document.getElementById('app-loading-overlay');
                
                if (!overlay) {
                    overlay = document.createElement('div');
                    overlay.id = 'app-loading-overlay';
                    overlay.innerHTML = `
                        <div class="loading-content">
                            <div class="loading-spinner"></div>
                            <div class="loading-message">${message}</div>
                        </div>
                    `;
                    overlay.style.cssText = `
                        position: fixed;
                        inset: 0;
                        background: rgba(0, 0, 0, 0.5);
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        z-index: 1000;
                    `;
                    overlay.querySelector('.loading-content').style.cssText = `
                        background: white;
                        padding: 24px 32px;
                        border-radius: 12px;
                        display: flex;
                        align-items: center;
                        gap: 16px;
                    `;
                    overlay.querySelector('.loading-spinner').style.cssText = `
                        width: 24px;
                        height: 24px;
                        border: 3px solid #e5e7eb;
                        border-top-color: #3b82f6;
                        border-radius: 50%;
                        animation: spin 1s linear infinite;
                    `;
                    document.body.appendChild(overlay);
                } else {
                    overlay.querySelector('.loading-message').textContent = message;
                    overlay.style.display = 'flex';
                }
            }
            
            /**
             * Esconde loading overlay
             */
            _hideLoading() {
                this.isLoading = false;
                
                const overlay = document.getElementById('app-loading-overlay');
                if (overlay) {
                    overlay.style.display = 'none';
                }
            }
            
            /**
             * Mostra aviso temporário
             */
            _showWarning(message) {
                console.warn('[BOApp]', message);
                
                const toast = document.createElement('div');
                toast.textContent = `⚠️ ${message}`;
                toast.style.cssText = `
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    background: #fef3c7;
                    color: #92400e;
                    padding: 12px 20px;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                    z-index: 1001;
                    animation: fadeIn 0.3s ease;
                `;
                document.body.appendChild(toast);
                
                setTimeout(() => {
                    toast.style.opacity = '0';
                    setTimeout(() => toast.remove(), 300);
                }, 5000);
            }
            
            /**
             * Mostra erro de validação
             */
            _showValidationError(message) {
                // O componente de input já trata isso
                console.log('[BOApp] Erro de validação:', message);
            }
            
            /**
             * Mostra erro fatal
             */
            _showFatalError(message) {
                console.error('[BOApp] ERRO FATAL:', message);
                
                const container = document.getElementById('section-container');
                if (container) {
                    container.innerHTML = `
                        <div style="padding: 40px; text-align: center;">
                            <div style="font-size: 48px; margin-bottom: 16px;">❌</div>
                            <h2 style="color: #dc2626; margin-bottom: 8px;">Erro</h2>
                            <p style="color: #6b7280;">${message}</p>
                            <button onclick="location.reload()" style="
                                margin-top: 16px;
                                padding: 12px 24px;
                                background: #3b82f6;
                                color: white;
                                border: none;
                                border-radius: 8px;
                                cursor: pointer;
                            ">
                                Recarregar página
                            </button>
                        </div>
                    `;
                }
            }
        }
        
        // ============================================
        // FIM CLASSE BOAPP
        // ============================================
        
```

---

### Tarefa 4.3: Atualizar inicialização para usar BOApp

**Objetivo:** Substituir a inicialização antiga pelo novo gerenciador.

**Localização:** Encontre o bloco de inicialização atual (criado na Fase 2):

```javascript
        // ============================================
        // INICIALIZAÇÃO - TESTE DOS COMPONENTES
        // ============================================
        
        // Variáveis globais para os novos componentes
        let progressBar = null;
        let sectionContainer = null;
        let currentSectionIndex = 0;
        
        window.addEventListener('load', () => {
            // ...código da Fase 2...
        });
```

**Substitua TODO esse bloco por:**

```javascript
        // ============================================
        // INICIALIZAÇÃO DA APLICAÇÃO
        // ============================================
        
        // Instância global da aplicação
        let app = null;
        
        window.addEventListener('load', async () => {
            console.log('[Init] BO Inteligente v0.5.0 - Novo Design');
            console.log('[Init] Inicializando...');
            
            // Criar e inicializar aplicação
            app = new BOApp();
            await app.init();
            
            // Expor para debug
            window.app = app;
            window.progressBar = app.progressBar;
            window.sectionContainer = app.sectionContainer;
            window.api = app.api;
            
            console.log('[Init] Aplicação pronta!');
            console.log('[Init] Use window.app para debug.');
        });
        
        // ============================================
        // FUNÇÕES GLOBAIS DE DEBUG
        // ============================================
        
        /**
         * Navega para uma seção (para debug)
         */
        function goToSection(sectionId) {
            if (app) {
                app._navigateToSection(sectionId);
            }
        }
        
        /**
         * Limpa rascunho e reinicia
         */
        function resetApp() {
            if (app) {
                app.clearDraft();
            }
            location.reload();
        }
        
        /**
         * Mostra estado atual
         */
        function showState() {
            if (app) {
                console.log('Estado das seções:', app.sectionsState);
                console.log('Seção atual:', app.currentSectionIndex + 1);
                console.log('API:', app.api.getIds());
            }
        }
```

---

### Tarefa 4.4: Adicionar CSS para loading overlay

**Objetivo:** Estilizar o overlay de loading.

**Localização:** No CSS, após os estilos dos componentes de input.

**Encontre:**
```css
        /* ============================================ */
        /* FIM COMPONENTES DE INPUT - ESTILOS */
        /* ============================================ */
```

**Adicione DEPOIS:**

```css
        
        /* ============================================ */
        /* LOADING E TOASTS - ESTILOS */
        /* ============================================ */
        
        #app-loading-overlay {
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            backdrop-filter: blur(2px);
        }
        
        #app-loading-overlay .loading-content {
            background: white;
            padding: 24px 32px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            gap: 16px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
        }
        
        #app-loading-overlay .loading-spinner {
            width: 28px;
            height: 28px;
            border: 3px solid #e5e7eb;
            border-top-color: #3b82f6;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        #app-loading-overlay .loading-message {
            font-size: 15px;
            color: #374151;
            font-weight: 500;
        }
        
        /* Toast de aviso */
        .app-toast {
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 1001;
            animation: slideInRight 0.3s ease;
        }
        
        .app-toast--warning {
            background: #fef3c7;
            color: #92400e;
            border: 1px solid #fcd34d;
        }
        
        .app-toast--error {
            background: #fee2e2;
            color: #dc2626;
            border: 1px solid #fca5a5;
        }
        
        .app-toast--success {
            background: #d1fae5;
            color: #065f46;
            border: 1px solid #6ee7b7;
        }
        
        @keyframes slideInRight {
            from {
                opacity: 0;
                transform: translateX(20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        /* ============================================ */
        /* FIM LOADING E TOASTS - ESTILOS */
        /* ============================================ */
```

---

### Tarefa 4.5: Remover código de teste da Fase 1-3

**Objetivo:** Limpar código de teste que não é mais necessário.

**Ação:** Procure e remova/comente:

1. **Código de teste da ProgressBar (Fase 1):**
   - Procure por `// Teste: simular estados` ou similar
   - Comente ou delete a simulação de setTimeout

2. **Função `navigateToSection()` antiga (Fase 2):**
   - Já foi substituída pela nova inicialização
   - Verificar se foi removida

3. **Variáveis globais antigas:**
   - `let progressBar = null;` (se ainda existir fora da classe)
   - `let sectionContainer = null;` (se ainda existir fora da classe)
   - `let currentSectionIndex = 0;` (se ainda existir fora da classe)

**Nota:** Com a nova estrutura, as variáveis são gerenciadas dentro de `BOApp`.

---

### Tarefa 4.6: Testar no navegador

**Objetivo:** Verificar se a integração funciona.

**Passos:**

1. **Iniciar backend (terminal 1):**
```bash
cd backend
source venv/bin/activate  # ou venv\Scripts\activate no Windows
uvicorn main:app --reload --port 8000
```

2. **Iniciar frontend (terminal 2):**
```bash
cd docs
python -m http.server 3000
```

3. Abrir `http://localhost:3000` no navegador

4. **Verificar inicialização:**
   - [ ] Loading "Conectando ao servidor..." aparece
   - [ ] Conexão com API estabelecida (ver console)
   - [ ] Primeira seção carrega
   - [ ] ProgressBar mostra seção 1 como atual

5. **Testar fluxo de perguntas:**
   - [ ] Responder perguntas da Seção 1
   - [ ] Validação funciona (API)
   - [ ] Progresso atualiza na barra
   - [ ] Seção completa gera texto

6. **Testar persistência:**
   - Responder algumas perguntas
   - Fechar aba
   - Abrir novamente
   - [ ] Modal de restauração aparece
   - [ ] Clicar "OK" restaura o estado

7. **Testar modo offline:**
   - Parar o backend (Ctrl+C)
   - Recarregar página
   - [ ] Aviso "Servidor offline" aparece
   - [ ] Sistema funciona em modo rascunho

8. **Verificar no console (F12):**
```javascript
// Ver estado completo
showState()

// Navegar manualmente
goToSection(3)

// Limpar e reiniciar
resetApp()

// Ver IDs da API
app.api.getIds()

// Ver estado de uma seção
app.sectionsState[1]
```

---

### Tarefa 4.7: Commit da Fase 4

**Objetivo:** Salvar o progresso.

**Comandos:**
```bash
cd /caminho/para/bo-assistant
git add .
git status

git commit -m "feat: implementar fluxo de navegação e API (Fase 4)

- Criar APIClient para comunicação com backend
- Criar BOApp como gerenciador global
- Integrar ProgressBar + SectionContainer + Inputs
- Implementar persistência com localStorage (rascunho)
- Adicionar tratamento de erros e loading states
- Modo offline funcional
- Funções de debug: goToSection(), resetApp(), showState()"

git push
```

---

## ✅ Checklist Final da Fase 4

Antes de prosseguir para a Fase 5, confirme:

- [ ] Classe APIClient implementada
- [ ] Classe BOApp implementada
- [ ] Inicialização nova funcionando
- [ ] CSS de loading/toasts adicionado
- [ ] Código de teste antigo removido
- [ ] Conexão com API funciona (Seção 1)
- [ ] Persistência (localStorage) funciona
- [ ] Modo offline funciona
- [ ] Navegação entre seções funciona
- [ ] Estado é mantido ao trocar seções
- [ ] Commit feito e pushado

---

## 🐛 Troubleshooting

### "APIClient is not defined"
- Verificar se a classe está antes de BOApp
- Verificar se não há erros de sintaxe acima

### API não conecta
- Verificar se backend está rodando
- Verificar URL no console (deve ser localhost:8000)
- Verificar CORS no backend

### Rascunho não restaura
- Verificar localStorage no DevTools (Application > Local Storage)
- Verificar se `bo_draft` existe
- Verificar console por erros de parse

### Perguntas não avançam
- Verificar se `_onAnswer` está sendo chamado
- Verificar se componentes de input têm callbacks corretos
- Ver console por erros

### Loading fica preso
- Verificar se `_hideLoading()` está sendo chamado
- Verificar se há erros não tratados (try/catch)

---

## ⏭️ Próxima Fase

**Fase 5: Tela Final**
- Modelo: 🟢 Haiku
- Arquivo: `FASE_5_TELA_FINAL.md`
- Objetivo: Criar tela de resumo com todos os textos gerados e exportação

---

## 📚 Referências

- `sections.js` - Estrutura das 8 seções
- `main.py` (backend) - Endpoints da API
- `PROPOSTA_REDESIGN_UX_BO_INTELIGENTE.md` - Visão geral do redesign

---

*Documento gerado em 31/12/2025*  
*Para execução com Claude Sonnet*
