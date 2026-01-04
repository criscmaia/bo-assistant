/**
 * EventBus - Mediator Pattern para comunicação desacoplada
 * BO Inteligente v0.13.2
 *
 * Implementa padrão Mediator para eliminar acoplamento direto entre componentes.
 * Componentes comunicam via eventos ao invés de referências diretas.
 *
 * Benefícios:
 * - Componentes independentes e testáveis
 * - Adicionar novo componente não requer modificar existentes
 * - Debug facilitado (eventos centralizados)
 * - Memory leak prevention (unsubscribe automático)
 *
 * Author: Cristiano Maia + Claude (Anthropic)
 * Date: 02/01/2026
 */

// ============================================
// SCHEMAS DE EVENTOS (JSDoc @typedef)
// ============================================

/**
 * Dados para mudança de seção
 * @typedef {Object} SectionChangeData
 * @property {number} sectionId - ID da seção destino (1-8)
 * @property {Object} [context] - Contexto adicional opcional
 * @property {string} [context.preAnswerSkipQuestion] - Resposta para skip question ('sim'/'não')
 */

/**
 * Dados de resposta salva
 * @typedef {Object} AnswerSavedData
 * @property {number} sectionId - ID da seção (1-8)
 * @property {string} questionId - ID da pergunta (ex: '1.1', '2.3')
 * @property {string} answer - Resposta do usuário
 */

/**
 * Dados de seção completada
 * @typedef {Object} SectionCompletedData
 * @property {number} sectionId - ID da seção completada (1-8)
 * @property {Object.<string, string>} answers - Map questionId → answer
 */

/**
 * Dados para tela final
 * @typedef {Object} FinalScreenData
 * @property {number[]} completedSections - IDs das seções completadas
 */

/**
 * Dados de erro genérico
 * @typedef {Object} ErrorData
 * @property {string} message - Mensagem de erro
 * @property {string} [code] - Código do erro (opcional)
 * @property {Object} [details] - Detalhes adicionais (opcional)
 */

/**
 * Dados de sessão
 * @typedef {Object} SessionData
 * @property {string} sessionId - UUID da sessão
 * @property {string} boId - ID do BO (ex: 'BO-20260103-abc123')
 */

/**
 * Dados de texto gerado
 * @typedef {Object} TextGeneratedData
 * @property {number} sectionId - ID da seção
 * @property {string} text - Texto gerado pela LLM
 */

// ============================================
// EVENTOS PADRONIZADOS
// ============================================

/**
 * Catálogo de eventos do sistema.
 * Centralizando aqui para evitar typos e facilitar descoberta.
 *
 * Legenda:
 * - [ATIVO] = Evento em uso no código
 * - [RESERVADO] = Declarado para uso futuro
 */
