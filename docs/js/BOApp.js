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

        // EventBus para comunicação desacoplada (v0.13.1+)
        this.eventBus = typeof window !== 'undefined' && window.eventBus ? window.eventBus : null;
        this._eventBusUnsubscribers = [];

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

        // Bind de métodos para callbacks internos
        this._onProgressBarClick = this._onProgressBarClick.bind(this);

        // Subscrever ao StateManager para sincronizar componentes
        this._setupStateSubscriptions();

        // Subscrever ao EventBus para comunicação desacoplada (v0.13.1+)
        this._setupEventBusListeners();
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
     * Configura listeners no EventBus (v0.13.1+)
     * Orquestra comunicação desacoplada entre componentes
     */
    _setupEventBusListeners() {
        if (!this.eventBus || typeof Events === 'undefined') {
            console.log('[BOApp] EventBus não disponível - usando apenas callbacks');
            return;
        }

        console.log('[BOApp] Configurando listeners do EventBus...');

        // Evento: SECTION_CHANGE_REQUESTED (de ProgressBar ou SectionContainer)
        const unsubscribeNavigation = this.eventBus.on(Events.SECTION_CHANGE_REQUESTED, (data) => {
            console.log('[BOApp] EventBus - SECTION_CHANGE_REQUESTED:', data);
            const { sectionId, context } = data;

            // Delegar para método de navegação existente
            if (context) {
                this._navigateToSection(sectionId, false, context);
            } else {
                this._navigateToSection(sectionId, false);
            }
        });
        this._eventBusUnsubscribers.push(unsubscribeNavigation);

        // Evento: ANSWER_SAVED (de SectionContainer)
        const unsubscribeAnswer = this.eventBus.on(Events.ANSWER_SAVED, (data) => {
            console.log('[BOApp] EventBus - ANSWER_SAVED:', data);
            // v0.13.2+: Este evento é para tracking/analytics
        });
        this._eventBusUnsubscribers.push(unsubscribeAnswer);

        // Evento: SECTION_COMPLETED (de SectionContainer)
        const unsubscribeComplete = this.eventBus.on(Events.SECTION_COMPLETED, (data) => {
            console.log('[BOApp] EventBus - SECTION_COMPLETED:', data);
            // v0.13.2+: Este evento é para tracking/analytics
        });
        this._eventBusUnsubscribers.push(unsubscribeComplete);

        // Evento: section:skipped (de SectionContainer)
        const unsubscribeSkip = this.eventBus.on('section:skipped', (data) => {
            console.log('[BOApp] EventBus - section:skipped:', data);
            // v0.13.2+: Este evento é para tracking/analytics
        });
        this._eventBusUnsubscribers.push(unsubscribeSkip);

        // Evento: FINAL_SCREEN_REQUESTED (de SectionContainer, quando usuário clica "Finalizar BO")
        const unsubscribeFinalScreen = this.eventBus.on(Events.FINAL_SCREEN_REQUESTED, (data) => {
            console.log('[BOApp] EventBus - FINAL_SCREEN_REQUESTED:', data);
            this._showFinalScreen();
        });
        this._eventBusUnsubscribers.push(unsubscribeFinalScreen);

        console.log('[BOApp] EventBus listeners configurados:', this._eventBusUnsubscribers.length);
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

        // Inicializar ConfirmationModal
        this._initConfirmationModal();

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
        // v0.13.2+: Apenas onGenerateText callback mantido
        // Navegação usa apenas EventBus (SECTION_CHANGE_REQUESTED)
        this.sectionContainer = new SectionContainer('section-container', {
            onGenerateText: async (sectionId) => {
                return await this._generateSectionText(sectionId);
            },
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
     * Inicializa ConfirmationModal
     */
    _initConfirmationModal() {
        this.confirmationModal = new ConfirmationModal('confirmation-modal-container');
        window.confirmationModal = this.confirmationModal; // Debug
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

        // Marcar como em progresso se pendente (StateManager já faz isso em setCurrentSection)
        const initialState = this.stateManager.getSectionState(currentSectionId);
        if (initialState.status === 'pending') {
            this.stateManager.setCurrentSection(currentSectionId);
        }

        // Re-ler o estado APÓS marcar como in_progress
        const sectionState = this.stateManager.getSectionState(currentSectionId);

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
     *
     * CORREÇÃO v0.13.2: Retorna { validationError } se validação falhar.
     * O chamador (SectionContainer) deve verificar e NÃO avançar se houver erro.
     */
    async _onAnswer(questionId, answer, options = {}) {
        console.log('[BOApp] Resposta:', questionId, '=', answer);

        const sectionId = this.stateManager.getCurrentSectionId();

        // Se online, enviar para API PRIMEIRO para validar
        // Só salvar no StateManager se validação passar
        if (this.stateManager.getState().isOnline) {
            try {
                const response = await this.api.sendAnswer(answer, 'groq', sectionId);

                // CORREÇÃO v0.13.2: Se validação falhou, retornar erro SEM salvar resposta
                if (response.validation_error) {
                    console.log('[BOApp] Erro de validação:', response.validation_error);
                    return { validationError: response.validation_error };
                }

                // Validação passou - agora sim salvar resposta
                this.stateManager.saveAnswer(sectionId, questionId, answer);

                // Sincronizar dados do SectionContainer com StateManager
                if (this.sectionContainer) {
                    this.stateManager.setCurrentQuestionIndex(sectionId, this.sectionContainer.currentQuestionIndex);
                }

                // Atualizar total de perguntas (perguntas condicionais podem mudar o total)
                const answers = this.stateManager.getAnswers(sectionId);
                const totalQuestions = window.calculateSectionTotal
                    ? window.calculateSectionTotal(sectionId, answers)
                    : this.stateManager.getSectionState(sectionId).totalCount;
                this.stateManager.updateTotalQuestions(sectionId, totalQuestions);

                // Se seção foi pulada, armazenar a razão do skip
                console.log('[BOApp] Verificando skip - section_skipped:', response.section_skipped, 'generated_text:', response.generated_text);
                if (response.section_skipped && response.generated_text) {
                    this.stateManager.setGeneratedText(sectionId, response.generated_text);
                    console.log('[BOApp] Seção pulada. Razão:', response.generated_text);
                    return { skipReason: response.generated_text };
                }

                // v0.13.2 (Opção B): Se seção completou e backend sinalizou para gerar texto
                // Retornar willGenerateNow para frontend mostrar loading e chamar _generateSectionText
                if (response.will_generate_now) {
                    console.log('[BOApp] Backend sinalizou will_generate_now - frontend deve mostrar loading e chamar _generateSectionText');
                    return {
                        willGenerateNow: true,
                        isComplete: true,
                        currentStep: response.current_step
                    };
                }

                // v0.13.2: Retornar dados do backend para arquitetura backend-driven
                return {
                    isComplete: response.is_section_complete || false,
                    currentStep: response.current_step,
                    willGenerateText: response.will_generate_text || false
                };
            } catch (error) {
                console.error('[BOApp] Erro ao enviar resposta:', error);
                // Em caso de erro de rede/API, salvar localmente e continuar
                this.stateManager.saveAnswer(sectionId, questionId, answer);

                // Se foi erro de API (rate limit, etc), retornar para mostrar no texto gerado
                if (error.message) {
                    return { apiError: error.message };
                }
            }
        } else {
            // Modo offline - salvar localmente sem validação
            this.stateManager.saveAnswer(sectionId, questionId, answer);
        }

        // Sincronizar dados do SectionContainer com StateManager
        if (this.sectionContainer) {
            this.stateManager.setCurrentQuestionIndex(sectionId, this.sectionContainer.currentQuestionIndex);
        }

        // Atualizar total de perguntas (perguntas condicionais podem mudar o total)
        const answers = this.stateManager.getAnswers(sectionId);
        const totalQuestions = window.calculateSectionTotal
            ? window.calculateSectionTotal(sectionId, answers)
            : this.stateManager.getSectionState(sectionId).totalCount;
        this.stateManager.updateTotalQuestions(sectionId, totalQuestions);
    }

    /**
     * Callback: seção completa
     * Usa StateManager para salvar estado (v0.13.1+)
     *
     * v0.13.2 (Opção B): Texto já foi gerado pelo _handleInputSubmit quando willGenerateNow=true.
     * Este callback só precisa garantir o estado e gerar placeholder se offline.
     */
    async _onSectionComplete(sectionId, answers) {
        console.log('[BOApp] Seção completa:', sectionId);

        // Marcar seção como completa via StateManager (notifica listeners automaticamente)
        this.stateManager.markSectionCompleted(sectionId, answers);

        // v0.13.2 (Opção B): Verificar se texto já foi gerado (pelo fluxo willGenerateNow)
        const existingText = this.stateManager.getGeneratedText(sectionId);
        if (existingText) {
            console.log('[BOApp] Texto já existe, não precisa gerar novamente');
            return;
        }

        // Se chegou aqui sem texto (modo offline ou fallback), gerar placeholder
        if (!this.stateManager.getState().isOnline) {
            const generatedText = this._generatePlaceholderText(sectionId, answers);
            this.stateManager.setGeneratedText(sectionId, generatedText);
            if (this.sectionContainer) {
                this.sectionContainer.setGeneratedText(generatedText);
            }
        } else {
            // Fallback: se online mas sem texto, chamar geração
            console.log('[BOApp] Seção completa sem texto - chamando geração como fallback');
            await this._generateSectionText(sectionId);
        }
    }

    /**
     * Gera texto via API
     * v0.13.2 (Opção B): Chama endpoint separado /generate/{session_id}/{section_number}
     * Usa StateManager para obter estado (v0.13.1+)
     */
    async _generateSectionText(sectionId) {
        console.log('[BOApp] _generateSectionText chamado para seção:', sectionId);

        try {
            // v0.13.2 (Opção B): Chamar endpoint separado de geração
            if (this.stateManager.getState().isOnline) {
                console.log('[BOApp] Chamando API generateText para seção:', sectionId);
                const response = await this.api.generateText(sectionId, 'groq');

                if (response.generated_text) {
                    console.log('[BOApp] Texto gerado recebido:', response.generated_text.substring(0, 50) + '...');
                    this.stateManager.setGeneratedText(sectionId, response.generated_text);

                    if (this.sectionContainer) {
                        this.sectionContainer.setGeneratedText(response.generated_text);
                    }
                    return response.generated_text;
                }
            }

            // Fallback: usar placeholder se offline ou sem texto
            let generatedText = this.stateManager.getGeneratedText(sectionId);

            if (!generatedText) {
                const answers = this.stateManager.getAnswers(sectionId);
                generatedText = this._generatePlaceholderText(sectionId, answers);
                this.stateManager.setGeneratedText(sectionId, generatedText);
            }

            if (this.sectionContainer) {
                this.sectionContainer.setGeneratedText(generatedText);
            }

            return generatedText;

        } catch (error) {
            console.error('[BOApp] Erro ao gerar texto:', error);

            // Usar placeholder em caso de erro
            const answers = this.stateManager.getAnswers(sectionId);
            const generatedText = this._generatePlaceholderText(sectionId, answers);
            this.stateManager.setGeneratedText(sectionId, generatedText);
            if (this.sectionContainer) {
                this.sectionContainer.setGeneratedText(generatedText);
            }

            return generatedText;
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

        // Re-ler o estado APÓS marcar como in_progress (BUG FIX: seção 2 não iniciava chat)
        const updatedSectionState = this.stateManager.getSectionState(sectionId);

        // Atualizar progresso de todas as seções (preservar barras completas)
        this._updateAllSectionsProgress();

        // Carregar no container
        this.sectionContainer.loadSection(sectionData, {
            state: updatedSectionState.status,
            messages: updatedSectionState.messages,
            answers: updatedSectionState.answers,
            currentQuestionIndex: updatedSectionState.currentQuestionIndex,
            generatedText: updatedSectionState.generatedText,
            skipReason: updatedSectionState.skipReason || null,
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
        const maxSections = window.ACTIVE_SECTIONS_COUNT || SECTIONS_DATA.length;

        if (nextIndex < maxSections) {
            this._navigateToSection(nextIndex + 1);
        } else {
            // Todas as seções ativas completas
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

        // DEBUG: Log estado das seções antes de passar para FinalScreen
        const sectionsState = this.stateManager.getState().sections;
        console.log('[BOApp] Estado das seções para FinalScreen:');
        Object.entries(sectionsState).forEach(([id, state]) => {
            console.log(`  Seção ${id}: status=${state.status}, generatedText=${state.generatedText ? state.generatedText.substring(0, 50) + '...' : 'NULL'}`);
        });

        // Criar e renderizar tela final
        this.finalScreen = new FinalScreen('section-container', {
            sectionsState: sectionsState,
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

            // ✅ NOVO: Validar se draft tem respostas salvas
            const hasSavedAnswers = draft.sections &&
                Object.values(draft.sections).some(section =>
                    section.answers && Object.keys(section.answers).length > 0
                );

            if (!hasSavedAnswers) {
                // Draft existe mas está vazio - limpar e não mostrar modal
                console.log('[BOApp] Draft encontrado mas sem respostas salvas - limpando');
                this.stateManager.clearDraft();
                return false;
            }

            // Só mostra modal se há conteúdo real
            console.log('[BOApp] Draft com respostas encontrado - exibindo modal');

            // Mostrar modal customizado
            this.draftModal.show(
                draft,
                this.sections, // Passar dados das seções para o preview
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

    /**
     * Dispose Pattern - Remove todos os event listeners (v0.13.1+)
     * Deve ser chamado ao destruir a aplicação para evitar memory leaks
     */
    dispose() {
        console.log('[BOApp] Dispose - limpando recursos...');

        // Remover listeners EventBus
        if (this._eventBusUnsubscribers && this._eventBusUnsubscribers.length > 0) {
            this._eventBusUnsubscribers.forEach(unsubscribe => {
                if (typeof unsubscribe === 'function') {
                    unsubscribe();
                }
            });
            console.log('[BOApp] Disposed - listeners EventBus removidos:', this._eventBusUnsubscribers.length);
            this._eventBusUnsubscribers = [];
        }

        // Dispose dos componentes
        if (this.progressBar && typeof this.progressBar.dispose === 'function') {
            this.progressBar.dispose();
        }

        if (this.sectionContainer && typeof this.sectionContainer.dispose === 'function') {
            this.sectionContainer.dispose();
        }

        console.log('[BOApp] Dispose completo');
    }

    // ==========================================
    // UI HELPERS
    // ==========================================

    /**
     * Mostra loading overlay
     * v0.13.2+: Refatorado para usar UIOverlay
     */
    _showLoading(message = 'Carregando...') {
        this.isLoading = true;
        UIOverlay.showLoading(message);
    }

    /**
     * Esconde loading overlay
     * v0.13.2+: Refatorado para usar UIOverlay
     */
    _hideLoading() {
        this.isLoading = false;
        UIOverlay.hideLoading();
    }

    /**
     * Mostra aviso temporário
     * v0.13.2+: Refatorado para usar UIOverlay
     */
    _showWarning(message) {
        console.warn('[BOApp]', message);
        UIOverlay.warning(message);
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
