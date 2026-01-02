# 💬 FASE 3: Componentes de Input

**Projeto:** BO Inteligente - Redesign UX  
**Fase:** 3 de 8  
**Modelo recomendado:** 🟢 Haiku  
**Tempo estimado:** 2-3 horas  
**Dependências:** Fase 2 concluída (SectionContainer funcionando)

---

## 📋 Contexto

### O que foi feito nas fases anteriores?
- **Fase 0:** Branch criada, `sections.js` com 8 seções e ~53 perguntas
- **Fase 1:** Componente `ProgressBar` com estados visuais e navegação
- **Fase 2:** Componente `SectionContainer` com chat, input básico e transições

### O que será feito nesta fase?
Criar **3 componentes de input especializados** que substituem o input de texto genérico:

1. **TextInput** - Campo de texto livre (já existe básico, será melhorado)
2. **SingleChoice** - Botões para seleção única (SIM/NÃO, opções exclusivas)
3. **MultipleChoice** - Checkboxes para seleção múltipla

### Por que componentes separados?
O `sections.js` define `inputType` para cada pergunta:
- `"text"` → TextInput
- `"single_choice"` → SingleChoice  
- `"multiple_choice"` → MultipleChoice

Isso permite uma UX mais rica e intuitiva, onde o usuário não precisa digitar "SIM" ou "NÃO" - basta clicar em botões.

### Wireframes de referência

**TextInput:**
```
┌─────────────────────────────────────────────────────────────────┐
│  📝 Digite sua resposta...                         [Enviar]    │
└─────────────────────────────────────────────────────────────────┘
```

**SingleChoice:**
```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   ┌──────────────────┐    ┌──────────────────┐                 │
│   │     ✅ SIM       │    │     ❌ NÃO       │                 │
│   └──────────────────┘    └──────────────────┘                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**MultipleChoice:**
```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   ☑️ Denúncia anônima                                          │
│   ☑️ Observação durante campana                                │
│   ☐ Atitude do suspeito                                        │
│   ☐ Local conhecido de tráfico                                 │
│                                                                 │
│                              [Confirmar seleção]               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Objetivo

Adicionar ao `index.html`:
1. CSS para os 3 componentes de input
2. Classes JavaScript: `TextInput`, `SingleChoice`, `MultipleChoice`
3. Modificar `SectionContainer` para usar o componente correto baseado no `inputType`

---

## 📁 Arquivo a Modificar

`docs/index.html`

---

## ✅ Tarefas

### Tarefa 3.1: Adicionar CSS dos componentes de input

**Objetivo:** Estilizar os 3 tipos de input.

**Localização:** Dentro da tag `<style>`, APÓS os estilos do SectionContainer.

**Encontre o comentário:**
```css
        /* ============================================ */
        /* FIM CONTAINER DE SEÇÃO - ESTILOS */
        /* ============================================ */
```

**Adicione DEPOIS:**