const Events = {
    // ==========================================
    // NAVEGAÇÃO ENTRE SEÇÕES
    // ==========================================

    /**
     * User solicitou mudança de seção (clique no ProgressBar ou botão transição)
     * @type {string}
     * @fires {SectionChangeData}
     * @status ATIVO - Emitido por: ProgressBar, SectionContainer
     */
    SECTION_CHANGE_REQUESTED: 'section:change:requested',

    /**
     * Seção carregada com sucesso
     * @type {string}
     * @fires {{ sectionId: number }}
     * @status RESERVADO
     */
    SECTION_LOADED: 'section:loaded',

    /**
     * Erro ao carregar seção
     * @type {string}
     * @fires {ErrorData}
     * @status RESERVADO
     */
    SECTION_LOAD_ERROR: 'section:load:error',

    // ==========================================
    // RESPOSTAS
    // ==========================================

    /**
     * User submeteu resposta (antes de salvar)
     * @type {string}
     * @fires {{ sectionId: number, questionId: string, answer: string }}
     * @status RESERVADO
     */
    ANSWER_SUBMITTED: 'answer:submitted',

    /**
     * Resposta salva com sucesso (backend confirmou)
     * @type {string}
     * @fires {AnswerSavedData}
     * @status ATIVO - Emitido por: SectionContainer
     */
    ANSWER_SAVED: 'answer:saved',

    /**
     * Erro ao salvar resposta
     * @type {string}
     * @fires {ErrorData}
     * @status RESERVADO
     */
    ANSWER_SAVE_ERROR: 'answer:save:error',

    // ==========================================
    // PROGRESSO
    // ==========================================

    /**
     * Progresso de seção atualizado
     * @type {string}
     * @fires {{ sectionId: number, progress: number, answeredCount: number }}
     * @status RESERVADO
     */
    PROGRESS_UPDATED: 'progress:updated',

    /**
     * Seção finalizada (todas perguntas respondidas + texto gerado)
     * @type {string}
     * @fires {SectionCompletedData}
     * @status ATIVO - Emitido por: SectionContainer
     */
    SECTION_COMPLETED: 'section:completed',

    /**
     * BO completo (todas seções finalizadas)
     * @type {string}
     * @fires {{ boId: string, completedSections: number[] }}
     * @status RESERVADO
     */
    BO_COMPLETED: 'bo:completed',

    /**
     * User solicitou ir para tela final
     * @type {string}
     * @fires {FinalScreenData}
     * @status ATIVO - Emitido por: ProgressBar, SectionContainer
     */
    FINAL_SCREEN_REQUESTED: 'final:screen:requested',

    // ==========================================
    // ESTADO GLOBAL
    // ==========================================

    /**
     * Estado global mudou (StateManager)
     * @type {string}
     * @fires {{ key: string, value: any }}
     * @status RESERVADO
     */
    STATE_CHANGED: 'state:changed',

    /**
     * Nova sessão criada
     * @type {string}
     * @fires {SessionData}
     * @status RESERVADO
     */
    SESSION_CREATED: 'session:created',

    /**
     * Sessão existente carregada (ex: restauração de draft)
     * @type {string}
     * @fires {SessionData}
     * @status RESERVADO
     */
    SESSION_LOADED: 'session:loaded',

    // ==========================================
    // UI
    // ==========================================

    /**
     * Mostrar indicador de loading
     * @type {string}
     * @fires {{ message?: string }}
     * @status RESERVADO
     */
    SHOW_LOADING: 'ui:loading:show',

    /**
     * Esconder loading
     * @type {string}
     * @fires {void}
     * @status RESERVADO
     */
    HIDE_LOADING: 'ui:loading:hide',

    /**
     * Mostrar mensagem de erro
     * @type {string}
     * @fires {ErrorData}
     * @status RESERVADO
     */
    SHOW_ERROR: 'ui:error:show',

    /**
     * Mostrar mensagem de sucesso
     * @type {string}
     * @fires {{ message: string }}
     * @status RESERVADO
     */
    SHOW_SUCCESS: 'ui:success:show',

    // ==========================================
    // TEXTO GERADO
    // ==========================================

    /**
     * Texto BO gerado pela LLM
     * @type {string}
     * @fires {TextGeneratedData}
     * @status RESERVADO
     */
    TEXT_GENERATED: 'text:generated',

    /**
     * User pediu para copiar texto
     * @type {string}
     * @fires {{ sectionId?: number, copyAll?: boolean }}
     * @status RESERVADO
     */
    TEXT_COPY_REQUESTED: 'text:copy:requested',

    /**
     * Texto copiado para clipboard
     * @type {string}
     * @fires {{ success: boolean, sectionId?: number }}
     * @status RESERVADO
     */
    TEXT_COPIED: 'text:copied'
};

// ============================================
// CLASSE EVENTBUS
// ============================================

class EventBus {
    /**
     * Singleton instance
     * @type {EventBus}
     */
    static _instance = null;

    /**
     * Retorna instância singleton do EventBus.
     * @returns {EventBus}
     */
    static getInstance() {
        if (!EventBus._instance) {
            EventBus._instance = new EventBus();
        }
        return EventBus._instance;
    }

    constructor() {
        if (EventBus._instance) {
            throw new Error('EventBus é singleton. Use EventBus.getInstance()');
        }

        /**
         * Mapa de event → Set de handlers
         * @type {Map<string, Set<Function>>}
         */
        this._handlers = new Map();

        /**
         * Rastreamento para debug
         * @type {Array<{event: string, data: any, timestamp: number}>}
         */
        this._eventHistory = [];
        this._maxHistorySize = 50;

        /**
         * Flag para debug mode
         * @type {boolean}
         */
        this._debug = false;
    }

    /**
     * Ativa/desativa modo debug (logs de eventos)
     * @param {boolean} enabled
     */
    setDebug(enabled) {
        this._debug = enabled;
        if (enabled) {
            console.log('[EventBus] Debug mode ativado');
        }
    }

