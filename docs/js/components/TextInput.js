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
        this.defaultValue = options.defaultValue || null;
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
            <div class="text-input__error" style="display: none;"></div>
            <div class="text-input">
                <input
                    type="text"
                    class="text-input__field"
                    placeholder="${this.placeholder}"
                    value="${this.defaultValue || ''}"
                >
                <button type="button" class="text-input__button">
                    Enviar
                </button>
            </div>
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

        // Required Keywords - Intelligent validation
        if (this.validation.requiredKeywords && this.validation.requiredKeywords.length > 0) {
            const lowerValue = trimmed.toLowerCase();
            const keywords = this.validation.requiredKeywords;

            // Detectar padrão de localização (rua + numero + bairro)
            const isLocationPattern = keywords.some(k => ['rua', 'numero', 'bairro'].includes(k.toLowerCase()));

            if (isLocationPattern) {
                // Validação de localização: TODOS os keywords devem estar presentes com variações de regex
                const patterns = {
                    rua: /(rua|avenida|travessa|alameda|via|rodovia|estrada|praça|largo)/i,
                    numero: /n[úu]mero|n[°º]|nº|número|num\.|no\s+\d+|\d+/i,
                    bairro: /bairro|região|setor|quadra|vila/i
                };

                const missingPatterns = [];
                for (const [key, pattern] of Object.entries(patterns)) {
                    if (!pattern.test(lowerValue)) {
                        missingPatterns.push(key);
                    }
                }

                if (missingPatterns.length > 0) {
                    return {
                        valid: false,
                        error: this.validation.errorMessage || `Informe endereço completo (rua, número e bairro).`
                    };
                }
            }
            // Detectar padrão de prefixo/viatura
            else if (keywords.some(k => ['prefixo', 'viatura'].includes(k.toLowerCase()))) {
                // Pelo menos UM keyword deve estar presente
                const hasAtLeastOne = keywords.some(k => lowerValue.includes(k.toLowerCase()));
                if (!hasAtLeastOne) {
                    return {
                        valid: false,
                        error: this.validation.errorMessage || 'Informe prefixo ou viatura.'
                    };
                }
            }
            // Detectar padrão de graduação militar
            else if (keywords.some(k => ['sargento', 'soldado', 'cabo', 'tenente', 'capitão'].includes(k.toLowerCase()))) {
                // Pelo menos UM keyword deve estar presente
                const hasAtLeastOne = keywords.some(k => lowerValue.includes(k.toLowerCase()));
                if (!hasAtLeastOne) {
                    return {
                        valid: false,
                        error: this.validation.errorMessage || 'Informe a graduação militar.'
                    };
                }
            }
            // Padrão genérico: TODOS keywords obrigatórios
            else {
                const missingKeywords = keywords.filter(k => !lowerValue.includes(k.toLowerCase()));
                if (missingKeywords.length > 0) {
                    return {
                        valid: false,
                        error: this.validation.errorMessage || `Palavras obrigatórias: ${missingKeywords.join(', ')}`
                    };
                }
            }
        }

        // Mercosul Plate Pattern
        if (this.validation.pattern === 'mercosul_plate') {
            const mercosulPattern = /[A-Z]{3}[-\s]?[0-9][A-Z][0-9]{2}/i;
            if (!mercosulPattern.test(trimmed)) {
                return {
                    valid: false,
                    error: 'Placa inválida. Use formato Mercosul: ABC-1D23'
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
            // NÃO limpar input - deixar usuário corrigir o erro
            return;
        }

        this._clearError();

        // Limpar input IMEDIATAMENTE após validação bem-sucedida
        const originalValue = value;
        this.inputField.value = '';

        // Callback com onError para restaurar input caso API falhe
        const onError = () => {
            if (this.inputField) {
                this.inputField.value = originalValue;
            }
        };

        this.onSubmit(trimmed, onError);
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
