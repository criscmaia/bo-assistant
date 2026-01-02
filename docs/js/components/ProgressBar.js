/**
 * ProgressBar - Barra de Progresso Visual
 * BO Inteligente v0.13.1
 *
 * NOTA: A partir da v0.13.1, o estado é sincronizado via callbacks do BOApp,
 * que por sua vez é notificado pelo StateManager.
 */

// ============================================
// CLASSE PROGRESSBAR - BARRA DE PROGRESSO
// ============================================

class ProgressBar {
    /**
     * Componente de barra de progresso horizontal
     * Mostra 8 seções com estados: pending, in_progress, completed, skipped
     */
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.tooltipEl = document.getElementById('progress-tooltip');

        // Referência ao StateManager (v0.13.1+) - opcional, usado para consultas diretas
        this.stateManager = typeof StateManager !== 'undefined' ? StateManager.getInstance() : null;

        // Dados das seções (do sections.js ou passado por opções)
        this.sections = options.sections || (window.SECTIONS_DATA ? window.SECTIONS_DATA.map(s => ({
            id: s.id,
            name: s.name,
            emoji: s.emoji,
            totalQuestions: s.questions.length + (s.skipQuestion ? 1 : 0)
        })) : []);

        // Estado visual de cada seção (sincronizado via callbacks do BOApp)
        this.sectionStates = {};
        this.sections.forEach(s => {
            this.sectionStates[s.id] = {
                status: 'pending', // pending, in_progress, completed, skipped
                answeredCount: 0,
                totalCount: s.totalQuestions,
                skipReason: null // Razão pela qual a seção foi pulada
            };
        });

        // Seção atual
        this.currentSectionId = options.currentSection || 1;

        // Callback para navegação (DEPRECATED - usar EventBus)
        this.onSectionClick = options.onSectionClick || ((sectionId) => {
            console.log('[ProgressBar] Clicou na seção:', sectionId);
        });

        // EventBus para comunicação desacoplada (v0.13.1+)
        this.eventBus = typeof window !== 'undefined' && window.eventBus ? window.eventBus : null;

        // Dispose Pattern - Rastreamento de listeners para cleanup (v0.13.1+)
        this._eventListeners = [];
        this._eventBusUnsubscribers = [];

