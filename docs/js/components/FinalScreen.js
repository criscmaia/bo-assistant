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
     * Renderiza a tela final com seções individuais
     */
    render() {
        if (!this.container) return;

        const stats = this._calculateStats();

        this.container.innerHTML = `
            <div class="final-screen">
                <!-- Header comemorativo -->
                <div class="final-screen__header">
                    <div class="final-screen__icon">🎉</div>
                    <h1 class="final-screen__title">BO Concluído com Sucesso!</h1>
                    <p class="final-screen__subtitle">
                        Todas as seções foram preenchidas. Tempo total: ${stats.duration}
                    </p>
                </div>

                <div class="final-screen__content">
                    <!-- Seções individuais (NOVO) -->
                    ${this._renderIndividualSections()}

                    <!-- Botão copiar tudo (MOVIDO PARA CÁ) -->
                    <div class="final-screen__copy-all-container">
                        <button class="final-screen__copy-all-btn" id="final-copy-all-btn">
                            📋 Copiar BO Completo (Todas Seções)
                        </button>
                    </div>

                    <!-- Botão de ação -->
                    <div class="final-screen__actions">
                        <button class="final-screen__action-btn final-screen__action-btn--primary" id="final-new-bo-btn">
                            ➕ Iniciar Novo BO
                        </button>
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
            const statusText = isCompleted ? 'Completa' : (isSkipped ? (state.skipReason || 'Não se aplica') : 'Pendente');
            const statusIcon = isCompleted ? '✅' : (isSkipped ? '⃠' : '⏳');

            return `
                <div class="final-screen__section-item" data-section-id="${section.id}">
                    <span class="final-screen__section-icon">${section.emoji}</span>
                    <span class="final-screen__section-name">
                        Seção ${section.id}: ${section.name}
                    </span>
                    <span class="final-screen__section-status final-screen__section-status--${statusClass}">
                        <span style="display: inline-block; margin-right: 3px;">${statusIcon}</span>${statusText}
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
     * Renderiza seções individuais com botões de cópia individuais
     * @returns {string} HTML das seções
     */
    _renderIndividualSections() {
        // Filtrar seções completas com texto gerado
        const sections = Object.entries(this.sectionsState)
            .map(([id, state]) => ({
                id: parseInt(id),
                ...state,
                sectionData: SECTIONS_DATA[parseInt(id) - 1]
            }))
            .filter(s => s.status === 'completed' && s.generatedText)
            .sort((a, b) => a.id - b.id);

        if (sections.length === 0) {
            return `
                <div class="final-screen__empty">
                    <p>Nenhum texto gerado ainda.</p>
                </div>
            `;
        }

        // Renderizar cada seção individualmente
        return sections.map(section => `
            <div class="final-screen__section-box" data-section-id="${section.id}">
                <div class="final-screen__section-header">
                    <span class="final-screen__section-title">
                        📄 Seção ${section.id}: ${section.sectionData.name}
                    </span>
                    <button
                        class="final-screen__section-copy-btn"
                        data-section-id="${section.id}"
                        title="Copiar Seção ${section.id}">
                        📋 Copiar Seção ${section.id}
                    </button>
                </div>
                <div class="final-screen__section-content">
                    ${this._formatTextToHTML(section.generatedText)}
                </div>
            </div>
        `).join('\n');
    }

    /**
     * Formata texto para HTML (mantém quebras de linha)
     */
    _formatTextToHTML(text) {
        if (!text) return '';
        // O CSS já usa white-space: pre-wrap, então só retornamos o texto
        return text;
    }

    /**
     * Gera texto completo para copiar (sem HTML)
     */
    _generateFullText() {
        let text = '';

        SECTIONS_DATA.forEach(section => {
            const state = this.sectionsState[section.id] || {};

            if (state.status === 'completed' && state.generatedText) {
                text += `=== SEÇÃO ${section.id}: ${section.name.toUpperCase()} ===\n\n`;
                text += `${state.generatedText}\n\n`;
                text += `${'='.repeat(60)}\n\n`;
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
        // Botão "Copiar BO Completo (Todas Seções)"
        const copyAllBtn = this.container.querySelector('#final-copy-all-btn');
        if (copyAllBtn) {
            copyAllBtn.addEventListener('click', () => this._copyAllText());
        }

        // Botões "Copiar Seção X" (individuais)
        const sectionCopyBtns = this.container.querySelectorAll('.final-screen__section-copy-btn');
        sectionCopyBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const sectionId = parseInt(e.target.dataset.sectionId);
                this._copySectionText(sectionId);
            });
        });

        // Botão "Iniciar Novo BO"
        const newBOBtn = this.container.querySelector('#final-new-bo-btn');
        if (newBOBtn) {
            newBOBtn.addEventListener('click', () => this._handleNewBO());
        }
    }

    /**
     * Copia texto de uma seção individual
     * @param {number} sectionId - ID da seção a copiar
     */
    _copySectionText(sectionId) {
        const section = this.sectionsState[sectionId];
        if (!section || !section.generatedText) {
            console.warn('[FinalScreen] Seção não encontrada ou sem texto:', sectionId);
            return;
        }

        const sectionData = SECTIONS_DATA[sectionId - 1];
        const header = `=== SEÇÃO ${sectionId}: ${sectionData.name.toUpperCase()} ===\n\n`;
        const textToCopy = header + section.generatedText;

        navigator.clipboard.writeText(textToCopy).then(() => {
            console.log('[FinalScreen] Seção copiada:', sectionId);
            this._showCopyFeedback(sectionId);
        }).catch(err => {
            console.error('[FinalScreen] Erro ao copiar seção:', err);
            alert('Erro ao copiar texto. Tente novamente.');
        });
    }

    /**
     * Mostra feedback visual ao copiar seção
     * @param {number} sectionId - ID da seção copiada
     */
    _showCopyFeedback(sectionId) {
        const btn = this.container.querySelector(`.final-screen__section-copy-btn[data-section-id="${sectionId}"]`);
        if (!btn) return;

        const originalText = btn.textContent;
        btn.textContent = '✅ Copiado!';
        btn.classList.add('final-screen__section-copy-btn--copied');

        setTimeout(() => {
            btn.textContent = originalText;
            btn.classList.remove('final-screen__section-copy-btn--copied');
        }, 2000);
    }

    /**
     * Copia todo o texto do BO para área de transferência
     */
    _copyAllText() {
        const fullText = this._generateFullText();

        navigator.clipboard.writeText(fullText).then(() => {
            console.log('[FinalScreen] Texto completo copiado');
            this._showCopyAllFeedback();
        }).catch(err => {
            console.error('[FinalScreen] Erro ao copiar:', err);
            alert('Erro ao copiar texto. Tente novamente.');
        });
    }

    /**
     * Mostra feedback visual ao copiar tudo
     */
    _showCopyAllFeedback() {
        const copyBtn = this.container.querySelector('#final-copy-all-btn');
        if (!copyBtn) return;

        const originalText = copyBtn.textContent;
        copyBtn.textContent = '✅ Copiado!';
        copyBtn.classList.add('final-screen__copy-all-btn--copied');

        setTimeout(() => {
            copyBtn.textContent = originalText;
            copyBtn.classList.remove('final-screen__copy-all-btn--copied');
        }, 2000);
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
