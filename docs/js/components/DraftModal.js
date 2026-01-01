/**
 * DraftModal - Modal customizado para restaurar rascunho
 * BO Inteligente v1.0
 */

class DraftModal {
    /**
     * Modal para confirmar restauração de rascunho
     */
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.onContinue = null;
        this.onDiscard = null;
    }

    /**
     * Exibe o modal com dados do rascunho
     */
    show(draft, onContinue, onDiscard, sectionsData) {
        this.onContinue = onContinue;
        this.onDiscard = onDiscard;

        const savedTime = new Date(draft.timestamp);
        const formattedTime = savedTime.toLocaleString('pt-BR');

        this.container.innerHTML = `
            <div class="draft-modal-overlay">
                <div class="draft-modal">
                    <div class="draft-modal__header">
                        <div class="draft-modal__icon">📄</div>
                        <h2 class="draft-modal__title">Rascunho Encontrado!</h2>
                        <p class="draft-modal__subtitle">
                            Você tem um BO em andamento. Deseja continuar de onde parou?
                        </p>
                        <p class="draft-modal__timestamp">
                            Salvo em ${formattedTime}
                        </p>
                    </div>

                    <div class="draft-modal__preview">
                        ${this._formatDraftPreview(draft, sectionsData)}
                    </div>

                    <div class="draft-modal__actions">
                        <button class="draft-modal__btn draft-modal__btn--continue" id="draft-continue-btn">
                            ✅ Continuar
                        </button>
                        <button class="draft-modal__btn draft-modal__btn--discard" id="draft-discard-btn">
                            🗑️ Começar Novo
                        </button>
                    </div>

                    <p class="draft-modal__hint">
                        O rascunho é salvo automaticamente a cada resposta
                    </p>
                </div>
            </div>
        `;

        this._bindEvents();
    }

    /**
     * Formata preview do rascunho
     */
    _formatDraftPreview(draft, sectionsData) {
        let html = '';

        // Informações de progresso por seção
        if (draft.sectionsState && sectionsData) {
            Object.entries(draft.sectionsState).forEach(([sectionId, state]) => {
                const answeredCount = Object.keys(state.answers || {}).length;

                if (answeredCount > 0) {
                    // Calcular total dinâmico baseado nas respostas (considera follow-ups ativados)
                    const totalQuestions = window.calculateSectionTotal
                        ? window.calculateSectionTotal(parseInt(sectionId), state.answers || {})
                        : answeredCount;

                    const statusText = state.status === 'completed' ? 'completa' :
                                      state.status === 'skipped' ? 'pulada' :
                                      'em andamento';

                    html += `<div class="draft-section-summary">
                        <strong>Seção ${sectionId}:</strong> ${answeredCount}/${totalQuestions} ${answeredCount === 1 ? 'pergunta respondida' : 'perguntas respondidas'} (${statusText})
                    </div>`;
                }
            });
        }

        // Lista de respostas (scrollable)
        html += '<div class="draft-answers-list">';

        if (draft.sectionsState) {
            // Ordenar seções por ID
            const sortedSections = Object.entries(draft.sectionsState)
                .sort(([a], [b]) => parseInt(a) - parseInt(b));

            sortedSections.forEach(([sectionId, state]) => {
                if (state.answers && Object.keys(state.answers).length > 0) {
                    // Ordenar respostas por ID (1.1, 1.2, etc)
                    const sortedAnswers = Object.entries(state.answers)
                        .sort(([a], [b]) => {
                            const aParts = a.split('.').map(Number);
                            const bParts = b.split('.').map(Number);
                            for (let i = 0; i < Math.max(aParts.length, bParts.length); i++) {
                                if (aParts[i] !== bParts[i]) {
                                    return (aParts[i] || 0) - (bParts[i] || 0);
                                }
                            }
                            return 0;
                        });

                    sortedAnswers.forEach(([questionId, answer]) => {
                        // Truncar resposta se muito longa
                        const truncated = answer.length > 60 ? answer.substring(0, 60) + '...' : answer;
                        html += `
                            <div class="draft-answer-item">
                                <span class="draft-answer-id">${questionId}:</span>
                                <span class="draft-answer-text">${this._escapeHtml(truncated)}</span>
                            </div>
                        `;
                    });
                }
            });
        }

        html += '</div>';

        return html;
    }

    /**
     * Escapa HTML para prevenir XSS
     */
    _escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Bind de eventos
     */
    _bindEvents() {
        const continueBtn = this.container.querySelector('#draft-continue-btn');
        const discardBtn = this.container.querySelector('#draft-discard-btn');

        if (continueBtn) {
            continueBtn.addEventListener('click', () => {
                this.hide();
                if (this.onContinue) this.onContinue();
            });
        }

        if (discardBtn) {
            discardBtn.addEventListener('click', () => {
                this.hide();
                if (this.onDiscard) this.onDiscard();
            });
        }
    }

    /**
     * Esconde o modal
     */
    hide() {
        if (this.container) {
            this.container.innerHTML = '';
        }
    }
}
