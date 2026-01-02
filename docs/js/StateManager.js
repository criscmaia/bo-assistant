/**
 * StateManager - Gerenciamento Centralizado de Estado
 * BO Inteligente v0.13.1
 *
 * Este módulo implementa um padrão de estado centralizado (Single Source of Truth)
 * para resolver o problema de múltiplas fontes de estado que causavam bugs de regressão.
 *
 * Fontes anteriores unificadas:
 * - BOApp.sectionsState
 * - SectionContainer.state/answers/messages
 * - ProgressBar.sectionStates
 * - localStorage (persistência)
 *
 * Padrão: Observer/Pub-Sub para notificar componentes de mudanças.
 *
 * Autor: Claude Opus 4.5
 * Data: 02/01/2026
 */

class StateManager {
    /**
     * Singleton instance
     * @type {StateManager|null}
     */
    static _instance = null;

    /**
     * Obtém instância singleton do StateManager
     * @returns {StateManager}
     */
    static getInstance() {
        if (!StateManager._instance) {
            StateManager._instance = new StateManager();
        }
        return StateManager._instance;
    }

    /**
     * Cria nova instância (use getInstance() para singleton)
     */
    constructor() {
        // Prevenir múltiplas instâncias
        if (StateManager._instance) {
            console.warn('[StateManager] Usando instância existente. Use StateManager.getInstance()');
            return StateManager._instance;
        }

        // Estado centralizado
        this._state = {
            // Sessão
            sessionId: null,
            boId: null,
            startTime: null,
            isOnline: true,

            // Navegação
            currentSectionId: 1,
            currentSectionIndex: 0,

            // Estado de todas as seções
            sections: {},
            // Formato: {
            //   [sectionId]: {
            //     status: 'pending' | 'in_progress' | 'completed' | 'skipped',
            //     answers: { [questionId]: answer },
            //     messages: [{ type: 'bot'|'user', text, hint?, timestamp }],
            //     currentQuestionIndex: number,
            //     generatedText: string | null,
            //     skipReason: string | null,
            //     answeredCount: number,
            //     totalCount: number
            //   }
            // }

            // UI flags
            isLoading: false,
            loadingMessage: '',
        };

        // Listeners para mudanças de estado
        this._listeners = new Set();

        // Listeners específicos por seção
        this._sectionListeners = new Map();

        // Configuração de persistência
        this._persistenceKey = 'bo_draft';
        this._persistenceVersion = '2.0';

        // Debounce para persistência
        this._persistDebounceTimer = null;
        this._persistDebounceMs = 500;

        // Inicializar com dados das seções se disponível
        if (typeof SECTIONS_DATA !== 'undefined') {
            this._initializeSections(SECTIONS_DATA);
        }

        console.log('[StateManager] Inicializado');
    }

    // =============================================================================
    // INICIALIZAÇÃO
    // =============================================================================

    /**
     * Inicializa estado das seções baseado em SECTIONS_DATA
     * @param {Array} sectionsData - Array de dados das seções
     */
    _initializeSections(sectionsData) {
        sectionsData.forEach(section => {
            this._state.sections[section.id] = {
                status: 'pending',
                answers: {},
                messages: [],
                currentQuestionIndex: 0,
                generatedText: null,
                skipReason: null,
                answeredCount: 0,
                totalCount: section.questions.length + (section.skipQuestion ? 1 : 0)
            };
        });
    }

    /**
     * Reinicializa todo o estado (novo BO)
     */
    reset() {
        const sectionsData = typeof SECTIONS_DATA !== 'undefined' ? SECTIONS_DATA : [];

        this._state = {
            sessionId: null,
            boId: null,
            startTime: new Date().toISOString(),
            isOnline: this._state.isOnline,
            currentSectionId: 1,
            currentSectionIndex: 0,
            sections: {},
            isLoading: false,
            loadingMessage: '',
        };

        this._initializeSections(sectionsData);
        this._notifyListeners('reset', null);
        this._clearPersistence();

        console.log('[StateManager] Estado resetado');
    }

    // =============================================================================
    // GETTERS (Imutáveis)
    // =============================================================================

    /**
     * Retorna cópia imutável do estado completo
     * @returns {Object}
     */
    getState() {
        return JSON.parse(JSON.stringify(this._state));
    }

    /**
     * Retorna estado de uma seção específica
     * @param {number} sectionId
     * @returns {Object|null}
     */
    getSectionState(sectionId) {
        const section = this._state.sections[sectionId];
        return section ? { ...section, answers: { ...section.answers }, messages: [...section.messages] } : null;
    }

