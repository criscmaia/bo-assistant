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
    show(draft, onContinue, onDiscard) {
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
                    </div>

                    <div class="draft-modal__preview">
                        ${this._formatDraftPreview(draft)}
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
    _formatDraftPreview(draft) {
        const savedTime = new Date(draft.timestamp);
        const formattedTime = savedTime.toLocaleString('pt-BR');

        let previewText = `<strong>Salvo em:</strong> ${formattedTime}<br>`;

        if (draft.currentSectionIndex !== undefined) {
            previewText += `<strong>Seção atual:</strong> ${draft.currentSectionIndex + 1}<br>`;
        }

        // Contar seções completadas
        let completedCount = 0;
        let skippedCount = 0;
        if (draft.sectionsState) {
            Object.values(draft.sectionsState).forEach(state => {
                if (state.status === 'completed') completedCount++;
                if (state.status === 'skipped') skippedCount++;
            });
        }

        if (completedCount > 0 || skippedCount > 0) {
            previewText += `<strong>Progresso:</strong> ${completedCount} completa(s), ${skippedCount} pulada(s)`;
        }

        return previewText;
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