```css
        
        /* ============================================ */
        /* COMPONENTES DE INPUT - ESTILOS */
        /* ============================================ */
        
        /* Container genérico de input */
        .input-component {
            padding: 16px 20px;
            border-top: 1px solid #e5e7eb;
            background: #f8fafc;
        }
        
        /* -------------------------------------------- */
        /* TEXT INPUT */
        /* -------------------------------------------- */
        
        .text-input {
            display: flex;
            gap: 12px;
        }
        
        .text-input__field {
            flex: 1;
            padding: 14px 18px;
            border: 2px solid #e5e7eb;
            border-radius: 12px;
            font-size: 15px;
            transition: all 0.2s ease;
            background: white;
        }
        
        .text-input__field:focus {
            outline: none;
            border-color: #3b82f6;
            box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
        }
        
        .text-input__field::placeholder {
            color: #9ca3af;
        }
        
        .text-input__field--error {
            border-color: #ef4444;
            background-color: #fef2f2;
        }
        
        .text-input__field--error:focus {
            box-shadow: 0 0 0 4px rgba(239, 68, 68, 0.1);
        }
        
        .text-input__button {
            padding: 14px 28px;
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-weight: 600;
            font-size: 15px;
            cursor: pointer;
            transition: all 0.2s ease;
            white-space: nowrap;
        }
        
        .text-input__button:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
        }
        
        .text-input__button:active:not(:disabled) {
            transform: translateY(0);
        }
        
        .text-input__button:disabled {
            background: #d1d5db;
            cursor: not-allowed;
            transform: none;
        }
        
        .text-input__error {
            margin-top: 8px;
            padding: 8px 12px;
            background: #fef2f2;
            border: 1px solid #fecaca;
            border-radius: 8px;
            color: #dc2626;
            font-size: 13px;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        
        .text-input__error::before {
            content: '⚠️';
        }
        
        /* -------------------------------------------- */
        /* SINGLE CHOICE */
        /* -------------------------------------------- */
        
        .single-choice {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            justify-content: center;
        }
        
        .single-choice__option {
            flex: 1;
            min-width: 120px;
            max-width: 200px;
            padding: 16px 24px;
            background: white;
            border: 3px solid #e5e7eb;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        
        .single-choice__option:hover {
            border-color: #3b82f6;
            background: #eff6ff;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
        }
        
        .single-choice__option:active {
            transform: translateY(0);
        }
        
        .single-choice__option--selected {
            border-color: #10b981;
            background: #d1fae5;
            color: #065f46;
        }
        
        .single-choice__option--yes {
            border-color: #10b981;
        }
        
        .single-choice__option--yes:hover {
            background: #d1fae5;
            border-color: #059669;
        }
        
        .single-choice__option--no {
            border-color: #f87171;
        }
        
        .single-choice__option--no:hover {
            background: #fee2e2;
            border-color: #ef4444;
        }
        
        .single-choice__option--primary {
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            color: white;
            border-color: transparent;
        }
        
        .single-choice__option--primary:hover {
            background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
        }
        
        .single-choice__icon {
            font-size: 20px;
        }
        
        /* -------------------------------------------- */
        /* MULTIPLE CHOICE */
        /* -------------------------------------------- */
        
        .multiple-choice {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        .multiple-choice__options {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        
        .multiple-choice__option {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 14px 18px;
            background: white;
            border: 2px solid #e5e7eb;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .multiple-choice__option:hover {
            border-color: #3b82f6;
            background: #f8fafc;
        }
        
        .multiple-choice__option--selected {
            border-color: #3b82f6;
            background: #eff6ff;
        }
        
        .multiple-choice__checkbox {
            width: 24px;
            height: 24px;
            border: 2px solid #d1d5db;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
            flex-shrink: 0;
        }
        
        .multiple-choice__option--selected .multiple-choice__checkbox {
            background: #3b82f6;
            border-color: #3b82f6;
        }
        
        .multiple-choice__checkmark {
            color: white;
            font-size: 14px;
            opacity: 0;
            transform: scale(0);
            transition: all 0.2s ease;
        }
        
        .multiple-choice__option--selected .multiple-choice__checkmark {
            opacity: 1;
            transform: scale(1);
        }
        
        .multiple-choice__label {
            font-size: 15px;
            color: #374151;
            flex: 1;
        }
        
        .multiple-choice__option--selected .multiple-choice__label {
            color: #1e40af;
            font-weight: 500;
        }
        
        .multiple-choice__confirm {
            margin-top: 12px;
            padding: 14px 24px;
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        
        .multiple-choice__confirm:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
        }
        
        .multiple-choice__confirm:disabled {
            background: #d1d5db;
            cursor: not-allowed;
            transform: none;
        }
        
        .multiple-choice__hint {
            margin-top: 8px;
            font-size: 13px;
            color: #6b7280;
            text-align: center;
        }
        
        /* -------------------------------------------- */
        /* RESPONSIVIDADE */
        /* -------------------------------------------- */
        
        @media (max-width: 768px) {
            .input-component {
                padding: 12px 16px;
            }
            
            .text-input {
                flex-direction: column;
            }
            
            .text-input__button {
                width: 100%;
            }
            
            .single-choice {
                flex-direction: column;
            }
            
            .single-choice__option {
                max-width: none;
                width: 100%;
            }
            
            .multiple-choice__option {
                padding: 12px 14px;
            }
            
            .multiple-choice__checkbox {
                width: 22px;
                height: 22px;
            }
        }
        
        /* ============================================ */
        /* FIM COMPONENTES DE INPUT - ESTILOS */
        /* ============================================ */
```

