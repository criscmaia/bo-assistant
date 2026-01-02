/**
 * BOApp - Aplicação principal do BO Inteligente
 * Gerencia estado global, navegação e integração
 * BO Inteligente v1.0
 */

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
        this.draftModal = null;

        // Estado global
        this.currentSectionIndex = 0;
        this.sectionsState = {}; // { sectionId: { status, answers, generatedText } }
        this.isLoading = false;
        this.isOnline = true;

        // Configurações
        this.autoSave = true;
        this.autoSaveKey = 'bo_draft';

        // Tracking
        this.sessionStartTime = new Date();
        this.finalScreen = null;

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
     */
    _initSectionsState() {
        SECTIONS_DATA.forEach(section => {
            this.sectionsState[section.id] = {
                status: 'pending', // pending, in_progress, completed, skipped
                answers: {},
                messages: [],
                currentQuestionIndex: 0,
                generatedText: null,
                skipReason: null,
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
     */
    _updateAllSectionsProgress() {
        console.log('[BOApp] _updateAllSectionsProgress - sectionsState:', this.sectionsState);

        Object.entries(this.sectionsState).forEach(([id, state]) => {
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
     */
    async _onAnswer(questionId, answer, options = {}) {
        console.log('[BOApp] Resposta:', questionId, '=', answer);

        const sectionId = this.currentSectionIndex + 1;
        const sectionState = this.sectionsState[sectionId];

        // Salvar resposta no estado
        sectionState.answers[questionId] = answer;
        sectionState.currentQuestionIndex = this.sectionContainer.currentQuestionIndex;
        sectionState.messages = [...this.sectionContainer.messages];

        // Atualizar progresso (com cálculo dinâmico de total)
        const section = SECTIONS_DATA[this.currentSectionIndex];
        const answeredCount = Object.keys(sectionState.answers).length;
        const totalQuestions = window.calculateSectionTotal
            ? window.calculateSectionTotal(sectionId, sectionState.answers)
            : section.questions.length + (section.skipQuestion ? 1 : 0);

        this.progressBar.updateProgress(sectionId, answeredCount, totalQuestions);

        // Auto-save
        if (this.autoSave) {
            this._saveDraft();
        }

        // Se online, enviar para API (validação + texto gerado se seção completa)
        if (this.isOnline) {
            try {
                const response = await this.api.sendAnswer(answer, 'groq', sectionId);

                if (response.validation_error) {
                    // Mostrar erro de validação
                    this._showValidationError(response.validation_error);
                }

                // Se seção foi pulada, armazenar a razão do skip
                console.log('[BOApp] Verificando skip - section_skipped:', response.section_skipped, 'generated_text:', response.generated_text);
                if (response.section_skipped && response.generated_text) {
                    sectionState.generatedText = response.generated_text;
                    sectionState.skipReason = response.generated_text;
                    // Passar o skip reason para o SectionContainer para exibição
                    this.sectionContainer.setSkipReason(response.generated_text);
                    console.log('[BOApp] Seção pulada. Razão:', response.generated_text);
                    console.log('[BOApp] SectionContainer skipReason após setSkipReason:', this.sectionContainer.skipReason);
                }
                // Se seção completou e tem texto gerado, armazenar
                else if (response.is_section_complete && response.generated_text) {
                    sectionState.generatedText = response.generated_text;
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
     */
    async _onSectionComplete(sectionId, answers) {
        console.log('[BOApp] Seção completa:', sectionId);

        const sectionState = this.sectionsState[sectionId];
        sectionState.status = 'completed';
        sectionState.answers = answers;
        sectionState.messages = [...this.sectionContainer.messages];

        // Marcar na barra de progresso
        this.progressBar.markCompleted(sectionId);

        // Gerar texto (se online, para todas as seções)
        if (this.isOnline) {
            await this._generateSectionText(sectionId);
        } else {
            // Texto placeholder para modo offline
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
            const sectionState = this.sectionsState[sectionId];

            // O texto já foi gerado e armazenado em _onAnswer quando a última resposta foi enviada
            // Se não existir (modo offline ou erro), usar placeholder
            if (!sectionState.generatedText) {
                sectionState.generatedText = this._generatePlaceholderText(sectionId, sectionState.answers);
            }

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

        // Obter razão do skip da SectionContainer
        const sectionContainer = this.currentSectionContainer;
        const skipReason = sectionContainer?.skipReason || null;

        // Marcar na barra de progresso com a razão
        this.progressBar.markSkipped(sectionId, skipReason);

        // NÃO avançar automaticamente - deixar usuário ver mensagem de skip e decidir
        // this._navigateToNextSection();

        // Auto-save
        if (this.autoSave) {
            this._saveDraft();
        }
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
     */
    _onProgressBarClick(sectionId) {
        console.log('[BOApp] Clique na seção:', sectionId);

        const sectionState = this.sectionsState[sectionId];

        // Só permitir navegar para seções já visitadas (não pending)
        if (sectionState.status === 'pending') {
            console.log('[BOApp] Seção ainda não disponível');
            return;
        }

        // Não forçar read-only - deixar _navigateToSection decidir baseado no status
        this._navigateToSection(sectionId, false);
    }

    /**
     * Navega para uma seção específica
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
        const sectionState = this.sectionsState[sectionId];

        // Determinar se é read-only
        // Uma seção é read-only se:
        // 1. Explicitamente marcada como read-only (parâmetro)
        // 2. Está completed/skipped E não é a seção ativa atual
        const currentActiveSectionId = this.currentSectionIndex + 1;
        const shouldBeReadOnly = isReadOnly ||
            ((sectionState.status === 'completed' || sectionState.status === 'skipped') &&
             sectionId !== currentActiveSectionId);

        // Atualizar índice APENAS se não for read-only (navegação real, não visualização)
        if (!shouldBeReadOnly) {
            this.currentSectionIndex = sectionIndex;
        }

        // Marcar como em progresso se necessário
        if (sectionState.status === 'pending') {
            sectionState.status = 'in_progress';
        }

        // Atualizar ProgressBar
        this.progressBar.setCurrentSection(sectionId);

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

        // Criar e renderizar tela final
        this.finalScreen = new FinalScreen('section-container', {
            sectionsState: this.sectionsState,
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

        // Marcar todas seções como completas na barra
        SECTIONS_DATA.forEach(section => {
            const state = this.sectionsState[section.id];
            if (state.status === 'completed') {
                this.progressBar.markCompleted(section.id);
            } else if (state.status === 'skipped') {
                this.progressBar.markSkipped(section.id);
            }
        });

        // Limpar rascunho (BO finalizado)
        this.clearDraft();
    }

    /**
     * Inicia novo BO (limpa tudo)
     */
    _startNewBO() {
        console.log('[BOApp] Iniciando novo BO...');

        // Limpar rascunho
        this.clearDraft();

        // Resetar estado
        this._initSectionsState();

        // Resetar barra de progresso
        this.progressBar.reset();

        // Voltar para seção 1
        this.currentSectionIndex = 0;

        // Iniciar nova sessão na API
        this._startNewSession().then(() => {
            this._loadCurrentSection();
        });
    }

    // ==========================================
    // PERSISTÊNCIA (RASCUNHO)
    // ==========================================

    /**
     * Salva rascunho no localStorage
     */
    _saveDraft() {
        const draft = {
            version: '1.0',
            timestamp: new Date().toISOString(),
            currentSectionIndex: this.currentSectionIndex,
            sectionsState: this.sectionsState,
            apiIds: this.api.getIds(),
        };

        try {
            localStorage.setItem(this.autoSaveKey, JSON.stringify(draft));
            DEBUG.log('BOApp', 'Rascunho salvo');
        } catch (e) {
            DEBUG.warn('BOApp', 'Erro ao salvar rascunho (localStorage pode estar cheio)', e.message);
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

            // Mostrar modal customizado
            this.draftModal.show(
                draft,
                // onContinue - continuar do rascunho
                () => {
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
                        } else if (state.status === 'in_progress') {
                            // Atualizar progresso da seção em andamento
                            const answeredCount = Object.keys(state.answers || {}).length;
                            const totalQuestions = window.calculateSectionTotal
                                ? window.calculateSectionTotal(sectionId, state.answers)
                                : answeredCount;
                            this.progressBar.updateProgress(sectionId, answeredCount, totalQuestions);
                        }
                    });

                    console.log('[BOApp] Rascunho restaurado');
                    this._loadCurrentSection();
                },
                // onDiscard - descartar e começar novo
                async () => {
                    localStorage.removeItem(this.autoSaveKey);
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