    /**
     * Registra handler para um evento.
     *
     * @param {string} event - Nome do evento
     * @param {Function} handler - Callback a executar
     * @returns {Function} Função para fazer unsubscribe
     *
     * @example
     * const unsubscribe = eventBus.on(Events.ANSWER_SAVED, (data) => {
     *     console.log('Resposta salva:', data.questionId);
     * });
     *
     * // Mais tarde...
     * unsubscribe();
     */
    on(event, handler) {
        if (typeof handler !== 'function') {
            throw new Error(`Handler deve ser função. Recebido: ${typeof handler}`);
        }

        if (!this._handlers.has(event)) {
            this._handlers.set(event, new Set());
        }

        this._handlers.get(event).add(handler);

        if (this._debug) {
            console.log(`[EventBus] Handler registrado: ${event} (total: ${this._handlers.get(event).size})`);
        }

        // Retorna função de cleanup
        return () => this.off(event, handler);
    }

    /**
     * Remove handler de um evento.
     *
     * @param {string} event - Nome do evento
     * @param {Function} handler - Handler a remover
     */
    off(event, handler) {
        if (!this._handlers.has(event)) {
            return;
        }

        const handlers = this._handlers.get(event);
        handlers.delete(handler);

        if (handlers.size === 0) {
            this._handlers.delete(event);
        }

        if (this._debug) {
            console.log(`[EventBus] Handler removido: ${event}`);
        }
    }

    /**
     * Emite um evento, notificando todos os handlers registrados.
     *
     * @param {string} event - Nome do evento
     * @param {any} data - Dados a passar para handlers
     *
     * @example
     * eventBus.emit(Events.ANSWER_SAVED, {
     *     questionId: '1.1',
     *     answer: 'Resposta do usuário',
     *     sectionNumber: 1
     * });
     */
    emit(event, data = null) {
        // Debug logging
        if (this._debug) {
            console.log(`[EventBus] Emit: ${event}`, data);
        }

        // Salvar no histórico
        this._eventHistory.push({
            event,
            data,
            timestamp: Date.now()
        });

        // Limitar tamanho do histórico
        if (this._eventHistory.length > this._maxHistorySize) {
            this._eventHistory.shift();
        }

        // Notificar handlers
        if (!this._handlers.has(event)) {
            if (this._debug) {
                console.log(`[EventBus] Nenhum handler para: ${event}`);
            }
            return;
        }

        const handlers = this._handlers.get(event);

        // Executar cada handler com tratamento de erro
        handlers.forEach(handler => {
            try {
                handler(data);
            } catch (error) {
                console.error(`[EventBus] Erro em handler para ${event}:`, error);
                // Não propagar erro para não afetar outros handlers
            }
        });
    }

    /**
     * Registra handler que será executado apenas uma vez.
     *
     * @param {string} event - Nome do evento
     * @param {Function} handler - Callback a executar
     * @returns {Function} Função para cancelar (fazer unsubscribe)
     *
     * @example
     * eventBus.once(Events.SESSION_CREATED, (data) => {
     *     console.log('Sessão criada:', data.sessionId);
     * });
     */
    once(event, handler) {
        const wrappedHandler = (data) => {
            handler(data);
            this.off(event, wrappedHandler);
        };

        return this.on(event, wrappedHandler);
    }

    /**
     * Remove todos os handlers de um evento (ou todos se event não fornecido).
     *
     * @param {string} [event] - Nome do evento (opcional)
     */
    clear(event = null) {
        if (event) {
            this._handlers.delete(event);
            if (this._debug) {
                console.log(`[EventBus] Handlers limpos para: ${event}`);
            }
        } else {
            this._handlers.clear();
            if (this._debug) {
                console.log('[EventBus] Todos handlers limpos');
            }
        }
    }

    /**
     * Retorna histórico de eventos recentes (para debug).
     *
     * @param {number} [limit=10] - Número de eventos a retornar
     * @returns {Array<{event: string, data: any, timestamp: number}>}
     */
    getHistory(limit = 10) {
        return this._eventHistory.slice(-limit);
    }

    /**
     * Retorna estatísticas do EventBus (para debug).
     *
     * @returns {Object}
     */
    getStats() {
        const stats = {
            totalEvents: this._handlers.size,
            events: []
        };

        this._handlers.forEach((handlers, event) => {
            stats.events.push({
                event,
                handlerCount: handlers.size
            });
        });

        return stats;
    }

    /**
     * Imprime estatísticas no console (debug helper).
     */
    printStats() {
        const stats = this.getStats();
        console.log('[EventBus] Estatísticas:', stats);
    }
}

// ============================================
// EXPORT
// ============================================

// Criar instância global
const eventBus = EventBus.getInstance();

// Expor no window para acesso global
if (typeof window !== 'undefined') {
    window.EventBus = EventBus;
    window.Events = Events;
    window.eventBus = eventBus;
}

// Export para módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { EventBus, Events, eventBus };
}
