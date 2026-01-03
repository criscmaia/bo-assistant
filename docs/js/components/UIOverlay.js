/**
 * UIOverlay - Componente unificado para overlays e toasts
 *
 * Substitui CSS inline duplicado e lógica repetida em:
 * - BOApp.js (_showLoading, _hideLoading, _showWarning)
 * - SectionContainer.js (_showGeneratingTextOverlay, _hideGeneratingTextOverlay)
 *
 * Uso:
 *   // Loading overlay
 *   UIOverlay.showLoading('Carregando...');
 *   UIOverlay.hideLoading();
 *
 *   // Generating text overlay
 *   UIOverlay.showGenerating('Gerando texto...');
 *   UIOverlay.hideGenerating();
 *
 *   // Toast notifications
 *   UIOverlay.toast('Mensagem', 'warning'); // warning, error, success, info
 *
 * v0.13.2+: Centralizado para manutenibilidade
 */
class UIOverlay {
    // IDs dos overlays (para evitar duplicação)
    static LOADING_ID = 'ui-overlay-loading';
    static GENERATING_ID = 'ui-overlay-generating';

    /**
     * Mostra overlay de loading (app-wide)
     * @param {string} message - Mensagem a exibir
     */
    static showLoading(message = 'Carregando...') {
        this._showOverlay(this.LOADING_ID, message, 'loading');
    }

    /**
     * Esconde overlay de loading
     */
    static hideLoading() {
        this._hideOverlay(this.LOADING_ID);
    }

    /**
     * Mostra overlay de "Gerando texto..." (durante geração de seção)
     * @param {string} message - Mensagem a exibir
     */
    static showGenerating(message = 'Seção finalizada com sucesso!<br>Gerando texto...') {
        this._showOverlay(this.GENERATING_ID, message, 'generating');
    }

    /**
     * Esconde overlay de "Gerando texto..."
     */
    static hideGenerating() {
        this._hideOverlay(this.GENERATING_ID);
    }

    /**
     * Mostra toast notification
     * @param {string} message - Mensagem a exibir
     * @param {string} type - Tipo: 'warning', 'error', 'success', 'info'
     * @param {number} duration - Duração em ms (default: 5000)
     */
    static toast(message, type = 'warning', duration = 5000) {
        // Remover toast anterior do mesmo tipo se existir
        const existingToast = document.querySelector(`.ui-toast--${type}`);
        if (existingToast) {
            existingToast.remove();
        }

        const toast = document.createElement('div');
        toast.className = `ui-toast ui-toast--${type}`;
        toast.innerHTML = this._getToastIcon(type) + ' ' + message;

        document.body.appendChild(toast);

        // Auto-remover após duração
        setTimeout(() => {
            toast.classList.add('ui-toast--closing');
            setTimeout(() => toast.remove(), 300);
        }, duration);

        return toast;
    }

    /**
     * Mostra toast de warning (atalho)
     * @param {string} message - Mensagem
     */
    static warning(message) {
        return this.toast(message, 'warning');
    }

    /**
     * Mostra toast de erro (atalho)
     * @param {string} message - Mensagem
     */
    static error(message) {
        return this.toast(message, 'error');
    }

    /**
     * Mostra toast de sucesso (atalho)
     * @param {string} message - Mensagem
     */
    static success(message) {
        return this.toast(message, 'success');
    }

    // ============================================================================
    // PRIVATE METHODS
    // ============================================================================

    /**
     * Mostra overlay genérico
     * @private
     */
    static _showOverlay(id, message, type) {
        // Remover existente se houver
        this._hideOverlay(id);

        const overlay = document.createElement('div');
        overlay.id = id;
        overlay.className = `ui-overlay ui-overlay--${type}`;
        overlay.innerHTML = `
            <div class="ui-overlay__content">
                <div class="ui-overlay__spinner"></div>
                <div class="ui-overlay__message">${message}</div>
            </div>
        `;

        document.body.appendChild(overlay);
        console.log(`[UIOverlay] ${type} overlay exibido: "${message.replace(/<br>/g, ' ')}"`);
    }

    /**
     * Esconde overlay genérico
     * @private
     */
    static _hideOverlay(id) {
        const overlay = document.getElementById(id);
        if (overlay) {
            overlay.classList.add('ui-overlay--closing');
            setTimeout(() => {
                overlay.remove();
                console.log(`[UIOverlay] Overlay ${id} removido`);
            }, 200);
        }
    }

    /**
     * Retorna ícone do toast baseado no tipo
     * @private
     */
    static _getToastIcon(type) {
        const icons = {
            warning: '⚠️',
            error: '❌',
            success: '✅',
            info: 'ℹ️'
        };
        return icons[type] || '';
    }

    /**
     * Atualiza mensagem de um overlay existente
     * @param {string} id - ID do overlay
     * @param {string} message - Nova mensagem
     */
    static updateMessage(id, message) {
        const overlay = document.getElementById(id);
        if (overlay) {
            const messageEl = overlay.querySelector('.ui-overlay__message');
            if (messageEl) {
                messageEl.innerHTML = message;
            }
        }
    }

    /**
     * Verifica se um overlay está visível
     * @param {string} id - ID do overlay
     * @returns {boolean}
     */
    static isVisible(id) {
        return document.getElementById(id) !== null;
    }
}

// Exportar para uso global
if (typeof window !== 'undefined') {
    window.UIOverlay = UIOverlay;
}

// Exportar para módulos ES6
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UIOverlay;
}
