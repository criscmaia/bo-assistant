/**
 * SectionContainer - Gerencia uma seção do BO
 * Inclui chat, input, texto gerado e transição
 * BO Inteligente v1.0
 */

class SectionContainer {
    /**
     * Componente que gerencia uma seção do BO
     * Inclui chat, input, texto gerado e transição
     */
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);

        // Dados da seção atual
        this.sectionData = options.sectionData || null;
        this.sectionId = options.sectionId || 1;

        // Estado
        this.state = 'pending'; // pending, in_progress, completed, skipped
        this.messages = []; // Histórico de mensagens do chat
        this.answers = {}; // Respostas do usuário { questionId: answer }
        this.currentQuestionIndex = 0;
        this.generatedText = null;
        this.isReadOnly = false;
        this.followUpQueue = []; // Fila de perguntas follow-up (1.5.1, 1.5.2, etc)

        // Callbacks
        this.onAnswer = options.onAnswer || ((questionId, answer) => {});
        this.onComplete = options.onComplete || ((sectionId, answers) => {});
        this.onSkip = options.onSkip || ((sectionId) => {});
        this.onNavigateNext = options.onNavigateNext || ((nextSectionId) => {});
        this.onNavigateBack = options.onNavigateBack || (() => {});

        // Elementos internos
        this.chatEl = null;
        this.inputEl = null;
        this.inputFieldEl = null;
        this.generatedEl = null;
        this.transitionEl = null;
    }

    /**
     * Carrega dados de uma seção
     *
     * options:
     *   - preAnswerSkipQuestion: Se fornecido, auto-responde o skipQuestion com este valor
     *     sem mostrar no chat (útil quando o usuário veio de um botão de transição tipo "Sim, havia veículo")
     */
    loadSection(sectionData, options = {}) {
        this.sectionData = sectionData;
        this.sectionId = sectionData.id;
        this.state = options.state || 'in_progress';
        this.messages = options.messages || [];
        this.answers = options.answers || {};
        this.currentQuestionIndex = options.currentQuestionIndex || 0;
        this.generatedText = options.generatedText || null;
        this.isReadOnly = options.isReadOnly || false;

        this.render();

        // Se não for read-only e estado é in_progress, garantir que mostra próxima pergunta
        if (!this.isReadOnly && this.state === 'in_progress') {
            if (this.messages.length === 0) {
                // Seção nova: mostrar primeira pergunta
                if (options.preAnswerSkipQuestion && this.sectionData.skipQuestion) {
                    const skipQ = this.sectionData.skipQuestion;
                    this.answers[skipQ.id] = options.preAnswerSkipQuestion;
                    this.onAnswer(skipQ.id, options.preAnswerSkipQuestion);
                    // Avançar para próxima pergunta sem mostrar no chat
                    this.currentQuestionIndex = 1; // Pular o skipQuestion
                    this._showCurrentQuestion();
                } else {
                    this._showCurrentQuestion();
                }
            } else {
                // Restaurando rascunho: mostrar próxima pergunta
                // currentQuestionIndex já está correto do estado salvo
                this._showCurrentQuestion();
            }
        }
    }

    /**
     * Renderiza o container completo
     */
    render() {
        if (!this.container || !this.sectionData) return;

        const section = this.sectionData;

        this.container.innerHTML = `
            <!-- Header da Seção -->
            <div class="section-header">
                <div class="section-header__title">
                    <span class="section-header__emoji">${section.emoji}</span>
                    <span>Seção ${section.id}: ${section.name}</span>
                </div>
                <span class="section-header__badge section-header__badge--${this.state}">
                    ${this._getStatusLabel()}
                </span>
            </div>

            <!-- Chat -->
            <div class="section-chat" id="section-chat">
                ${this._renderMessages()}
            </div>

            <!-- Área de Input Dinâmica -->
            ${!this.isReadOnly && this.state === 'in_progress' ? `
            <div id="section-input-area">
                <!-- Input será renderizado pelo _renderInput() -->
            </div>
            ` : ''}

            <!-- Texto Gerado (se completed) -->
            ${this.state === 'completed' && this.generatedText ? `
            <div class="section-generated" id="section-generated">
                <div class="section-generated__header">
                    <span class="section-generated__title">
                        📄 Texto Gerado - Seção ${section.id}
                    </span>
                    <button class="section-generated__copy" id="section-copy-btn">
                        📋 Copiar
                    </button>
                </div>
                <div class="section-generated__text">${this.generatedText}</div>
            </div>
            ` : ''}

            <!-- Transição para próxima seção (se completed e não for última) -->
            ${this.state === 'completed' && this.sectionId < 8 ? this._renderTransition() : ''}

            <!-- Aviso de modo leitura -->
            ${this.isReadOnly ? `
            <div class="section-readonly-notice">
                <span class="section-readonly-notice__text">
                    📖 Modo leitura - Esta seção já foi finalizada
                </span>
                <button class="section-readonly-notice__btn" id="section-back-btn">
                    ↩️ Voltar para seção atual
                </button>
            </div>
            ` : ''}
        `;

        // Guardar referências
        this.chatEl = this.container.querySelector('#section-chat');
        this.inputEl = this.container.querySelector('#section-input');
        this.inputFieldEl = this.container.querySelector('#section-input-field');
        this.generatedEl = this.container.querySelector('#section-generated');
        this.transitionEl = this.container.querySelector('.section-transition');

        // Bind eventos
        this._bindEvents();

        // Scroll para o final do chat
        this._scrollToBottom();
    }

    /**
     * Retorna label do status
     */
    _getStatusLabel() {
        switch (this.state) {
            case 'in_progress': return `${Object.keys(this.answers).length}/${this.sectionData.questions.length} perguntas`;
            case 'completed': return '✓ Completa';
            case 'skipped': return '⏭️ Pulada';
            default: return 'Pendente';
        }
    }

    /**
     * Renderiza mensagens do chat
     */
    _renderMessages() {
        if (this.messages.length === 0) {
            return '<div class="section-loading"><span class="section-loading__spinner"></span> Carregando...</div>';
        }

        return this.messages.map(msg => {
            if (msg.type === 'bot') {
                return `
                    <div class="chat-message chat-message--bot">
                        <div class="chat-message__bubble chat-message__bubble--bot">
                            <div class="chat-message__text">${msg.text}</div>
                            ${msg.hint ? `<div class="chat-message__hint">${msg.hint}</div>` : ''}
                        </div>
                    </div>
                `;
            } else {
                return `
                    <div class="chat-message chat-message--user">
                        <div class="chat-message__bubble chat-message__bubble--user">
                            <div class="chat-message__text">${msg.text}</div>
                        </div>
                    </div>
                `;
            }
        }).join('');
    }

    /**
     * Renderiza área de transição
     */
    _renderTransition() {
        const nextSection = window.SECTIONS_DATA ? window.SECTIONS_DATA.find(s => s.id === this.sectionId + 1) : null;

        if (!nextSection) return '';

        const canSkip = nextSection.skippable !== false;

        // Textos específicos para cada seção (contexto-aware)
        const startTexts = {
            2: 'Sim, havia veículo',
            3: 'Sim, houve campana',
            4: 'Sim, houve entrada em domicílio',
            5: 'Sim, houve fundada suspeita',
            6: 'Sim, houve resistência',
            7: 'Sim, houve apreensão',
            8: 'Iniciar Seção 8 (FINAL)'
        };

        const skipTexts = {
            2: 'Não havia veículo',
            3: 'Não houve campana',
            4: 'Não houve entrada em domicílio',
            5: 'Não houve fundada suspeita',
            6: 'Não houve resistência',
            7: 'Não houve apreensão'
        };

        const nextSectionId = nextSection.id;
        const startButtonText = startTexts[nextSectionId] || `Iniciar Seção ${nextSectionId}`;
        const skipButtonText = skipTexts[nextSectionId] || 'Pular';

        // Icon para o botão de início
        const startButtonIcon = nextSectionId === 8 ? '▶️' : '✅';

        return `
            <div class="section-transition">
                <div class="section-transition__preview">
                    <span class="section-transition__preview-emoji">${nextSection.emoji}</span>
                    <div class="section-transition__preview-info">
                        <div class="section-transition__preview-label">Próxima seção</div>
                        <div class="section-transition__preview-name">Seção ${nextSection.id}: ${nextSection.name}</div>
                    </div>
                </div>
                <div class="section-transition__buttons">
                    <button class="section-transition__btn section-transition__btn--start" id="section-start-next">
                        ${startButtonIcon} ${startButtonText}
                    </button>
                    ${canSkip ? `
                    <button class="section-transition__btn section-transition__btn--skip" id="section-skip-next">
                        ⏭️ ${skipButtonText}
                    </button>
                    ` : ''}
                </div>
            </div>
        `;
    }

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
                // Para pergunta 1.1, pré-preencher com data/hora atual
                let defaultValue = null;
                if (question.id === '1.1') {
                    defaultValue = this._generateCurrentDateTime();
                }

                return new TextInput({
                    placeholder: question.hint || 'Digite sua resposta...',
                    validation: question.validation || {},
                    defaultValue: defaultValue,
                    onSubmit: (value, onError) => {
                        this._handleInputSubmit(value, question, null, onError);
                    }
                });
        }
    }

    /**
     * Trata resposta do componente de input
     */
    _handleInputSubmit(answer, question, option = null, onError = null) {
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

        // Verificar se é uma pergunta follow-up (tem mais de um ponto no ID)
        const dotCount = (question.id.match(/\./g) || []).length;
        const isFollowUp = dotCount > 1;  // Ex: "1.5.1" tem 2 pontos, "1.5" tem 1 ponto

        if (isFollowUp && this.followUpQueue.length > 0) {
            // Ainda há follow-ups na fila
            setTimeout(() => {
                this._showNextFollowUp();
            }, 500);
            return;
        }

        // Verificar follow-up da pergunta atual
        if (question.followUp && question.followUp.condition) {
            const conditionMet = answer.toLowerCase().includes(question.followUp.condition.toLowerCase());

            if (conditionMet) {
                // Suportar múltiplas perguntas (questions array)
                if (question.followUp.questions && question.followUp.questions.length > 0) {
                    // Adicionar todas as perguntas follow-up à fila
                    this.followUpQueue = [...question.followUp.questions];
                    setTimeout(() => {
                        this._showNextFollowUp();
                    }, 500);
                    return;
                }
                // Suportar uma única pergunta (question singular) - backward compatibility
                else if (question.followUp.question) {
                    setTimeout(() => {
                        this._showQuestion(question.followUp.question);
                    }, 500);
                    return;
                }
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
     * Mostra próxima pergunta follow-up da fila
     */
    _showNextFollowUp() {
        if (this.followUpQueue.length > 0) {
            const nextQuestion = this.followUpQueue.shift();
            this._showQuestion(nextQuestion);
        } else {
            // Todas as follow-ups respondidas, avançar para próxima pergunta principal
            this.currentQuestionIndex++;
            this._updateBadge();
            setTimeout(() => {
                this._showCurrentQuestion();
            }, 500);
        }
    }

    /**
     * Mostra uma pergunta específica com o input correto
     */
    _showQuestion(question) {
        // Adicionar mensagem do bot com o número da pergunta
        const questionWithNumber = `${question.id}) ${question.text}`;
        this._addBotMessage(questionWithNumber, question.hint);

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

    /**
     * Bind de eventos
     */
    _bindEvents() {
        // Copiar texto gerado
        const copyBtn = this.container.querySelector('#section-copy-btn');
        if (copyBtn) {
            copyBtn.addEventListener('click', () => this._copyGeneratedText());
        }

        // Iniciar próxima seção
        const startNextBtn = this.container.querySelector('#section-start-next');
        if (startNextBtn) {
            startNextBtn.addEventListener('click', () => {
                // Passar "sim" como resposta pré-definida para o skipQuestion da próxima seção
                this.onNavigateNext(this.sectionId + 1, { preAnswerSkipQuestion: 'sim' });
            });
        }

        // Pular próxima seção
        const skipNextBtn = this.container.querySelector('#section-skip-next');
        if (skipNextBtn) {
            skipNextBtn.addEventListener('click', () => {
                this.onSkip(this.sectionId + 1);
            });
        }

        // Voltar para seção atual
        const backBtn = this.container.querySelector('#section-back-btn');
        if (backBtn) {
            backBtn.addEventListener('click', () => {
                this.onNavigateBack();
            });
        }
    }

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

    /**
     * Adiciona mensagem do bot
     */
    _addBotMessage(text, hint = null) {
        this.messages.push({ type: 'bot', text, hint });
        this._updateChat();
    }

    /**
     * Adiciona mensagem do usuário
     */
    _addUserMessage(text) {
        this.messages.push({ type: 'user', text });
        this._updateChat();
    }

    /**
     * Atualiza área de chat
     */
    _updateChat() {
        if (this.chatEl) {
            this.chatEl.innerHTML = this._renderMessages();
            this._scrollToBottom();
        }
    }

    /**
     * Scroll para o final do chat
     */
    _scrollToBottom() {
        if (this.chatEl) {
            this.chatEl.scrollTop = this.chatEl.scrollHeight;
        }
    }

    /**
     * Atualiza badge de status
     */
    _updateBadge() {
        const badge = this.container.querySelector('.section-header__badge');
        if (badge) {
            badge.textContent = this._getStatusLabel();
        }
    }

    /**
     * Completa a seção
     */
    async _completeSection() {
        this.state = 'completed';

        // Simular texto gerado (será substituído pela API real na Fase 4)
        this.generatedText = `[Texto da Seção ${this.sectionId} será gerado pela API]\n\nRespostas coletadas:\n${
            Object.entries(this.answers).map(([k, v]) => `- ${k}: ${v}`).join('\n')
        }`;

        // Callback - AGUARDAR conclusão antes de renderizar
        await this.onComplete(this.sectionId, this.answers);

        // Re-renderizar SOMENTE depois que onComplete terminar
        this.render();
    }

    /**
     * Pula a seção
     */
    _skipSection() {
        this.state = 'skipped';
        this.onSkip(this.sectionId);
        this.render();
    }

    /**
     * Copia texto gerado
     */
    _copyGeneratedText() {
        if (!this.generatedText) return;

        navigator.clipboard.writeText(this.generatedText).then(() => {
            const copyBtn = this.container.querySelector('#section-copy-btn');
            if (copyBtn) {
                copyBtn.textContent = '✅ Copiado!';
                setTimeout(() => {
                    copyBtn.textContent = '📋 Copiar';
                }, 2000);
            }
        });
    }

    /**
     * Mostra transição com fade
     */
    fadeOut() {
        return new Promise(resolve => {
            this.container.classList.remove('section-container--visible');
            this.container.classList.add('section-container--hidden');
            setTimeout(resolve, 200);
        });
    }

    /**
     * Mostra seção com fade
     */
    fadeIn() {
        return new Promise(resolve => {
            this.container.classList.remove('section-container--hidden');
            this.container.classList.add('section-container--visible');
            setTimeout(resolve, 200);
        });
    }

    /**
     * Define texto gerado (vem da API)
     */
    setGeneratedText(text) {
        this.generatedText = text;
        // Não precisa renderizar aqui - _completeSection() já vai renderizar após onComplete
        // Se precisar atualizar em outros contextos, pode descomentar:
        // if (this.state === 'completed') {
        //     this.render();
        // }
    }

    /**
     * Retorna estado atual
     */
    getState() {
        return {
            sectionId: this.sectionId,
            state: this.state,
            answers: this.answers,
            messages: this.messages,
            currentQuestionIndex: this.currentQuestionIndex,
            generatedText: this.generatedText
        };
    }

    /**
     * Gera string com data e hora atual no formato: "31/12/2025, 14h30, terça-feira"
     * Usada como pré-preenchimento para pergunta 1.1
     */
    _generateCurrentDateTime() {
        const now = new Date();

        // Formatar dia/mês
        const day = String(now.getDate()).padStart(2, '0');
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const year = now.getFullYear();
        const date = `${day}/${month}/${year}`;

        // Formatar hora
        const hour = String(now.getHours()).padStart(2, '0');
        const minute = String(now.getMinutes()).padStart(2, '0');
        const time = `${hour}h${minute}`;

        // Dia da semana em português
        const daysOfWeek = ['domingo', 'segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira', 'sábado'];
        const dayOfWeek = daysOfWeek[now.getDay()];

        return `${date}, ${time}, ${dayOfWeek}`;
    }
}
