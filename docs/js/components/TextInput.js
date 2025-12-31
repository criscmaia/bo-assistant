/**
 * TextInput - Componente de Input de Texto
 * BO Inteligente v1.0
 */

// ============================================
// CLASSE TEXTINPUT - INPUT DE TEXTO
// ============================================

class TextInput {
    /**
     * Componente de input de texto com validação
     */
    constructor(options = {}) {
        this.placeholder = options.placeholder || 'Digite sua resposta...';
        this.hint = options.hint || null;
        this.validation = options.validation || {};
        this.onSubmit = options.onSubmit || (() => {});

        this.element = null;
        this.inputField = null;
        this.errorEl = null;
        this.isValid = true;
    }

    /**
     * Renderiza o componente e retorna o elemento
     */
    render() {
        this.element = document.createElement('div');
        this.element.className = 'input-component';

        this.element.innerHTML = `
            <div class="text-input">
                <input
                    type="text"
                    class="text-input__field"
                    placeholder="${this.placeholder}"
                >
                <button type="button" class="text-input__button">
                    Enviar
                </button>
            </div>
            <div class="text-input__error" style="display: none;"></div>
        `;

        this.inputField = this.element.querySelector('.text-input__field');
        this.errorEl = this.element.querySelector('.text-input__error');
        const button = this.element.querySelector('.text-input__button');

        // Eventos
        button.addEventListener('click', () => this._handleSubmit());
        this.inputField.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this._handleSubmit();
        });
        this.inputField.addEventListener('input', () => this._clearError());

        // Auto-focus após render
        requestAnimationFrame(() => {
            const field = this.element.querySelector('.text-input__field');
            if (field) field.focus();
        });

        return this.element;
    }

    /**
     * Foca no input
     */
    focus() {
        if (this.inputField) {
            setTimeout(() => this.inputField.focus(), 100);
        }
    }

    /**
     * Limpa o input
     */
    clear() {
        if (this.inputField) {
            this.inputField.value = '';
        }
        this._clearError();
    }

    /**
     * Valida o valor
     */
    validate(value) {
        const trimmed = value.trim();

        // Required
        if (this.validation.required && !trimmed) {
            return { valid: false, error: 'Este campo é obrigatório.' };
        }

        // Min length
        if (this.validation.minLength && trimmed.length < this.validation.minLength) {
            return {
                valid: false,
                error: `Mínimo de ${this.validation.minLength} caracteres.`
            };
        }

        // Pattern (datetime)
        if (this.validation.pattern === 'datetime') {
            const hasDate = /\d{1,2}\/\d{1,2}/.test(trimmed) ||
                           /(janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)/i.test(trimmed);
            const hasTime = /\d{1,2}[h:]\d{0,2}/.test(trimmed);

            if (!hasDate || !hasTime) {
                return {
                    valid: false,
                    error: 'Informe data e hora. Ex: 22/03/2025, às 19h03'
                };
            }
        }

        return { valid: true };
    }

    /**
     * Trata o envio
     */
    _handleSubmit() {
        if (!this.inputField) return;

        const value = this.inputField.value;
        const trimmed = value.trim();

        // Validar resposta não vazia
        if (!trimmed || trimmed.length === 0) {
            DEBUG.warn('TextInput', 'Resposta vazia ignorada');
            return;
        }

        const validation = this.validate(value);

        if (!validation.valid) {
            this._showError(validation.error);
            return;
        }

        this._clearError();
        this.onSubmit(trimmed);
    }

    /**
     * Mostra erro
     */
    _showError(message) {
        if (this.errorEl) {
            this.errorEl.textContent = message;
            this.errorEl.style.display = 'flex';
        }
        if (this.inputField) {
            this.inputField.classList.add('text-input__field--error');
        }
        this.isValid = false;
    }

    /**
     * Limpa erro
     */
    _clearError() {
        if (this.errorEl) {
            this.errorEl.style.display = 'none';
        }
        if (this.inputField) {
            this.inputField.classList.remove('text-input__field--error');
        }
        this.isValid = true;
    }

    /**
     * Desabilita o input
     */
    disable() {
        if (this.inputField) {
            this.inputField.disabled = true;
        }
        const button = this.element?.querySelector('.text-input__button');
        if (button) {
            button.disabled = true;
        }
    }

    /**
     * Habilita o input
     */
    enable() {
        if (this.inputField) {
            this.inputField.disabled = false;
        }
        const button = this.element?.querySelector('.text-input__button');
        if (button) {
            button.disabled = false;
        }
    }
}

// ============================================
// FIM CLASSE TEXTINPUT
// ============================================
