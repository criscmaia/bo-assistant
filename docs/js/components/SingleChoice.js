/**
 * SingleChoice - Componente de Escolha Única
 * BO Inteligente v1.0
 */

// ============================================
// CLASSE SINGLECHOICE - SELEÇÃO ÚNICA
// ============================================

class SingleChoice {
    /**
     * Componente de seleção única com botões
     */
    constructor(options = {}) {
        this.options = options.options || [
            { value: 'sim', label: 'SIM' },
            { value: 'nao', label: 'NÃO' }
        ];
        this.onSelect = options.onSelect || (() => {});

        this.element = null;
        this.selectedValue = null;
    }

    /**
     * Renderiza o componente e retorna o elemento
     */
    render() {
        this.element = document.createElement('div');
        this.element.className = 'input-component';

        const optionsHtml = this.options.map(opt => {
            // Determinar classe especial
            let specialClass = '';
            const labelUpper = opt.label.toUpperCase();

            if (labelUpper === 'SIM' || labelUpper === 'YES') {
                specialClass = 'single-choice__option--yes';
            } else if (labelUpper === 'NÃO' || labelUpper === 'NAO' || labelUpper === 'NO') {
                specialClass = 'single-choice__option--no';
            }

            // Determinar ícone
            let icon = '';
            if (labelUpper === 'SIM' || labelUpper === 'YES') {
                icon = '<span class="single-choice__icon">✅</span>';
            } else if (labelUpper === 'NÃO' || labelUpper === 'NAO' || labelUpper === 'NO') {
                icon = '<span class="single-choice__icon">❌</span>';
            }

            return `
                <button
                    type="button"
                    class="single-choice__option ${specialClass}"
                    data-value="${opt.value}"
                >
                    ${icon}
                    <span>${opt.label}</span>
                </button>
            `;
        }).join('');

        this.element.innerHTML = `
            <div class="single-choice">
                ${optionsHtml}
            </div>
        `;

        // Eventos
        const buttons = this.element.querySelectorAll('.single-choice__option');
        buttons.forEach(btn => {
            btn.addEventListener('click', () => {
                const value = btn.dataset.value;
                this._handleSelect(value, btn);
            });
        });

        return this.element;
    }

    /**
     * Trata a seleção
     */
    _handleSelect(value, buttonEl) {
        // Proteção contra clique duplo
        if (this.isSelecting) return;
        this.isSelecting = true;

        // Remover seleção anterior
        const allButtons = this.element.querySelectorAll('.single-choice__option');
        allButtons.forEach(btn => btn.classList.remove('single-choice__option--selected'));

        // Marcar como selecionado
        buttonEl.classList.add('single-choice__option--selected');
        this.selectedValue = value;

        // Encontrar o label correspondente
        const option = this.options.find(o => o.value === value);
        const label = option ? option.label : value;

        // Callback após pequeno delay (para ver a animação)
        this.isSelecting = false;
        setTimeout(() => {
            this.onSelect(value, label, option);
        }, 150);
    }

    /**
     * Retorna valor selecionado
     */
    getValue() {
        return this.selectedValue;
    }

    /**
     * Desabilita todas as opções
     */
    disable() {
        const buttons = this.element?.querySelectorAll('.single-choice__option');
        buttons?.forEach(btn => {
            btn.disabled = true;
            btn.style.pointerEvents = 'none';
            btn.style.opacity = '0.6';
        });
    }
}

// ============================================
// FIM CLASSE SINGLECHOICE
// ============================================
