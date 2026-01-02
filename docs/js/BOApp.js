/**
 * BOApp - Aplicação principal do BO Inteligente
 * Gerencia estado global, navegação e integração
 * BO Inteligente v0.13.1
 *
 * IMPORTANTE: A partir da v0.13.1, o estado é gerenciado pelo StateManager.
 * BOApp atua como orquestrador, delegando estado para StateManager.
 */

class BOApp {
    /**
     * Aplicação principal do BO Inteligente
     * Gerencia estado global, navegação e integração
     */
    constructor() {
        // StateManager centralizado (Single Source of Truth)
        this.stateManager = StateManager.getInstance();

        // Componentes
        this.api = new APIClient();
        this.progressBar = null;
        this.sectionContainer = null;
        this.draftModal = null;

        // Estado local (UI only - não duplica StateManager)
        this.finalScreen = null;

        // Getters delegados ao StateManager
        Object.defineProperty(this, 'currentSectionIndex', {
            get: () => this.stateManager.getState().currentSectionIndex,
            set: (val) => this.stateManager.setCurrentSection(val + 1)
        });

        Object.defineProperty(this, 'sectionsState', {
            get: () => this.stateManager.getState().sections,
            set: (val) => console.warn('[BOApp] sectionsState é read-only. Use StateManager.')
        });

        Object.defineProperty(this, 'isLoading', {
            get: () => this.stateManager.getState().isLoading,
            set: (val) => this.stateManager.setLoading(val)
        });

        Object.defineProperty(this, 'isOnline', {
            get: () => this.stateManager.getState().isOnline,
            set: (val) => this.stateManager.setOnlineStatus(val)
        });

        // Configurações (não migradas - são constantes)
        this.autoSave = true;
        this.autoSaveKey = 'bo_draft';

        // Tracking
        this.sessionStartTime = new Date();

        // Bind de métodos para callbacks
        this._onAnswer = this._onAnswer.bind(this);
        this._onSectionComplete = this._onSectionComplete.bind(this);
        this._onSectionSkip = this._onSectionSkip.bind(this);
        this._onNavigateNext = this._onNavigateNext.bind(this);
        this._onNavigateBack = this._onNavigateBack.bind(this);
        this._onProgressBarClick = this._onProgressBarClick.bind(this);

        // Subscrever ao StateManager para sincronizar componentes
        this._setupStateSubscriptions();
    }

    /**
     * Configura subscriptions no StateManager
     */
    _setupStateSubscriptions() {
        this.stateManager.subscribe((eventType, data) => {
            switch (eventType) {
                case 'sectionComplete':
                    if (this.progressBar) {
                        this.progressBar.markCompleted(data.sectionId);
                    }
                    break;
                case 'sectionSkipped':
                    if (this.progressBar) {
                        this.progressBar.markSkipped(data.sectionId, data.reason);
                    }
                    break;
                case 'navigation':
                    if (this.progressBar) {
                        this.progressBar.setCurrentSection(data.currentId);
                    }
                    break;
                case 'answer':
                    this._syncProgressOnAnswer(data.sectionId);
                    break;
            }
        });
    }

    /**
     * Sincroniza progresso na ProgressBar após resposta
     */
    _syncProgressOnAnswer(sectionId) {
        if (!this.progressBar) return;

        const sectionState = this.stateManager.getSectionState(sectionId);
        if (sectionState) {
            const answeredCount = sectionState.answeredCount;
            const totalQuestions = window.calculateSectionTotal
                ? window.calculateSectionTotal(sectionId, sectionState.answers)
                : sectionState.totalCount;
            this.progressBar.updateProgress(sectionId, answeredCount, totalQuestions);
        }
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

        // Inicializar DraftModal
        this._initDraftModal();

        // Verificar conexão com API
        await this._checkApiConnection();

        // Tentar restaurar rascunho
        const hasDraft = this._tryRestoreDraft();

        if (!hasDraft) {
            // Iniciar nova sessão
            await this._startNewSession();
            // Carregar primeira seção
            this._loadCurrentSection();
        }
        // Se hasDraft é true, o modal será mostrado e seus callbacks vão chamar _loadCurrentSection()

        console.log('[BOApp] Inicialização completa!');
    }

