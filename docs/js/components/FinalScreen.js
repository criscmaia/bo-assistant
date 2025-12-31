/**
 * FinalScreen - Tela final com resumo e texto completo do BO
 * BO Inteligente v1.0
 */

class FinalScreen {
    /**
     * Tela final com resumo e texto completo do BO
     */
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.sectionsState = options.sectionsState || {};
        this.onNewBO = options.onNewBO || (() => {});
        this.onSectionClick = options.onSectionClick || (() => {});
        this.startTime = options.startTime || new Date();
    }

    /**
     * Renderiza a tela final
     */
    render() {
        if (!this.container) return;

        const stats = this._calculateStats();
        const fullText = this._generateFullText();

        this.container.innerHTML = `
            <div class="final-screen">
                <!-- Header comemorativo -->
                <div class="final-screen__header">
                    <div class="final-screen__icon">🎉</div>
                    <h1 class="final-screen__title">BO Completo!</h1>
                    <p class="final-screen__subtitle">
                        Todas as seções foram preenchidas com sucesso.
                    </p>
                </div>

                <div class="final-screen__content">
                    <!-- Resumo das seções -->
                    <div class="final-screen__summary">
                        <h2 class="final-screen__summary-title">
                            📊 Resumo das Seções
                        </h2>
                        <div class="final-screen__section-list">
                            ${this._renderSectionsList()}
                        </div>
                    </div>

                    <!-- Texto completo -->
                    <div class="final-screen__text-box">
                        <div class="final-screen__text-header">
                            <span class="final-screen__text-title">
                                📄 Texto Completo do BO
                            </span>
                            <button class="final-screen__copy-btn" id="final-copy-btn">
                                📋 Copiar Tudo
                            </button>
                        </div>
                        <div class="final-screen__text-content" id="final-text-content">
                            ${this._renderFullText()}
                        </div>
                    </div>

                    <!-- Botões de ação -->
                    <div class="final-screen__actions">
                        <button class="final-screen__action-btn final-screen__action-btn--primary" id="final-copy-all">
                            📋 Copiar Texto Completo
                        </button>
                        <button class="final-screen__action-btn final-screen__action-btn--secondary" id="final-new-bo">
                            🔄 Iniciar Novo BO
                        </button>
                    </div>

                    <!-- Estatísticas -->
                    <div class="final-screen__stats">
                        <div class="final-screen__stat">
                            <span>✅</span>
                            <span class="final-screen__stat-value">${stats.completed}</span>
                            <span>seções completas</span>
                        </div>
                        <div class="final-screen__stat">
                            <span>⏭️</span>
                            <span class="final-screen__stat-value">${stats.skipped}</span>
                            <span>seções puladas</span>
                        </div>
                        <div class="final-screen__stat">
                            <span>⏱️</span>
                            <span class="final-screen__stat-value">${stats.duration}</span>
                            <span>de duração</span>
                        </div>
                    </div>
                </div>
            </div>
        `;

        this._bindEvents();
    }

    /**
     * Renderiza lista de seções
     */
    _renderSectionsList() {
        return SECTIONS_DATA.map(section => {
            const state = this.sectionsState[section.id] || {};
            const isCompleted = state.status === 'completed';
            const isSkipped = state.status === 'skipped';

            const statusClass = isCompleted ? 'completed' : (isSkipped ? 'skipped' : 'pending');
            const statusText = isCompleted ? 'Completa' : (isSkipped ? 'Pulada' : 'Pendente');
            const statusIcon = isCompleted ? '✅' : (isSkipped ? '⏭️' : '⏳');

            return `
                <div class="final-screen__section-item" data-section-id="${section.id}">
                    <span class="final-screen__section-icon">${section.emoji}</span>
                    <span class="final-screen__section-name">
                        Seção ${section.id}: ${section.name}
                    </span>
                    <span class="final-screen__section-status final-screen__section-status--${statusClass}">
                        ${statusIcon} ${statusText}
                    </span>
                </div>
            `;
        }).join('');
    }

    /**
     * Renderiza texto completo formatado para HTML
     */
    _renderFullText() {
        let html = '';

        SECTIONS_DATA.forEach(section => {
            const state = this.sectionsState[section.id] || {};

            if (state.status === 'completed' && state.generatedText) {
                html += `
                    <div class="final-screen__text-section">
                        <div class="final-screen__text-section-title">
                            ${section.emoji} Seção ${section.id}: ${section.name}
                        </div>
                        <div>${state.generatedText}</div>
                    </div>
                `;
            } else if (state.status === 'skipped') {
                html += `
                    <div class="final-screen__text-section">
                        <div class="final-screen__text-section-title">
                            ${section.emoji} Seção ${section.id}: ${section.name}
                        </div>
                        <div style="color: #6b7280; font-style: italic;">
                            [Seção não aplicável / pulada]
                        </div>
                    </div>
                `;
            }
        });

        return html || '<p style="color: #6b7280;">Nenhum texto gerado.</p>';
    }

    /**
     * Gera texto completo para copiar (sem HTML)
     */
    _generateFullText() {
        let text = '';

        SECTIONS_DATA.forEach(section => {
            const state = this.sectionsState[section.id] || {};

            if (state.status === 'completed' && state.generatedText) {
                text += `[SEÇÃO ${section.id}: ${section.name.toUpperCase()}]\n\n`;
                text += `${state.generatedText}\n\n`;
                text += `${'─'.repeat(50)}\n\n`;
            }
        });

        return text.trim();
    }

    /**
     * Calcula estatísticas
     */
    _calculateStats() {
        let completed = 0;
        let skipped = 0;

        Object.values(this.sectionsState).forEach(state => {
            if (state.status === 'completed') completed++;
            if (state.status === 'skipped') skipped++;
        });

        // Calcular duração
        const now = new Date();
        const diffMs = now - this.startTime;
        const diffMin = Math.floor(diffMs / 60000);

        let duration;
        if (diffMin < 1) {
            duration = 'menos de 1 min';
        } else if (diffMin < 60) {
            duration = `${diffMin} min`;
        } else {
            const hours = Math.floor(diffMin / 60);
            const mins = diffMin % 60;
            duration = `${hours}h ${mins}min`;
        }

        return { completed, skipped, duration };
    }

    /**
     * Bind eventos
     */
    _bindEvents() {
        // Copiar texto (botão pequeno)
        const copyBtn = this.container.querySelector('#final-copy-btn');
        if (copyBtn) {
            copyBtn.addEventListener('click', () => this._copyFullText(copyBtn));
        }

        // Copiar texto (botão grande)
        const copyAllBtn = this.container.querySelector('#final-copy-all');
        if (copyAllBtn) {
            copyAllBtn.addEventListener('click', () => this._copyFullText(copyAllBtn));
        }

        // Novo BO
        const newBoBtn = this.container.querySelector('#final-new-bo');
        if (newBoBtn) {
            newBoBtn.addEventListener('click', () => this._handleNewBO());
        }

        // Clique nas seções
        const sectionItems = this.container.querySelectorAll('.final-screen__section-item');
        sectionItems.forEach(item => {
            item.addEventListener('click', () => {
                const sectionId = parseInt(item.dataset.sectionId);
                this.onSectionClick(sectionId);
            });
        });
    }

    /**
     * Copia texto completo
     */
    _copyFullText(buttonEl) {
        const text = this._generateFullText();

        navigator.clipboard.writeText(text).then(() => {
            // Feedback visual
            const originalText = buttonEl.innerHTML;
            buttonEl.innerHTML = '✅ Copiado!';
            buttonEl.classList.add('final-screen__copy-btn--copied');

            setTimeout(() => {
                buttonEl.innerHTML = originalText;
                buttonEl.classList.remove('final-screen__copy-btn--copied');
            }, 2000);
        }).catch(err => {
            console.error('[FinalScreen] Erro ao copiar:', err);
            alert('Erro ao copiar. Tente selecionar o texto manualmente.');
        });
    }

    /**
     * Inicia novo BO
     */
    _handleNewBO() {
        const confirm = window.confirm(
            '🔄 Iniciar Novo BO\n\n' +
            'Isso vai limpar todos os dados atuais.\n' +
            'Certifique-se de ter copiado o texto antes de continuar.\n\n' +
            'Deseja continuar?'
        );

        if (confirm) {
            this.onNewBO();
        }
    }

    /**
     * Atualiza estado das seções
     */
    updateSectionsState(sectionsState) {
        this.sectionsState = sectionsState;
    }
}
