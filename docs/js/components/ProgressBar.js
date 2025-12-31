/**
 * ProgressBar - Barra de Progresso Visual
 * BO Inteligente v1.0
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

        // Dados das seções (do sections.js ou passado por opções)
        this.sections = options.sections || (window.SECTIONS_DATA ? window.SECTIONS_DATA.map(s => ({
            id: s.id,
            name: s.name,
            emoji: s.emoji,
            totalQuestions: s.questions.length + (s.skipQuestion ? 1 : 0)
        })) : []);

        // Estado de cada seção
        this.sectionStates = {};
        this.sections.forEach(s => {
            this.sectionStates[s.id] = {
                status: 'pending', // pending, in_progress, completed, skipped
                answeredCount: 0,
                totalCount: s.totalQuestions
            };
        });

        // Seção atual
        this.currentSectionId = options.currentSection || 1;

        // Callback para navegação
        this.onSectionClick = options.onSectionClick || ((sectionId) => {
            console.log('[ProgressBar] Clicou na seção:', sectionId);
        });

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

            // Eventos
            node.addEventListener('click', () => this._handleNodeClick(section.id));
            node.addEventListener('mouseenter', (e) => this._showTooltip(e, section));
            node.addEventListener('mouseleave', () => this._hideTooltip());

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

        // Remover classes anteriores
        node.classList.remove(
            'progress-node--pending',
            'progress-node--in-progress',
            'progress-node--completed',
            'progress-node--skipped'
        );

        // Aplicar classe do estado atual
        node.classList.add(`progress-node--${state.status}`);
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
        // Remover status in_progress da seção anterior
        if (this.currentSectionId && this.sectionStates[this.currentSectionId]) {
            const oldState = this.sectionStates[this.currentSectionId];
            if (oldState.status === 'in_progress') {
                oldState.status = 'pending';
                const oldNode = this.container.querySelector(`[data-section-id="${this.currentSectionId}"]`);
                if (oldNode) this._applyNodeState(oldNode, this.currentSectionId);
            }
        }

        // Definir nova seção atual
        this.currentSectionId = sectionId;
        this.updateSection(sectionId, 'in_progress');
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
    markSkipped(sectionId) {
        this.updateSection(sectionId, 'skipped');
        this._updateLineFill(sectionId);
    }

    /**
     * Atualiza preenchimento de uma linha
     */
    _updateLineFill(sectionId) {
        const lineFill = document.getElementById(`line-fill-${sectionId}`);
        if (!lineFill) return;

        const state = this.sectionStates[sectionId];
        let percentage = 0;

        if (state.status === 'completed' || state.status === 'skipped') {
            percentage = 100;
        } else if (state.status === 'in_progress' && state.totalCount > 0) {
            percentage = (state.answeredCount / state.totalCount) * 100;
        }

        lineFill.style.width = `${percentage}%`;
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

        // Só permite clicar em seções já visitadas (completed ou skipped)
        // ou na seção atual
        if (state.status === 'completed' || state.status === 'skipped' || sectionId === this.currentSectionId) {
            this.onSectionClick(sectionId);
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
                    statusSpan.textContent = '⏭️ Pulada';
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
