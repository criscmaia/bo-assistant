/**
 * EventBus - Mediator Pattern para comunicação desacoplada
 * BO Inteligente v0.13.1
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
// EVENTOS PADRONIZADOS
// ============================================

/**
 * Catálogo de eventos do sistema.
 * Centralizando aqui para evitar typos e facilitar descoberta.
 */
const Events = {
    // Navegação entre seções
    SECTION_CHANGE_REQUESTED: 'section:change:requested',  // User clicou em seção
    SECTION_LOADED: 'section:loaded',                      // Seção carregada com sucesso
    SECTION_LOAD_ERROR: 'section:load:error',              // Erro ao carregar seção

    // Respostas
    ANSWER_SUBMITTED: 'answer:submitted',                  // User submeteu resposta
    ANSWER_SAVED: 'answer:saved',                          // Resposta salva no backend
    ANSWER_SAVE_ERROR: 'answer:save:error',                // Erro ao salvar resposta

    // Progresso
    PROGRESS_UPDATED: 'progress:updated',                  // Progresso de seção atualizado
    SECTION_COMPLETED: 'section:completed',                // Seção finalizada
    BO_COMPLETED: 'bo:completed',                          // BO completo (seção 8 finalizada)
    FINAL_SCREEN_REQUESTED: 'final:screen:requested',     // User solicitou ir para tela final

    // Estado global
    STATE_CHANGED: 'state:changed',                        // Estado global mudou
    SESSION_CREATED: 'session:created',                    // Nova sessão criada
    SESSION_LOADED: 'session:loaded',                      // Sessão existente carregada

    // UI
    SHOW_LOADING: 'ui:loading:show',                       // Mostrar indicador de loading
    HIDE_LOADING: 'ui:loading:hide',                       // Esconder loading
    SHOW_ERROR: 'ui:error:show',                           // Mostrar erro
    SHOW_SUCCESS: 'ui:success:show',                       // Mostrar sucesso

    // Texto gerado
    TEXT_GENERATED: 'text:generated',                      // Texto BO gerado
    TEXT_COPY_REQUESTED: 'text:copy:requested',            // User pediu para copiar
    TEXT_COPIED: 'text:copied'                             // Texto copiado para clipboard
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
