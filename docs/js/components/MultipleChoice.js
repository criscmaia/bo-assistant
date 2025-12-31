/**
 * MultipleChoice - Componente de Múltipla Escolha
 * BO Inteligente v1.0
 */

// ============================================
// CLASSE MULTIPLECHOICE - SELEÇÃO MÚLTIPLA
// ============================================

class MultipleChoice {
    /**
     * Componente de seleção múltipla com checkboxes
     */
    constructor(options = {}) {
        this.options = options.options || [];
        this.minSelections = options.minSelections || 1;
        this.maxSelections = options.maxSelections || null;
        this.onConfirm = options.onConfirm || (() => {});

        this.element = null;
        this.selectedValues = new Set();
    }

    /**
     * Renderiza o componente e retorna o elemento
     */
    render() {
        this.element = document.createElement('div');
        this.element.className = 'input-component';

        const optionsHtml = this.options.map(opt => `
            <div class="multiple-choice__option" data-value="${opt.value}">
                <div class="multiple-choice__checkbox">
                    <span class="multiple-choice__checkmark">✓</span>
                </div>
                <span class="multiple-choice__label">${opt.label}</span>
            </div>
        `).join('');

        this.element.innerHTML = `
            <div class="multiple-choice">
                <div class="multiple-choice__options">
                    ${optionsHtml}
                </div>
                <button
                    type="button"
                    class="multiple-choice__confirm"
                    disabled
                >
                    ✓ Confirmar seleção
                </button>
                <div class="multiple-choice__hint">
                    Selecione ${this.minSelections === 1 ? 'pelo menos 1 opção' : `pelo menos ${this.minSelections} opções`}
                </div>
            </div>
        `;

        // Eventos - opções
        const optionEls = this.element.querySelectorAll('.multiple-choice__option');
        optionEls.forEach(opt => {
            opt.addEventListener('click', () => {
                const value = opt.dataset.value;
                this._toggleOption(value, opt);
            });
        });

        // Evento - confirmar
        const confirmBtn = this.element.querySelector('.multiple-choice__confirm');
        confirmBtn.addEventListener('click', () => this._handleConfirm());

        return this.element;
    }

    /**
     * Toggle de opção
     */
    _toggleOption(value, optionEl) {
        if (this.selectedValues.has(value)) {
            // Desmarcar
            this.selectedValues.delete(value);
            optionEl.classList.remove('multiple-choice__option--selected');
        } else {
            // Verificar limite máximo
            if (this.maxSelections && this.selectedValues.size >= this.maxSelections) {
                return;
            }

            // Marcar
            this.selectedValues.add(value);
            optionEl.classList.add('multiple-choice__option--selected');
        }

        this._updateConfirmButton();
    }

    /**
     * Atualiza estado do botão confirmar
     */
    _updateConfirmButton() {
        const confirmBtn = this.element?.querySelector('.multiple-choice__confirm');
        if (confirmBtn) {
            const isValid = this.selectedValues.size >= this.minSelections;
            confirmBtn.disabled = !isValid;

            // Atualizar texto
            const count = this.selectedValues.size;
            if (count === 0) {
                confirmBtn.textContent = '✓ Confirmar seleção';
            } else {
                confirmBtn.textContent = `✓ Confirmar (${count} selecionado${count > 1 ? 's' : ''})`;
            }
        }
    }

    /**
     * Trata confirmação
     */
    _handleConfirm() {
        if (this.selectedValues.size < this.minSelections) return;

        // Converter Set para Array
        const values = Array.from(this.selectedValues);

        // Encontrar labels
        const labels = values.map(v => {
            const opt = this.options.find(o => o.value === v);
            return opt ? opt.label : v;
        });

        // Callback
        this.onConfirm(values, labels);
    }

    /**
     * Retorna valores selecionados
     */
    getValues() {
        return Array.from(this.selectedValues);
    }

    /**
     * Desabilita o componente
     */
    disable() {
        const options = this.element?.querySelectorAll('.multiple-choice__option');
        options?.forEach(opt => {
            opt.style.pointerEvents = 'none';
            opt.style.opacity = '0.6';
        });

        const confirmBtn = this.element?.querySelector('.multiple-choice__confirm');
        if (confirmBtn) {
            confirmBtn.disabled = true;
        }
    }
}

// ============================================
// FIM CLASSE MULTIPLECHOICE
// ============================================