    /**
     * Retorna seção atual
     * @returns {Object}
     */
    getCurrentSection() {
        return this.getSectionState(this._state.currentSectionId);
    }

    /**
     * Retorna ID da seção atual
     * @returns {number}
     */
    getCurrentSectionId() {
        return this._state.currentSectionId;
    }

    /**
     * Retorna resposta de uma pergunta específica
     * @param {number} sectionId
     * @param {string} questionId
     * @returns {any|null}
     */
    getAnswer(sectionId, questionId) {
        return this._state.sections[sectionId]?.answers[questionId] ?? null;
    }

    /**
     * Retorna todas as respostas de uma seção
     * @param {number} sectionId
     * @returns {Object}
     */
    getAnswers(sectionId) {
        return { ...(this._state.sections[sectionId]?.answers || {}) };
    }

    /**
     * Retorna status de uma seção
     * @param {number} sectionId
     * @returns {string}
     */
    getSectionStatus(sectionId) {
        return this._state.sections[sectionId]?.status || 'pending';
    }

    /**
     * Verifica se seção está completa
     * @param {number} sectionId
     * @returns {boolean}
     */
    isSectionCompleted(sectionId) {
        return this._state.sections[sectionId]?.status === 'completed';
    }

    /**
     * Verifica se seção foi pulada
     * @param {number} sectionId
     * @returns {boolean}
     */
    isSectionSkipped(sectionId) {
        return this._state.sections[sectionId]?.status === 'skipped';
    }

    /**
     * Retorna texto gerado de uma seção
     * @param {number} sectionId
     * @returns {string|null}
     */
    getGeneratedText(sectionId) {
        return this._state.sections[sectionId]?.generatedText || null;
    }

    /**
     * Retorna todas as seções completadas
     * @returns {number[]}
     */
    getCompletedSections() {
        return Object.entries(this._state.sections)
            .filter(([_, state]) => state.status === 'completed')
            .map(([id, _]) => parseInt(id));
    }

    /**
     * Calcula progresso geral (0-100)
     * @returns {number}
     */
    getOverallProgress() {
        const totalSections = Object.keys(this._state.sections).length;
        if (totalSections === 0) return 0;

        const completed = Object.values(this._state.sections)
            .filter(s => s.status === 'completed' || s.status === 'skipped').length;

        return Math.round((completed / totalSections) * 100);
    }

    /**
     * Retorna IDs da sessão
     * @returns {Object}
     */
    getSessionIds() {
        return {
            sessionId: this._state.sessionId,
            boId: this._state.boId
        };
    }

    // =============================================================================
    // SETTERS (Com notificação)
    // =============================================================================

    /**
     * Define IDs da sessão
     * @param {string} sessionId
     * @param {string} boId
     */
    setSession(sessionId, boId) {
        this._state.sessionId = sessionId;
        this._state.boId = boId;
        this._state.startTime = new Date().toISOString();
        this._notifyListeners('session', { sessionId, boId });
        this._schedulePersist();
    }

    /**
     * Define status online/offline
     * @param {boolean} isOnline
     */
    setOnlineStatus(isOnline) {
        this._state.isOnline = isOnline;
        this._notifyListeners('online', { isOnline });
    }

    /**
     * Navega para uma seção
     * @param {number} sectionId
     */
    setCurrentSection(sectionId) {
        const previousId = this._state.currentSectionId;
        this._state.currentSectionId = sectionId;
        this._state.currentSectionIndex = sectionId - 1;

        // Se seção estava pending, marcar como in_progress
        if (this._state.sections[sectionId]?.status === 'pending') {
            this._state.sections[sectionId].status = 'in_progress';
        }

        this._notifyListeners('navigation', { previousId, currentId: sectionId });
        this._notifySectionListeners(sectionId, 'navigation');
        this._schedulePersist();
    }

    /**
     * Salva resposta de uma pergunta
     * @param {number} sectionId
     * @param {string} questionId
     * @param {any} answer
     */
    saveAnswer(sectionId, questionId, answer) {
        if (!this._state.sections[sectionId]) {
            console.error('[StateManager] Seção não existe:', sectionId);
            return;
        }

        const section = this._state.sections[sectionId];
        section.answers[questionId] = answer;
        section.answeredCount = Object.keys(section.answers).length;

        // Atualizar status se estava pending
        if (section.status === 'pending') {
            section.status = 'in_progress';
        }

        this._notifyListeners('answer', { sectionId, questionId, answer });
        this._notifySectionListeners(sectionId, 'answer', { questionId, answer });
        this._schedulePersist();

        console.log('[StateManager] Resposta salva:', { sectionId, questionId, answeredCount: section.answeredCount });
    }