        // Renderizar
        if (this.container) {
            this.render();
        }
    }

    /**
     * Renderiza a barra de progresso completa
     */
    render() {
        if (!this.container) return;

        // Limpar listeners anteriores (Dispose Pattern - v0.13.1+)
        this.dispose();

        this.container.innerHTML = '';

        this.sections.forEach((section, index) => {
            // Wrapper da bolinha
            const nodeWrapper = document.createElement('div');
            nodeWrapper.className = 'progress-node-wrapper';

            // Bolinha
            const node = document.createElement('div');
            node.className = 'progress-node';
            node.dataset.sectionId = section.id;

            // Número dentro da bolinha
            const nodeNumber = document.createElement('span');
            nodeNumber.className = 'node-number';
            nodeNumber.textContent = section.id;
            node.appendChild(nodeNumber);

            // Aplicar estado visual
            this._applyNodeState(node, section.id);

            // Eventos com rastreamento para cleanup
            const clickHandler = () => this._handleNodeClick(section.id);
            const mouseEnterHandler = (e) => this._showTooltip(e, section);
            const mouseLeaveHandler = () => this._hideTooltip();

            node.addEventListener('click', clickHandler);
            node.addEventListener('mouseenter', mouseEnterHandler);
            node.addEventListener('mouseleave', mouseLeaveHandler);

            // Rastrear listeners para cleanup (Dispose Pattern - v0.13.1+)
            this._eventListeners.push({ element: node, event: 'click', handler: clickHandler });
            this._eventListeners.push({ element: node, event: 'mouseenter', handler: mouseEnterHandler });
            this._eventListeners.push({ element: node, event: 'mouseleave', handler: mouseLeaveHandler });

            nodeWrapper.appendChild(node);

            // Label abaixo (número)
            const label = document.createElement('div');
            label.className = 'progress-node-label';
            label.textContent = `Seção ${section.id}`;
            nodeWrapper.appendChild(label);

            this.container.appendChild(nodeWrapper);

            // Linha de conexão (exceto após a última)
            if (index < this.sections.length - 1) {
                const lineContainer = document.createElement('div');
                lineContainer.className = 'progress-line-container';
                lineContainer.dataset.lineAfter = section.id;

                const lineFill = document.createElement('div');
                lineFill.className = 'progress-line-fill';
                lineFill.id = `line-fill-${section.id}`;

                lineContainer.appendChild(lineFill);
                this.container.appendChild(lineContainer);
            }
        });

        // Aplicar estados iniciais
        this._updateAllLines();
    }

    /**
     * Aplica o estado visual correto à bolinha
     */
    _applyNodeState(node, sectionId) {
        const state = this.sectionStates[sectionId];

        // Remover classes anteriores (com hyphen e underscore)
        node.classList.remove(
            'progress-node--pending',
            'progress-node--in-progress',
            'progress-node--in_progress',  // Removido o suporte a underscore aqui
            'progress-node--completed',
            'progress-node--skipped'
        );

        // Aplicar classe do estado atual (normalizado com hyphen)
        const normalizedStatus = state.status.replace('_', '-');
        node.classList.add(`progress-node--${normalizedStatus}`);
    }

    /**
     * Atualiza estado de uma seção
     */
    updateSection(sectionId, status, answeredCount = null) {
        if (!this.sectionStates[sectionId]) return;

        this.sectionStates[sectionId].status = status;
        if (answeredCount !== null) {
            this.sectionStates[sectionId].answeredCount = answeredCount;
        }

        // Atualizar visual da bolinha
        const node = this.container.querySelector(`[data-section-id="${sectionId}"]`);
        if (node) {
            this._applyNodeState(node, sectionId);
        }

        // Atualizar linhas
        this._updateAllLines();
    }

    /**
     * Define a seção atual (em progresso)
     */
    setCurrentSection(sectionId) {
        // Não mudar status da seção anterior - apenas atualizar highlight visual
        // A seção anterior pode estar completed/in_progress e deve manter esse status

        console.log('[ProgressBar] setCurrentSection:', sectionId);

        // Definir nova seção atual
        this.currentSectionId = sectionId;

        // Atualizar status no sectionStates para in_progress se estava pending
        if (this.sectionStates[sectionId] && this.sectionStates[sectionId].status === 'pending') {
            console.log('[ProgressBar] Mudando status de pending → in_progress para seção:', sectionId);
            this.sectionStates[sectionId].status = 'in_progress';
        }

        // Atualizar visual de todas as seções
        this.container.querySelectorAll('.progress-node').forEach(node => {
            const id = parseInt(node.dataset.sectionId);
            this._applyNodeState(node, id);
        });
    }

    /**
     * Atualiza o progresso dentro de uma seção
     */
    updateProgress(sectionId, answeredCount, totalCount = null) {
        if (!this.sectionStates[sectionId]) return;

        const state = this.sectionStates[sectionId];
        state.answeredCount = answeredCount;
        if (totalCount !== null) {
            state.totalCount = totalCount;
        }

        console.log('[ProgressBar] updateProgress:', { sectionId, answeredCount, totalCount, status: state.status });

        // Atualizar linha correspondente
        this._updateLineFill(sectionId);
    }

    /**
     * Marca seção como completa
     */
    markCompleted(sectionId) {
        this.updateSection(sectionId, 'completed');
        this.sectionStates[sectionId].answeredCount = this.sectionStates[sectionId].totalCount;
        this._updateLineFill(sectionId);
    }

    /**
     * Marca seção como pulada
     */
    markSkipped(sectionId, skipReason = null) {
        this.updateSection(sectionId, 'skipped');
        this.sectionStates[sectionId].skipReason = skipReason || null;
        this._updateLineFill(sectionId);
    }

    /**
     * Atualiza preenchimento de uma linha
     */
    _updateLineFill(sectionId) {
        const lineFill = document.getElementById(`line-fill-${sectionId}`);
        if (!lineFill) {
            console.warn('[ProgressBar] line-fill element not found for section:', sectionId);
            return;
        }

        const state = this.sectionStates[sectionId];
        let percentage = 0;

        if (state.status === 'completed' || state.status === 'skipped') {
            percentage = 100;
        } else if (state.status === 'in_progress' && state.totalCount > 0) {
            percentage = (state.answeredCount / state.totalCount) * 100;
        }

        console.log('[ProgressBar] _updateLineFill:', { sectionId, percentage, answeredCount: state.answeredCount, totalCount: state.totalCount, status: state.status });

        lineFill.style.width = `${percentage}%`;

        // Atualizar atributo data-section-status no container pai para styling tracejado
        const lineContainer = lineFill.parentElement;
        if (lineContainer) {
            lineContainer.dataset.sectionStatus = state.status;
        }
    }

    /**
     * Atualiza todas as linhas
     */
    _updateAllLines() {
        this.sections.forEach(section => {
            this._updateLineFill(section.id);
        });
    }

    /**
     * Trata clique em uma bolinha
     */
    _handleNodeClick(sectionId) {
        const state = this.sectionStates[sectionId];

        console.log('[ProgressBar] Clique na bolinha:', { sectionId, status: state.status, isPending: state.status === 'pending' });

        // Permitir clicar em qualquer seção já visitada (não-pending)
        // Isso inclui: in_progress, completed, skipped
        if (state.status !== 'pending') {
            // v0.13.1+: Emitir evento via EventBus (desacoplado)
            if (this.eventBus && typeof Events !== 'undefined') {
                this.eventBus.emit(Events.SECTION_CHANGE_REQUESTED, { sectionId });
            }

            // Fallback: Manter callback para compatibilidade (DEPRECATED)
            if (this.onSectionClick) {
                this.onSectionClick(sectionId);
            }
        } else {
            console.log('[ProgressBar] Bolinha bloqueada - status é pending');
        }
    }

    /**
     * Mostra tooltip ao passar mouse
     */
    _showTooltip(event, section) {
        if (!this.tooltipEl) return;

        const state = this.sectionStates[section.id];

        // Emoji
        const emojiSpan = this.tooltipEl.querySelector('.tooltip-emoji');
        if (emojiSpan) emojiSpan.textContent = section.emoji;

        // Nome
        const nameSpan = this.tooltipEl.querySelector('.tooltip-name');
        if (nameSpan) nameSpan.textContent = section.name;

        // Status
        const statusSpan = this.tooltipEl.querySelector('.tooltip-status');
        if (statusSpan) {
            switch (state.status) {
                case 'completed':
                    statusSpan.textContent = '✓ Completa';
                    break;
                case 'skipped':
                    const skipText = state.skipReason || 'Não se aplica';
                    statusSpan.innerHTML = `<span style="display: inline-block; margin-right: 3px;">⃠</span>${skipText}`;
                    break;
                case 'in_progress':
                    statusSpan.textContent = `${state.answeredCount}/${state.totalCount}`;
                    break;
                default:
                    statusSpan.textContent = 'Pendente';
            }
        }

        // Posicionar tooltip
        const rect = event.target.getBoundingClientRect();
        const containerRect = this.container.parentElement.getBoundingClientRect();

        this.tooltipEl.style.left = `${rect.left - containerRect.left + rect.width / 2}px`;
        this.tooltipEl.style.top = `${rect.top - containerRect.top - 45}px`;

        this.tooltipEl.classList.remove('hidden');
    }

    /**
     * Esconde tooltip
     */
    _hideTooltip() {
        if (this.tooltipEl) {
            this.tooltipEl.classList.add('hidden');
        }
    }

    /**
     * Dispose Pattern - Remove todos os event listeners (v0.13.1+)
     * Deve ser chamado ao destruir a barra ou re-renderizar para evitar memory leaks
     */
    dispose() {
        // Remover listeners DOM
        if (this._eventListeners && this._eventListeners.length > 0) {
            this._eventListeners.forEach(({ element, event, handler }) => {
                if (element) {
                    element.removeEventListener(event, handler);
                }
            });
            console.log('[ProgressBar] Disposed - listeners DOM removidos:', this._eventListeners.length);
            this._eventListeners = [];
        }

        // Remover listeners EventBus (v0.13.1+)
        if (this._eventBusUnsubscribers && this._eventBusUnsubscribers.length > 0) {
            this._eventBusUnsubscribers.forEach(unsubscribe => {
                if (typeof unsubscribe === 'function') {
                    unsubscribe();
                }
            });
            console.log('[ProgressBar] Disposed - listeners EventBus removidos:', this._eventBusUnsubscribers.length);
            this._eventBusUnsubscribers = [];
        }
    }

    /**
     * Reseta a barra de progresso
     */
    reset() {
        this.sections.forEach(s => {
            this.sectionStates[s.id] = {
                status: 'pending',
                answeredCount: 0,
                totalCount: s.totalQuestions
            };
        });
        this.currentSectionId = 1;
        this.render();
    }
}

// ============================================
// FIM CLASSE PROGRESSBAR
// ============================================
