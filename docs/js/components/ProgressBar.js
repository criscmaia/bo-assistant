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
        const maxSections = window.ACTIVE_SECTIONS_COUNT || 8;
        const allSections = window.SECTIONS_DATA || [];
        this.sections = options.sections || allSections.slice(0, maxSections).map(s => ({
            id: s.id,
            name: s.name,
            emoji: s.emoji,
            totalQuestions: s.questions.length + (s.skipQuestion ? 1 : 0)
        }));

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

        // Adicionar bolinha "BO Final" - SEMPRE visível
        // Verificar se as seções DISPONÍVEIS estão completas (completed ou skipped)
        // TEMPORÁRIO: Fluxo limitado às seções 1-3 (até perguntas finais serem implementadas)
        const availableSections = this.sections.filter(s => s.id <= 3);
        const allSectionsCompleted = availableSections.every(section => {
            const state = this.sectionStates[section.id];
            // Seção está "completa" se status é completed OU skipped
            return state && (state.status === 'completed' || state.status === 'skipped');
        });

        // Container da bolinha BO Final
        const finalNodeWrapper = document.createElement('div');
        finalNodeWrapper.className = 'progress-node-wrapper progress-node-wrapper--final';

        // Bolinha com estado condicional
        const finalNode = document.createElement('div');
        const isLocked = !allSectionsCompleted;

        if (isLocked) {
            // Estado LOCKED (cinza com cadeado) - não clicável
            finalNode.className = 'progress-node progress-node--pending progress-node--final progress-node--locked';
            finalNode.innerHTML = '<span class="node-number">🔒</span>';
        } else {
            // Estado COMPLETED (verde com checkmark) - clicável
            finalNode.className = 'progress-node progress-node--completed progress-node--final';
            finalNode.innerHTML = '<span class="node-number">✓</span>';
        }

        finalNode.dataset.sectionId = 'final';
        finalNode.dataset.locked = isLocked ? 'true' : 'false';

        // Label
        const finalLabel = document.createElement('div');
        finalLabel.className = 'progress-node-label';
        finalLabel.textContent = 'BO Final';

        finalNodeWrapper.appendChild(finalNode);
        finalNodeWrapper.appendChild(finalLabel);

        // Eventos - só permite clique se não estiver locked
        // NOTA: Verificar dataset.locked em vez de closure para refletir estado atualizado
        const finalClickHandler = () => {
            const currentlyLocked = finalNode.dataset.locked === 'true';
            if (!currentlyLocked) {
                this._handleFinalNodeClick();
            }
        };
        const finalMouseEnterHandler = (e) => {
            const currentlyLocked = finalNode.dataset.locked === 'true';
            this._showFinalTooltip(e, currentlyLocked);
        };
        const finalMouseLeaveHandler = () => this._hideTooltip();

        finalNode.addEventListener('click', finalClickHandler);
        finalNode.addEventListener('mouseenter', finalMouseEnterHandler);
        finalNode.addEventListener('mouseleave', finalMouseLeaveHandler);

        // Rastrear listeners para cleanup
        this._eventListeners.push({ element: finalNode, event: 'click', handler: finalClickHandler });
        this._eventListeners.push({ element: finalNode, event: 'mouseenter', handler: finalMouseEnterHandler });
        this._eventListeners.push({ element: finalNode, event: 'mouseleave', handler: finalMouseLeaveHandler });

        // Adicionar linha de conexão antes da bolinha final
        const lineContainer = document.createElement('div');
        lineContainer.className = 'progress-line-container progress-line-container--final';
        // Linha completa se todas seções completas, caso contrário vazia
        const fillWidth = allSectionsCompleted ? '100%' : '0%';
        const lineFill = document.createElement('div');
        lineFill.className = 'progress-line-fill';
        lineFill.style.width = fillWidth;
        lineContainer.appendChild(lineFill);

        this.container.appendChild(lineContainer);
        this.container.appendChild(finalNodeWrapper);

        // Aplicar estados iniciais
        this._updateAllLines();
    }

    /**
     * Aplica o estado visual correto à bolinha
     */
    _applyNodeState(node, sectionId) {
        const state = this.sectionStates[sectionId];

        // Guard: Se não há estado para esta seção, retornar
        if (!state) {
            console.warn('[ProgressBar] _applyNodeState - state not found for section:', sectionId);
            return;
        }

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
            // Skip se não for um número válido (ex: 'final')
            if (!isNaN(id)) {
                this._applyNodeState(node, id);
            }
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
        this._updateFinalNodeState();
    }

    /**
     * Marca seção como pulada
     */
    markSkipped(sectionId, skipReason = null) {
        this.updateSection(sectionId, 'skipped');
        this.sectionStates[sectionId].skipReason = skipReason || null;
        this._updateLineFill(sectionId);
        this._updateFinalNodeState();
    }

    /**
     * Atualiza estado visual da bolinha BO Final
     * Chamado quando seções são completadas/puladas
     */
    _updateFinalNodeState() {
        const finalNode = this.container.querySelector('.progress-node--final');
        if (!finalNode) return;

        // Verificar se seções 1-3 estão completas (temporário: fluxo limitado)
        const availableSections = this.sections.filter(s => s.id <= 3);
        const allCompleted = availableSections.every(section => {
            const state = this.sectionStates[section.id];
            return state && (state.status === 'completed' || state.status === 'skipped');
        });

        console.log('[ProgressBar] _updateFinalNodeState - allCompleted:', allCompleted);

        if (allCompleted) {
            // Mudar para COMPLETED
            finalNode.classList.remove('progress-node--pending', 'progress-node--locked');
            finalNode.classList.add('progress-node--completed');
            finalNode.innerHTML = '<span class="node-number">✓</span>';
            finalNode.dataset.locked = 'false';
            finalNode.style.cursor = 'pointer';

            // Atualizar linha de conexão
            const lineFill = this.container.querySelector('.progress-line-container--final .progress-line-fill');
            if (lineFill) {
                lineFill.style.width = '100%';
            }
        }
    }

    /**
     * Atualiza preenchimento de uma linha
     */
    _updateLineFill(sectionId) {
        const lineFill = document.getElementById(`line-fill-${sectionId}`);
        if (!lineFill) {
            // Não é erro - a última seção não tem linha após ela
            return;
        }

        const state = this.sectionStates[sectionId];

        // Guard: Se não há estado para esta seção, retornar
        if (!state) {
            console.warn('[ProgressBar] _updateLineFill - state not found for section:', sectionId);
            return;
        }

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
     * Manipula clique na bolinha "BO Final"
     */
    _handleFinalNodeClick() {
        console.log('[ProgressBar] Clique na bolinha BO Final');

        // Emitir evento via EventBus para navegar para tela final
        if (this.eventBus && typeof Events !== 'undefined') {
            this.eventBus.emit(Events.FINAL_SCREEN_REQUESTED, {
                context: 'progress_bar_final_node_click'
            });
        }
    }

    /**
     * Mostra tooltip ao passar mouse
     * Usa position: fixed com coordenadas do viewport para posicionamento preciso
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

        // Posicionar tooltip RELATIVO AO VIEWPORT (position: fixed)
        const nodeRect = event.target.getBoundingClientRect();

        // Calcular posição horizontal (centralizado na bolinha)
        // left do nó + metade da largura = centro da bolinha
        const left = nodeRect.left + (nodeRect.width / 2);

        // Calcular posição vertical com validação de espaço
        const tooltipHeight = 50; // Altura estimada do tooltip
        const spaceAbove = nodeRect.top; // Espaço até o topo do viewport
        const gap = 10; // Espaçamento entre bolinha e tooltip

        let top;

        // Se NÃO há espaço suficiente acima (menos de 70px), mostrar ABAIXO
        if (spaceAbove < 70) {
            // Posicionar ABAIXO da bolinha
            top = nodeRect.bottom + gap;
            this.tooltipEl.classList.add('progress-tooltip--bottom');
            this.tooltipEl.classList.remove('progress-tooltip--top');
        } else {
            // Posicionar ACIMA da bolinha (comportamento padrão)
            top = nodeRect.top - tooltipHeight - gap;
            this.tooltipEl.classList.add('progress-tooltip--top');
            this.tooltipEl.classList.remove('progress-tooltip--bottom');
        }

        // Aplicar posicionamento (coordenadas do viewport)
        this.tooltipEl.style.left = `${left}px`;
        this.tooltipEl.style.top = `${top}px`;

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
     * Mostra tooltip da bolinha "BO Final"
     * Usa position: fixed com coordenadas do viewport para posicionamento preciso
     */
    _showFinalTooltip(event, isLocked) {
        if (!this.tooltipEl) return;

        // Conteúdo do tooltip
        const emojiSpan = this.tooltipEl.querySelector('.tooltip-emoji');
        const nameSpan = this.tooltipEl.querySelector('.tooltip-name');
        const statusSpan = this.tooltipEl.querySelector('.tooltip-status');

        if (emojiSpan) emojiSpan.textContent = '📋';
        if (nameSpan) nameSpan.textContent = 'BO Final';

        if (statusSpan) {
            if (isLocked) {
                statusSpan.textContent = '🔒 Aguardando conclusão';
            } else {
                statusSpan.textContent = '✅ Clique para ver';
            }
        }

        // Posicionar tooltip RELATIVO AO VIEWPORT (position: fixed)
        const nodeRect = event.target.getBoundingClientRect();

        // Calcular posição horizontal (centralizado na bolinha)
        const left = nodeRect.left + (nodeRect.width / 2);

        // Calcular posição vertical com validação de espaço
        const tooltipHeight = 50;
        const spaceAbove = nodeRect.top;
        const gap = 10;

        let top;
        if (spaceAbove < 70) {
            // Posicionar ABAIXO
            top = nodeRect.bottom + gap;
            this.tooltipEl.classList.add('progress-tooltip--bottom');
            this.tooltipEl.classList.remove('progress-tooltip--top');
        } else {
            // Posicionar ACIMA
            top = nodeRect.top - tooltipHeight - gap;
            this.tooltipEl.classList.add('progress-tooltip--top');
            this.tooltipEl.classList.remove('progress-tooltip--bottom');
        }

        // Aplicar posicionamento (coordenadas do viewport)
        this.tooltipEl.style.left = `${left}px`;
        this.tooltipEl.style.top = `${top}px`;
        this.tooltipEl.classList.remove('hidden');
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