    /**
     * Adiciona mensagem ao histórico de chat
     * @param {number} sectionId
     * @param {string} type - 'bot' | 'user'
     * @param {string} text
     * @param {string|null} hint
     */
    addMessage(sectionId, type, text, hint = null) {
        if (!this._state.sections[sectionId]) return;

        const message = {
            type,
            text,
            hint,
            timestamp: new Date().toISOString()
        };

        this._state.sections[sectionId].messages.push(message);
        this._notifySectionListeners(sectionId, 'message', message);
        this._schedulePersist();
    }

    /**
     * Atualiza índice da pergunta atual
     * @param {number} sectionId
     * @param {number} index
     */
    setCurrentQuestionIndex(sectionId, index) {
        if (!this._state.sections[sectionId]) return;

        this._state.sections[sectionId].currentQuestionIndex = index;
        this._notifySectionListeners(sectionId, 'questionIndex', { index });
        this._schedulePersist();
    }

    /**
     * Marca seção como completa
     * @param {number} sectionId
     * @param {Object} answers - Respostas finais (opcional, usa as existentes)
     */
    markSectionCompleted(sectionId, answers = null) {
        if (!this._state.sections[sectionId]) return;

        const section = this._state.sections[sectionId];
        section.status = 'completed';
        if (answers) {
            section.answers = { ...answers };
        }
        section.answeredCount = section.totalCount;

        this._notifyListeners('sectionComplete', { sectionId });
        this._notifySectionListeners(sectionId, 'complete');
        this._schedulePersist();

        console.log('[StateManager] Seção completada:', sectionId);
    }

    /**
     * Marca seção como pulada
     * @param {number} sectionId
     * @param {string|null} reason
     */
    markSectionSkipped(sectionId, reason = null) {
        if (!this._state.sections[sectionId]) return;

        const section = this._state.sections[sectionId];
        section.status = 'skipped';
        section.skipReason = reason;

        this._notifyListeners('sectionSkipped', { sectionId, reason });
        this._notifySectionListeners(sectionId, 'skipped', { reason });
        this._schedulePersist();

        console.log('[StateManager] Seção pulada:', sectionId, reason);
    }

    /**
     * Define texto gerado para uma seção
     * @param {number} sectionId
     * @param {string} text
     */
    setGeneratedText(sectionId, text) {
        if (!this._state.sections[sectionId]) return;

        this._state.sections[sectionId].generatedText = text;
        this._notifySectionListeners(sectionId, 'generatedText', { text });
        this._schedulePersist();
    }

    /**
     * Atualiza total de perguntas da seção (para perguntas condicionais)
     * @param {number} sectionId
     * @param {number} total
     */
    updateTotalQuestions(sectionId, total) {
        if (!this._state.sections[sectionId]) return;

        this._state.sections[sectionId].totalCount = total;
        this._notifySectionListeners(sectionId, 'totalUpdate', { total });
    }

    /**
     * Define estado de loading
     * @param {boolean} isLoading
     * @param {string} message
     */
    setLoading(isLoading, message = '') {
        this._state.isLoading = isLoading;
        this._state.loadingMessage = message;
        this._notifyListeners('loading', { isLoading, message });
    }

    // =============================================================================
    // RESTAURAÇÃO DE ESTADO
    // =============================================================================

    /**
     * Restaura estado de um rascunho salvo
     * @param {Object} savedState
     */
    restoreFromDraft(savedState) {
        if (!savedState || savedState.version !== this._persistenceVersion) {
            console.warn('[StateManager] Versão de rascunho incompatível');
            return false;
        }

        try {
            this._state.sessionId = savedState.sessionId;
            this._state.boId = savedState.boId;
            this._state.startTime = savedState.startTime;
            this._state.currentSectionId = savedState.currentSectionId;
            this._state.currentSectionIndex = savedState.currentSectionIndex;
            this._state.sections = savedState.sections;

            this._notifyListeners('restore', savedState);

            console.log('[StateManager] Estado restaurado do rascunho');
            return true;
        } catch (error) {
            console.error('[StateManager] Erro ao restaurar rascunho:', error);
            return false;
        }
    }