    /**
     * Inicializa estado de todas as seções
     * Delegado ao StateManager (v0.13.1+)
     */
    _initSectionsState() {
        // StateManager já inicializa seções automaticamente no construtor
        // Este método existe para compatibilidade com código legado
        console.log('[BOApp] Estado das seções já inicializado pelo StateManager');
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
     * Inicializa DraftModal
     */
    _initDraftModal() {
        this.draftModal = new DraftModal('draft-modal-container');
        window.draftModal = this.draftModal; // Debug
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
     * Atualiza progresso de todas as seções
     * Usa StateManager para obter estado (v0.13.1+)
     */
    _updateAllSectionsProgress() {
        const sections = this.stateManager.getState().sections;
        console.log('[BOApp] _updateAllSectionsProgress via StateManager');

        Object.entries(sections).forEach(([id, state]) => {
            const sectionId = parseInt(id);
            const answeredCount = Object.keys(state.answers || {}).length;

            console.log('[BOApp] Seção', sectionId, '- status:', state.status, ', answeredCount:', answeredCount);

            // Atualizar progresso para seções com respostas ou completas
            if (answeredCount > 0 || state.status === 'completed') {
                const totalQuestions = window.calculateSectionTotal
                    ? window.calculateSectionTotal(sectionId, state.answers)
                    : answeredCount;
                this.progressBar.updateProgress(sectionId, answeredCount, totalQuestions);
            }
        });
    }

    /**
     * Carrega a seção atual
     * Usa StateManager para obter estado (v0.13.1+)
     */
    _loadCurrentSection() {
        const currentSectionId = this.stateManager.getCurrentSectionId();
        const sectionIndex = currentSectionId - 1;
        const sectionData = SECTIONS_DATA[sectionIndex];
        const sectionState = this.stateManager.getSectionState(currentSectionId);

        // Marcar como em progresso se pendente (StateManager já faz isso em setCurrentSection)
        if (sectionState.status === 'pending') {
            this.stateManager.setCurrentSection(currentSectionId);
        }

        // Atualizar ProgressBar
        this.progressBar.setCurrentSection(currentSectionId);

        // Atualizar progresso de todas as seções (preservar barras completas)
        this._updateAllSectionsProgress();

        // Carregar no container
        this.sectionContainer.loadSection(sectionData, {
            state: sectionState.status,
            messages: sectionState.messages,
            answers: sectionState.answers,
            currentQuestionIndex: sectionState.currentQuestionIndex,
            generatedText: sectionState.generatedText,
            skipReason: sectionState.skipReason || null,
            isReadOnly: false,
        });
    }

    /**
     * Callback: resposta enviada
     * Usa StateManager para salvar estado (v0.13.1+)
     */
    async _onAnswer(questionId, answer, options = {}) {
        console.log('[BOApp] Resposta:', questionId, '=', answer);

        const sectionId = this.stateManager.getCurrentSectionId();

        // Salvar resposta via StateManager (notifica listeners automaticamente)
        this.stateManager.saveAnswer(sectionId, questionId, answer);

        // Sincronizar dados do SectionContainer com StateManager
        if (this.sectionContainer) {
            this.stateManager.setCurrentQuestionIndex(sectionId, this.sectionContainer.currentQuestionIndex);
            // Messages são atualizados pelo SectionContainer diretamente no StateManager
        }

        // Atualizar total de perguntas (perguntas condicionais podem mudar o total)
        const answers = this.stateManager.getAnswers(sectionId);
        const totalQuestions = window.calculateSectionTotal
            ? window.calculateSectionTotal(sectionId, answers)
            : this.stateManager.getSectionState(sectionId).totalCount;
        this.stateManager.updateTotalQuestions(sectionId, totalQuestions);

        // Se online, enviar para API (validação + texto gerado se seção completa)
        if (this.stateManager.getState().isOnline) {
            try {
                const response = await this.api.sendAnswer(answer, 'groq', sectionId);

                if (response.validation_error) {
                    // Mostrar erro de validação
                    this._showValidationError(response.validation_error);
                }

                // Se seção foi pulada, armazenar a razão do skip
                console.log('[BOApp] Verificando skip - section_skipped:', response.section_skipped, 'generated_text:', response.generated_text);
                if (response.section_skipped && response.generated_text) {
                    this.stateManager.setGeneratedText(sectionId, response.generated_text);
                    // Passar o skip reason para o SectionContainer para exibição
                    if (this.sectionContainer) {
                        this.sectionContainer.setSkipReason(response.generated_text);
                    }
                    console.log('[BOApp] Seção pulada. Razão:', response.generated_text);
                }
                // Se seção completou e tem texto gerado, armazenar
                else if (response.is_section_complete && response.generated_text) {
                    this.stateManager.setGeneratedText(sectionId, response.generated_text);
                    console.log('[BOApp] Texto gerado recebido do backend:', response.generated_text.substring(0, 100));
                }
            } catch (error) {
                console.error('[BOApp] Erro ao enviar resposta:', error);
                // Continuar offline
            }
        }
    }

    /**
     * Callback: seção completa
     * Usa StateManager para salvar estado (v0.13.1+)
     */
    async _onSectionComplete(sectionId, answers) {
        console.log('[BOApp] Seção completa:', sectionId);

        // Marcar seção como completa via StateManager (notifica listeners automaticamente)
        this.stateManager.markSectionCompleted(sectionId, answers);

        // Gerar texto (se online, para todas as seções)
        if (this.stateManager.getState().isOnline) {
            await this._generateSectionText(sectionId);
        } else {
            // Texto placeholder para modo offline
            const generatedText = this._generatePlaceholderText(sectionId, answers);
            this.stateManager.setGeneratedText(sectionId, generatedText);
            if (this.sectionContainer) {
                this.sectionContainer.setGeneratedText(generatedText);
            }
        }
    }

    /**
     * Gera texto via API
     * Usa StateManager para obter estado (v0.13.1+)
     */
    async _generateSectionText(sectionId) {
        this._showLoading('Gerando texto...');

        try {
            // O texto já foi gerado e armazenado em _onAnswer quando a última resposta foi enviada
            // Se não existir (modo offline ou erro), usar placeholder
            let generatedText = this.stateManager.getGeneratedText(sectionId);

            if (!generatedText) {
                const answers = this.stateManager.getAnswers(sectionId);
                generatedText = this._generatePlaceholderText(sectionId, answers);
                this.stateManager.setGeneratedText(sectionId, generatedText);
            }

            if (this.sectionContainer) {
                this.sectionContainer.setGeneratedText(generatedText);
            }

        } catch (error) {
            console.error('[BOApp] Erro ao gerar texto:', error);

            // Usar placeholder
            const answers = this.stateManager.getAnswers(sectionId);
            const generatedText = this._generatePlaceholderText(sectionId, answers);
            this.stateManager.setGeneratedText(sectionId, generatedText);
            if (this.sectionContainer) {
                this.sectionContainer.setGeneratedText(generatedText);
            }

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
     * Usa StateManager para salvar estado (v0.13.1+)
     */
    _onSectionSkip(sectionId) {
        console.log('[BOApp] Seção pulada:', sectionId);

        // Obter razão do skip do SectionContainer
        const skipReason = this.sectionContainer?.skipReason || null;

        // Marcar seção como pulada via StateManager (notifica listeners automaticamente)
        this.stateManager.markSectionSkipped(sectionId, skipReason);

        // NÃO avançar automaticamente - deixar usuário ver mensagem de skip e decidir
    }

    /**
     * Callback: navegar para próxima seção
     */
    _onNavigateNext(nextSectionId, options = {}) {
        console.log('[BOApp] Navegar para seção:', nextSectionId, 'com opções:', options);
        this._navigateToSection(nextSectionId, false, options);
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
     * Usa StateManager para verificar status (v0.13.1+)
     */
    _onProgressBarClick(sectionId) {
        console.log('[BOApp] Clique na seção:', sectionId);

        const status = this.stateManager.getSectionStatus(sectionId);

        // Só permitir navegar para seções já visitadas (não pending)
        if (status === 'pending') {
            console.log('[BOApp] Seção ainda não disponível');
            return;
        }

        // Não forçar read-only - deixar _navigateToSection decidir baseado no status
        this._navigateToSection(sectionId, false);
    }

    /**
     * Navega para uma seção específica
     * Usa StateManager para obter estado (v0.13.1+)
     *
     * options:
     *   - preAnswerSkipQuestion: Valor para auto-responder o skipQuestion (sem mostrar no chat)
     */
    async _navigateToSection(sectionId, isReadOnly = false, options = {}) {
        const sectionIndex = sectionId - 1;

        if (sectionIndex < 0 || sectionIndex >= SECTIONS_DATA.length) {
            console.warn('[BOApp] Seção inválida:', sectionId);
            return;
        }

        // Fade out
        await this.sectionContainer.fadeOut();

        // Carregar seção
        const sectionData = SECTIONS_DATA[sectionIndex];
        const sectionState = this.stateManager.getSectionState(sectionId);

        // Determinar se é read-only
        // Uma seção é read-only se:
        // 1. Explicitamente marcada como read-only (parâmetro)
        // 2. Está completed/skipped E não é a seção ativa atual
        const currentActiveSectionId = this.stateManager.getCurrentSectionId();
        const shouldBeReadOnly = isReadOnly ||
            ((sectionState.status === 'completed' || sectionState.status === 'skipped') &&
             sectionId !== currentActiveSectionId);

        // Atualizar seção atual via StateManager APENAS se não for read-only
        if (!shouldBeReadOnly) {
            this.stateManager.setCurrentSection(sectionId);
        }

        // Atualizar progresso de todas as seções (preservar barras completas)
        this._updateAllSectionsProgress();

        // Carregar no container
        this.sectionContainer.loadSection(sectionData, {
            state: sectionState.status,
            messages: sectionState.messages,
            answers: sectionState.answers,
            currentQuestionIndex: sectionState.currentQuestionIndex,
            generatedText: sectionState.generatedText,
            skipReason: sectionState.skipReason || null,
            isReadOnly: shouldBeReadOnly,
            preAnswerSkipQuestion: options.preAnswerSkipQuestion,
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
     * Usa StateManager (v0.13.1+)
     */
    _getCurrentActiveSectionId() {
        return this.stateManager.getCurrentSectionId();
    }

    /**
     * Mostra tela final (todas seções completas)
     * Usa StateManager para obter estado (v0.13.1+)
     */
    _showFinalScreen() {
        console.log('[BOApp] Todas as seções completas!');

        // Criar e renderizar tela final
        this.finalScreen = new FinalScreen('section-container', {
            sectionsState: this.stateManager.getState().sections,
            startTime: this.sessionStartTime || new Date(),
            onNewBO: () => {
                this._startNewBO();
            },
            onSectionClick: (sectionId) => {
                // Navegar para seção (modo leitura)
                this._navigateToSection(sectionId, true);
            }
        });

        this.finalScreen.render();

        // Marcar todas seções como completas na barra (já sincronizado via StateManager)
        SECTIONS_DATA.forEach(section => {
            const status = this.stateManager.getSectionStatus(section.id);
            if (status === 'completed') {
                this.progressBar.markCompleted(section.id);
            } else if (status === 'skipped') {
                this.progressBar.markSkipped(section.id);
            }
        });

        // Limpar rascunho (BO finalizado)
        this.stateManager.clearDraft();
    }

    /**
     * Inicia novo BO (limpa tudo)
     * Usa StateManager para resetar estado (v0.13.1+)
     */
    _startNewBO() {
        console.log('[BOApp] Iniciando novo BO...');

        // Resetar estado via StateManager (já limpa rascunho)
        this.stateManager.reset();

        // Resetar barra de progresso
        this.progressBar.reset();

        // Iniciar nova sessão na API
        this._startNewSession().then(() => {
            this._loadCurrentSection();
        });
    }

    // ==========================================
    // PERSISTÊNCIA (RASCUNHO)
    // Delegada ao StateManager (v0.13.1+)
    // ==========================================

    /**
     * Salva rascunho no localStorage
     * DEPRECATED: StateManager faz auto-save com debounce
     */
    _saveDraft() {
        // StateManager já persiste automaticamente com debounce
        // Este método existe para compatibilidade com código legado
        console.log('[BOApp] _saveDraft() delegado ao StateManager');
    }

    /**
     * Tenta restaurar rascunho
     * Usa StateManager para carregar e restaurar estado (v0.13.1+)
     */
    _tryRestoreDraft() {
        try {
            // Tentar carregar do StateManager
            const draft = this.stateManager.loadFromPersistence();

            if (!draft) return false;

            // Mostrar modal customizado
            this.draftModal.show(
                draft,
                // onContinue - continuar do rascunho
                () => {
                    // Restaurar estado via StateManager
                    this.stateManager.restoreFromDraft(draft);

                    // Restaurar sessão API se disponível
                    if (draft.sessionId) {
                        this.api.restoreSession(draft.sessionId, draft.boId);
                    }

                    // Atualizar ProgressBar com estados salvos
                    const sections = this.stateManager.getState().sections;
                    Object.entries(sections).forEach(([id, state]) => {
                        const sectionId = parseInt(id);
                        if (state.status === 'completed') {
                            this.progressBar.markCompleted(sectionId);
                        } else if (state.status === 'skipped') {
                            this.progressBar.markSkipped(sectionId);
                        } else if (state.status === 'in_progress') {
                            // Atualizar progresso da seção em andamento
                            const answeredCount = Object.keys(state.answers || {}).length;
                            const totalQuestions = window.calculateSectionTotal
                                ? window.calculateSectionTotal(sectionId, state.answers)
                                : answeredCount;
                            this.progressBar.updateProgress(sectionId, answeredCount, totalQuestions);
                        }
                    });

                    console.log('[BOApp] Rascunho restaurado via StateManager');
                    this._loadCurrentSection();
                },
                // onDiscard - descartar e começar novo
                async () => {
                    this.stateManager.clearDraft();
                    console.log('[BOApp] Rascunho descartado');
                    await this._startNewSession();
                    this._loadCurrentSection();
                },
                // sectionsData - para calcular total de perguntas
                SECTIONS_DATA
            );

            return true;

        } catch (error) {
            console.error('[BOApp] Erro ao restaurar rascunho:', error);
            this.stateManager.clearDraft();
            return false;
        }
    }

    /**
     * Limpa rascunho
     * Delegado ao StateManager (v0.13.1+)
     */
    clearDraft() {
        this.stateManager.clearDraft();
        console.log('[BOApp] Rascunho removido via StateManager');
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