---

### Tarefa 3.2: Criar classe TextInput

**Objetivo:** Componentizar o input de texto com validação.

**Localização:** Dentro da tag `<script>`, APÓS a classe `SectionContainer`.

**Encontre o comentário:**
```javascript
        // ============================================
        // FIM CLASSE SECTIONCONTAINER
        // ============================================
```

**Adicione DEPOIS:**

```javascript
        
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
                const validation = this.validate(value);
                
                if (!validation.valid) {
                    this._showError(validation.error);
                    return;
                }
                
                this._clearError();
                this.onSubmit(value.trim());
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
        
```

---

### Tarefa 3.3: Criar classe SingleChoice

**Objetivo:** Criar componente de seleção única com botões.

**Localização:** Logo após a classe TextInput.

**Adicione:**

```javascript
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
        
```

---

### Tarefa 3.4: Criar classe MultipleChoice

**Objetivo:** Criar componente de seleção múltipla com checkboxes.

**Localização:** Logo após a classe SingleChoice.

**Adicione:**

```javascript
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
        
```

---

### Tarefa 3.5: Modificar SectionContainer para usar os componentes

**Objetivo:** Integrar os novos componentes ao SectionContainer.

**Localização:** Dentro da classe `SectionContainer`, modificar os métodos relevantes.

#### 3.5.1: Adicionar método para criar input correto

**Encontre o método `_bindEvents()` na classe SectionContainer.**

**Adicione ANTES de `_bindEvents()`:**

```javascript
            /**
             * Cria o componente de input correto baseado na pergunta
             */
            _createInputComponent(question) {
                const inputType = question.inputType || 'text';
                
                switch (inputType) {
                    case 'single_choice':
                        return new SingleChoice({
                            options: question.options || [
                                { value: 'sim', label: 'SIM' },
                                { value: 'nao', label: 'NÃO' }
                            ],
                            onSelect: (value, label, option) => {
                                this._handleInputSubmit(label, question, option);
                            }
                        });
                    
                    case 'multiple_choice':
                        return new MultipleChoice({
                            options: question.options || [],
                            minSelections: question.validation?.minSelections || 1,
                            maxSelections: question.validation?.maxSelections || null,
                            onConfirm: (values, labels) => {
                                this._handleInputSubmit(labels.join(', '), question);
                            }
                        });
                    
                    case 'text':
                    default:
                        return new TextInput({
                            placeholder: question.hint || 'Digite sua resposta...',
                            validation: question.validation || {},
                            onSubmit: (value) => {
                                this._handleInputSubmit(value, question);
                            }
                        });
                }
            }
            
            /**
             * Trata resposta do componente de input
             */
            _handleInputSubmit(answer, question, option = null) {
                // Verificar se deve pular seção (para skipQuestion)
                if (option?.skipsSection) {
                    this._addUserMessage(answer);
                    setTimeout(() => {
                        this._skipSection();
                    }, 300);
                    return;
                }
                
                // Adicionar mensagem do usuário
                this._addUserMessage(answer);
                
                // Salvar resposta
                this.answers[question.id] = answer;
                this.onAnswer(question.id, answer);
                
                // Verificar follow-up
                if (question.followUp && question.followUp.condition) {
                    const conditionMet = answer.toLowerCase().includes(question.followUp.condition.toLowerCase());
                    if (conditionMet && question.followUp.question) {
                        // Mostrar follow-up
                        setTimeout(() => {
                            this._showQuestion(question.followUp.question);
                        }, 500);
                        return;
                    }
                }
                
                // Avançar para próxima pergunta
                this.currentQuestionIndex++;
                this._updateBadge();
                
                setTimeout(() => {
                    this._showCurrentQuestion();
                }, 500);
            }
            
            /**
             * Mostra uma pergunta específica com o input correto
             */
            _showQuestion(question) {
                // Adicionar mensagem do bot
                this._addBotMessage(question.text, question.hint);
                
                // Renderizar input correto
                this._renderInput(question);
            }
            
            /**
             * Renderiza o input na área de input
             */
            _renderInput(question) {
                // Remover input anterior
                const inputArea = this.container.querySelector('#section-input-area');
                if (inputArea) {
                    inputArea.innerHTML = '';
                    
                    // Criar novo componente
                    this.currentInputComponent = this._createInputComponent(question);
                    const inputEl = this.currentInputComponent.render();
                    inputArea.appendChild(inputEl);
                    
                    // Focar se for TextInput
                    if (this.currentInputComponent instanceof TextInput) {
                        this.currentInputComponent.focus();
                    }
                }
            }
            
```