    // =============================================================================
    // OBSERVERS (PUB/SUB)
    // =============================================================================

    /**
     * Registra listener para mudanças de estado
     * @param {Function} listener - Callback (eventType, data) => void
     * @returns {Function} - Função para remover listener
     */
    subscribe(listener) {
        this._listeners.add(listener);
        return () => this._listeners.delete(listener);
    }

    /**
     * Registra listener para mudanças em uma seção específica
     * @param {number} sectionId
     * @param {Function} listener - Callback (eventType, data) => void
     * @returns {Function} - Função para remover listener
     */
    subscribeToSection(sectionId, listener) {
        if (!this._sectionListeners.has(sectionId)) {
            this._sectionListeners.set(sectionId, new Set());
        }
        this._sectionListeners.get(sectionId).add(listener);
        return () => this._sectionListeners.get(sectionId)?.delete(listener);
    }

    /**
     * Notifica todos os listeners globais
     * @param {string} eventType
     * @param {any} data
     */
    _notifyListeners(eventType, data) {
        this._listeners.forEach(listener => {
            try {
                listener(eventType, data);
            } catch (error) {
                console.error('[StateManager] Erro em listener:', error);
            }
        });
    }

    /**
     * Notifica listeners de uma seção específica
     * @param {number} sectionId
     * @param {string} eventType
     * @param {any} data
     */
    _notifySectionListeners(sectionId, eventType, data = null) {
        const listeners = this._sectionListeners.get(sectionId);
        if (listeners) {
            listeners.forEach(listener => {
                try {
                    listener(eventType, data);
                } catch (error) {
                    console.error('[StateManager] Erro em section listener:', error);
                }
            });
        }
    }

    // =============================================================================
    // PERSISTÊNCIA (localStorage)
    // =============================================================================

    /**
     * Agenda persistência com debounce
     */
    _schedulePersist() {
        if (this._persistDebounceTimer) {
            clearTimeout(this._persistDebounceTimer);
        }
        this._persistDebounceTimer = setTimeout(() => {
            this._persist();
        }, this._persistDebounceMs);
    }

    /**
     * Persiste estado no localStorage
     */
    _persist() {
        const draft = {
            version: this._persistenceVersion,
            timestamp: new Date().toISOString(),
            sessionId: this._state.sessionId,
            boId: this._state.boId,
            startTime: this._state.startTime,
            currentSectionId: this._state.currentSectionId,
            currentSectionIndex: this._state.currentSectionIndex,
            sections: this._state.sections,
        };

        try {
            localStorage.setItem(this._persistenceKey, JSON.stringify(draft));
            console.log('[StateManager] Estado persistido');
        } catch (error) {
            console.error('[StateManager] Erro ao persistir estado:', error);
        }
    }

    /**
     * Carrega estado do localStorage
     * @returns {Object|null}
     */
    loadFromPersistence() {
        try {
            const saved = localStorage.getItem(this._persistenceKey);
            if (!saved) return null;

            const draft = JSON.parse(saved);

            // Verificar expiração (24h)
            const savedTime = new Date(draft.timestamp);
            const hoursDiff = (new Date() - savedTime) / (1000 * 60 * 60);

            if (hoursDiff > 24) {
                console.log('[StateManager] Rascunho expirado');
                this._clearPersistence();
                return null;
            }

            return draft;
        } catch (error) {
            console.error('[StateManager] Erro ao carregar persistência:', error);
            return null;
        }
    }

    /**
     * Limpa dados persistidos
     */
    _clearPersistence() {
        localStorage.removeItem(this._persistenceKey);
    }

    /**
     * Limpa rascunho (chamado externamente)
     */
    clearDraft() {
        this._clearPersistence();
        console.log('[StateManager] Rascunho limpo');
    }

    // =============================================================================
    // DEBUG
    // =============================================================================

    /**
     * Imprime estado atual (debug)
     */
    debug() {
        console.group('[StateManager] Estado Atual');
        console.log('Session:', this._state.sessionId, this._state.boId);
        console.log('Current Section:', this._state.currentSectionId);
        console.log('Sections:', this._state.sections);
        console.log('Listeners:', this._listeners.size);
        console.groupEnd();
    }
}

// Exportar instância singleton
const stateManager = StateManager.getInstance();

// Expor globalmente para debug
if (typeof window !== 'undefined') {
    window.stateManager = stateManager;
    window.StateManager = StateManager;
}
