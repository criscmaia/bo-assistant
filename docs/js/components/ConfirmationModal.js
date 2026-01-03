/**
 * ConfirmationModal - Modal de confirmação customizado
 * REUTILIZA as classes CSS do DraftModal para consistência
 */
class ConfirmationModal {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.onConfirm = null;
        this.onCancel = null;
    }

    /**
     * Exibe o modal de confirmação
     * @param {Object} options - Opções do modal
     * @param {string} options.title - Título do modal
     * @param {string} options.message - Mensagem principal
     * @param {string} options.icon - Emoji do ícone
     * @param {string} options.confirmText - Texto do botão confirmar
     * @param {string} options.cancelText - Texto do botão cancelar
     * @param {string} options.confirmStyle - 'danger' | 'success' (controla cor do botão)
     * @param {Function} onConfirm - Callback ao confirmar
     * @param {Function} onCancel - Callback ao cancelar
     */
    show(options, onConfirm, onCancel) {
        this.onConfirm = onConfirm;
        this.onCancel = onCancel;

        const {
            title = 'Confirmação',
            message = 'Deseja continuar?',
            icon = '⚠️',
            confirmText = 'Confirmar',
            cancelText = 'Cancelar',
            confirmStyle = 'danger' // 'danger' (vermelho) ou 'success' (verde)
        } = options;

        // Usar EXATAMENTE as mesmas classes do DraftModal
        this.container.innerHTML = `
            <div class="draft-modal-overlay">
                <div class="draft-modal">
                    <div class="draft-modal__header">
                        <div class="draft-modal__icon">${icon}</div>
                        <h2 class="draft-modal__title">${title}</h2>
                    </div>

                    <div class="draft-modal__preview">
                        <p style="color: #6b7280; font-size: 0.95rem; line-height: 1.6; text-align: center; margin: 0; white-space: pre-line;">
                            ${message}
                        </p>
                    </div>

                    <div class="draft-modal__actions">
                        <button class="draft-modal__btn draft-modal__btn--continue draft-modal__btn--${confirmStyle}" id="confirm-btn">
                            ${confirmText}
                        </button>
                        <button class="draft-modal__btn draft-modal__btn--discard" id="cancel-btn">
                            ${cancelText}
                        </button>
                    </div>
                </div>
            </div>
        `;

        this._bindEvents();
    }

    _bindEvents() {
        const confirmBtn = this.container.querySelector('#confirm-btn');
        const cancelBtn = this.container.querySelector('#cancel-btn');
        const overlay = this.container.querySelector('.draft-modal-overlay');

        confirmBtn.addEventListener('click', () => {
            this.hide();
            if (this.onConfirm) this.onConfirm();
        });

        cancelBtn.addEventListener('click', () => {
            this.hide();
            if (this.onCancel) this.onCancel();
        });

        // Clicar fora do modal = cancelar
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                this.hide();
                if (this.onCancel) this.onCancel();
            }
        });

        // ESC = cancelar
        this._escKeyHandler = (e) => {
            if (e.key === 'Escape') {
                this.hide();
                if (this.onCancel) this.onCancel();
            }
        };
        document.addEventListener('keydown', this._escKeyHandler);
    }

    hide() {
        this.container.innerHTML = '';
        if (this._escKeyHandler) {
            document.removeEventListener('keydown', this._escKeyHandler);
            this._escKeyHandler = null;
        }
    }
}