#### 3.5.2: Modificar o método `render()` para usar área de input dinâmica

**Encontre no método `render()` da classe SectionContainer a parte do HTML que gera o input:**

```javascript
                    <!-- Input (oculto se readonly ou completed) -->
                    ${!this.isReadOnly && this.state === 'in_progress' ? `
                    <div class="section-input" id="section-input">
                        <div class="section-input__form">
                            <input 
                                type="text" 
                                id="section-input-field"
                                class="section-input__field" 
                                placeholder="Digite sua resposta..."
                            >
                            <button 
                                type="button" 
                                id="section-input-btn"
                                class="section-input__button"
                            >
                                Enviar
                            </button>
                        </div>
                    </div>
                    ` : ''}
```

**Substitua por:**

```javascript
                    <!-- Área de Input Dinâmica -->
                    ${!this.isReadOnly && this.state === 'in_progress' ? `
                    <div id="section-input-area">
                        <!-- Input será renderizado pelo _renderInput() -->
                    </div>
                    ` : ''}
```

#### 3.5.3: Modificar o método `_showCurrentQuestion()` para usar os novos métodos

**Encontre o método `_showCurrentQuestion()` e substitua por:**

```javascript
            /**
             * Mostra a pergunta atual
             */
            _showCurrentQuestion() {
                if (!this.sectionData) return;
                
                const questions = this.sectionData.questions;
                
                // Verificar se tem skipQuestion primeiro
                if (this.sectionData.skipQuestion && this.currentQuestionIndex === 0 && !this.answers[this.sectionData.skipQuestion.id]) {
                    const skipQ = this.sectionData.skipQuestion;
                    this._showQuestion(skipQ);
                    return;
                }
                
                // Calcular índice real (considerando skipQuestion)
                const realIndex = this.sectionData.skipQuestion ? this.currentQuestionIndex - 1 : this.currentQuestionIndex;
                
                if (realIndex >= 0 && realIndex < questions.length) {
                    const question = questions[realIndex];
                    this._showQuestion(question);
                } else if (realIndex >= questions.length) {
                    // Todas as perguntas respondidas
                    this._completeSection();
                }
            }
```

#### 3.5.4: Remover/Comentar o método `_handleSubmit()` antigo e `_bindEvents()` relacionados ao input antigo

**Encontre o método `_handleSubmit()` na classe SectionContainer.**

**Comente ou delete o método, pois não será mais usado (os novos componentes têm seus próprios handlers).**

**No método `_bindEvents()`, remova ou comente as linhas que fazem binding do input antigo:**

```javascript
            _bindEvents() {
                // REMOVER ESTAS LINHAS:
                // const inputBtn = this.container.querySelector('#section-input-btn');
                // if (inputBtn) {
                //     inputBtn.addEventListener('click', () => this._handleSubmit());
                // }
                // 
                // if (this.inputFieldEl) {
                //     this.inputFieldEl.addEventListener('keypress', (e) => {
                //         if (e.key === 'Enter') this._handleSubmit();
                //     });
                //     setTimeout(() => this.inputFieldEl.focus(), 100);
                // }
                
                // MANTER O RESTO (copiar, transição, back)...
```

---

### Tarefa 3.6: Testar no navegador

**Objetivo:** Verificar se os componentes funcionam corretamente.

**Passos:**

1. Iniciar servidor local:
```bash
cd docs
python -m http.server 3000
```

2. Abrir `http://localhost:3000` no navegador

3. **Testar TextInput (Seção 1, pergunta 1.1):**
   - [ ] Input de texto aparece
   - [ ] Placeholder está correto
   - [ ] Digitar resposta e pressionar Enter funciona
   - [ ] Clicar em "Enviar" funciona
   - [ ] Validação funciona (tentar enviar vazio)

4. **Testar SingleChoice (Seção 1, pergunta 1.7 ou Seção 2, pergunta 2.0):**
   - [ ] Botões SIM/NÃO aparecem
   - [ ] Hover muda a cor
   - [ ] Clique seleciona e envia
   - [ ] Ícones ✅ e ❌ aparecem

5. **Testar MultipleChoice (Seção 5, pergunta 5.1):**
   - [ ] Checkboxes aparecem
   - [ ] Clique marca/desmarca
   - [ ] Botão "Confirmar" só habilita com seleção mínima
   - [ ] Contador de selecionados aparece

6. **Verificar no console (F12):**
```javascript
// Ver componente atual
sectionContainer.currentInputComponent

// Navegar para seção com SingleChoice
navigateToSection(2)  // Seção 2 tem skipQuestion com SIM/NÃO

// Navegar para seção com MultipleChoice
navigateToSection(5)  // Seção 5 tem multiple choice
```

7. **Verificar responsividade:**
   - Botões devem empilhar em mobile
   - Checkboxes devem continuar usáveis

---

### Tarefa 3.7: Commit da Fase 3

**Objetivo:** Salvar o progresso.

**Comandos:**
```bash
cd /caminho/para/bo-assistant
git add .
git status

git commit -m "feat: implementar componentes de input (Fase 3)

- Criar TextInput com validação
- Criar SingleChoice com botões SIM/NÃO
- Criar MultipleChoice com checkboxes
- Integrar componentes ao SectionContainer
- Renderização dinâmica baseada em inputType
- Suporte a follow-up questions
- CSS responsivo para todos os componentes"

git push
```

---

## ✅ Checklist Final da Fase 3

Antes de prosseguir para a Fase 4, confirme:

- [ ] CSS dos 3 componentes adicionado
- [ ] Classe TextInput implementada com validação
- [ ] Classe SingleChoice implementada com botões
- [ ] Classe MultipleChoice implementada com checkboxes
- [ ] SectionContainer modificado para usar componentes
- [ ] TextInput funciona (Seção 1)
- [ ] SingleChoice funciona (botões SIM/NÃO)
- [ ] MultipleChoice funciona (checkboxes)
- [ ] Follow-up questions funcionam
- [ ] Responsivo em mobile
- [ ] Commit feito e pushado

---

## 🐛 Troubleshooting

### Componentes não aparecem
- Verificar se `_renderInput()` está sendo chamado
- Verificar se `#section-input-area` existe no HTML
- Verificar console por erros

### SingleChoice não responde ao clique
- Verificar se o event listener foi adicionado
- Verificar se `onSelect` callback está definido

### MultipleChoice não confirma
- Verificar se `minSelections` está correto
- Verificar se botão está sendo habilitado

### Validação não funciona
- Verificar objeto `validation` na pergunta do `sections.js`
- Verificar método `validate()` do TextInput

### Erro "TextInput/SingleChoice/MultipleChoice is not defined"
- Verificar se as classes foram adicionadas ANTES de serem usadas
- Verificar ordem das classes no arquivo

---

## ⏭️ Próxima Fase

**Fase 4: Fluxo de Navegação**
- Modelo: 🟡 **Sonnet** (integração complexa)
- Arquivo: `FASE_4_FLUXO_NAVEGACAO.md`
- Objetivo: Integrar com API real, gerenciar estado global, navegação completa

---

## 📚 Referências

Arquivos na pasta `redesign/`:
- `PROPOSTA_REDESIGN_UX_BO_INTELIGENTE.md` - Seção "Componentes de Input"
- `PLANO_IMPLEMENTACAO_REDESIGN_UX.md` - Fase 3 detalhada
- `sections.js` - Estrutura das perguntas com `inputType`

---

*Documento gerado em 31/12/2025*  
*Para execução com Claude Haiku*
